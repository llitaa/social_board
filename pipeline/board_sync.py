#!/usr/bin/env python3
"""Two-way sync with the board on the server (rsync over the SSH alias).
push: cards.json, queue/, photos.json, messages.json, img/  ->  server data/
pull: decisions/, uploads/, settings.json, overlay.json      <-  server data/
Then apply_decisions.py folds the pulled decisions into content-plan.csv and the library.
"""
import os, subprocess, sys
from common import CFG, BOARD_LOCAL, remote_dir, log

ALIAS = CFG["board"]["ssh_alias"]; R = remote_dir()

def rsync(args):
    cmd = ["rsync", "-az", "--timeout=60"] + args
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: log("rsync failed:", " ".join(cmd), r.stderr.strip()); sys.exit(1)

def push():
    for item in ("cards.json", "photos.json", "messages.json"):
        f = os.path.join(BOARD_LOCAL, item)
        if os.path.isfile(f): rsync([f, f"{ALIAS}:{R}/data/"])
    for d in ("queue", "img"):
        src = os.path.join(BOARD_LOCAL, d)
        if os.path.isdir(src): rsync([src + "/", f"{ALIAS}:{R}/data/{d}/"])

def pull():
    for d in ("decisions", "uploads"):
        os.makedirs(os.path.join(BOARD_LOCAL, d), exist_ok=True)
        rsync([f"{ALIAS}:{R}/data/{d}/", os.path.join(BOARD_LOCAL, d) + "/"])
    for item in ("settings.json", "overlay.json"):
        subprocess.run(["rsync", "-az", "--ignore-missing-args", f"{ALIAS}:{R}/data/{item}", BOARD_LOCAL + "/"], capture_output=True)

def deploy():
    """Code only: index.php, api.php, .htaccess, icon."""
    board = os.path.join(os.path.dirname(BOARD_LOCAL))
    subprocess.run(["ssh", ALIAS, f"mkdir -p {R}/data"], check=True)
    rsync(["--exclude", "data/", board + "/", f"{ALIAS}:{R}/"])

if __name__ == "__main__":
    what = sys.argv[1:] or ["pull", "push"]
    for w in what: {"push": push, "pull": pull, "deploy": deploy}[w](); log(w, "ok")
