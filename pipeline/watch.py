#!/usr/bin/env python3
"""The worker's trigger. Runs forever (launchd KeepAlive on the Mac, a service on any other worker):
every POLL seconds it asks the board for its change stamp (api.php?a=ping, a few bytes, no model call); when the stamp
moves (a press, an upload, a memo) it runs the fast chain at once, and every FULL seconds the full chain
(photos, memos, slot filling); an approved card whose slot arrives also starts the fast chain (publish.py). So a note on a card is applied while Anton is still looking at it, not 10 minutes later."""
import json, os, subprocess, sys, time, urllib.request
from datetime import datetime
from common import CFG, ROOT, TOKEN, BOARD_LOCAL, jload, log

POLL, FULL = 15, 600
URL = CFG["board"]["url"].rstrip("/") + "/" + TOKEN + "/api.php?a=ping"
RUN = os.path.join(ROOT, "pipeline", "run.sh")

def stamp():
    with urllib.request.urlopen(URL, timeout=20) as r: return json.load(r).get("stamp", 0)

def slot_due():
    """An approved card whose slot has arrived: publish.py must run now, not at the next full run."""
    now = datetime.now().isoformat(timespec="minutes")
    return any(c.get("status") == "approved" and c.get("slot", "9999") <= now for c in jload(os.path.join(BOARD_LOCAL, "cards.json"), []))

LIMIT = 1500   # a run that is still going after 25 minutes is stuck (a hung ssh, a stuck model call): kill it and free the lock

def run(mode):
    import signal
    t = time.time(); p = subprocess.Popen(["/bin/zsh", RUN, mode], start_new_session=True)
    try: rc = p.wait(timeout=LIMIT)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL); rc = -9
        lock = os.path.join(os.path.dirname(RUN), "..", "library", "log", ".run.lock")
        if os.path.isdir(lock): os.rmdir(lock)
        log(f"{datetime.now():%H:%M:%S} {mode} run KILLED after {LIMIT}s, lock freed")
    log(f"{datetime.now():%H:%M:%S} {mode} run rc={rc} in {time.time() - t:.0f}s")

TICK = URL.replace("a=ping", "a=tick"); last_tick = 0
def tick():
    """Ask the server to publish what is due (server/publish.php). Independent of the Mac's chain; the hPanel cron does the same every 5 min."""
    global last_tick
    if time.time() - last_tick < 60: return
    last_tick = time.time()
    try:
        with urllib.request.urlopen(TICK, timeout=90) as r: d = json.load(r)
        if d.get("published") or d.get("failed"): log("server tick:", d)
    except Exception as e: log("tick failed:", str(e)[:120])

def main():
    last = None; last_full = 0
    while True:
        tick()
        try: s = stamp()
        except Exception as e: log("ping failed:", str(e)[:120]); time.sleep(30); continue
        if last is None: last = s                       # first stamp: the full run below handles whatever is there
        if time.time() - last_full >= FULL: run("full"); last_full = time.time(); last = s
        elif s != last or slot_due(): run("fast"); last = s
        time.sleep(POLL)

if __name__ == "__main__": main()
