#!/usr/bin/env python3
"""Voice memos from the board -> library/memos/<ts>.{m4a,txt} + index.csv. Local whisper.cpp, zero tokens.
A memo recorded on a card (<file>.card.txt holds the card id) is a spoken note for that post: its transcript is written as a
change decision into board/data/decisions-local/ (never into the server mirror), apply_decisions.py applies it in the same run,
redraft.py rewrites the post, learn.py reads the note like a typed one. Runs in the fast chain, so about a minute after Stop."""
import csv, json, os, shutil, subprocess, sys
from datetime import datetime
from common import LIB, BOARD_LOCAL, p, log

MEM = os.path.join(LIB, "memos"); INDEX = os.path.join(MEM, "index.csv")
FIELDS = ["id", "file", "recorded", "seconds", "words", "status", "used_in", "note"]
MODEL = p("pipeline", "models", "ggml-small.bin")
WHISPER = shutil.which("whisper-cli") or shutil.which("whisper-cpp") or "/opt/homebrew/bin/whisper-cli"

def rows():
    return list(csv.DictReader(open(INDEX, newline="", encoding="utf-8"))) if os.path.isfile(INDEX) and os.path.getsize(INDEX) else []

def transcribe(src):
    wav = src + ".wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ar", "16000", "-ac", "1", wav], check=True)
    r = subprocess.run([WHISPER, "-m", MODEL, "-l", "auto", "-nt", "-np", "-f", wav], capture_output=True, text=True)
    os.remove(wav)
    if r.returncode: raise RuntimeError(r.stderr[-400:])
    return " ".join(l.strip() for l in r.stdout.splitlines() if l.strip())

def main():
    os.makedirs(MEM, exist_ok=True); up = os.path.join(BOARD_LOCAL, "uploads", "memos"); done = {r["id"] for r in rows()}; out = rows(); n = 0
    for f in sorted(os.listdir(up)) if os.path.isdir(up) else []:
        if f.endswith(".txt") or f in done: continue
        src = os.path.join(up, f); dst = os.path.join(MEM, f); shutil.move(src, dst)
        note_f = src + ".note.txt"; note = open(note_f).read().strip() if os.path.isfile(note_f) else ""
        card_f = src + ".card.txt"; card = open(card_f).read().strip() if os.path.isfile(card_f) else ""
        for x in (note_f, card_f):
            if os.path.isfile(x): os.remove(x)
        try: text = transcribe(dst)
        except Exception as e: log("transcribe failed", f, e); text = ""
        open(os.path.splitext(dst)[0] + ".txt", "w", encoding="utf-8").write(text)
        status = ("new" if len(text.split()) >= 15 else "short") if text else "failed"
        if card and text:
            ld = os.path.join(BOARD_LOCAL, "decisions-local"); os.makedirs(ld, exist_ok=True)
            d = {"type": "post", "card_id": card, "decision": "change", "note": text, "via": "voice", "ts": datetime.now().astimezone().isoformat(timespec="seconds")}
            open(os.path.join(ld, datetime.now().strftime("%Y-%m-%d") + ".jsonl"), "a", encoding="utf-8").write(json.dumps(d, ensure_ascii=False) + "\n")
            status, note = "card-note", f"note for {card}"; log("voice note for", card, "->", text[:80])
        out.append({"id": f, "file": os.path.relpath(dst, LIB), "recorded": datetime.fromtimestamp(os.path.getmtime(dst)).isoformat(timespec="seconds"),
                    "seconds": "", "words": str(len(text.split())), "status": status, "used_in": card, "note": note}); n += 1
    with open(INDEX, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader(); w.writerows(out)
    log(f"memos transcribed: {n}")

if __name__ == "__main__": main()
