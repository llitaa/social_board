#!/usr/bin/env python3
"""Post numbers from LinkedIn's API into posts-log.csv (spec metrics-loop), zero tokens.
Personal posts: memberCreatorPostAnalytics (scope r_member_postAnalytics, part of the Community Management API that the
app "AlpiType Board" has requested; token in config.local.linkedin-org.json after `linkedin_auth.py --org`).
Company posts: organizationalEntityShareStatistics (scope r_organization_social, same token, org_urn needed).
Until those scopes exist the script says so once and does nothing; the manual way stays: LinkedIn export into
library/metrics/inbox/ -> metrics_import.py. Runs in the full chain; a post is refreshed at most every 6 hours and
only within 90 days of its date. Docs: learn.microsoft.com/linkedin/marketing/community-management/members/post-statistics"""
import json, os, re, urllib.parse, urllib.request
from datetime import datetime, timedelta
from common import CFG, ROOT, read_csv, write_csv, log

ORG_FILE = os.path.join(ROOT, "config.local.linkedin-org.json")
API = "https://api.linkedin.com/rest"; VERSION = (datetime.now().replace(day=1) - timedelta(days=40)).strftime("%Y%m")
METRICS = {"impressions": "IMPRESSION", "reactions": "REACTION", "comments": "COMMENT"}

def creds():
    try: c = json.load(open(ORG_FILE))
    except (FileNotFoundError, json.JSONDecodeError): return None
    return c if c.get("access_token") and "r_member_postAnalytics" in c.get("scope", "") else None

def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token, "LinkedIn-Version": VERSION, "X-Restli-Protocol-Version": "2.0.0"})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def urn_of(link):
    m = re.search(r"urn:li:(share|ugcPost):\d+", urllib.parse.unquote(link or ""))
    return m.group(0) if m else ""

def member_post(urn, token):
    kind = "ugc" if ":ugcPost:" in urn else "share"; out = {}
    for col, q in METRICS.items():
        d = get(f"{API}/memberCreatorPostAnalytics?q=entity&entity=({kind}:{urllib.parse.quote(urn, safe='')})&queryType={q}&aggregation=TOTAL", token)
        el = d.get("elements", [])
        if el: out[col] = str(el[0].get("count", ""))
    return out

def org_posts(urns, org_urn, token):
    shares = ",".join(urllib.parse.quote(u, safe="") for u in urns)
    d = get(f"{API}/organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity={urllib.parse.quote(org_urn, safe='')}&shares=List({shares})", token)
    out = {}
    for e in d.get("elements", []):
        s = e.get("totalShareStatistics", {}); u = e.get("share") or e.get("ugcPost") or ""
        out[u] = {"impressions": str(s.get("impressionCount", "")), "reactions": str(s.get("likeCount", "")), "comments": str(s.get("commentCount", "")), "reposts": str(s.get("shareCount", ""))}
    return out

def main():
    c = creds()
    if not c: log("metrics: no analytics scope yet (Community Management API pending); export by hand -> library/metrics/inbox"); return
    plog, lf = read_csv(CFG["posts_log"]); now = datetime.now(); changed = 0
    due = [r for r in plog if urn_of(r.get("link")) and r["date"] >= (now - timedelta(days=90)).strftime("%Y-%m-%d")
           and not (r.get("note", "").startswith("metrics api ") and now - datetime.strptime(r["note"][12:28], "%Y-%m-%d %H:%M") < timedelta(hours=6))]
    org = [r for r in due if "company" in r["channel"]]; me = [r for r in due if "company" not in r["channel"]]
    try:
        for r in me:
            vals = member_post(urn_of(r["link"]), c["access_token"]); r.update({k: v for k, v in vals.items() if k in lf and v}); changed += 1
            r["note"] = re.sub(r"^metrics api \S+ \S+\. ", "", r.get("note", "")); r["note"] = f"metrics api {now:%Y-%m-%d %H:%M}. " + r["note"]
        if org and c.get("org_urn"):
            vals = org_posts([urn_of(r["link"]) for r in org], c["org_urn"], c["access_token"])
            for r in org:
                v = vals.get(urn_of(r["link"]))
                if v: r.update({k: x for k, x in v.items() if k in lf and x}); changed += 1; r["note"] = f"metrics api {now:%Y-%m-%d %H:%M}. " + re.sub(r"^metrics api \S+ \S+\. ", "", r.get("note", ""))
    except Exception as e: log("metrics api failed:", str(e)[:200])
    if changed: write_csv(CFG["posts_log"], plog, lf); log(f"metrics: {changed} posts updated from the API")
    else: log("metrics: nothing due")

if __name__ == "__main__": main()
