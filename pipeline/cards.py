#!/usr/bin/env python3
"""Board cards + pipeline from content-plan.csv and posts-log.csv (the truth lives in those two CSVs).
cards.json    = every LinkedIn row with a slot today or later that is not posted/skipped/dropped
                (draft, ready, approved, change, scheduled). Status comes from the CSV; board decisions
                reach the CSV through apply_decisions.py, so the next run shows them here.
pipeline.json = upcoming slots (rows + open slots of the Mon/Wed/Fri personal, Thu company rule for 14 days)
                and the last published posts with their numbers.
planned in content-plan.csv may be 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' (the time LinkedIn will publish).
Images are copied as web copies (max 1600 px) + final file into board/data/img/.
"""
import json, os, re
from datetime import datetime, timedelta, date
from PIL import Image, ImageOps
from common import CFG, BOARD_LOCAL, LIB, read_csv, jdump, log, resolve

PLAN, OUT, IMG = CFG["content_plan"], CFG["post_texts"], CFG["post_images"]
CAMP = CFG["campaign_repo"]
SLOT = {"linkedin": "07:30", "linkedin-company": "09:00"}
RULE = {0: "linkedin", 2: "linkedin", 4: "linkedin", 3: "linkedin-company"}      # weekday -> channel
STATUS = {"scheduled": "scheduled", "approved": "approved", "change": "change", "draft": "draft", "ready": "draft",
          "skipped": "skipped", "posted": "posted", "dropped": "dropped"}
PILLAR = {"foto-post": "", "grafik-post": "", "opinion": "decision", "case": "case"}

def chan(r): return "company" if r["channel"] == "linkedin-company" else "personal"

def when(r):
    p = (r.get("planned") or "").strip()
    if not p: return None
    if len(p) == 10: p += " " + SLOT.get(r["channel"], "07:30")
    try: return datetime.strptime(p[:16], "%Y-%m-%d %H:%M")
    except ValueError: return None

def card_id(r):
    return "-".join(os.path.basename(r["caption_ref"]).split("-")[0:3]) if r.get("caption_ref") else f"row-{r['id']}"

def text_of(r):
    path = resolve(r.get("caption_ref"))
    return open(path, encoding="utf-8").read().strip() if path and os.path.isfile(path) else ""

def meta_of(r):
    path = resolve(r.get("caption_ref")); mp = os.path.splitext(path)[0] + ".json" if path else ""
    try: return json.load(open(mp, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError): return {}

def board_note(notes):
    m = re.search(r"\[(?:board [^\]]*? change|redraft [^\]]*? applied|redraft failed [^\]]*?): (.*?)\]", notes or "")
    return m.group(1).strip() if m else ""

def hook(text, n=110):
    for ln in text.splitlines():
        if ln.strip(): return ln.strip()[:n] + ("…" if len(ln.strip()) > n else "")
    return ""

def find_image(asset):
    for m in re.findall(r"[\w./\-]+\.(?:jpg|jpeg|png)", asset or ""):
        for cand in (m, resolve(m), os.path.join(CAMP, m), os.path.join(IMG, os.path.basename(m))):
            if os.path.isfile(cand): return cand
    return None

def web_copy(src, dst_base):
    os.makedirs(os.path.join(BOARD_LOCAL, "img"), exist_ok=True)
    final = os.path.join(BOARD_LOCAL, "img", dst_base + "-final.jpg"); web = os.path.join(BOARD_LOCAL, "img", dst_base + ".jpg")
    if not (os.path.isfile(final) and os.path.isfile(web) and os.path.getmtime(final) >= os.path.getmtime(src)):
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im.save(final, "JPEG", quality=92); im.thumbnail((1600, 1600)); im.save(web, "JPEG", quality=85)
    im = Image.open(web); v = int(os.path.getmtime(final))
    return {"url": f"data/img/{os.path.basename(web)}?v={v}", "final": f"data/img/{os.path.basename(final)}?v={v}", "w": im.width, "h": im.height}

def prune_images(keep_ids):
    """Card images for posts that left the board are deleted 7 days after their slot (spec: storage rule);
    the push mirrors img/ with delete, so the server never holds more than the current cards + thumbnails."""
    d = os.path.join(BOARD_LOCAL, "img"); n = 0; total = 0
    for f in os.listdir(d) if os.path.isdir(d) else []:
        fp = os.path.join(d, f)
        if not os.path.isfile(fp): continue
        cid = re.sub(r"(-final)?\.jpg$", "", f)
        if cid not in keep_ids and (datetime.now().timestamp() - os.path.getmtime(fp)) > 7 * 86400: os.remove(fp); n += 1; continue
        total += os.path.getsize(fp)
    for f in os.listdir(os.path.join(d, "thumbs")) if os.path.isdir(os.path.join(d, "thumbs")) else []: total += os.path.getsize(os.path.join(d, "thumbs", f))
    if total > 200 * 1024 * 1024: log(f"WARNING board images {total // 1048576} MB on the server, above the 200 MB rule")
    return n, total

def main():
    rows, _ = read_csv(PLAN)
    today = date.today(); now = datetime.now()
    photos, _ = read_csv(os.path.join(LIB, "photos", "index.csv"))
    cards, upcoming = [], []
    for r in rows:
        if r["channel"] not in SLOT: continue
        w = when(r); st = STATUS.get(r["status"], r["status"])
        if not w or st in ("posted", "dropped", "skipped") or (w.date() < today and st != "approved"): continue   # an approved post stays until it is out
        text = text_of(r); cid = card_id(r)
        if not text: log("no text for", cid); continue
        meta = meta_of(r); pm = re.search(r"pillar=([\w-]+)", r.get("notes", ""))
        upcoming.append({"id": cid, "when": w.isoformat(timespec="minutes"), "channel": chan(r), "lang": r["language"], "status": st,
                         "hook": hook(text) or r["slot"], "on_board": True, "pillar": pm.group(1) if pm else PILLAR.get(r["format"], "")})
        img = find_image(r["asset"]); image = web_copy(img, cid) | {"id": os.path.basename(img)} if img else None
        cards.append({"id": cid, "channel": chan(r), "lang": r["language"], "slot": w.isoformat(timespec="minutes"),
                      "pillar": pm.group(1) if pm else PILLAR.get(r["format"], r["format"]), "text": text, "image": image, "status": st, "plan_row": r["id"],
                      "note": board_note(r.get("notes", "")), "updated": r.get("notes", "").startswith("[redraft ") and "applied" in r.get("notes", "")[:40],
                      "failed": r.get("notes", "").startswith("[redraft failed"), "versions": len(meta.get("versions", [])),
                      "photo_scene": meta.get("photo", "") and next((p.get("scene", "") for p in photos if p["id"] == meta.get("photo")), "")})
    upcoming.sort(key=lambda u: u["when"])   # only slots that have a draft; empty slots are filled by draft.py, never listed
    # published: posts-log rows that really went out (plan says posted, or the log note says so, or numbers exist)
    plog, _ = read_csv(CFG["posts_log"]); posted_ids = {card_id(r) for r in rows if r["status"] == "posted"}
    published = []
    for r in plog:
        note = (r.get("note") or "").upper()
        if r["post_id"] not in posted_ids and not note.startswith("POSTED") and not (r.get("impressions") or r.get("reactions")): continue
        if r["date"] > today.isoformat(): continue
        published.append({"id": r["post_id"], "date": r["date"], "channel": "company" if "company" in r["channel"] else "personal",
                          "hook": (r.get("hook") or "")[:110], "impressions": r.get("impressions", ""), "reactions": r.get("reactions", ""), "comments": r.get("comments", "")})
    published.sort(key=lambda p: p["date"], reverse=True)
    # Featured section candidates: the personal posts with the most impressions in the last 90 days (Anton pins them on his profile by hand)
    recent = [p for p in published if p["channel"] == "personal" and p["date"] >= (today - timedelta(days=90)).isoformat() and str(p["impressions"]).isdigit()]
    featured = sorted(recent, key=lambda p: int(p["impressions"]), reverse=True)[:3]
    missing = sum(1 for p in published if p["date"] >= (today - timedelta(days=90)).isoformat() and p["date"] <= (today - timedelta(days=3)).isoformat() and not str(p["impressions"]).isdigit())
    pruned, total = prune_images({c["id"] for c in cards})
    jdump(os.path.join(BOARD_LOCAL, "cards.json"), cards)
    inv, _ = read_csv(os.path.join(LIB, "inventory.csv")); material = {}
    for r in inv:
        if r.get("status") == "unused": material[r["pillar"]] = material.get(r["pillar"], 0) + 1
    memos, _ = read_csv(os.path.join(LIB, "memos", "index.csv"))
    jdump(os.path.join(BOARD_LOCAL, "pipeline.json"), {"upcoming": upcoming, "published": published[:12], "featured": featured, "metrics_missing": missing, "material": material,
          "memos": [{"id": m["id"], "recorded": m["recorded"], "words": m["words"], "status": m["status"], "used_in": m["used_in"]} for m in memos[-5:] if m["status"] in ("new", "drafted")],
          "generated": now.isoformat(timespec="seconds")})
    log(f"{len(cards)} cards: " + ", ".join(f"{c['id']}@{c['slot'][:16]}[{c['status']}]" for c in cards) + f"; {len(upcoming)} upcoming, {len(published)} published; images {total // 1024} KB, pruned {pruned}")

if __name__ == "__main__": main()
