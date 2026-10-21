#!/usr/bin/env python3
"""Publish approved cards at their slot through LinkedIn's Posts API (spec linkedin-publishing).
Only status approved, only at or after the slot, only once; the post URL goes into posts-log.csv and the plan row
becomes posted. Company cards need the organisation scope; until granted they stay on the board with Copy text.
Dry run: python3 pipeline/publish.py --dry   (shows what would go out, publishes nothing)."""
import json, os, re, sys, urllib.request
from datetime import datetime
from common import CFG, ROOT, read_csv, write_csv, resolve, log

CFG_FILE = os.path.join(ROOT, "config.local.linkedin.json"); ORG_FILE = os.path.join(ROOT, "config.local.linkedin-org.json")
API = "https://api.linkedin.com/rest"; VERSION = "202609"   # LinkedIn keeps a version about a year; 202509 answered 426 on 21.10.2026

def creds(org=False):
    f = ORG_FILE if org else CFG_FILE
    c = json.load(open(f)) if os.path.isfile(f) else {}
    if not c.get("access_token"): raise RuntimeError(("company page: no API yet" if org else "no LinkedIn token") + ": run pipeline/linkedin_auth.py" + (" --org" if org else ""))
    if c.get("expires", "9999") < datetime.now().isoformat(): raise RuntimeError("LinkedIn token expired: run pipeline/linkedin_auth.py" + (" --org" if org else ""))
    return c

def call(c, method, path, body=None, raw=None, ctype="application/json"):
    req = urllib.request.Request(API + path if path.startswith("/") else path, method=method, data=raw if raw is not None else (json.dumps(body).encode() if body is not None else None),
                                 headers={"Authorization": "Bearer " + c["access_token"], "LinkedIn-Version": VERSION, "X-Restli-Protocol-Version": "2.0.0", "Content-Type": ctype})
    with urllib.request.urlopen(req) as r: return r.status, dict(r.headers), r.read()

def upload_image(c, owner, path):
    _, _, b = call(c, "POST", "/images?action=initializeUpload", {"initializeUploadRequest": {"owner": owner}})
    v = json.loads(b)["value"]
    call(c, "PUT", v["uploadUrl"], raw=open(path, "rb").read(), ctype="application/octet-stream")
    return v["image"]

def publish(row, dry=False):
    channel = "company" if row["channel"] == "linkedin-company" else "personal"
    try: c = creds(channel == "company")
    except RuntimeError as e: return None, str(e)
    author = c.get("org_urn") if channel == "company" else c["person_urn"]
    if not author: return None, "company page: no API yet"
    text = open(resolve(row["caption_ref"]), encoding="utf-8").read().strip()
    img = None
    for m in re.findall(r"[\w./\-]+\.(?:png|jpg|jpeg)", row.get("asset", "")):
        p = resolve(m)
        if os.path.isfile(p): img = p; break
    if dry: return "dry", f"{channel}: {len(text)} chars, image {os.path.basename(img) if img else '-'}"
    body = {"author": author, "commentary": text, "visibility": "PUBLIC", "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
            "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False}
    if img: body["content"] = {"media": {"id": upload_image(c, author, img), "altText": ""}}
    st, h, _ = call(c, "POST", "/posts", body)
    urn = h.get("x-restli-id") or h.get("X-RestLi-Id", "")
    return urn, f"https://www.linkedin.com/feed/update/{urn}/" if urn else ""

def main():
    dry = "--dry" in sys.argv; now = datetime.now()
    plan, pf = read_csv(CFG["content_plan"]); plog, lf = read_csv(CFG["posts_log"]); n = 0
    for r in plan:
        if r["status"] != "approved" or not r["channel"].startswith("linkedin"): continue
        slot = r.get("planned", "")
        try: when = datetime.strptime(slot[:16], "%Y-%m-%d %H:%M")
        except ValueError: continue
        cid = "-".join(os.path.basename(r["caption_ref"]).split("-")[0:3])
        if when > now:
            if dry: log(f"approved, waits for its slot: {cid} @ {slot}")
            continue
        try:
            urn, url = publish(r, dry)
            if urn == "dry": log(f"would publish {cid} @ {slot}: {url}"); continue
            if not urn: log(f"{cid}: {url}"); continue
            r["status"] = "posted"; r["notes"] = f"[published via API {now:%Y-%m-%d %H:%M} {url}] " + r.get("notes", ""); n += 1
            found = False
            for l in plog:
                if l["post_id"] == cid: l["link"], l["note"] = url, f"POSTED via API {now:%Y-%m-%d}. " + l.get("note", ""); found = True
            if not found: plog.append({"date": slot[:10], "channel": r["channel"], "post_id": cid, "hook": open(resolve(r["caption_ref"]), encoding="utf-8").readline().strip()[:120], "type": r["format"], "language": r["language"], "link": url, "note": f"POSTED via API {now:%Y-%m-%d}"})
            log(f"published {cid}: {url}")
        except Exception as e:
            r["notes"] = f"[publish failed {now:%Y-%m-%d %H:%M}: {str(e)[:120]}] " + r.get("notes", ""); log("publish failed", cid, e)
    if not dry: write_csv(CFG["content_plan"], plan, pf); write_csv(CFG["posts_log"], plog, lf)
    log(f"published {n}")

if __name__ == "__main__": main()
