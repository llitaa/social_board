#!/usr/bin/env python3
"""The worker's trigger. Runs forever (launchd KeepAlive on the Mac, a service on any other worker):
every POLL seconds it asks the board for its change stamp (api.php?a=ping, a few bytes, no model call); when the stamp
moves (a press, an upload, a memo) it runs the fast chain at once, and every FULL seconds the full chain
(photos, memos, slot filling); an approved card whose slot arrives also starts the fast chain (publish.py). So a note on a card is applied while Anton is still looking at it, not 10 minutes later."""
import json, os, subprocess, sys, time, urllib.request
from datetime import datetime
from common import CFG, ROOT, TOKEN, BOARD_LOCAL, jload, log, users

POLL, FULL = 15, 600
BASE = CFG["board"]["url"].rstrip("/") + "/"
RUN = os.path.join(ROOT, "pipeline", "run.sh")

def boards():
    """[(user, token, local mirror)] for every board this worker serves: Anton's plus users/<slug>/ (common.users())."""
    out = [("", TOKEN, BOARD_LOCAL)]
    for u in users():
        d = os.path.join(ROOT, "users", u)
        out.append((u, open(os.path.join(d, "token")).read().strip(), os.path.join(d, "board-data")))
    return out

def stamp(token):
    with urllib.request.urlopen(BASE + token + "/api.php?a=ping", timeout=20) as r: return json.load(r).get("stamp", 0)

def slot_due(local):
    """An approved card whose slot has arrived: publish.py must run now, not at the next full run."""
    now = datetime.now().isoformat(timespec="minutes")
    return any(c.get("status") == "approved" and c.get("slot", "9999") <= now for c in jload(os.path.join(local, "cards.json"), []))

LIMIT = 1500   # a run that is still going after 25 minutes is stuck (a hung ssh, a stuck model call): kill it and free the lock

def run(mode, user=""):
    import signal
    t = time.time(); p = subprocess.Popen(["/bin/zsh", RUN, mode], start_new_session=True, env=dict(os.environ, BOARD_USER=user))
    try: rc = p.wait(timeout=LIMIT)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL); rc = -9
        lock = os.path.join(ROOT, "users", user, "library", "log", ".run.lock") if user else os.path.join(ROOT, "library", "log", ".run.lock")
        if os.path.isdir(lock): os.rmdir(lock)
        log(f"{datetime.now():%H:%M:%S} {user or 'anton'} {mode} run KILLED after {LIMIT}s, lock freed")
    log(f"{datetime.now():%H:%M:%S} {user or 'anton'} {mode} run rc={rc} in {time.time() - t:.0f}s")

last_tick = 0
def tick(token):
    """Ask the server to publish what is due (server/publish.php). Independent of the Mac's chain; the hPanel cron does the same every 5 min."""
    try:
        with urllib.request.urlopen(BASE + token + "/api.php?a=tick", timeout=90) as r: d = json.load(r)
        if d.get("published") or d.get("failed"): log("server tick:", d)
    except Exception as e: log("tick failed:", str(e)[:120])

def main():
    global last_tick
    last = {}; last_full = 0
    while True:
        bs = boards()
        if time.time() - last_tick >= 60:
            last_tick = time.time()
            for u, tok, _ in bs: tick(tok)
        if time.time() - last_full >= FULL:            # the full chain, every board in turn (Anton first: his run syncs the user registry)
            for u, tok, _ in bs: run("full", u)
            last_full = time.time()
            for u, tok, _ in boards():
                try: last[u] = stamp(tok)
                except Exception: pass
            time.sleep(POLL); continue
        for u, tok, local in bs:
            try: s = stamp(tok)
            except Exception as e: log("ping failed:", u or "anton", str(e)[:120]); continue
            if u not in last: last[u] = s; continue       # first stamp: the next full run handles whatever is there
            if s != last[u] or slot_due(local): run("fast", u); last[u] = s
        time.sleep(POLL)

if __name__ == "__main__": main()
