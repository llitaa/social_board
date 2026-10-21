#!/usr/bin/env python3
"""Fold pulled decisions into the truth on the Mac:
- post decisions -> content-plan.csv status (approved / change / skipped / posted) and posts-log.csv on posted;
  a text edited on the card (decision post with text) replaces the draft text, the old text stays as <id>.vN.txt
- scheduled rows whose slot has passed -> posted (LinkedIn published them itself; the board stops showing them)
- comment decisions -> library/log/comment-log.csv
- photo / upload / memo decisions -> library/log/board-events.csv (processed by photo_index / transcribe)
Idempotent: remembers the last processed line per decisions file in library/log/.applied.json
"""
import csv, glob, json, os, shutil
from datetime import datetime
from common import CFG, BOARD_LOCAL, LIB, read_csv, write_csv, jload, jdump, log, resolve

STATE = os.path.join(LIB, "log", ".applied.json")
LOGDIR = os.path.join(LIB, "log")

def append(path, fields, row):
    new = not os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new: w.writeheader()
        w.writerow({k: row.get(k, "") for k in fields})

def write_edit(r, text, ts):
    """Anton's final text from the card: becomes the draft text; the previous one is kept as a version."""
    tp = resolve(r.get("caption_ref", ""))
    if not tp or not os.path.isfile(tp): return False
    old = open(tp, encoding="utf-8").read().strip()
    if old == text.strip(): return False
    base = os.path.splitext(tp)[0]; mp = base + ".json"
    meta = jload(mp, {"versions": []}); ver = len(meta.get("versions", [])) + 1
    shutil.copy2(tp, f"{base}.v{ver}.txt"); meta.setdefault("versions", []).append({"v": ver, "note": "edited on the card", "ts": ts})
    open(tp, "w", encoding="utf-8").write(text.strip() + "\n"); jdump(mp, meta)
    return True

def promote_scheduled(plan, plog):
    """A post Anton scheduled in LinkedIn is posted once its slot has passed: the board must not show it as open."""
    now = datetime.now(); n = 0
    for r in plan:
        if r["status"] != "scheduled" or not r["channel"].startswith("linkedin"): continue
        p = (r.get("planned") or "").strip()
        if len(p) == 10: p += " 23:59"
        try: w = datetime.strptime(p[:16], "%Y-%m-%d %H:%M")
        except ValueError: continue
        if w <= now:
            r["status"] = "posted"; r["notes"] = f"[posted by LinkedIn schedule {w:%d.%m. %H:%M}] " + r.get("notes", ""); n += 1
            cid = "-".join(os.path.basename(r.get("caption_ref", "")).split("-")[0:3])
            for l in plog:
                if l["post_id"] == cid and not (l.get("note") or "").upper().startswith("POSTED"): l["note"] = f"POSTED (LinkedIn schedule) {w:%d.%m.%Y %H:%M}. " + (l.get("note") or "")
    return n

def main():
    os.makedirs(LOGDIR, exist_ok=True)
    done = jload(STATE, {})
    plan, pf = read_csv(CFG["content_plan"]); plog, lf = read_csv(CFG["posts_log"])
    cards = {c["id"]: c for c in jload(os.path.join(BOARD_LOCAL, "cards.json"), [])}
    changed_plan = changed_log = False; last_ts = jload(os.path.join(BOARD_LOCAL, "applied.json"), {}).get("until", "")
    files = [(os.path.basename(f), f) for f in sorted(glob.glob(os.path.join(BOARD_LOCAL, "decisions", "*.jsonl")))] + \
            [("local/" + os.path.basename(f), f) for f in sorted(glob.glob(os.path.join(BOARD_LOCAL, "decisions-local", "*.jsonl")))]   # voice notes transcribed on the Mac
    for key, f in files:
        lines = open(f, encoding="utf-8").read().splitlines()
        start = done.get(key, 0); ok_upto = start
        for ln in lines[start:]:
            try: d = json.loads(ln)
            except json.JSONDecodeError: break   # a half-written last line: stop here, read it again next run
            ok_upto += 1
            t = d.get("type")
            try: last_ts = d["ts"] if not last_ts or datetime.fromisoformat(d.get("ts", "")) > datetime.fromisoformat(last_ts) else last_ts
            except (ValueError, KeyError): pass
            if t == "post":
                cid = d["card_id"]; card = cards.get(cid, {})
                if not card:   # the card left cards.json (aged off, renamed): find the plan row by the same id derivation cards.py uses
                    for r in plan:
                        if r.get("caption_ref") and "-".join(os.path.basename(r["caption_ref"]).split("-")[0:3]) == cid: card = {"plan_row": r["id"], "status": r["status"]}; break
                if d["decision"] == "order":   # the listed cards take their existing slots in the new sequence (rows Anton scheduled in LinkedIn are never moved)
                    ids = [x for x in d.get("order", []) if x in cards and cards[x].get("status") != "scheduled"]
                    byrow = {x: next((r for r in plan if r["id"] == cards[x].get("plan_row")), None) for x in ids}
                    ids = [x for x in ids if byrow[x] and byrow[x].get("planned")]
                    free = sorted(byrow[x]["planned"] for x in ids)
                    for i, x in enumerate(ids):
                        if byrow[x]["planned"] != free[i]: byrow[x]["planned"] = free[i]; byrow[x]["notes"] = f"[board {d['ts'][:16]} reordered to {free[i]}] " + byrow[x].get("notes", ""); changed_plan = True
                    append(os.path.join(LOGDIR, "post-decisions.csv"), ["ts", "card_id", "decision", "option", "note", "reason", "url", "edited", "when"], {**d, "note": " ".join(ids)}); continue
                status = {"post": "approved", "schedule": "approved", "change": "change", "skip": "skipped", "posted": "posted", "unschedule": "draft", "photo_next": None}.get(d["decision"], "")
                if status == "": continue
                for r in plan:
                    if r["id"] == card.get("plan_row"):
                        if status: r["status"] = status
                        if d["decision"] == "post": r["planned"] = d["ts"][:16].replace("T", " ")          # Post now: the row's slot is now, publish.py takes it in this run
                        if d["decision"] == "schedule" and d.get("when"): r["planned"] = d["when"][:16].replace("T", " ")
                        if d["decision"] == "unschedule": r["notes"] = f"[board {d['ts'][:16]} unscheduled] " + r.get("notes", "")
                        if d["decision"] == "photo_next": r["notes"] = f"[board {d['ts'][:16]} photo: next] " + r.get("notes", "")
                        if d.get("note"): r["notes"] = f"[board {d['ts'][:16]} {d['decision']}: {d['note']}] " + r.get("notes", "")
                        if d.get("reason"): r["notes"] = f"[board skip: {d['reason']}] " + r.get("notes", "")
                        if d.get("text") and status in ("approved", "posted") and write_edit(r, d["text"], d["ts"]): r["notes"] = f"[board {d['ts'][:16]} edited on the card] " + r.get("notes", ""); d["edited"] = "yes"
                        changed_plan = True
                if status == "posted":
                    hit = False
                    for r in plog:
                        if r["post_id"] == cid:
                            r["note"] = f"POSTED via {d.get('via', 'board')} {d['ts'][:10]}. " + r.get("note", "")
                            if d.get("url"): r["link"] = d["url"]
                            changed_log = hit = True
                    if not hit:   # drafts have no posts-log row yet: create it (21.10.: server-published posts were invisible to metrics and featured)
                        row = next((r for r in plan if r["id"] == card.get("plan_row")), None)
                        if row:
                            tp = resolve(row.get("caption_ref", "")); hook = open(tp, encoding="utf-8").readline().strip()[:120] if tp and os.path.isfile(tp) else ""
                            plog.append({"date": (row.get("planned") or d["ts"])[:10], "channel": row["channel"], "post_id": cid, "hook": hook, "type": row.get("format", ""), "language": row.get("language", ""),
                                         "link": d.get("url", ""), "note": f"POSTED via {d.get('via', 'board')} {d['ts'][:10]}"}); changed_log = True
                if card and status: card["status"] = status
                append(os.path.join(LOGDIR, "post-decisions.csv"), ["ts", "card_id", "decision", "option", "note", "reason", "url", "edited", "when"], d)
            elif t == "comment":
                append(os.path.join(LOGDIR, "comment-log.csv"), ["ts", "card_id", "decision", "reason"], d)
            elif t in ("photo", "upload", "memo", "settings", "answer"):
                append(os.path.join(LOGDIR, "board-events.csv"), ["ts", "type", "id", "decision", "files", "file", "note", "answer", "expiry", "review", "card_id"],
                       {**d, "files": ",".join(d.get("files", []) or [])})
        done[key] = ok_upto
    if promote_scheduled(plan, plog): changed_plan = changed_log = True
    if changed_plan: write_csv(CFG["content_plan"], plan, pf); log("content-plan.csv updated")
    if changed_log: write_csv(CFG["posts_log"], plog, lf); log("posts-log.csv updated")
    jdump(os.path.join(BOARD_LOCAL, "cards.json"), list(cards.values()))
    # everything up to the newest applied decision is now in the CSVs; the board drops overlay entries older than this
    if last_ts: jdump(os.path.join(BOARD_LOCAL, "applied.json"), {"until": last_ts, "at": datetime.now().isoformat(timespec="seconds")})
    jdump(STATE, done); log("decisions applied", "until", last_ts or "-")

if __name__ == "__main__": main()
