#!/usr/bin/env python3
"""LinkedIn connection made on the board (05.11.2026). api.php (li_start) sends the person to LinkedIn; board/li.php writes the
returned code into data/uploads/profile/li-code.json, the pull brings it here, and this step exchanges it for a member token
with the app's client secret (config.local.linkedin.json, never on the host). The token goes to this board's LI_FILE
(users/<slug>/linkedin.json, or Anton's config.local.linkedin.json), with the person URN from /v2/userinfo: publish.py posts
as that person, and the URN is what an @-mention of them needs. profile.json gets linkedin_connected {name, expires} for the board."""
import json, os, urllib.parse, urllib.request
from datetime import datetime, timedelta
from common import ROOT, LIB, BOARD_LOCAL, LI_FILE, USER, jload, jdump, log

CODE = os.path.join(BOARD_LOCAL, "uploads", "profile", "li-code.json")

def main():
    if not os.path.isfile(CODE): return
    req = jload(CODE, {}); app = jload(os.path.join(ROOT, "config.local.linkedin.json"), {})
    status, err = None, ""
    if not app.get("client_id") or not app.get("client_secret"): err = "app credentials missing on the worker"
    else:
        try:
            data = urllib.parse.urlencode({"grant_type": "authorization_code", "code": req.get("code", ""), "redirect_uri": req.get("redirect", ""), "client_id": app["client_id"], "client_secret": app["client_secret"]}).encode()
            tok = json.load(urllib.request.urlopen(urllib.request.Request("https://www.linkedin.com/oauth/v2/accessToken", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}), timeout=30))
            c = jload(LI_FILE, {}); c.update({"client_id": app["client_id"], "access_token": tok["access_token"], "scopes": tok.get("scope", "openid profile w_member_social"),
                                              "expires": (datetime.now() + timedelta(seconds=int(tok.get("expires_in", 0)))).isoformat(timespec="seconds"), "connected": datetime.now().isoformat(timespec="minutes")})
            me = json.load(urllib.request.urlopen(urllib.request.Request("https://api.linkedin.com/v2/userinfo", headers={"Authorization": "Bearer " + c["access_token"]}), timeout=30))
            if me.get("sub"): c["person_urn"] = "urn:li:person:" + me["sub"]
            if me.get("name"): c["name"] = me["name"]
            jdump(LI_FILE, c); os.chmod(LI_FILE, 0o600)
            status = {"name": c.get("name", ""), "expires": c["expires"][:10], "ts": datetime.now().isoformat(timespec="seconds")}
            log(f"linkedin connected: {c.get('name', '?')} until {c['expires'][:10]}")
        except urllib.error.HTTPError as e: err = f"LinkedIn {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}"
        except Exception as e: err = repr(e)[:200]
    if err: log("linkedin connect failed:", err)
    os.remove(CODE)
    if not USER: return
    for f in (os.path.join(LIB, "profile.json"), os.path.join(BOARD_LOCAL, "profile.json")):
        pr = jload(f, {})
        if status: pr["linkedin_connected"] = status; pr.pop("linkedin_error", None)
        else: pr["linkedin_error"] = err
        jdump(f, pr)

if __name__ == "__main__": main()
