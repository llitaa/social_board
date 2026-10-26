#!/usr/bin/env python3
"""Model work on demand (Anton, 26.10.2026). The background chain (watch.py -> run.sh) no longer calls a model: config
llm.auto is false, so drafts for open slots, redrafts on notes, learning from notes and photo tags wait. This command,
run in a terminal when the Mac is open, does them in one go and shows what it did:
  python3 pipeline/process.py           what waits -> question -> full chain with model calls -> what came out
  python3 pipeline/process.py --status  only the first part
  python3 pipeline/process.py --yes     no question
Transcription (whisper.cpp, local) keeps running in the background; it costs no tokens."""
import os, subprocess, sys, time
from datetime import date
from common import CFG, ROOT, LIB, read_csv, resolve, log

RUN = os.path.join(ROOT, "pipeline", "run.sh"); LOCK = os.path.join(LIB, "log", ".run.lock"); CALLS = os.path.join(LIB, "log", "llm-calls.csv")
PY = sys.executable

def pending():
    plan, _ = read_csv(CFG["content_plan"]); memos, _ = read_csv(os.path.join(LIB, "memos", "index.csv"))
    import draft
    slots = draft.open_slots(plan, date.today())
    notes = [r for r in plan if r["status"] == "change" and "[redraft failed" not in r.get("notes", "")]
    inv, _ = read_csv(os.path.join(LIB, "inventory.csv")); open_topics = {r["id"] for r in inv if r["status"] == "unused"}
    new_memos = [m for m in memos if m.get("status") == "new" or (m.get("status") == "phrase" and m.get("used_in") in open_topics)]   # a phrase whose topic is drafted is done
    ph, _ = read_csv(os.path.join(LIB, "photos", "index.csv")); photos = [r for r in ph if not r.get("scene") and r.get("status") != "deleted"]
    unused = sum(1 for r in inv if r["status"] == "unused" and r["pillar"] != "company")
    return plan, slots, notes, new_memos, photos, unused

def hook_of(r):
    tp = resolve(r.get("caption_ref", ""))
    try: return open(tp, encoding="utf-8").readline().strip()[:90]
    except OSError: return ""

def show(plan, slots, notes, memos, photos, unused):
    print(f"\n{date.today():%a %d.%m.}  what waits for a model call")
    print(f"  memos not yet a post : {len(memos)}" + "".join(f"\n      {m['recorded'][:16].replace('T', ' ')}  {m['words']} words  {m.get('used_in') or ''}" for m in memos))
    print(f"  notes to apply       : {len(notes)}" + "".join(f"\n      {os.path.basename(r.get('caption_ref', ''))[:11]}  {r['notes'][:80]}" for r in notes))
    print(f"  open slots to fill   : {len(slots)}  ({unused} unused topics)" + "".join(f"\n      {dt:%a %d.%m. %H:%M}  {c}" for dt, c in slots))
    print(f"  photos to tag        : {len(photos)}")
    calls = len(slots) + 2 * len(notes); print(f"  model calls          : about {calls} Opus/Sonnet + {len(photos)} Haiku  (a draft ~ $0.15 list price, on the subscription it counts against the 5-hour window)")

def main():
    args = sys.argv[1:]
    plan, slots, notes, memos, photos, unused = pending()
    show(plan, slots, notes, memos, photos, unused)
    if "--status" in args: return
    if not (slots or notes or photos or memos): print("\nnothing to do; the chain still syncs the board (pull, decisions, cards, push)")
    if "--yes" not in args:
        try: a = input("\nrun it now? [Y/n] ").strip().lower()
        except EOFError: a = "n"
        if a not in ("", "y", "yes", "j", "ja"): print("not run"); return
    waited = 0
    while os.path.isdir(LOCK) and waited < 180: print("another run is active, waiting …"); time.sleep(10); waited += 10
    before_ids = {r["id"] for r in plan}; before_calls = sum(1 for _ in open(CALLS, encoding="utf-8")) if os.path.isfile(CALLS) else 0
    t = time.time(); env = dict(os.environ, LLM_INTERACTIVE="1", PYTHON=PY)
    print(); rc = subprocess.call(["/bin/zsh", RUN, "full"], env=env)
    plan2, _ = read_csv(CFG["content_plan"])
    new = [r for r in plan2 if r["id"] not in before_ids]; redone = [r for r in plan2 if r["status"] == "draft" and "[redraft " in r.get("notes", "")[:12] and r["id"] in {x["id"] for x in notes}]
    calls = read_csv(CALLS)[0][before_calls:] if os.path.isfile(CALLS) else []
    print(f"\ndone in {time.time() - t:.0f}s, rc={rc}")
    for r in new: print(f"  new draft  {os.path.basename(r.get('caption_ref', ''))[:11]}  {r.get('planned', '')}  {hook_of(r)}")
    for r in redone: print(f"  redrafted  {os.path.basename(r.get('caption_ref', ''))[:11]}  {r.get('planned', '')}  {hook_of(r)}")
    if calls:
        cost = sum(float(c["cost_usd"] or 0) for c in calls)
        print(f"  model calls: {len(calls)} ({', '.join(sorted({c['step'] for c in calls}))}), {sum(int(c['ms']) for c in calls) / 1000:.0f}s, ${cost:.2f} at list price")
    print("  the board shows the new cards after the push; decide them on the phone")

if __name__ == "__main__": main()
