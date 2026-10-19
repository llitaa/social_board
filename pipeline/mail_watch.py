#!/usr/bin/env python3
"""Read-only mailbox watch (Microsoft Graph, anton@alpitype.com): mails from LinkedIn about the developer apps
(API access review, app verification, token) become a line on the board's system line and a note in the log.
Reads only; never sends (hard rule in ~/dev/campaign/CLAUDE.md). Zero tokens.
Usage: mail_watch.py            -> writes board/data/mail.json (used by health.py)
       mail_watch.py list [n]   -> prints the last n LinkedIn mails (subject, from, date)"""
import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta
from common import BOARD_LOCAL, LIB, jdump, log

SECRETS = os.path.expanduser("~/dev/alpi_marketer/server/src/system/config/secrets.json")
MAILBOX = "anton@alpitype.com"
KEYS = ("community management", "api", "developer", "app", "access", "verif", "review", "token")

def token():
    import msal
    s = json.load(open(SECRETS))
    app = msal.ConfidentialClientApplication(s["ms_client_id"], authority=f"https://login.microsoftonline.com/{s['ms_tenant_id']}", client_credential=s["ms_client_secret"])
    t = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in t: raise RuntimeError(t.get("error_description", "no token"))
    return t["access_token"]

def linkedin_mails(days=14, n=25):
    since = (datetime.now(__import__("datetime").timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = urllib.parse.urlencode({"$filter": f"receivedDateTime ge {since} and contains(from/emailAddress/address,'linkedin')", "$orderby": "receivedDateTime desc", "$top": n,
                                "$select": "subject,from,receivedDateTime,bodyPreview,isRead"})
    req = urllib.request.Request(f"https://graph.microsoft.com/v1.0/users/{MAILBOX}/messages?{q}", headers={"Authorization": "Bearer " + token()})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r).get("value", [])

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        for m in linkedin_mails(30, int(sys.argv[2]) if len(sys.argv) > 2 else 25):
            print(m["receivedDateTime"][:16], "|", m["from"]["emailAddress"]["address"], "|", m["subject"][:90])
        return
    out = []
    for m in linkedin_mails():
        s = (m["subject"] + " " + m["bodyPreview"]).lower()
        if any(k in s for k in KEYS) and "developer" in m["from"]["emailAddress"]["address"] + s:
            out.append({"ts": m["receivedDateTime"], "from": m["from"]["emailAddress"]["address"], "subject": m["subject"][:120], "preview": m["bodyPreview"][:200], "read": m["isRead"]})
    jdump(os.path.join(BOARD_LOCAL, "mail.json"), {"ts": datetime.now().isoformat(timespec="seconds"), "linkedin_developer": out})
    log(f"mail watch: {len(out)} LinkedIn developer mail(s) in 14 days")

if __name__ == "__main__": main()
