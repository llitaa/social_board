#!/usr/bin/env python3
"""The system fetches what fits (03.11.2026, text since 04.11.). For every open draft on this board it looks at what the OTHER
boards in a common group have made available: shared photos (index.csv share = network) and public material (their published
posts with link, the facts of their confirmed profile from their website, memos marked for the network). Word overlap makes a
shortlist; one small model call per card and kind asks whether ONE piece fits so well that the person would say yes.
Result: board-data/proposals.json {card id: photo proposal, card id + "#t": text proposal}, shown on the card and in the feed
"Für dich gefunden" with "Ja, nehmen" / "Nein" (api.php a=proposal; apply_decisions.py does the rest: photo on the card with
"Foto: Name", or one sentence in the author's voice plus "Gedanke von Name" and link in the text). "Nichts Passendes" is a valid
answer and is remembered until more material appears. Never posts anything; never proposes this board's own material.
Model calls: config llm.auto, process.py, or llm.match_auto (Anton, 04.11.: matching may run in the background on his board)."""
import json, os, re, shutil, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CFG, LIB, ROOT, BOARD_LOCAL, USER, boards, profile, jload, jdump, log, read_csv, resolve
import yaml

PROP = os.path.join(BOARD_LOCAL, "proposals.json")
STOP = set("""und oder aber der die das den dem des ein eine einer eines einem einen ist sind war waren wird werden hat haben habe nicht auch noch mit von für auf aus bei nach über
unter vor zu zum zur als wie wenn dann dass weil ich wir sie ihr mein meine dein deine sein seine ihre unser unsere euer eure sich man es er im am an in um bis durch ohne
the and for with from that this these those have has had was were are not but you your they their our his her its into onto over under about after before while than then
heute morgen dieser diese dieses jeder jede jedes mehr sehr schon dort hier wieder immer ganz einfach genau""".split())
KIND = {"post": "Beitrag", "fact": "Website", "memo": "Sprachnotiz"}

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
    """board-data/network.json for the Profil tab: my groups, who else is in each, how many photos and texts they share (no model call)."""
    me = USER or "anton"; bs = boards(); out = []
    for g in bs.get(me, {}).get("groups", []):
        members = []
        for slug, b in bs.items():
            if slug == me or g not in b.get("groups", []): continue
            rows, _ = read_csv(os.path.join(b["lib"], "photos", "index.csv"))
            members.append({"name": b["name"], "shared": sum(1 for r in rows if r.get("share") == "network" and r.get("status") not in ("deleted", "hold") and not r.get("owner")), "texts": len(board_texts(slug, b))})
        out.append({"group": g, "members": members})
    jdump(os.path.join(BOARD_LOCAL, "network.json"), {"groups": out, "ts": datetime.now().isoformat(timespec="minutes")})

def main():
    network()
    if (CFG.get("llm") or {}).get("match_auto"): os.environ["LLM_INTERACTIVE"] = "1"   # Anton 04.11.: matching is the one model step allowed in his background chain (small calls, the demo needs it)
    pool = shared_photos(); tpool = shared_texts(); props = jload(PROP, {})
    if not pool and not tpool:
        if props: jdump(PROP, props)
        log("match: nothing shared on the other boards"); return
    from llm import llm_json, allowed
    who = profile(); de = who["lang"] == "de"; n = 0; strict = bool((CFG.get("match") or {}).get("strict", True))   # pilot 04.11.: strict false = propose a real bridge, the person decides
    drafts = open_drafts()
    for cid, text, r in drafts:
        if not pool: break
        p = props.get(cid, {})
        if p.get("state") in ("accept", "decline"): continue
        if p.get("state") == "none" and p.get("seen", 0) >= len(pool): continue      # already judged against these photos
        if p.get("state") == "open": continue
        tw = words(text) | words(r.get("notes", ""))
        ranked = sorted(pool, key=lambda c: (-len(tw & words(c["text"])), c["taken"]), reverse=False)[:6]
        if not allowed(): jdump(PROP, props); log("match waits for process.py"); return
        cand = "\n".join(f"{i + 1}. von {c['owner_name']}, {c['taken'] or 'ohne Datum'}: {c['scene'] or c['note'] or c['tags']} [{c['tags']}]" for i, c in enumerate(ranked))
        prompt = f"""Ein LinkedIn-Entwurf und Fotos, die andere Personen für ihr Netzwerk freigegeben haben. Passt genau EIN Foto so gut zum Entwurf, dass der Autor es gern nehmen würde (gleiche Situation, gleicher Ort oder dieselbe Stimmung, nicht nur dasselbe Stichwort)? Kein Foto nehmen ist die Regel, ein Foto die Ausnahme. Antworte nur mit einem JSON-Objekt:
{{"pick": <Nummer oder 0>, "why": "ein Satz in {'Deutsch' if de else 'Englisch'}, Du-Form, warum es passt (leer bei 0)"}}

=== Entwurf ===
{text[:1800]}

=== Fotos ===
{cand}
"""
        try: d = llm_json("match", prompt)
        except Exception as e: log("match failed", cid, repr(e)[:200]); continue
        k = int(d.get("pick") or 0)
        if 1 <= k <= len(ranked):
            c = ranked[k - 1]; os.makedirs(os.path.join(BOARD_LOCAL, "img", "thumbs"), exist_ok=True)
            th = f"p-{c['owner']}-{c['id']}.jpg"
            if os.path.isfile(c["thumb"]): shutil.copy2(c["thumb"], os.path.join(BOARD_LOCAL, "img", "thumbs", th))
            props[cid] = {"kind": "photo", "photo": c["id"], "owner": c["owner"], "owner_name": c["owner_name"], "file": c["file"], "thumb": f"data/img/thumbs/{th}", "scene": c["scene"] or c["note"],
                          "why": str(d.get("why", ""))[:240], "ts": datetime.now().isoformat(timespec="minutes"), "state": "open"}; n += 1
            log(f"proposal for {cid}: {c['id']} von {c['owner_name']}")
        else: props[cid] = {"kind": "photo", "state": "none", "seen": len(pool), "ts": datetime.now().isoformat(timespec="minutes")}
    for cid, text, r in drafts:
        if not tpool: break
        key = cid + "#t"; p = props.get(key, {})
        if p.get("state") in ("accept", "decline", "open"): continue
        if p.get("state") == "none" and p.get("seen", 0) >= len(tpool): continue    # already judged against this material
        tw = words(text) | words(r.get("notes", ""))
        ranked = sorted(tpool, key=lambda c: -len(tw & words(c["text"])))[:5]
        if not allowed(): jdump(PROP, props); log("match waits for process.py"); return
        cand = "\n\n".join(f"{i + 1}. {KIND.get(c['kind'], c['kind'])} von {c['owner_name']}: {c['title']}\n{c['text'][:700]}" for i, c in enumerate(ranked))
        rule = ("Nichts nehmen ist die Regel, ein Stück die Ausnahme." if strict else
                "Gibt es eine echte Brücke (dieselbe Entscheidung, dieselbe Situation beim Kunden, ein Beleg oder Gegenbeispiel aus der anderen Branche), schlage sie vor: der Autor entscheidet mit Ja oder Nein. Nur wenn gar keine Brücke trägt, 0.")
        prompt = f"""Ein LinkedIn-Entwurf von {who['name']} und Material, das andere Personen aus dem Netzwerk öffentlich gemacht haben (eigene Beiträge, Fakten ihrer Website, Sprachnotizen). Passt EIN Stück so, dass {who['first']} dazu einen Satz in den eigenen Entwurf aufnehmen würde, mit Nennung der Person: dieselbe Situation aus einer anderen Branche, ein Beleg, ein Gegenbeispiel, nicht nur dasselbe Stichwort? {rule} Nichts erfinden: nur, was im Material steht. Antworte nur mit einem JSON-Objekt:
{{"pick": <Nummer oder 0>, "why": "ein Satz in {'Deutsch' if de else 'Englisch'}, Du-Form, warum es passt (leer bei 0)", "line": "ein bis zwei Sätze in der Stimme des Entwurfs, die den Gedanken aufnehmen und die Person mit Namen nennen, {'Deutsch' if de else 'Englisch'} (leer bei 0)"}}

=== Entwurf ===
{text[:1800]}

=== Material ===
{cand}
"""
        try: d = llm_json("match", prompt)
        except Exception as e: log("match failed", key, repr(e)[:200]); continue
        k = int(d.get("pick") or 0); line = str(d.get("line") or "").strip()
        if 1 <= k <= len(ranked) and line:
            c = ranked[k - 1]
            props[key] = {"kind": "text", "card": cid, "src": c["kind"], "item": c["id"], "owner": c["owner"], "owner_name": c["owner_name"], "title": c["title"], "excerpt": c["text"][:240], "url": c["url"],
                          "why": str(d.get("why", ""))[:240], "line": line[:400], "ts": datetime.now().isoformat(timespec="minutes"), "state": "open"}; n += 1
            log(f"text proposal for {cid}: {c['kind']} {c['id']} von {c['owner_name']}")
        else: props[key] = {"kind": "text", "state": "none", "seen": len(tpool), "ts": datetime.now().isoformat(timespec="minutes")}
    jdump(PROP, props); log(f"match: {n} new proposal(s), {len(pool)} shared photos and {len(tpool)} texts on the other boards")

if __name__ == "__main__": main()
