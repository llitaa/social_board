#!/usr/bin/env python3
"""Put a post Anton wrote or approved outside the pipeline (e.g. library/drafts/examples/ex-money.json) on the board as a draft.
No model call. The JSON holds text, graphic (eyebrow, title, lines, footer), pillar, optional topic id and signals.
  python3 pipeline/import_draft.py library/drafts/examples/ex-money.json                 -> next free personal slot
  python3 pipeline/import_draft.py library/drafts/examples/ex-money.json --slot "2026-11-02 07:30"
A --slot that already holds an undecided draft moves that draft to the next free personal slot after the last planned one."""
import json, os, re, sys
from datetime import date, datetime, timedelta
from common import CFG, LIB, read_csv, write_csv, log
import draft, rules_check, inventory as inv

def next_free_after(plan, after):
    taken = {(r.get("planned") or "")[:10] for r in plan if r["channel"] == "linkedin" and r["status"] not in ("dropped", "skipped", "idea", "blocked")}
    d = after + timedelta(days=1); days = draft.SLOTS["personal"]["days"]
    while True:
        if d.strftime("%a") in days and d.isoformat() not in taken: return datetime.strptime(f"{d} {draft.SLOTS['personal']['time']}", "%Y-%m-%d %H:%M")
        d += timedelta(days=1)

def main():
    if len(sys.argv) < 2: print(__doc__); return
    e = json.load(open(sys.argv[1], encoding="utf-8")); plan, fields = read_csv(CFG["content_plan"])
    text = rules_check.fix_orthography(e["text"].strip(), "personal"); v = rules_check.check(text, "personal", e.get("signals"))
    if v: print("rules:", v); return
    if "--slot" in sys.argv:
        dt = datetime.strptime(sys.argv[sys.argv.index("--slot") + 1], "%Y-%m-%d %H:%M")
        for r in plan:   # the draft that holds this slot moves to the end of the queue
            if r["channel"] == "linkedin" and r["status"] == "draft" and (r.get("planned") or "")[:16] == dt.strftime("%Y-%m-%d %H:%M"):
                last = max(date.fromisoformat(x["planned"][:10]) for x in plan if x["channel"] == "linkedin" and len(x.get("planned") or "") >= 10 and x["status"] not in ("dropped", "skipped"))
                nd = next_free_after(plan, last); r["planned"] = nd.strftime("%Y-%m-%d %H:%M"); r["notes"] = f"[moved {date.today()}: slot given to an imported post] " + r.get("notes", "")
                log("moved", os.path.basename(r.get("caption_ref", ""))[:11], "to", r["planned"])
    else:
        slots = draft.open_slots(plan, date.today()); per = [s for s in slots if s[1] == "personal"]
        dt = per[0][0] if per else next_free_after(plan, max(date.fromisoformat(x["planned"][:10]) for x in plan if x["channel"] == "linkedin" and len(x.get("planned") or "") >= 10 and x["status"] not in ("dropped", "skipped")))
    ids = draft.next_ids(plan); num = ids["post"] + 1; cid = f"li-post-{num:02d}"
    slug = re.sub(r"[^a-z0-9]+", "-", e["graphic"].get("title", e["pillar"]).lower()).strip("-")[:28]; base = f"{cid}-{slug}"
    open(os.path.join(draft.DRAFTS, base + ".txt"), "w", encoding="utf-8").write(text + "\n")
    png = draft.render_graphic(e["graphic"], base, brand="personal")
    meta = {"id": cid, "channel": "personal", "pillar": e["pillar"], "topic": e.get("topic", ""), "memo": "", "photo": "", "neighbour_shoots": [], "model": "anton",
            "created": datetime.now().isoformat(timespec="seconds"), "versions": [], "graphic": e["graphic"], "card": None, "signals": e.get("signals")}
    json.dump(meta, open(os.path.join(draft.DRAFTS, base + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    plan.append({"id": str(max(int(r["id"]) for r in plan if r["id"].isdigit()) + 1), "campaign": "linkedin-anton", "channel": "linkedin", "slot": slug,
                 "asset": f"library/drafts/{base}.png (1200x1200 graphic; source library/drafts/{base}.html)" if png else "", "format": "grafik-post", "language": "de",
                 "caption_ref": f"library/drafts/{base}.txt", "planned": dt.strftime("%Y-%m-%d %H:%M"), "status": "draft",
                 "notes": f"[imported {date.today()} pillar={e['pillar']} topic={e.get('topic', '-')} photo=-] {e['graphic'].get('title', '')}"})
    write_csv(CFG["content_plan"], plan, fields)
    if e.get("topic"): inv.set_status(e["topic"], "drafted", cid)
    print(f"{cid} on the board at {dt:%a %d.%m. %H:%M} (next chain run pushes it; or: zsh pipeline/run.sh fast)")

if __name__ == "__main__": main()
