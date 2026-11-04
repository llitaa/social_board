"""Shared helpers for the pipeline: config, paths, CSV access (safe: extra columns survive, temp file + replace).

Users (03.11.2026): the same code serves several boards. BOARD_USER empty = the default board (Anton: library/, board/data,
~/dev/campaign). BOARD_USER=<slug> = users/<slug>/ with its own library, campaign CSVs, board mirror, token and LinkedIn
token; users/<slug>/config.yaml overrides the root config (slots, llm, name). Every script imports its paths from here,
so `BOARD_USER=krickl python3 pipeline/draft.py` is the whole switch."""
import csv, json, os, sys, tempfile
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = os.environ.get("BOARD_USER", "").strip()
if USER and not all(c.isalnum() or c in "-_" for c in USER): raise SystemExit(f"bad BOARD_USER {USER!r}")
UDIR = os.path.join(ROOT, "users", USER) if USER else ROOT

REPLACE = {"slots", "engagement", "photo_sources"}   # a user's config replaces these whole (no company slot inherited from Anton's), the rest is merged key by key
def _merge(a, b):
    out = dict(a)
    for k, v in (b or {}).items(): out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) and k not in REPLACE else v
    return out

CFG = yaml.safe_load(open(os.path.join(ROOT, "config.yaml")))
if USER:
    uf = os.path.join(UDIR, "config.yaml")
    CFG = _merge(CFG, yaml.safe_load(open(uf)) or {} if os.path.isfile(uf) else {})
    CFG.update({"campaign_repo": os.path.join(UDIR, "campaign"), "content_plan": os.path.join(UDIR, "campaign", "content-plan.csv"),
                "posts_log": os.path.join(UDIR, "campaign", "posts-log.csv"), "inbound_log": os.path.join(UDIR, "campaign", "inbound-log.csv"),
                "profile_weekly": os.path.join(UDIR, "campaign", "profile-weekly.csv"), "post_texts": os.path.join(UDIR, "library", "drafts"),
                "post_images": os.path.join(UDIR, "library", "images"), "legacy_photos": "", "photo_sources": [os.path.join(UDIR, "inbox")],
                "cv_pdf": "", "company_context": os.path.join(UDIR, "library", "profile.md")})
    CFG.setdefault("llm", {}); CFG["llm"].setdefault("auto", False)
LIB = os.path.join(UDIR, "library")
BOARD_LOCAL = os.path.join(UDIR, "board-data" if USER else os.path.join("board", "data"))   # local mirror of the server's data/ dir
_tf = os.path.join(UDIR, "token") if USER else os.path.join(ROOT, "config.local.token")
TOKEN = open(_tf).read().strip() if os.path.isfile(_tf) else ""
if not TOKEN: raise SystemExit(f"no board token in {_tf} (python3 pipeline/users.py sync creates users/<slug>/)")
LI_FILE = os.path.join(UDIR, "linkedin.json") if USER else os.path.join(ROOT, "config.local.linkedin.json")
LI_ORG_FILE = "" if USER else os.path.join(ROOT, "config.local.linkedin-org.json")
CAMP = CFG["campaign_repo"]

def p(*parts): return os.path.join(ROOT, *parts)

def users():
    """Slugs of all non-default boards on this worker (users/<slug>/token exists)."""
    d = os.path.join(ROOT, "users")
    return sorted(u for u in os.listdir(d) if os.path.isfile(os.path.join(d, u, "token"))) if os.path.isdir(d) else []

def groups_of(cfg):
    """The groups a board belongs to (04.11.: a list; the old single `group:` still works). A group is who shares with whom."""
    g = cfg.get("groups") or cfg.get("group") or ["bni-gilching"]
    if isinstance(g, str): g = [x.strip() for x in g.split(",")]
    return [x for x in g if x]

def boards():
    """Every board on this worker: {slug: {"dir": base dir, "lib": library, "mirror": board data mirror, "name": display name, "groups": [...]}}. Anton = "anton"."""
    root = yaml.safe_load(open(os.path.join(ROOT, "config.yaml")))
    reg = jload(os.path.join(ROOT, "users", ".registry.json"), {})   # host registry copy (users.py sync); the registry wins for groups, config.yaml is the fallback
    out = {"anton": {"dir": ROOT, "lib": os.path.join(ROOT, "library"), "mirror": os.path.join(ROOT, "board", "data"), "name": "Anton Lytvynenko", "groups": groups_of(reg.get("anton") or root)}}
    for u in users():
        d = os.path.join(ROOT, "users", u); pr = jload(os.path.join(d, "library", "profile.json"), {})
        uc = os.path.join(d, "config.yaml"); ucfg = (yaml.safe_load(open(uc)) or {}) if os.path.isfile(uc) else {}
        out[u] = {"dir": d, "lib": os.path.join(d, "library"), "mirror": os.path.join(d, "board-data"), "name": pr.get("name") or u, "groups": groups_of(ucfg)}
    return out

def profile():
    """Who this board belongs to: name, first name, language, role line, facts text. Default = Anton (as the code was written);
    a user's profile comes from library/profile.json (written by onboard.py, confirmed on the board)."""
    if not USER: return {"slug": "anton", "name": "Anton Lytvynenko", "first": "Anton", "initials": "AL", "lang": "de", "default": True}
    pr = jload(os.path.join(LIB, "profile.json"), {})
    name = pr.get("name") or CFG.get("name") or USER
    first = pr.get("first") or name.split()[0]
    ini = "".join(w[0] for w in name.split()[:2]).upper()
    return {"slug": USER, "name": name, "first": first, "initials": ini, "lang": pr.get("lang") or CFG.get("lang", "de"), "default": False,
            "role": pr.get("role", ""), "company": pr.get("company", ""), "website": pr.get("website", ""), "audience": pr.get("audience", ""),
            "topics": pr.get("topics", []), "confirmed": bool(pr.get("confirmed")),
            # Mein Profil (04.11.): what the person set on the board; draft.py, inventory.py and rules_check.py read it
            "offer": pr.get("offer", ""), "tone": pr.get("tone", ""), "avoid": pr.get("avoid", []), "examples": pr.get("examples", ""),
            "style": {"register": "", "length": "mittel", "question": "ja", **(pr.get("style") or {})}, "share_default": bool(pr.get("share_default"))}

def resolve(ref):
    """A path from a CSV: absolute, or 'library/...' (this board's library), else relative to the campaign repo."""
    ref = os.path.expanduser((ref or "").strip())
    if not ref: return ""
    if os.path.isabs(ref): return ref
    if ref.startswith("library/"): return os.path.join(UDIR, ref)
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
    d = os.path.dirname(os.path.abspath(path)); os.makedirs(d, exist_ok=True); fd, tmp = tempfile.mkstemp(dir=d, suffix=".csv.tmp"); os.close(fd)
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

def remote_dir(token=None):
    return CFG["board"]["remote_dir"].rstrip("/") + "/" + (token or TOKEN)

def log(*a): print(*a, file=sys.stderr)
