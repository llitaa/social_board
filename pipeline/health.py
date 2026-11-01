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

def pending(plan, memos):
    """What waits for a model call (config llm.auto: false): memos not yet drafted, notes not yet applied, open slots, untagged photos."""
    inv, _ = read_csv(os.path.join(LIB, "inventory.csv")); unused = {r["id"] for r in inv if r["status"] == "unused"}
    out = {"memos": sum(1 for m in memos if m.get("status") == "new" or (m.get("status") == "phrase" and m.get("used_in") in unused)), "notes": sum(1 for r in plan if r["status"] == "change" and "[redraft failed" not in r.get("notes", ""))}
    try:
        import draft; out["slots"] = len(draft.open_slots(plan, date.today()))
    except Exception as e: out["slots"] = 0; log("pending slots:", repr(e)[:80])
    ph, _ = read_csv(os.path.join(LIB, "photos", "index.csv")); out["photos"] = sum(1 for r in ph if not r.get("scene") and r.get("status") != "deleted")
    return out

def last_runs(n=3):
    rows = [json.loads(l) for l in open(STEPS, encoding="utf-8")] if os.path.isfile(STEPS) else []
    by = {}
    for r in rows: by.setdefault(r["step"], []).append(r)
    return {k: v[-n:] for k, v in by.items()}

def weekly(n=4):
    """S5 (01.11.2026): one indicator line per ISO week, side by side, no rates between columns. Posts and comments from posts-log,
    profile visits from profile-weekly.csv, contacts and qualified conversations from inbound-log.csv. Missing stays empty, never zero."""
    from datetime import date as _date, timedelta as _td
    plog, _ = read_csv(CFG["posts_log"])
    ib_p = os.path.expanduser(CFG.get("inbound_log", "~/dev/campaign/inbound-log.csv")); ib = read_csv(ib_p)[0] if os.path.isfile(ib_p) else []
    pw_p = os.path.expanduser(CFG.get("profile_weekly", "~/dev/campaign/profile-weekly.csv")); pw = read_csv(pw_p)[0] if os.path.isfile(pw_p) else []
    def wk(s):
        try: y, m, d = map(int, (s or "")[:10].split("-")); iso = _date(y, m, d).isocalendar(); return f"{iso[0]}-W{iso[1]:02d}"
        except Exception: return ""
    today = _date.today(); weeks = []
    for i in range(n - 1, -1, -1):
        iso = (today - _td(weeks=i)).isocalendar(); weeks.append(f"{iso[0]}-W{iso[1]:02d}")
    rows = []
    for w in weeks:
        posts = [r for r in plog if wk(r.get("date")) == w]
        have = [int(r["comments"]) for r in posts if str(r.get("comments", "")).isdigit()]
        contacts = [r for r in ib if wk(r.get("date")) == w]
        rows.append({"week": w, "posts": len(posts), "comments": sum(have) if have else "", "visits": next((r.get("visits", "") for r in pw if r.get("week") == w), ""),
                     "contacts": len(contacts), "linkedin": sum(1 for r in contacts if "linkedin" in (r.get("source") or "").lower()), "qualified": sum(1 for r in contacts if (r.get("qualified") or "").lower() == "yes")})
    return rows

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
    if pipe.get("metrics_missing", 0) >= 3: ok.append(f"numbers missing for {pipe['metrics_missing']} published posts: tap the post under Published on the board and type them, or download LinkedIn's export (Analytics > Post impressions > Export; page: Analytics > Content > Export) into ~/Downloads; the API fills them itself once LinkedIn grants the Community Management API")
    memos, _ = read_csv(os.path.join(LIB, "memos", "index.csv")); fb = sum(1 for m in memos if m.get("status") == "feedback")
    if fb: ok.append(f"{fb} note{'s' if fb > 1 else ''} for the builder in library/feedback.md")
    if not li["connected"]: issues.append({"what": "LinkedIn token", "since": today.isoformat(), "times": 1, "log": "no valid token for the profile: nothing can be published", "fix": "run: python3 pipeline/linkedin_auth.py (then the full run pushes it to the host)"})
    if li["connected"] and li["days_left"] < 7: issues.append({"what": "LinkedIn token", "since": today.isoformat(), "times": 1, "log": f"expires in {li['days_left']} days", "fix": "run: python3 pipeline/linkedin_auth.py"})
    rules = [l for l in open(os.path.join(LIB, "style-rules.txt"), encoding="utf-8") if l.strip() and not l.startswith("#")] if os.path.isfile(os.path.join(LIB, "style-rules.txt")) else []
    auto = bool(CFG.get("llm", {}).get("auto", True)); pend = pending(plan, memos)
    if not auto and any(pend.values()): ok.append("waiting for python3 pipeline/process.py on the Mac: " + ", ".join(f"{v} {k}" for k, v in pend.items() if v))
    jdump(os.path.join(BOARD_LOCAL, "health.json"), {"ts": datetime.now().isoformat(timespec="seconds"), "issues": issues, "ok": ok, "month_cost_usd": round(cost, 2), "slots_planned": len(slots), "topics_unused": unused,
          "linkedin": li, "rules_learned": len(rules), "builder_notes": fb, "auto": auto, "pending": pend, "weekly": weekly()})
    log(f"health: {len(issues)} issue(s)" + (": " + "; ".join(i["what"] for i in issues) if issues else ""))

if __name__ == "__main__": main()
