#!/usr/bin/env python3
"""Two-way sync with the board on the server (rsync over the SSH alias).
push: cards.json, queue/, photos.json, messages.json, img/  ->  server data/
pull: decisions/, uploads/, settings.json, overlay.json      <-  server data/
Then apply_decisions.py folds the pulled decisions into content-plan.csv and the library.
"""
import os, subprocess, sys
from common import CFG, BOARD_LOCAL, remote_dir, log

ALIAS = CFG["board"]["ssh_alias"]; R = remote_dir()

SSH = "ssh -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o BatchMode=yes"   # a dead connection ends in a minute, never hangs (21.10.: a pull hung 4.5 h)
def rsync(args, must=True):
    cmd = ["rsync", "-az", "--timeout=60", "-e", SSH] + args
    try: r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired: log("rsync timed out:", " ".join(cmd)); sys.exit(1) if must else None; return
    if r.returncode: log("rsync failed:", " ".join(cmd), r.stderr.strip()); sys.exit(1)

def push():
    for item in ("cards.json", "pipeline.json", "photos.json", "messages.json", "applied.json", "health.json"):
        f = os.path.join(BOARD_LOCAL, item)
        if os.path.isfile(f): rsync([f, f"{ALIAS}:{R}/data/"])
    for d in ("queue", "img"):
        src = os.path.join(BOARD_LOCAL, d)
        if os.path.isdir(src): rsync(["--delete", src + "/", f"{ALIAS}:{R}/data/{d}/"])   # mirror: pruned images leave the server too

def pull():
    os.makedirs(os.path.join(BOARD_LOCAL, "decisions"), exist_ok=True)
    rsync([f"{ALIAS}:{R}/data/decisions/", os.path.join(BOARD_LOCAL, "decisions") + "/"])
    # uploads are MOVED to the Mac: once pulled they leave the server, so "pending" on the board = not yet pulled
    for d in ("uploads/photos", "uploads/memos"):
        os.makedirs(os.path.join(BOARD_LOCAL, d), exist_ok=True)
        rsync(["--remove-source-files", f"{ALIAS}:{R}/data/{d}/", os.path.join(BOARD_LOCAL, d) + "/"])
    # macOS ships openrsync without --ignore-missing-args (19.10.: that flag silently skipped these three files for two days); a missing file is simply ignored
    for src, dst in ((f"{R}/data/uploads/photo-notes.json", os.path.join(BOARD_LOCAL, "uploads") + "/"), (f"{R}/data/settings.json", BOARD_LOCAL + "/"), (f"{R}/data/overlay.json", BOARD_LOCAL + "/")):
        try: subprocess.run(["rsync", "-az", "--timeout=60", "-e", SSH, f"{ALIAS}:{src}", dst], capture_output=True, timeout=120)
        except subprocess.TimeoutExpired: log("rsync timed out:", src)

def deploy():
    """Code only: index.php, api.php, .htaccess, icon."""
    board = os.path.join(os.path.dirname(BOARD_LOCAL))
    subprocess.run(["ssh", ALIAS, f"mkdir -p {R}/data"], check=True)
    rsync(["--exclude", "data/", board + "/", f"{ALIAS}:{R}/"])

if __name__ == "__main__":
    what = sys.argv[1:] or ["pull", "push"]
    for w in what: {"push": push, "pull": pull, "deploy": deploy}[w](); log(w, "ok")
