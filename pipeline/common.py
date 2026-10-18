"""Shared helpers for the pipeline: config, paths, CSV access."""
import csv, json, os, subprocess, sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = yaml.safe_load(open(os.path.join(ROOT, "config.yaml")))
LIB = os.path.join(ROOT, "library")
BOARD_LOCAL = os.path.join(ROOT, "board", "data")   # local mirror of the server's data/ dir
TOKEN = open(os.path.join(ROOT, "config.local.token")).read().strip()

def p(*parts): return os.path.join(ROOT, *parts)

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f); return list(r), r.fieldnames

def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def jload(path, default):
    try: return json.load(open(path, encoding="utf-8"))
    except FileNotFoundError: return default

def jdump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def remote_dir():
    return CFG["board"]["remote_dir"].rstrip("/") + "/" + TOKEN

def log(*a): print(*a, file=sys.stderr)
