#!/usr/bin/env python3
"""The system fetches what fits (03.11.2026; since 04.11. evening as its own tile, Anton: "should just be an item in the pipeline").
For this board it looks at what the OTHER boards in a common group have made available: shared photos, published posts with link,
memos marked for the network (never website facts: marketing copy is not a thought). One small model call asks whether ONE piece
is something this person would make a post of (same decision or customer situation from another trade, a proof, a counter-example).
If so, draft.py writes a new draft from it in the person's voice, the teammate named in the text, "Foto: Name" or "Gedanke von Name:
link" before the hashtags, pillar network; the card shows the teammate's initials. At most one such post a week per board; existing
drafts are never touched; approved posts never. The old per-draft proposals (proposals.json) are no longer produced.
Earlier docstring: For every open draft on this board it looks at what the OTHER
boards in a common group have made available: shared photos (index.csv share = network) and public material (their published
posts with link, the facts of their confirmed profile from their website, memos marked for the network). Word overlap makes a
shortlist; one small model call per card and kind asks whether ONE piece fits so well that the person would say yes.
Result: board-data/proposals.json {card id: photo proposal, card id + "#t": text proposal}, shown on the card and in the feed
"Für dich gefunden" with "Ja, nehmen" / "Nein" (api.php a=proposal; apply_decisions.py does the rest: photo on the card with
"Foto: Name", or one sentence in the author's voice plus "Gedanke von Name" and link in the text). "Nichts Passendes" is a valid
answer and is remembered until more material appears. Never posts anything; never proposes this board's own material.
Model calls: config llm.auto, process.py, or llm.match_auto (Anton, 04.11.: matching may run in the background on his board)."""
import csv, json, os, re, shutil, sys
from datetime import date, datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CFG, LIB, ROOT, BOARD_LOCAL, USER, boards, profile, jload, jdump, log, read_csv, write_csv, resolve
import yaml

PROP = os.path.join(BOARD_LOCAL, "proposals.json")
STOP = set("""und oder aber der die das den dem des ein eine einer eines einem einen ist sind war waren wird werden hat haben habe nicht auch noch mit von für auf aus bei nach über
unter vor zu zum zur als wie wenn dann dass weil ich wir sie ihr mein meine dein deine sein seine ihre unser unsere euer eure sich man es er im am an in um bis durch ohne
the and for with from that this these those have has had was were are not but you your they their our his her its into onto over under about after before while than then
heute morgen dieser diese dieses jeder jede jedes mehr sehr schon dort hier wieder immer ganz einfach genau""".split())
KIND = {"post": "Beitrag", "fact": "Website", "memo": "Sprachnotiz", "photo": "Foto"}
USED = os.path.join(LIB, "network-used.json")   # what this board already made a post from, judged as no fit, or failed on

def words(t): return {w for w in re.findall(r"[a-zäöüß]{4,}", (t or "").lower()) if w not in STOP}

def others():
    """The other boards that share a group with this one. A group is who shares with whom; a board may be in several (04.11.)."""
    me = USER or "anton"; bs = boards(); mine = set(bs.get(me, {}).get("groups", []))
    return [(slug, b) for slug, b in bs.items() if slug != me and (mine & set(b.get("groups", [])))]

def shared_photos():
    """Shared photos of every other board, with the owner's name and the path to the file and thumbnail."""
    out = []
    for slug, b in others():
        rows, _ = read_csv(os.path.join(b["lib"], "photos", "index.csv"))
        for r in rows:
            if r.get("share") != "network" or r.get("status") in ("deleted", "hold") or r.get("owner"): continue
            out.append({"id": r["id"], "owner": slug, "owner_name": b["name"], "file": os.path.join(b["lib"], r["file"]), "thumb": os.path.join(b["mirror"], "img", "thumbs", r["id"] + ".jpg"),
                        "scene": r.get("scene", ""), "tags": r.get("tags", ""), "note": r.get("note", ""), "taken": (r.get("taken") or "")[:10], "text": " ".join([r.get("scene", ""), r.get("tags", ""), r.get("note", "")])})
    return out

def board_texts(slug, b):
    """Public material of one board: published posts (text and link), the facts of a confirmed profile (from the person's own
    website), memos marked for the network (index.csv share = network). Nothing private, nothing unpublished."""
    items = []
    plog = os.path.expanduser((yaml.safe_load(open(os.path.join(ROOT, "config.yaml"))) or {}).get("posts_log", "")) if slug == "anton" else os.path.join(b["dir"], "campaign", "posts-log.csv")
    rows, _ = read_csv(plog) if plog and os.path.isfile(plog) else ([], [])
    dirs = [os.path.join(b["lib"], "drafts"), os.path.join(b["lib"], "published")]   # a draft's text stays in drafts/; older posts have their text in published/
    files = [(d_, x) for d_ in dirs if os.path.isdir(d_) for x in sorted(os.listdir(d_))]
    for r in rows:
        pid = r.get("post_id", "")
        f = next((os.path.join(d_, x) for d_, x in files if x.startswith(pid + "-") and x.endswith(".txt") and not re.search(r"\.v\d+\.txt$", x)), None)
        if not pid or not f: continue
        try: text = open(f, encoding="utf-8").read().strip()
        except OSError: continue
        if not text: continue
        items.append({"id": pid, "kind": "post", "owner": slug, "owner_name": b["name"], "title": (r.get("hook") or text.split("\n")[0])[:120], "text": text, "url": r.get("link", ""), "date": r.get("date", "")})
    pr = jload(os.path.join(b["lib"], "profile.json"), {})
    facts = (pr.get("facts") or "").strip()
    if facts and pr.get("confirmed"):
        items.append({"id": "facts", "kind": "fact", "owner": slug, "owner_name": b["name"], "title": f"{pr.get('company') or b['name']}: {(pr.get('role') or '')[:90]}", "text": facts, "url": pr.get("website", ""), "date": ""})
    mi = os.path.join(b["lib"], "memos", "index.csv"); mrows, _ = read_csv(mi) if os.path.isfile(mi) else ([], [])
    for m in mrows:
        if m.get("share") != "network": continue
        tp = os.path.join(b["lib"], "memos", os.path.splitext(m["id"])[0] + ".txt")
        try: text = open(tp, encoding="utf-8").read().strip()
        except OSError: continue
        if text: items.append({"id": m["id"], "kind": "memo", "owner": slug, "owner_name": b["name"], "title": text[:100], "text": text, "url": "", "date": (m.get("recorded") or "")[:10]})
    return items

def shared_texts():
    out = []
    for slug, b in others(): out += board_texts(slug, b)
    return out

def open_drafts():
    plan, _ = read_csv(CFG["content_plan"]); out = []
    for r in plan:
        if r.get("channel") != "linkedin" or r.get("status") not in ("draft", "change") or not r.get("caption_ref"): continue
        tp = resolve(r["caption_ref"]); text = open(tp, encoding="utf-8").read() if os.path.isfile(tp) else ""
        if text: out.append(("-".join(os.path.basename(r["caption_ref"]).split("-")[0:3]), text, r))
    return out

def network():
    """board-data/network.json: my groups, who else is in each, how many photos and texts they share, and the shared material
    itself (05.11.: the board shows it under Fotos and Netzwerk, a tap makes a post from one piece). No model call."""
    me = USER or "anton"; bs = boards(); out = []
    for g in bs.get(me, {}).get("groups", []):
        members = []
        for slug, b in bs.items():
            if slug == me or g not in b.get("groups", []): continue
            rows, _ = read_csv(os.path.join(b["lib"], "photos", "index.csv"))
            members.append({"name": b["name"], "shared": sum(1 for r in rows if r.get("share") == "network" and r.get("status") not in ("deleted", "hold") and not r.get("owner")), "texts": len(board_texts(slug, b))})
        out.append({"group": g, "members": members})
    used = jload(USED, {}); nd = os.path.join(BOARD_LOCAL, "img", "net"); os.makedirs(nd, exist_ok=True); shared = []; keep = set()
    for it in material():
        u = used.get(it["key"], {}); e = {"key": it["key"], "kind": it["kind"], "owner": it["owner"], "owner_name": it["owner_name"], "title": it["title"].replace(" · ", ", ").replace("·", ",")[:140], "date": it["date"], "url": it["url"],
                                          "state": u.get("state", ""), "card": u.get("card", ""), "ts": u.get("ts", "")}
        if it["kind"] == "photo":
            c = it["photo"]; fn = f"{it['owner']}-{it['id']}.jpg"; dst = os.path.join(nd, fn); keep.add(fn)
            if not os.path.isfile(dst):
                try:
                    if os.path.isfile(c["thumb"]): shutil.copyfile(c["thumb"], dst)
                    else:
                        import photo_index as ph; ph.thumb(c["file"], dst)
                except Exception as ex: log("network thumb failed", it["key"], repr(ex)[:120])
            if os.path.isfile(dst): e["thumb"] = f"data/img/net/{fn}"
            e["scene"] = c["scene"]
        shared.append(e)
    for fn in os.listdir(nd):   # a photo no longer shared leaves this board too
        if fn not in keep: os.remove(os.path.join(nd, fn))
    shared.sort(key=lambda e: e["date"], reverse=True)
    jdump(os.path.join(BOARD_LOCAL, "network.json"), {"groups": out, "shared": shared, "ts": datetime.now().isoformat(timespec="minutes")})

REQ = os.path.join(LIB, "network-request.json")   # items the person tapped on the board ("Daraus einen Post machen"), written by apply_decisions, one draft each

def material():
    """Everything the other boards share, as one list: photos, published posts, memos. Website facts stay out (04.11.)."""
    items = []
    for c in shared_photos():
        items.append({"key": f"{c['owner']}:photo:{c['id']}", "kind": "photo", "id": c["id"], "text": c["text"], "title": c["scene"] or c["note"] or c["tags"], "url": "", "date": c["taken"], "owner": c["owner"], "owner_name": c["owner_name"], "photo": c})
    for t in shared_texts():
        if t["kind"] == "fact": continue
        items.append({"key": f"{t['owner']}:{t['kind']}:{t['id']}", "kind": t["kind"], "id": t["id"], "text": t["text"], "title": t["title"], "url": t["url"], "date": t["date"], "owner": t["owner"], "owner_name": t["owner_name"]})
    return items

def next_slot(plan):
    """The next open personal slot; when the horizon is full, the next personal slot day after tomorrow (two cards at one slot: the person decides)."""
    import draft
    per = [dt for dt, c in draft.open_slots(plan, date.today()) if c == "personal"]
    if per: return per[0]
    s = CFG["slots"]["personal"]; d = date.today() + timedelta(days=1)
    for _ in range(14):
        if d.strftime("%a") in s["days"]: return datetime.strptime(f"{d} {s['time']}", "%Y-%m-%d %H:%M")
        d += timedelta(days=1)
    return None

def network_drafts(force_item=None):
    """force_item = "owner:kind:id" (CLI --item, demo or admin): that piece, now, regardless of the weekly limit and earlier verdicts."""
    items = material(); used = jload(USED, {}); now = datetime.now().isoformat(timespec="minutes")
    if not items: log("network: nothing shared on the other boards"); return
    week_ago = (datetime.now() - timedelta(days=7)).isoformat(timespec="minutes"); day_ago = (datetime.now() - timedelta(days=1)).isoformat(timespec="minutes")
    if force_item:
        items = [i for i in items if i["key"] == force_item]
        if not items: log("network: item not shared:", force_item); return
        used.pop(force_item, None)
    elif any(v.get("state") == "drafted" and v.get("ts", "") >= week_ago for v in used.values()): log("network: one post from the network this week already"); return
    def fresh(i):
        u = used.get(i["key"])
        if not u: return True
        if u.get("state") == "none": return u.get("seen", 0) < len(items)
        if u.get("state") == "failed": return u.get("ts", "") < day_ago
        return False
    cands = sorted([i for i in items if fresh(i)], key=lambda i: i["date"], reverse=True)[:10]
    if force_item: cands = items
    if not cands: log("network: nothing new to judge"); return
    from llm import llm_json, allowed
    if not allowed(): log("match waits for process.py"); return
    who = profile(); de = who["lang"] == "de"; first = who["first"]; strict = bool((CFG.get("match") or {}).get("strict", True))
    pos_f = os.path.join(LIB, "positioning.md"); pos = open(pos_f, encoding="utf-8").read()[:1500] if os.path.isfile(pos_f) else ""
    inv_rows, _ = read_csv(os.path.join(LIB, "inventory.csv")); topics = [r["topic"] for r in inv_rows if r.get("status") == "unused"][:15]
    cand = "\n\n".join(f"{n + 1}. {KIND.get(c['kind'], c['kind'])} von {c['owner_name']}, {c['date'] or 'ohne Datum'}: {c['title'][:120]}\n{c['text'][:600]}" for n, c in enumerate(cands))
    rule = (f"Dieses Stück ist gesetzt: pick ist 1. Finde die Brücke zu {first}s Themen und Lesern und schreibe den Gedanken dazu." if force_item else
            "Nichts nehmen ist die Regel, ein Stück die Ausnahme." if strict else "Gibt es eine echte Brücke, nimm sie: der Autor entscheidet am Ende mit einem Tipp. Nur wenn gar nichts trägt, 0.")
    prompt = f"""{who['name']} postet auf LinkedIn für die eigenen Kunden. Worum es in diesen Posts geht:
{pos or '-'}
Offene Themen: {'; '.join(topics) or '-'}

Unten Material, das andere aus dem Netzwerk freigegeben haben (Foto, veröffentlichter Beitrag, Sprachnotiz). Gibt es EIN Stück, aus dem {first} einen eigenen Post machen würde: dieselbe Entscheidung oder dieselbe Kundensituation aus einer anderen Branche, ein Beleg, ein Gegenbeispiel, verbunden mit eigener Erfahrung? {rule} Nichts erfinden: nur, was im Material und in den Themen steht. Antworte nur mit einem JSON-Objekt:
{{"pick": <Nummer oder 0>, "why": "ein Satz in {'Deutsch' if de else 'Englisch'}, Du-Form, warum (leer bei 0)", "topic": "Titel des Posts, max. 8 Wörter (leer bei 0)", "angle": "zwei bis drei Sätze in {'Deutsch' if de else 'Englisch'}: der eigene Gedanke von {first} zu diesem Material, der Post beginnt damit; die Person wird mit Namen genannt (leer bei 0)"}}

=== Material ===
{cand}
"""
    try: d = llm_json("match", prompt)
    except Exception as e: log("network judge failed", repr(e)[:200]); return
    k = int(d.get("pick") or 0); angle = str(d.get("angle") or "").strip()
    if not (1 <= k <= len(cands)) or not angle:
        for c in cands: used[c["key"]] = {"state": "none", "seen": len(items), "ts": now}
        jdump(USED, used); log(f"network: nothing fits ({len(cands)} judged)"); return
    it = cands[k - 1]
    import draft, photo_index as ph
    plan, fields = read_csv(CFG["content_plan"]); idx = {r["id"]: r for r in ph.read_index()}
    dt = next_slot(plan)
    if not dt: log("network: no slot"); return
    topic = {"id": f"net-{it['key']}", "pillar": "network", "topic": (str(d.get("topic") or "") or it["title"])[:80], "tags": "", "source": f"Netzwerk: {it['owner_name']}", "status": "unused", "used_in": "",
             "angle": f"{angle}\n\nMaterial von {it['owner_name']} ({KIND.get(it['kind'], it['kind'])}), die Person heisst genau so und wird im Text mit Vor- und Nachnamen genannt; keine Dankeszeile, kein Link, keine Quellenangabe am Ende (das System hängt die Zeile mit dem Namen selbst an):\n{it['text'][:1200]}"}
    prow = None; orig = ph.pick
    if it["kind"] == "photo":
        c = it["photo"]
        prow = ph.ingest(c["file"], note=f"von {c['owner_name']}", status="ready", copy=True, src="shared") or next((x for x in ph.read_index() if os.path.basename(x["file"]) == os.path.basename(c["file"])), None)
        if prow:
            rows = ph.read_index()
            for x in rows:
                if x["id"] == prow["id"]: x["owner"] = c["owner"]; x["share"] = ""
            ph.write_index(rows); idx = {r["id"]: r for r in rows}; ph.pick = lambda *a, **k: [prow]   # the shared photo is the photo of this post
    try: row = draft.draft_one(dt, "personal", plan, idx, topic=topic)
    except Exception as e: log("network draft failed", repr(e)[:300]); row = None
    finally: ph.pick = orig
    if not row:
        used[it["key"]] = {"state": "failed", "ts": now}; jdump(USED, used); log("network: draft not written (no photo in the pool, or rules)"); return
    tp = resolve(row["caption_ref"]); txt = open(tp, encoding="utf-8").read().rstrip()
    credit = f"Foto: {it['owner_name']}" if it["kind"] == "photo" else f"Gedanke von {it['owner_name']}" + (f": {it['url']}" if it["url"] else "")
    if credit not in txt:
        lines = txt.split("\n"); k = next((i for i, l in enumerate(lines) if l.strip().startswith("#")), len(lines))
        body = "\n".join(lines[:k]).rstrip(); rest = "\n".join(lines[k:]).strip()
        open(tp, "w", encoding="utf-8").write(body + "\n\n" + credit + ("\n\n" + rest if rest else "") + "\n")
    mp = os.path.splitext(tp)[0] + ".json"; meta = jload(mp, {}); meta["credit"] = it["owner_name"]; meta["network"] = {"owner": it["owner"], "kind": it["kind"], "item": it["id"], "why": str(d.get("why", ""))[:240]}; jdump(mp, meta)
    row["notes"] = f"[network {it['key']}] " + row.get("notes", ""); write_csv(CFG["content_plan"], plan, fields)
    cid = "-".join(os.path.basename(row["caption_ref"]).split("-")[0:3])
    used[it["key"]] = {"state": "drafted", "card": cid, "ts": now}; jdump(USED, used)
    ob = boards().get(it["owner"], {})
    if ob:
        f = os.path.join(ob["lib"], "log", "shared-uses.csv"); new = not os.path.isfile(f)
        with open(f, "a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["ts", "photo", "used_by", "used_by_name", "card"])
            if new: w.writeheader()
            w.writerow({"ts": now, "photo": it["id"] if it["kind"] == "photo" else f"Text: {it['title'][:60]}", "used_by": USER or "anton", "used_by_name": who["name"], "card": cid})
    log(f"network draft {cid} from {it['kind']} {it['id']} von {it['owner_name']}: {str(d.get('why', ''))[:100]}")

def main():
    network()
    if (CFG.get("llm") or {}).get("match_auto"): os.environ["LLM_INTERACTIVE"] = "1"   # Anton 04.11.: matching is the one model step allowed in his background chain
    if "--item" in sys.argv: network_drafts(sys.argv[sys.argv.index("--item") + 1]); network(); return
    req = jload(REQ, [])
    if req:
        from llm import allowed
        if not allowed(): log("network: requests wait for process.py", len(req)); return
        left = []
        for r in req:
            try: network_drafts(r["item"])
            except Exception as e: log("network request failed", r.get("item"), repr(e)[:200]); left.append(r)
        jdump(REQ, left) if left else os.path.isfile(REQ) and os.remove(REQ); network(); return
    network_drafts()

if __name__ == "__main__": main()
