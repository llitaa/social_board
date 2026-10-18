#!/usr/bin/env python3
"""Photo pool: board uploads + legacy photos -> library/photos/{inbox,shoots,square} + index.csv,
and board/data/photos.json (+ thumbnails under board/data/img/thumbs/) for the Photos screen.

Rules (spec photo-pool): shoot = same calendar day + GPS within 500 m (+/- 3 h), else same day + note;
crop = 1200x1200 around the largest face, else centre; crop only, never retouch;
status new -> ready -> used (with used_in); previous-shoot rule is enforced by the card proposal step.
Re-runnable; the index is the truth.
"""
import csv, json, math, os, re, shutil
from datetime import datetime
import cv2
from PIL import Image, ImageOps
import pillow_heif
from common import CFG, LIB, BOARD_LOCAL, p, jload, jdump, log

pillow_heif.register_heif_opener()
PH = os.path.join(LIB, "photos"); INBOX, SHOOTS, SQUARE = (os.path.join(PH, d) for d in ("inbox", "shoots", "square"))
THUMBS = os.path.join(BOARD_LOCAL, "img", "thumbs")
INDEX = os.path.join(PH, "index.csv")
FIELDS = ["id", "file", "taken", "shoot", "note", "status", "used_in", "crop", "face", "label", "added"]
YUNET = p("pipeline", "models", "face_detection_yunet_2023mar.onnx")
try: cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
except Exception: pass

def read_index():
    if not os.path.isfile(INDEX) or os.path.getsize(INDEX) == 0: return []
    return list(csv.DictReader(open(INDEX, newline="", encoding="utf-8")))

def write_index(rows):
    with open(INDEX, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

def exif_info(path):
    """Return (taken datetime or None, (lat, lon) or None)."""
    try:
        im = Image.open(path); ex = im.getexif()
        taken = None; gps = None
        for tag in (36867, 306):  # DateTimeOriginal, DateTime
            v = ex.get(tag) or ex.get_ifd(0x8769).get(tag)
            if v:
                try: taken = datetime.strptime(str(v)[:19], "%Y:%m:%d %H:%M:%S"); break
                except ValueError: pass
        g = ex.get_ifd(0x8825)
        if g and 2 in g and 4 in g:
            def dec(t): return float(t[0]) + float(t[1]) / 60 + float(t[2]) / 3600
            lat = dec(g[2]) * (-1 if g.get(1) == "S" else 1); lon = dec(g[4]) * (-1 if g.get(3) == "W" else 1)
            gps = (lat, lon)
        return taken, gps
    except Exception as e:
        log("exif fail", path, e); return None, None

def dist_m(a, b):
    R = 6371000; la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def face_box(im):
    """Largest face in the (transposed) image as (x, y, w, h) or None. YuNet, local, zero tokens."""
    import numpy as np
    a = cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)
    scale = min(1.0, 640 / max(a.shape[:2])); small = cv2.resize(a, None, fx=scale, fy=scale) if scale < 1 else a
    det = cv2.FaceDetectorYN.create(YUNET, "", (small.shape[1], small.shape[0]), 0.6)
    _, faces = det.detect(small)
    if faces is None or len(faces) == 0: return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])[:4]
    return int(x / scale), int(y / scale), int(w / scale), int(h / scale)

def square_crop(im, face):
    W, H = im.size; side = min(W, H)
    if face:
        fx, fy, fw, fh = face; cx = fx + fw / 2; cy = fy + fh / 2 + side * 0.08  # face in the upper half
        x = int(min(max(cx - side / 2, 0), W - side)); y = int(min(max(cy - side / 2, 0), H - side))
    else:
        x, y = (W - side) // 2, (H - side) // 2
    return x, y, side

def render_square(src, crop, dst):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB"); x, y, s = crop
    im.crop((x, y, x + s, y + s)).resize((1200, 1200), Image.LANCZOS).save(dst, "PNG")

def thumb(src, dst):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB"); im.thumbnail((400, 400)); im.save(dst, "JPEG", quality=80)

def slug(s): return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:30]

def assign_shoot(rows, taken, gps, note):
    """Find an existing shoot for this photo or make a new shoot id."""
    day = (taken or datetime.now()).strftime("%Y-%m-%d")
    for r in rows:
        if not r["shoot"].startswith(day): continue
        rt = datetime.fromisoformat(r["taken"]) if r["taken"] else None
        if gps and r.get("_gps"):
            if dist_m(gps, r["_gps"]) <= 500 and (not rt or not taken or abs((rt - taken).total_seconds()) <= 3 * 3600): return r["shoot"]
        elif not gps and (r["note"] == note or not note): return r["shoot"]
    return f"{day}_{slug(note) or 'shoot'}"

def ingest(path, note="", status="new", legacy=False):
    rows = read_index()
    if any(r["file"].endswith(os.path.basename(path)) or r["id"] == os.path.splitext(os.path.basename(path))[0] for r in rows): return None
    taken, gps = exif_info(path)
    for r in rows: r["_gps"] = None
    shoot = assign_shoot(rows, taken, gps, note)
    pid = os.path.splitext(os.path.basename(path))[0].replace("IMG_", "img")[-12:]
    sdir = os.path.join(SHOOTS, shoot); os.makedirs(sdir, exist_ok=True); os.makedirs(SQUARE, exist_ok=True); os.makedirs(THUMBS, exist_ok=True)
    dst = os.path.join(sdir, os.path.basename(path))
    if legacy: shutil.copy2(path, dst)
    else: shutil.move(path, dst)
    im = ImageOps.exif_transpose(Image.open(dst)); face = face_box(im); crop = square_crop(im, face)
    render_square(dst, crop, os.path.join(SQUARE, pid + "_sq.png")); thumb(dst, os.path.join(THUMBS, pid + ".jpg"))
    row = {"id": pid, "file": os.path.relpath(dst, LIB), "taken": taken.isoformat() if taken else "", "shoot": shoot, "note": note,
           "status": status, "used_in": "", "crop": f"{crop[0]},{crop[1]},{crop[2]}", "face": "yes" if face else "no", "label": "", "added": datetime.now().isoformat(timespec="seconds")}
    rows = [{k: v for k, v in r.items() if k in FIELDS} for r in rows] + [row]; write_index(rows); return row

def apply_board_events():
    """Photo decisions from the board (delete / mark_used / use_friday) and upload notes."""
    ev = os.path.join(LIB, "log", "board-events.csv"); rows = read_index()
    if os.path.isfile(ev):
        for e in csv.DictReader(open(ev, newline="", encoding="utf-8")):
            if e["type"] != "photo": continue
            for r in rows:
                if r["id"] == e["id"] or r["shoot"] == e["id"]:
                    if e["decision"] == "mark_used" and r["status"] != "used": r["status"], r["used_in"] = "used", r["used_in"] or "manual"
                    if e["decision"] == "delete": r["status"] = "deleted"
                    if e["decision"] == "use_friday": r["label"] = "friday"
    write_index(rows)

def mark_used_from_posts():
    """A photo whose square was the image of a published post is used; its whole shoot too."""
    plog = list(csv.DictReader(open(CFG["posts_log"], newline="", encoding="utf-8"))); rows = read_index()
    plan = list(csv.DictReader(open(CFG["content_plan"], newline="", encoding="utf-8")))
    text = "\n".join(r.get("post_id", "") + " " + r.get("note", "") + " " + r.get("type", "") for r in plog if "POSTED" in r.get("note", "").upper() or r.get("impressions") or r.get("reactions"))
    text += "\n" + "\n".join(os.path.basename(r.get("caption_ref", "")).rsplit("-", 2)[0] + " " + r.get("asset", "") + " " + r.get("notes", "") for r in plan if r.get("status") == "posted")
    for r in rows:
        base = os.path.splitext(os.path.basename(r["file"]))[0]
        if base in text and r["status"] != "used":
            m = re.search(r"(li-(?:post|comp)-\d+)[^\n]*" + re.escape(base), text) or re.search(re.escape(base) + r"[^\n]*(li-(?:post|comp)-\d+)", text)
            r["status"], r["used_in"] = "used", (m.group(1) if m else "posts-log")
    shoots_used = {r["shoot"]: r["used_in"] for r in rows if r["status"] == "used"}
    for r in rows:
        if r["shoot"] in shoots_used and r["status"] in ("ready", "new"): r["status"], r["used_in"] = "used", shoots_used[r["shoot"]]
    write_index(rows)

def export_board():
    rows = [r for r in read_index() if r["status"] != "deleted"]; shoots = {}
    for r in rows:
        s = shoots.setdefault(r["shoot"], {"id": r["shoot"], "date": r["shoot"][:10], "label": r["note"] or r["shoot"][11:].replace("-", " "), "photos": [], "status": "ready"})
        s["photos"].append({"id": r["id"], "thumb": f"data/img/thumbs/{r['id']}.jpg", "status": r["status"], "used_in": r["used_in"], "face": r["face"], "label": r["label"]})
    for s in shoots.values():
        st = {p["status"] for p in s["photos"]}
        s["status"] = "used" if st == {"used"} else ("new" if "new" in st else "ready")
    out = sorted(shoots.values(), key=lambda s: s["date"], reverse=True)
    jdump(os.path.join(BOARD_LOCAL, "photos.json"), {"shoots": out, "generated": datetime.now().isoformat(timespec="seconds")})
    return out

def main():
    os.makedirs(INBOX, exist_ok=True)
    n = 0
    notes = jload(os.path.join(BOARD_LOCAL, "uploads", "photo-notes.json"), {})
    up = os.path.join(BOARD_LOCAL, "uploads", "photos")
    for f in sorted(os.listdir(up)) if os.path.isdir(up) else []:
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp")):
            if ingest(os.path.join(up, f), notes.get(f, ""), "ready"): n += 1
    leg = CFG.get("legacy_photos")
    if leg and os.path.isdir(leg):
        for f in sorted(os.listdir(leg)):
            if f.lower().endswith(".heic") and ingest(os.path.join(leg, f), "", "ready", legacy=True): n += 1
    apply_board_events(); mark_used_from_posts()
    shoots = export_board()
    log(f"ingested {n}; shoots: " + ", ".join(f"{s['id']}[{s['status']}:{len(s['photos'])}]" for s in shoots))

if __name__ == "__main__": main()
