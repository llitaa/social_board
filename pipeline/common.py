"""Shared helpers for the pipeline: config, paths, CSV access (safe: extra columns survive, temp file + replace)."""
import csv, json, os, sys, tempfile
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = yaml.safe_load(open(os.path.join(ROOT, "config.yaml")))
LIB = os.path.join(ROOT, "library")
BOARD_LOCAL = os.path.join(ROOT, "board", "data")   # local mirror of the server's data/ dir
TOKEN = open(os.path.join(ROOT, "config.local.token")).read().strip()
CAMP = CFG["campaign_repo"]

def p(*parts): return os.path.join(ROOT, *parts)

def resolve(ref):
    """A path from a CSV: absolute, or 'library/...' (this repo), else relative to the campaign repo."""
    ref = os.path.expanduser((ref or "").strip())
    if not ref: return ""
    if os.path.isabs(ref): return ref
    if ref.startswith("library/"): return os.path.join(ROOT, ref)
    return os.path.join(CAMP, ref)

def read_csv(path):
    """Rows as dicts; values beyond the header are kept under the key None (DictReader behaviour)."""
    if not os.path.isfile(path): return [], []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f); return list(r), list(r.fieldnames or [])

def write_csv(path, rows, fields):
    """Never loses data: unknown keys are appended as extra columns, extra positional values are kept,
    the file is written to a temp file first and then replaced atomically."""
    fields = list(fields)
    for r in rows:
        for k in r:
            if k is not None and k not in fields: fields.append(k)
    d = os.path.dirname(os.path.abspath(path)); fd, tmp = tempfile.mkstemp(dir=d, suffix=".csv.tmp"); os.close(fd)
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(fields)
        for r in rows: w.writerow([r.get(k, "") if r.get(k) is not None else "" for k in fields] + list(r.get(None) or []))
    os.replace(tmp, path)

def jload(path, default):
    try: return json.load(open(path, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError): return default

def jdump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"; json.dump(obj, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1); os.replace(tmp, path)

def remote_dir():
    return CFG["board"]["remote_dir"].rstrip("/") + "/" + TOKEN

def log(*a): print(*a, file=sys.stderr)
