#!/usr/bin/env python3
"""The system fetches what fits (03.11.2026). For every open draft on this board it looks at the photos the OTHER boards have
shared (index.csv share = network), shortlists by word overlap, and asks one small model call whether one of them fits this
draft so well that the person would say yes. Result: board-data/proposals.json {card id: {photo, owner, why, state}}, shown on
the card with "Ja, nehmen" / "Nein" (api.php a=proposal; apply_decisions.py does the rest). "Nichts Passendes" is a valid answer
and is remembered until more shared photos appear. Never posts anything; never proposes a photo of this board's own pool."""
import json, os, re, shutil, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CFG, LIB, BOARD_LOCAL, USER, boards, profile, jload, jdump, log, read_csv, resolve

PROP = os.path.join(BOARD_LOCAL, "proposals.json")
STOP = set("""und oder aber der die das den dem des ein eine einer eines einem einen ist sind war waren wird werden hat haben habe nicht auch noch mit von für auf aus bei nach über
unter vor zu zum zur als wie wenn dann dass weil ich wir sie ihr mein meine dein deine sein seine ihre unser unsere euer eure sich man es er im am an in um bis durch ohne
the and for with from that this these those have has had was were are not but you your they their our his her its into onto over under about after before while than then""".split())

def words(t): return {w for w in re.findall(r"[a-zäöüß]{4,}", (t or "").lower()) if w not in STOP}

def shared_photos():
    """Shared photos of every other board, with the owner's name and the path to the file and thumbnail."""
    out = []
    me = USER or "anton"; bs = boards(); mine = bs.get(me, {}).get("group", "bni-gilching")
    for slug, b in bs.items():
        if slug == me or b.get("group", "bni-gilching") != mine: continue   # a group is who shares with whom; other groups never see each other's material
        rows, _ = read_csv(os.path.join(b["lib"], "photos", "index.csv"))
        for r in rows:
            if r.get("share") != "network" or r.get("status") in ("deleted", "hold") or r.get("owner"): continue
            out.append({"id": r["id"], "owner": slug, "owner_name": b["name"], "file": os.path.join(b["lib"], r["file"]), "thumb": os.path.join(b["mirror"], "img", "thumbs", r["id"] + ".jpg"),
                        "scene": r.get("scene", ""), "tags": r.get("tags", ""), "note": r.get("note", ""), "taken": (r.get("taken") or "")[:10], "text": " ".join([r.get("scene", ""), r.get("tags", ""), r.get("note", "")])})
    return out

def open_drafts():
    plan, _ = read_csv(CFG["content_plan"]); out = []
    for r in plan:
        if r.get("channel") != "linkedin" or r.get("status") not in ("draft", "change") or not r.get("caption_ref"): continue
        tp = resolve(r["caption_ref"]); text = open(tp, encoding="utf-8").read() if os.path.isfile(tp) else ""
        if text: out.append(("-".join(os.path.basename(r["caption_ref"]).split("-")[0:3]), text, r))
    return out

def main():
    pool = shared_photos(); props = jload(PROP, {})
    if not pool:
        if props: jdump(PROP, props)
        log("match: no shared photos on the other boards"); return
    from llm import llm_json, allowed
    who = profile(); de = who["lang"] == "de"; n = 0
    for cid, text, r in open_drafts():
        p = props.get(cid, {})
        if p.get("state") in ("accept", "decline"): continue
        if p.get("state") == "none" and p.get("seen", 0) >= len(pool): continue      # already judged against these photos
        if p.get("state") == "open": continue
        tw = words(text) | words(r.get("notes", ""))
        ranked = sorted(pool, key=lambda c: (-len(tw & words(c["text"])), c["taken"]), reverse=False)[:6]
        if not allowed(): log("match waits for process.py"); return
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
            props[cid] = {"photo": c["id"], "owner": c["owner"], "owner_name": c["owner_name"], "file": c["file"], "thumb": f"data/img/thumbs/{th}", "scene": c["scene"] or c["note"],
                          "why": str(d.get("why", ""))[:240], "ts": datetime.now().isoformat(timespec="minutes"), "state": "open"}; n += 1
            log(f"proposal for {cid}: {c['id']} von {c['owner_name']}")
        else: props[cid] = {"state": "none", "seen": len(pool), "ts": datetime.now().isoformat(timespec="minutes")}
    jdump(PROP, props); log(f"match: {n} new proposal(s), {len(pool)} shared photos on the other boards")

if __name__ == "__main__": main()
