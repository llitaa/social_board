#!/usr/bin/env python3
"""One-time LinkedIn authorisation, run by Anton himself (the assistant never signs in):
  1. create an app at https://www.linkedin.com/developers/apps (company page: AlpiType), add the product
     "Share on LinkedIn" (+ "Sign In with LinkedIn using OpenID Connect"); for the company page later
     "Community Management API" (needs LinkedIn's review);
  2. Auth → redirect URL: http://localhost:8765/callback
  3. put client_id / client_secret into config.local.linkedin.json  {"client_id": "...", "client_secret": "..."}
  4. run: python3 pipeline/linkedin_auth.py   → opens the browser, you log in and consent, the token is saved
     into config.local.linkedin.json (gitignored). Tokens live 60 days; the board warns 7 days before.
"""
import json, os, secrets, sys, urllib.parse, urllib.request, webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from common import ROOT

CFG_FILE = os.path.join(ROOT, "config.local.linkedin.json")
REDIRECT = "http://localhost:8765/callback"
SCOPES_MEMBER = "openid profile w_member_social"
SCOPES_ORG = "w_organization_social r_organization_social"

def load(): return json.load(open(CFG_FILE)) if os.path.isfile(CFG_FILE) else {}
def save(d): json.dump(d, open(CFG_FILE, "w"), indent=1); os.chmod(CFG_FILE, 0o600)

def main():
    c = load()
    if not c.get("client_id") or not c.get("client_secret"): sys.exit(f"put client_id and client_secret into {CFG_FILE} first (see the docstring)")
    scopes = SCOPES_MEMBER + (" " + SCOPES_ORG if "--org" in sys.argv else "")
    state = secrets.token_urlsafe(16)
    url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode({"response_type": "code", "client_id": c["client_id"], "redirect_uri": REDIRECT, "state": state, "scope": scopes})
    got = {}
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query); got.update(q)
            self.send_response(200); self.end_headers(); self.wfile.write(b"<h2>Done. You can close this tab.</h2>")
        def log_message(self, *a): pass
    print("Opening the browser; log in and allow. Waiting on", REDIRECT); webbrowser.open(url)
    srv = HTTPServer(("localhost", 8765), H); srv.handle_request()
    if got.get("state", [""])[0] != state or "code" not in got: sys.exit("no code received: " + str(got.get("error_description", got)))
    data = urllib.parse.urlencode({"grant_type": "authorization_code", "code": got["code"][0], "redirect_uri": REDIRECT, "client_id": c["client_id"], "client_secret": c["client_secret"]}).encode()
    tok = json.load(urllib.request.urlopen(urllib.request.Request("https://www.linkedin.com/oauth/v2/accessToken", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})))
    c["access_token"] = tok["access_token"]; c["expires"] = (datetime.now() + timedelta(seconds=int(tok.get("expires_in", 0)))).isoformat(timespec="seconds"); c["scopes"] = tok.get("scope", scopes)
    me = json.load(urllib.request.urlopen(urllib.request.Request("https://api.linkedin.com/v2/userinfo", headers={"Authorization": "Bearer " + c["access_token"]})))
    c["person_urn"] = "urn:li:person:" + me["sub"]; c["name"] = me.get("name", "")
    save(c); print(f"authorised as {c['name']}, token valid until {c['expires'][:10]}, scopes: {c['scopes']}; saved to {CFG_FILE}")

if __name__ == "__main__": main()
