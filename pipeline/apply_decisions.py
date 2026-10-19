#!/usr/bin/env python3
"""Fold pulled decisions into the truth on the Mac:
- post decisions -> content-plan.csv status (approved / change / skipped / posted) and posts-log.csv on posted
- comment decisions -> library/log/comment-log.csv
- photo / upload / memo decisions -> library/log/board-events.csv (processed by photo_index / transcribe)
Idempotent: remembers the last processed line per decisions file in library/log/.applied.json
"""
import csv, glob, json, os
from datetime import datetime
from common import CFG, BOARD_LOCAL, LIB, read_csv, write_csv, jload, jdump, log

STATE = os.path.join(LIB, "log", ".applied.json")
LOGDIR = os.path.join(LIB, "log")

def append(path, fields, row):
    new = not os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new: w.writeheader()
        w.writerow({k: row.get(k, "") for k in fields})

def main():
    os.makedirs(LOGDIR, exist_ok=True)
    done = jload(STATE, {})
    plan, pf = read_csv(CFG["content_plan"]); plog, lf = read_csv(CFG["posts_log"])
    cards = {c["id"]: c for c in jload(os.path.join(BOARD_LOCAL, "cards.json"), [])}
    changed_plan = changed_log = False; last_ts = jload(os.path.join(BOARD_LOCAL, "applied.json"), {}).get("until", "")
    for f in sorted(glob.glob(os.path.join(BOARD_LOCAL, "decisions", "*.jsonl"))):
        lines = open(f, encoding="utf-8").read().splitlines()
        start = done.get(os.path.basename(f), 0)
        for ln in lines[start:]:
            try: d = json.loads(ln)
            except json.JSONDecodeError: continue
            t = d.get("type"); last_ts = max(last_ts, d.get("ts", ""))
            if t == "post":
                cid = d["card_id"]; card = cards.get(cid, {})
                status = {"post": "approved", "change": "change", "skip": "skipped", "posted": "posted"}.get(d["decision"])
                if not status: continue
                for r in plan:
                    if r["id"] == card.get("plan_row"):
                        r["status"] = status
                        if d.get("note"): r["notes"] = f"[board {d['ts'][:16]} {d['decision']}: {d['note']}] " + r.get("notes", "")
                        if d.get("reason"): r["notes"] = f"[board skip: {d['reason']}] " + r.get("notes", "")
                        changed_plan = True
                if status == "posted":
                    for r in plog:
                        if r["post_id"] == cid:
                            r["note"] = f"POSTED via board {d['ts'][:10]}. " + r.get("note", "")
                            if d.get("url"): r["link"] = d["url"]
                            changed_log = True
                if card: card["status"] = status
                append(os.path.join(LOGDIR, "post-decisions.csv"), ["ts", "card_id", "decision", "option", "note", "reason", "url"], d)
            elif t == "comment":
                append(os.path.join(LOGDIR, "comment-log.csv"), ["ts", "card_id", "decision", "reason"], d)
            elif t in ("photo", "upload", "memo", "settings", "answer"):
                append(os.path.join(LOGDIR, "board-events.csv"), ["ts", "type", "id", "decision", "files", "file", "note", "answer", "expiry", "review"],
                       {**d, "files": ",".join(d.get("files", []) or [])})
        done[os.path.basename(f)] = len(lines)
    if changed_plan: write_csv(CFG["content_plan"], plan, pf); log("content-plan.csv updated")
    if changed_log: write_csv(CFG["posts_log"], plog, lf); log("posts-log.csv updated")
    jdump(os.path.join(BOARD_LOCAL, "cards.json"), list(cards.values()))
    # everything up to the newest applied decision is now in the CSVs; the board drops overlay entries older than this
    if last_ts: jdump(os.path.join(BOARD_LOCAL, "applied.json"), {"until": last_ts, "at": datetime.now().isoformat(timespec="seconds")})
    jdump(STATE, done); log("decisions applied", "until", last_ts or "-")

if __name__ == "__main__": main()
