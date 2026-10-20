#!/usr/bin/env python3
"""Photo pool: board uploads + photo sources (e.g. ~/Downloads) + legacy photos
-> library/photos/{shoots,square} + index.csv, and board/data/photos.json (+ thumbnails) for the Photos screen.

Rules (spec photo-pool):
- a camera photo (EXIF date + camera model) with a detected face is taken into the pool; originals stay where they are
- shoot = same calendar day (GPS within 500 m when both have it)
- crop = 1200x1200 around the largest face, else centre; crop only, never retouch
- status new/ready/used/hold/deleted; used photos become eligible again photo_reuse_days (90) after used_at
- the system picks the photo for a post (pick()); newest first, never-used before re-used, photos older than
  photo_fresh_months only when nothing newer is eligible, never the shoot of the neighbouring posts (+/- 3 days)
- each photo gets scene/tags/people once from the tags model (Haiku) so drafts can match picture and topic
Re-runnable; index.csv is the truth.
"""
import sys, csv, json, math, os, re, shutil, tempfile
from datetime import datetime, date, timedelta
import cv2
from PIL import Image, ImageOps
import pillow_heif
from common import CFG, LIB, BOARD_LOCAL, p, jload, jdump, log, read_csv, write_csv, resolve

pillow_heif.register_heif_opener()
PH = os.path.join(LIB, "photos"); SHOOTS, SQUARE = (os.path.join(PH, d) for d in ("shoots", "square"))
THUMBS = os.path.join(BOARD_LOCAL, "img", "thumbs")
INDEX = os.path.join(PH, "index.csv")
FIELDS = ["id", "file", "taken", "gps", "shoot", "note", "status", "used_in", "used_at", "crop", "face", "faces", "scene", "tags", "people", "label", "added", "src"]
YUNET = p("pipeline", "models", "face_detection_yunet_2023mar.onnx")
EXCLUDE = re.compile(r"ust-id|invoice|rechnung|mwst|meme|whatsapp|screenshot|^image ?\(|^image0|quelle|dirk|controllers|^li-post|_upright|^d24-198 \(13\)", re.I)
REUSE = int(CFG.get("photo_reuse_days", 90)); FRESH = int(CFG.get("photo_fresh_months", 24))
try: cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
except Exception: pass

def read_index():
    rows, _ = read_csv(INDEX)
    for r in rows:
        for k in FIELDS: r.setdefault(k, "")
    return rows

def write_index(rows):
    fd, tmp = tempfile.mkstemp(dir=PH, suffix=".tmp"); os.close(fd)
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    os.replace(tmp, INDEX)

def exif_info(path):
    """(taken datetime or None, (lat, lon) or None, camera model or '')."""
    try:
        im = Image.open(path); ex = im.getexif(); ifd = ex.get_ifd(0x8769)
        taken = None
        for v in (ifd.get(36867), ex.get(306)):
            if v:
                try: taken = datetime.strptime(str(v)[:19], "%Y:%m:%d %H:%M:%S"); break
                except ValueError: pass
        g = ex.get_ifd(0x8825); gps = None
        if g and 2 in g and 4 in g:
            def dec(t): return float(t[0]) + float(t[1]) / 60 + float(t[2]) / 3600
            gps = (dec(g[2]) * (-1 if g.get(1) == "S" else 1), dec(g[4]) * (-1 if g.get(3) == "W" else 1))
        return taken, gps, str(ex.get(272) or "").strip()
    except Exception as e:
        log("exif fail", path, e); return None, None, ""

def dist_m(a, b):
    R = 6371000; la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def square_of(r): return os.path.join(SQUARE, r["id"] + "_sq.png")

def faces_of(im):
    """All faces (x, y, w, h) in the transposed image, largest first. YuNet, local, zero tokens."""
    import numpy as np
    a = cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)
    scale = min(1.0, 640 / max(a.shape[:2])); small = cv2.resize(a, None, fx=scale, fy=scale) if scale < 1 else a
    det = cv2.FaceDetectorYN.create(YUNET, "", (small.shape[1], small.shape[0]), 0.6)
    _, f = det.detect(small)
    if f is None: return []
    return sorted([tuple(int(v / scale) for v in x[:4]) for x in f], key=lambda b: -b[2] * b[3])

def square_crop(im, face):
    W, H = im.size; side = min(W, H)
    if face:
        fx, fy, fw, fh = face; cx = fx + fw / 2; cy = fy + fh / 2 + side * 0.08  # face in the upper half
        x = int(min(max(cx - side / 2, 0), W - side)); y = int(min(max(cy - side / 2, 0), H - side))
    else: x, y = (W - side) // 2, (H - side) // 2
    return x, y, side

def render_square(src, crop, dst):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB"); x, y, s = crop
    im.crop((x, y, x + s, y + s)).resize((1200, 1200), Image.LANCZOS).save(dst, "PNG")

def thumb(src, dst):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB"); im.thumbnail((400, 400)); im.save(dst, "JPEG", quality=80)

def slug(s): return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:30]

def pid_of(path):
    base = os.path.splitext(os.path.basename(path))[0]
    if base.upper().startswith("IMG"): base = re.sub(r"\s*\(\d+\)$|\s+\d$", "", base)   # "IMG_1766 (1)" / "IMG_1221 2" are copies
    return re.sub(r"[^a-z0-9]+", "", base.lower().replace("img_", "img").replace("img-", "img"))[-14:]

def assign_shoot(rows, taken, gps, note):
    day = (taken or datetime.now()).strftime("%Y-%m-%d")
    for r in rows:
        if not r["shoot"].startswith(day): continue
        rg = tuple(map(float, r["gps"].split(","))) if r.get("gps") else None
        if gps and rg and dist_m(gps, rg) > 500: continue
        return r["shoot"]
    return f"{day}_{slug(note) or 'shoot'}"

def ingest(path, note="", status="ready", copy=True, src="board"):
    """One photo into the pool. Returns the new row or None (duplicate / no face / excluded)."""
    rows = read_index(); pid = pid_of(path); base = os.path.basename(path)
    if EXCLUDE.search(base): return None
    taken, gps, model = exif_info(path)
    if src != "board" and not taken: return None                      # no camera date: a download, a scan, a meme
    tk = taken.isoformat() if taken else ""
    for r in rows:
        if r["id"] == pid or os.path.basename(r["file"]) == base or (tk and r["taken"] == tk): return None
    im = ImageOps.exif_transpose(Image.open(path)); faces = faces_of(im)
    if src != "board" and not faces: return None                      # pool = photos with a person in them
    shoot = assign_shoot(rows, taken, gps, note)
    sdir = os.path.join(SHOOTS, shoot); os.makedirs(sdir, exist_ok=True); os.makedirs(SQUARE, exist_ok=True); os.makedirs(THUMBS, exist_ok=True)
    dst = os.path.join(sdir, base)
    if not os.path.isfile(dst): (shutil.copy2 if copy else shutil.move)(path, dst)
    face = faces[0] if faces else None; crop = square_crop(im, face)
    render_square(dst, crop, os.path.join(SQUARE, pid + "_sq.png")); thumb(dst, os.path.join(THUMBS, pid + ".jpg"))
    row = {k: "" for k in FIELDS} | {"id": pid, "file": os.path.relpath(dst, LIB), "taken": tk, "gps": f"{gps[0]:.5f},{gps[1]:.5f}" if gps else "",
           "shoot": shoot, "note": note, "status": status, "crop": f"{crop[0]},{crop[1]},{crop[2]}", "face": "yes" if face else "no",
           "faces": str(len(faces)), "added": datetime.now().isoformat(timespec="seconds"), "src": src}
    write_index(rows + [row]); return row

def tag_photos(limit=120):
    """scene / tags / people for rows that have none yet: one small model call per photo on the 400 px thumbnail."""
    from llm import llm_json
    rows = read_index(); n = 0
    for r in rows:
        if r["scene"] or r["status"] == "deleted" or n >= limit: continue
        th = os.path.join(THUMBS, r["id"] + ".jpg")
        if not os.path.isfile(th): continue
        try:
            d = llm_json("tags", f"Read the image file {th} and answer with one JSON object only, no prose: "
                         '{"scene": "one short line, what and where", "tags": ["3-6 lowercase words: place, setting, objects, mood"], '
                         '"people": "one of: one man | man with others | several adults | child present | woman only | none", '
                         '"li_ok": "yes or no: a natural photo a professional could post on LinkedIn"}', files=True)
            r["scene"] = str(d.get("scene", ""))[:120]; r["tags"] = " ".join(str(t) for t in d.get("tags", []))[:120]; r["people"] = str(d.get("people", ""))[:30]
            if SENSITIVE.search(r["scene"] + " " + r["tags"]) or r["people"] in ("child present", "woman only"): purge(r)   # never on the board
            elif r["status"] == "ready" and (d.get("li_ok") == "no" or r["people"] == "none"): r["status"] = "hold"
            n += 1
        except Exception as e: log("tag fail", r["id"], e); r["scene"] = "(untagged)"
    write_index(rows); return n

SENSITIVE = re.compile(r"passport|reisepass|ausweis|id card|identity|document|scan(ned)?\b|invoice|rechnung|certificate|urkunde|screenshot", re.I)

def purge(r):
    """Documents, other people's photos: index row deleted and every copy removed (pool, square, thumbnail)."""
    for f in (os.path.join(LIB, r["file"]), square_of(r), os.path.join(THUMBS, r["id"] + ".jpg")):
        if os.path.isfile(f): os.remove(f)
    r["status"] = "deleted"; r["note"] = (r["note"] + " purged: not a post photo").strip()

def apply_board_events():
    """Photo decisions from the board (delete / hold / mark_used / use_friday)."""
    ev = os.path.join(LIB, "log", "board-events.csv"); rows = read_index()
    if os.path.isfile(ev):
        for e in csv.DictReader(open(ev, newline="", encoding="utf-8")):
            if e["type"] != "photo": continue
            for r in rows:
                if r["id"] == e["id"] or r["shoot"] == e["id"]:
                    if e["decision"] == "mark_used" and r["status"] != "used": r["status"], r["used_in"], r["used_at"] = "used", r["used_in"] or "manual", r["used_at"] or e["ts"][:10]
                    if e["decision"] == "hold" and r["status"] in ("ready", "new"): r["status"] = "hold"
                    if e["decision"] == "delete": r["status"] = "deleted"
                    if e["decision"] == "use_friday": r["label"] = "friday"
    write_index(rows)

def plan_images():
    """post id -> (photo id, date) for every plan row whose asset names a pool photo (posted, scheduled, approved, draft)."""
    plan, _ = read_csv(CFG["content_plan"]); out = {}
    for r in plan:
        if r.get("channel") != "linkedin" or r.get("status") in ("dropped", "skipped", "idea"): continue
        for m in re.findall(r"(IMG[_-]\d{4}|D24-198 \(\d+\)|img\d{4})", r.get("asset", "")):
            cid = "-".join(os.path.basename(r.get("caption_ref", "")).split("-")[0:3]) or f"row-{r['id']}"
            out.setdefault(pid_of(m), []).append((cid, (r.get("planned") or "")[:10], r.get("status")))
    return out

def mark_used_from_posts():
    """A photo named in a posted/scheduled/approved plan row is used, with used_at = the post date; its shoot too."""
    rows = read_index(); pi = plan_images()
    for r in rows:
        for cid, d, st in pi.get(r["id"], []):
            if st in ("posted", "scheduled", "approved") and r["status"] != "used":
                r["status"], r["used_in"], r["used_at"] = "used", cid, d
    shoots_used = {r["shoot"]: (r["used_in"], r["used_at"]) for r in rows if r["status"] == "used"}
    for r in rows:
        if r["shoot"] in shoots_used and r["status"] in ("ready", "new"): r["status"], (r["used_in"], r["used_at"]) = "used", shoots_used[r["shoot"]]
    write_index(rows)

# ---- picking (used by draft.py / redraft.py)
def eligible(r, today):
    if r["status"] == "ready": return True
    if r["status"] == "used" and r["used_at"]:
        try: return (today - date.fromisoformat(r["used_at"][:10])).days >= REUSE
        except ValueError: return False
    return False

def pick(slot_day, neighbour_shoots=(), exclude_ids=(), topic_tags=(), friday=False, today=None):
    """Ranked list of eligible photos for a personal post on slot_day. neighbour_shoots = shoots of the posts just before
    and after this slot (never the same shoot, nor one within 3 days of it)."""
    today = today or date.today()
    reserved = {pid for pid, uses in plan_images().items() if any(st in ("draft", "change", "approved", "scheduled") for _, _, st in uses)}
    rows = [r for r in read_index() if eligible(r, today) and r["id"] not in exclude_ids and r["id"] not in reserved]
    nb = []
    for s in neighbour_shoots:
        try: nb.append(date.fromisoformat(s[:10]))
        except ValueError: pass
    def ok(r):
        try: d = date.fromisoformat(r["shoot"][:10])
        except ValueError: return True
        return all(abs((d - n).days) > 3 for n in nb) and r["shoot"] not in neighbour_shoots
    rows = [r for r in rows if ok(r)]
    tt = {t.lower() for t in topic_tags}
    def key(r):
        tk = r["taken"] or "0000"; old = (today - date.fromisoformat(tk[:10])).days > FRESH * 30 if tk[:4] != "0000" else True
        match = len(tt & set(r["tags"].lower().split())) if tt else 0
        return (0 if friday and r["label"] == "friday" else 1, 1 if r["used_at"] else 0, 0 if r["people"] == "one man" else 1, 1 if old else 0, -match, tk and -int(tk[:10].replace("-", "")) or 0)
    return sorted(rows, key=key)


def export_board():
    rows = [r for r in read_index() if r["status"] != "deleted"]; shoots = {}; today = date.today()
    for r in rows:
        s = shoots.setdefault(r["shoot"], {"id": r["shoot"], "date": r["shoot"][:10], "label": r["note"] or r["scene"] or r["shoot"][11:].replace("-", " "), "photos": [], "status": "ready"})
        free = ""
        if r["status"] == "used" and r["used_at"]:
            try: free = (date.fromisoformat(r["used_at"][:10]) + timedelta(days=REUSE)).isoformat()
            except ValueError: pass
        s["photos"].append({"id": r["id"], "thumb": f"data/img/thumbs/{r['id']}.jpg", "status": r["status"], "used_in": r["used_in"], "free_from": free,
                            "scene": r["scene"], "label": r["label"], "eligible": eligible(r, today)})
    for s in shoots.values():
        st = {p["status"] for p in s["photos"]}
        s["status"] = "used" if st == {"used"} else "hold" if st == {"hold"} else ("new" if "new" in st else "ready")
        s["eligible"] = any(p["eligible"] for p in s["photos"])
    out = sorted(shoots.values(), key=lambda s: s["date"], reverse=True)
    n_el = sum(1 for r in rows if eligible(r, today)); n_used = sum(1 for r in rows if r["status"] == "used" and not eligible(r, today))
    nxt = sorted(p["free_from"] for s in out for p in s["photos"] if p["free_from"] and p["free_from"] > today.isoformat())
    jdump(os.path.join(BOARD_LOCAL, "photos.json"), {"shoots": out, "summary": {"eligible": n_el, "used": n_used, "hold": sum(1 for r in rows if r["status"] == "hold"),
                                                       "next_free": nxt[0] if nxt else "", "reuse_days": REUSE}, "generated": datetime.now().isoformat(timespec="seconds")})
    return out

def card_rows():
    """plan rows of cards on the board by card id, with the plan list and fields for writing back."""
    plan, f = read_csv(CFG["content_plan"]); by = {}
    for r in plan:
        if r.get("channel", "").startswith("linkedin") and r.get("caption_ref"): by["-".join(os.path.basename(r["caption_ref"]).split("-")[0:3])] = r
    return plan, f, by

def set_card_image(r, photo, why):
    """The row's asset and the draft's meta point to this photo; square crop for personal posts, the file itself for company cards."""
    personal = r["channel"] == "linkedin"
    r["asset"] = f"{os.path.basename(photo['file'])} (square: library/photos/square/{photo['id']}_sq.png, {why})" if personal else f"library/photos/{photo['file']} ({why})"
    tp = resolve(r.get("caption_ref", "")); mp = os.path.splitext(tp)[0] + ".json" if tp else ""
    if personal and tp and CFG.get("personal_card", {}).get("style", "off") != "off":
        meta0 = jload(mp, {}); card = meta0.get("card") or {"kicker": "", "headline": open(tp, encoding="utf-8").readline().strip()[:95]}
        import personal_card
        base = os.path.basename(os.path.splitext(tp)[0]); png = personal_card.render(square_of(photo), card, base)
        if png: r["asset"] = f"library/drafts/{base}.png (card: photo {photo['id']} + headline, style {CFG['personal_card']['style']}; {why})"
    if mp and os.path.isfile(mp):
        meta = jload(mp, {}); hist = set(meta.get("photo_history", [])) | ({meta["photo"]} if meta.get("photo") else set())
        meta["photo_history"] = sorted(hist); meta["photo"] = photo["id"]; jdump(mp, meta)

def card_images(uploaded):
    """Board requests for one card's image: 'next photo' (notes marker) and uploads made on the card (uploaded = {card id: index row})."""
    plan, f, by = card_rows(); rows = read_index(); changed = 0; now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for cid, r in by.items():
        if r["status"] in ("posted", "skipped", "dropped"): continue
        m = re.search(r"\[board [^\]]*? photo: next\] ", r.get("notes", ""))
        if m:
            tp = resolve(r.get("caption_ref", "")); meta = jload(os.path.splitext(tp)[0] + ".json", {}) if tp else {}
            ex = set(meta.get("photo_history", [])) | {meta.get("photo", "")}
            try: day = date.fromisoformat((r.get("planned") or "")[:10])
            except ValueError: day = date.today()
            cands = pick(day, meta.get("neighbour_shoots", []), exclude_ids=ex) if r["channel"] == "linkedin" else []
            r["notes"] = r["notes"].replace(m.group(0), f"[photo changed {now}] " if cands else f"[photo: no other photo available {now}] ")
            if cands: set_card_image(r, cands[0], cands[0]["scene"][:60]); changed += 1
        if cid in uploaded:
            ph = uploaded[cid]; set_card_image(r, ph, f"uploaded for {cid}"); changed += 1
            for x in rows:
                if x["id"] == ph["id"]: x["status"], x["used_in"], x["used_at"] = "used", cid, (r.get("planned") or "")[:10]
    if changed: write_csv(CFG["content_plan"], plan, f); write_index(rows); log(f"card images changed: {changed}")

def main(fast=False):
    n = 0; uploaded = {}
    notes = jload(os.path.join(BOARD_LOCAL, "uploads", "photo-notes.json"), {})
    up = os.path.join(BOARD_LOCAL, "uploads", "photos")
    for f in sorted(os.listdir(up)) if os.path.isdir(up) else []:
        if not f.lower().endswith((".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp")): continue
        note = notes.get(f, ""); card = note[5:] if note.startswith("card:") else ""
        row = ingest(os.path.join(up, f), note, "used" if card else "ready", copy=False, src="board")
        if row: n += 1
        elif card: row = next((r for r in read_index() if os.path.basename(r["file"]) == f), None)   # already in the pool
        if card and row: uploaded[card] = row
        if card and not row: log("card upload not usable:", f)
    card_images(uploaded)
    if fast: export_board(); return
    srcs = [CFG.get("legacy_photos")] + [os.path.expanduser(s) for s in CFG.get("photo_sources", [])]
    for d in srcs:
        if not d or not os.path.isdir(d): continue
        for f in sorted(os.listdir(d)):
            fp = os.path.join(d, f)
            if os.path.isfile(fp) and f.lower().endswith((".jpg", ".jpeg", ".heic", ".heif")) and os.path.getsize(fp) >= 300_000:
                try:
                    if ingest(fp, "", "ready", copy=True, src=os.path.basename(d)): n += 1
                except Exception as e: log("ingest fail", f, e)
    apply_board_events(); mark_used_from_posts()
    t = tag_photos()
    shoots = export_board()
    log(f"ingested {n}, tagged {t}; shoots: " + ", ".join(f"{s['id']}[{s['status']}:{len(s['photos'])}]" for s in shoots))

if __name__ == "__main__": main(fast="fast" in sys.argv)
