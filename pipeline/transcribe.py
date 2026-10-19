#!/usr/bin/env python3
"""Voice memos from the board -> library/memos/<ts>.{m4a,txt} + index.csv. Local whisper.cpp, zero tokens."""
import csv, os, shutil, subprocess, sys
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
        try: text = transcribe(dst)
        except Exception as e: log("transcribe failed", f, e); text = ""
        open(os.path.splitext(dst)[0] + ".txt", "w", encoding="utf-8").write(text)
        out.append({"id": f, "file": os.path.relpath(dst, LIB), "recorded": datetime.fromtimestamp(os.path.getmtime(dst)).isoformat(timespec="seconds"),
                    "seconds": "", "words": str(len(text.split())), "status": ("new" if len(text.split()) >= 15 else "short") if text else "failed", "used_in": "", "note": note}); n += 1
    with open(INDEX, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader(); w.writerows(out)
    log(f"memos transcribed: {n}")

if __name__ == "__main__": main()
