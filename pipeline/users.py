#!/usr/bin/env python3
"""Boards for other people (03.11.2026). A board = a directory on the server (board/<token>/, same code, own data/) and a
directory on the worker (users/<slug>/: library, campaign CSVs, board mirror, token, config). The registry of boards is
~/board-worker/users.json on the host, written by the admin page (board/admin/) or by `users.py add`.
  python3 pipeline/users.py sync                 pull the registry, create users/<slug>/ for new boards, deploy the code to every board
  python3 pipeline/users.py add <slug> "<Name>" [lang] [group,group]   create a board from here (prints the link and the one-time password)
  python3 pipeline/users.py admin                set or reset the admin password of board/admin/ (asks for it)
  python3 pipeline/users.py list"""
import json, os, secrets, shutil, subprocess, sys, tempfile, yaml
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CFG, ROOT, read_csv, write_csv, jload, jdump, log

ALIAS = CFG["board"]["ssh_alias"]; REMOTE = CFG["board"]["remote_dir"].rstrip("/"); URL = CFG["board"]["url"].rstrip("/")
SSH = ["ssh", "-o", "ConnectTimeout=20", "-o", "BatchMode=yes", ALIAS]
UDIR = os.path.join(ROOT, "users"); CAMP = CFG["campaign_repo"]
CSV_HEADERS = {"content-plan.csv": "id,campaign,channel,slot,asset,format,language,caption_ref,planned,status,notes",
               "posts-log.csv": "date,channel,post_id,hook,type,language,link,link_placement,src_tag,impressions,link_impressions,reactions,comments,targeting,note,reposts,numbers_at,situation",
               "inbound-log.csv": "date,source,who,what,qualified,next", "profile-weekly.csv": "week,visits,entered_at"}

def ssh(cmd, must=True):
    r = subprocess.run(SSH + [cmd], capture_output=True, text=True, timeout=90)
    if r.returncode and must: raise RuntimeError(f"ssh failed: {cmd}: {r.stderr.strip()[:300]}")
    return r.stdout

def registry():
    out = ssh("cat ~/board-worker/users.json 2>/dev/null || echo '{}'")
    try: return json.loads(out or "{}")
    except json.JSONDecodeError: return {}

def write_registry(reg):
    fd, tmp = tempfile.mkstemp(suffix=".json"); os.close(fd); json.dump(reg, open(tmp, "w"), ensure_ascii=False, indent=1)
    subprocess.run(["scp", "-q", tmp, f"{ALIAS}:~/board-worker/users.json"], check=True, timeout=90); os.remove(tmp)
    ssh("chmod 600 ~/board-worker/users.json")

def local_config(slug, name, lang, groups=("bni-gilching",)):
    return {"name": name, "lang": lang, "groups": list(groups),   # boards share material only within a common group (match.py); several groups allowed (04.11.)
            "llm": {"auto": True},                                       # a user's board must work without Anton at the terminal (decision 03.11.: per-user exception to llm.auto false)
            "slots": {"personal": {"days": ["Tue"], "time": "08:00", "lang": lang}},   # one post a week; the user changes it in users/<slug>/config.yaml
            "engagement": {"days": [], "pillars": []}, "personal_card": {"style": "off"}, "orthography": "de" if lang == "de" else "en",
            "photo_sources": [], "publish": {"where": "server"}}

def ensure_local(slug, info):
    """users/<slug>/ with everything the chain expects; idempotent."""
    d = os.path.join(UDIR, slug); new = not os.path.isdir(d)
    for sub in ("library/drafts", "library/photos/shoots", "library/photos/square", "library/memos", "library/log", "library/images", "library/sources", "campaign", "board-data", "inbox"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    for f, h in CSV_HEADERS.items():
        p = os.path.join(d, "campaign", f)
        if not os.path.isfile(p): open(p, "w", encoding="utf-8").write(h + "\n")
    inv = os.path.join(d, "library", "inventory.csv")
    if not os.path.isfile(inv): open(inv, "w", encoding="utf-8").write(open(os.path.join(ROOT, "library", "inventory.csv"), encoding="utf-8").readline())
    cf = os.path.join(d, "config.yaml")
    from common import groups_of
    want = groups_of(info)
    if not os.path.isfile(cf): yaml.safe_dump(local_config(slug, info.get("name", slug), info.get("lang", "de"), want), open(cf, "w"), allow_unicode=True, sort_keys=False)
    else:
        c = yaml.safe_load(open(cf)) or {}
        if groups_of(c) != want or "group" in c: c.pop("group", None); c["groups"] = want; yaml.safe_dump(c, open(cf, "w"), allow_unicode=True, sort_keys=False)   # the registry (admin page) decides the groups
    open(os.path.join(d, "token"), "w").write(info["token"] + "\n"); os.chmod(os.path.join(d, "token"), 0o600)
    pj = os.path.join(d, "library", "profile.json")
    if not os.path.isfile(pj): jdump(pj, {"name": info.get("name", slug), "lang": info.get("lang", "de"), "confirmed": False})
    if new: log("created users/" + slug)
    return d

def deploy(token):
    """Code only (index.php, api.php, auth.php, .htaccess, icon, admin/) into board/<token>/ on the host; data/ untouched."""
    board = os.path.join(ROOT, "board")
    ssh(f"mkdir -p {REMOTE}/{token}/data/decisions {REMOTE}/{token}/data/uploads/photos {REMOTE}/{token}/data/uploads/memos {REMOTE}/{token}/data/uploads/profile {REMOTE}/{token}/data/queue {REMOTE}/{token}/data/img")
    subprocess.run(["rsync", "-az", "--exclude", "data/", "--exclude", "admin/", board + "/", f"{ALIAS}:{REMOTE}/{token}/"], check=True, timeout=120)

def deploy_code_copy():
    """The same files into ~/board-worker/code/ (outside public_html): the admin page copies them into a new board's directory."""
    board = os.path.join(ROOT, "board")
    ssh("mkdir -p ~/board-worker/code ~/board-worker/code/admin")
    subprocess.run(["rsync", "-az", "--delete", "--exclude", "data/", board + "/", f"{ALIAS}:~/board-worker/code/"], check=True, timeout=120)
    subprocess.run(["rsync", "-az", "--delete", "--exclude", "data/", os.path.join(board, "admin") + "/", f"{ALIAS}:{REMOTE}/admin/"], check=True, timeout=120)
    subprocess.run(["scp", "-q", os.path.join(board, "boards.php"), f"{ALIAS}:{REMOTE}/boards.php"], check=True, timeout=60)   # the admin page requires ../boards.php
    subprocess.run(["scp", "-q", os.path.join(board, "li.php"), f"{ALIAS}:{REMOTE}/li.php"], check=True, timeout=60)   # LinkedIn OAuth callback for all boards (05.11.)

def sync():
    reg = registry(); n = 0
    jdump(os.path.join(UDIR, ".registry.json"), reg)   # local copy: common.boards() reads Anton's groups from it (the board's Profil tab edits them on the host)
    for slug, info in reg.items():
        if slug == "anton" or not info.get("token") or info.get("disabled"): continue
        ensure_local(slug, info); n += 1
    deploy_code_copy()
    for slug, info in reg.items():
        if info.get("token") and not info.get("disabled") and slug != "anton": deploy(info["token"])
    log(f"users sync: {n} boards")

def add(slug, name, lang="de", groups="bni-gilching"):
    if not slug.isalnum() and not all(c.isalnum() or c in "-_" for c in slug): raise SystemExit("slug: letters, digits, - _")
    reg = registry()
    if slug in reg: raise SystemExit(f"{slug} exists: {URL}/{reg[slug]['token']}/")
    token = secrets.token_urlsafe(24).replace("-", "x").replace("_", "y")[:32]; pw = secrets.token_urlsafe(9)
    import hashlib
    reg[slug] = {"name": name, "lang": lang, "groups": [g.strip() for g in groups.split(",") if g.strip()], "token": token, "created": datetime.now().isoformat(timespec="minutes")}
    deploy_code_copy(); deploy(token)
    # password hash via PHP on the host (same algorithm the login uses)
    h = ssh(f"php -r 'echo password_hash($argv[1], PASSWORD_DEFAULT);' {json.dumps(pw)}").strip()
    auth = {"slug": slug, "name": name, "lang": lang, "hash": h, "created": reg[slug]["created"], "must_change": True}
    fd, tmp = tempfile.mkstemp(suffix=".json"); os.close(fd); json.dump(auth, open(tmp, "w"), ensure_ascii=False)
    subprocess.run(["scp", "-q", tmp, f"{ALIAS}:{REMOTE}/{token}/data/auth.json"], check=True, timeout=60); os.remove(tmp)
    write_registry(reg); ensure_local(slug, reg[slug])
    print(f"board for {name}: {URL}/{token}/\npassword (once, they change it at the first login): {pw}")

def admin():
    import getpass
    pw = getpass.getpass("admin password for board/admin/: ")
    h = ssh(f"php -r 'echo password_hash($argv[1], PASSWORD_DEFAULT);' {json.dumps(pw)}").strip()
    ssh("mkdir -p ~/board-worker && chmod 700 ~/board-worker")
    fd, tmp = tempfile.mkstemp(suffix=".json"); os.close(fd); json.dump({"hash": h, "set": datetime.now().isoformat(timespec="minutes")}, open(tmp, "w"))
    subprocess.run(["scp", "-q", tmp, f"{ALIAS}:~/board-worker/admin.json"], check=True, timeout=60); os.remove(tmp); ssh("chmod 600 ~/board-worker/admin.json")
    deploy_code_copy(); print(f"admin: {URL}/admin/")

if __name__ == "__main__":
    a = sys.argv[1:] or ["list"]
    if a[0] == "sync": sync()
    elif a[0] == "add": add(a[1], a[2], a[3] if len(a) > 3 else "de", a[4] if len(a) > 4 else "bni-gilching")
    elif a[0] == "admin": admin()
    else:
        for s, i in registry().items(): print(f"{s:12} {i.get('name', ''):28} {URL}/{i.get('token', '')}/  {'disabled' if i.get('disabled') else ''}")
