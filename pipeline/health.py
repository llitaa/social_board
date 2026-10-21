#!/usr/bin/env python3
"""The watchdog. Reads library/log/steps.jsonl (one line per step per run) and the state files, decides per component
whether it is healthy, and writes board/data/health.json; the board shows a red line with the failing step and its
last log line. The page itself adds "Mac not seen for N min" from the timestamp, so a dead Mac shows too."""
import json, os, glob
from datetime import datetime, date, timedelta
from common import CFG, LIB, BOARD_LOCAL, read_csv, jdump, jload, log

STEPS = os.path.join(LIB, "log", "steps.jsonl")
NAMES = {"worker": "token push to the host", "metrics": "metrics import", "metrics_api": "metrics from the API", "pull": "server sync (pull)", "apply": "decisions → CSV", "learn": "notes → preferences", "transcribe": "memo transcription", "photos": "photo pool",
         "redraft": "notes → redraft", "publish": "LinkedIn publishing", "mail": "mailbox watch (read only)", "draft": "slot filling", "cards": "cards + pipeline", "push": "server sync (push)"}
LI = os.path.join(os.path.dirname(LIB), "config.local.linkedin.json"); LI_ORG = os.path.join(os.path.dirname(LIB), "config.local.linkedin-org.json")

def linkedin():
    """What the board says next to an approved card: posts itself, or 'you post it' until the app exists."""
    c = {}
    if os.path.isfile(LI):
        try: c = json.load(open(LI))
        except json.JSONDecodeError: c = {}
    exp = c.get("expires", "")
    ok = bool(c.get("access_token")) and exp > datetime.now().isoformat()
    o = {}
    if os.path.isfile(LI_ORG):
        try: o = json.load(open(LI_ORG))
        except json.JSONDecodeError: o = {}
    org_ok = bool(o.get("access_token")) and o.get("expires", "") > datetime.now().isoformat() and bool(o.get("org_urn"))
    if org_ok and o["expires"] < exp: exp = o["expires"]
    return {"connected": ok, "org": org_ok, "expires": exp[:10], "days_left": (date.fromisoformat(exp[:10]) - date.today()).days if ok else 0}

def last_runs(n=3):
    rows = [json.loads(l) for l in open(STEPS, encoding="utf-8")] if os.path.isfile(STEPS) else []
    by = {}
    for r in rows: by.setdefault(r["step"], []).append(r)
    return {k: v[-n:] for k, v in by.items()}

def main():
    issues, ok = [], []
    runs = last_runs()
    for step, name in NAMES.items():
        rs = runs.get(step, [])
        if not rs: continue
        bad = [r for r in rs if r["rc"] != 0]
        if rs[-1]["rc"] != 0: issues.append({"what": name, "since": bad[0]["ts"], "times": len(bad), "log": rs[-1]["last"], "fix": f"run: python3 pipeline/{ {'pull':'board_sync.py pull','push':'board_sync.py push'}.get(step, step + '.py') } and read library/log/board-sync.err"})
        else: ok.append(name)
    # content checks
    plan, _ = read_csv(CFG["content_plan"]); today = date.today(); horizon = today + timedelta(days=int(CFG.get("horizon_days", 14)))
    slots = [r for r in plan if r["channel"].startswith("linkedin") and r["status"] in ("draft", "approved", "scheduled", "change") and today.isoformat() <= (r.get("planned") or "")[:10] <= horizon.isoformat()]
    if len(slots) < 4: issues.append({"what": "slot filling", "since": today.isoformat(), "times": 1, "log": f"only {len(slots)} posts planned in the next 14 days", "fix": "check library/log/draft.out, inventory.csv (unused topics) and the photo pool"})
    stuck = [r for r in plan if r["status"] == "change" and "[redraft failed" in r.get("notes", "")]
    for r in stuck: issues.append({"what": "notes → redraft", "since": today.isoformat(), "times": 1, "log": r["notes"][:160], "fix": "decide the card again or rephrase the note"})
    li = linkedin()
    # (20.10.) a by-hand company post is no issue any more: the company page gets its API soon; the card itself still says "post it by hand"
    for r in plan:
        if r["status"] == "approved" and (r["channel"] == "linkedin" or li["org"]) and (r.get("planned") or "9999")[:16].replace("T", " ") < (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"):
            issues.append({"what": "post overdue", "since": r.get("planned", ""), "times": 1, "log": f"{os.path.basename(r.get('caption_ref', ''))[:10]} was due {r.get('planned', '')} and is not published", "fix": "check library/log/board-sync.err; run: zsh pipeline/run.sh fast"})
    for r in plan:
        if r["status"] == "approved" and r.get("notes", "").startswith("[publish failed"): issues.append({"what": "LinkedIn publishing", "since": today.isoformat(), "times": 1, "log": r["notes"][:160], "fix": "post it yourself (Copy text) or run: python3 pipeline/publish.py; token: pipeline/linkedin_auth.py"})
    inv, _ = read_csv(os.path.join(LIB, "inventory.csv")); unused = sum(1 for r in inv if r["status"] == "unused" and r["pillar"] != "company")
    if unused < 4: issues.append({"what": "material", "since": today.isoformat(), "times": 1, "log": f"{unused} unused personal topics left", "fix": "record memos or run inventory.py"})
    calls = os.path.join(LIB, "log", "llm-calls.csv"); failed = 0; cost = 0.0
    if os.path.isfile(calls):
        for r in read_csv(calls)[0]:
            if r["ts"][:7] == today.isoformat()[:7]: cost += float(r["cost_usd"] or 0); failed += r["ok"] == "no"
    if failed: issues.append({"what": "model calls", "since": today.isoformat(), "times": failed, "log": f"{failed} failed claude -p calls this month", "fix": "run `claude -p 'ok'` by hand; check the subscription limit"})
    mail = jload(os.path.join(BOARD_LOCAL, "mail.json"), {})
    for m in mail.get("linkedin_developer", [])[:3]:
        if (date.today() - date.fromisoformat(m["ts"][:10])).days <= 14:
            issues.append({"what": "LinkedIn mail", "since": m["ts"][:10], "times": 1, "log": f"{m['ts'][:10]} {m['subject']} — {m['preview'][:140]}", "fix": "read it in anton@alpitype.com; if the Community Management API is granted: python3 pipeline/linkedin_auth.py --org"})
    pipe = jload(os.path.join(BOARD_LOCAL, "pipeline.json"), {})
    if pipe.get("metrics_missing", 0) >= 3: ok.append(f"numbers missing for {pipe['metrics_missing']} published posts: export from LinkedIn (post > View analytics > Export, page: Analytics > Content > Export) into library/metrics/inbox; the API fills them itself once the Community Management API is granted")
    memos, _ = read_csv(os.path.join(LIB, "memos", "index.csv")); fb = sum(1 for m in memos if m.get("status") == "feedback")
    if fb: ok.append(f"{fb} note{'s' if fb > 1 else ''} for the builder in library/feedback.md")
    if not li["connected"]: issues.append({"what": "LinkedIn token", "since": today.isoformat(), "times": 1, "log": "no valid token for the profile: nothing can be published", "fix": "run: python3 pipeline/linkedin_auth.py (then the full run pushes it to the host)"})
    if li["connected"] and li["days_left"] < 7: issues.append({"what": "LinkedIn token", "since": today.isoformat(), "times": 1, "log": f"expires in {li['days_left']} days", "fix": "run: python3 pipeline/linkedin_auth.py"})
    rules = [l for l in open(os.path.join(LIB, "style-rules.txt"), encoding="utf-8") if l.strip() and not l.startswith("#")] if os.path.isfile(os.path.join(LIB, "style-rules.txt")) else []
    jdump(os.path.join(BOARD_LOCAL, "health.json"), {"ts": datetime.now().isoformat(timespec="seconds"), "issues": issues, "ok": ok, "month_cost_usd": round(cost, 2), "slots_planned": len(slots), "topics_unused": unused,
          "linkedin": li, "rules_learned": len(rules), "builder_notes": fb})
    log(f"health: {len(issues)} issue(s)" + (": " + "; ".join(i["what"] for i in issues) if issues else ""))

if __name__ == "__main__": main()
