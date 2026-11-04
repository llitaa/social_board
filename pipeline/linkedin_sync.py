#!/usr/bin/env python3
"""Posts made by hand on the company page (04.11.2026, Anton: "the system does not track what I posted directly on LinkedIn").
The page's posts can be listed through the API (r_organization_social, versioned Posts API); a member's own posts cannot.
For every post of the page: a posts-log row that carries its URN is known; otherwise the first line is matched against the
open drafts (content-plan rows not yet posted) and against posts-log hooks without a link. A matching draft becomes posted
with the link and the real date; an unknown post is added to posts-log as an external row. Anton's board only."""
import json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CFG, LI_ORG_FILE, USER, read_csv, write_csv, resolve, log

API = "https://api.linkedin.com/rest"; VERSION = "202511"

def norm(t): return re.sub(r"[^a-z0-9äöüß]+", " ", (t or "").lower()).strip()[:40]   # the first words of the first line; a hook logged by hand may stop at the first sentence

def page_posts(c, n=20):
    url = f"{API}/posts?author={urllib.parse.quote(c['org_urn'], safe='')}&q=author&count={n}"
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + c["access_token"], "LinkedIn-Version": VERSION, "X-Restli-Protocol-Version": "2.0.0"})
    with urllib.request.urlopen(req, timeout=40) as r: d = json.load(r)
    out = []
    for e in d.get("elements", []):
        urn = e.get("id", ""); text = (e.get("commentary") or "").strip()
        out.append({"urn": urn, "text": text, "hook": text.split("\n")[0][:200], "date": datetime.fromtimestamp(e.get("createdAt", 0) / 1000), "link": f"https://www.linkedin.com/feed/update/{urn}"})
    return out

def main():
    if USER: return
    try: c = json.load(open(LI_ORG_FILE))
    except Exception: log("linkedin sync: no company token"); return
    if not c.get("org_urn") or "r_organization_social" not in (c.get("scopes") or ""): log("linkedin sync: company token without read scope"); return
    try: posts = page_posts(c)
    except Exception as e: log("linkedin sync failed:", str(e)[:160]); return
    plan, pf = read_csv(CFG["content_plan"]); plog, lf = read_csv(CFG["posts_log"])
    known = {m.group(0) for r in plog for m in [re.search(r"urn:li:(share|ugcPost):\d+", r.get("link", ""))] if m}
    by_hook = {norm(r.get("hook", "")): r for r in plog if r.get("channel") == "linkedin-company"}
    changed = 0
    PROMO = re.compile(r"professional profile|Join over \d+ professionals|Discover the professional|engage with Anton", re.I)   # LinkedIn's own page promotions, not posts
    START = datetime(2026, 9, 1)   # the system's first company post; older page posts stay out of the log
    for p in posts:
        if p["urn"] in known or not p["hook"] or p["date"] < START or PROMO.search(p["text"][:200]): continue
        key = norm(p["hook"]); row = by_hook.get(key)
        if not row: row = next((r for r in plog if r.get("channel") == "linkedin-company" and not r.get("link") and r.get("date") == p["date"].strftime("%Y-%m-%d")), None)   # same day, no link: the text was changed by hand before posting
        if row:   # logged, link or date missing (posted by hand, marked on the board without the link)
            if not row.get("link"): row["link"] = p["link"]
            if not row.get("date"): row["date"] = p["date"].strftime("%Y-%m-%d")
            log("linkedin sync: link added", row.get("post_id")); changed += 1; continue
        draft = next((r for r in plan if r.get("channel") == "linkedin-company" and r.get("status") not in ("posted", "dropped", "skipped") and r.get("caption_ref")
                      and norm(open(resolve(r["caption_ref"]), encoding="utf-8").readline()) == key), None) if key else None
        if draft:
            cid = "-".join(os.path.basename(draft["caption_ref"]).split("-")[0:3])
            draft["status"] = "posted"; draft["notes"] = f"[posted by hand on LinkedIn {p['date']:%d.%m.%Y %H:%M}, found by linkedin_sync] " + draft.get("notes", "")
            have = next((r for r in plog if r.get("post_id") == cid), None)
            if have: have["link"] = have.get("link") or p["link"]; have["date"] = have.get("date") or p["date"].strftime("%Y-%m-%d")
            else: plog.append({"date": p["date"].strftime("%Y-%m-%d"), "channel": "linkedin-company", "post_id": cid, "hook": p["hook"][:120], "type": draft.get("format", ""), "language": draft.get("language", "en"), "link": p["link"], "note": f"POSTED by hand {p['date']:%d.%m.%Y %H:%M}, found by linkedin_sync"})
            log("linkedin sync: draft posted by hand", cid); changed += 1
        else:
            n = 1 + sum(1 for r in plog if (r.get("post_id") or "").startswith("li-comp-x"))
            plog.append({"date": p["date"].strftime("%Y-%m-%d"), "channel": "linkedin-company", "post_id": f"li-comp-x{n:02d}", "hook": p["hook"][:120], "type": "external", "language": "en", "link": p["link"], "note": f"posted directly in LinkedIn {p['date']:%d.%m.%Y %H:%M}, found by linkedin_sync"})
            log("linkedin sync: external post added", p["hook"][:50]); changed += 1
    if changed:
        write_csv(CFG["content_plan"], plan, pf); write_csv(CFG["posts_log"], plog, lf)
    log(f"linkedin sync: {len(posts)} page posts checked, {changed} change(s)")

if __name__ == "__main__": main()
