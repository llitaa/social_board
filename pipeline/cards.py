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
import os, re
from datetime import datetime, timedelta, date
from PIL import Image, ImageOps
from common import CFG, BOARD_LOCAL, read_csv, jdump, log

PLAN, OUT, IMG = CFG["content_plan"], CFG["post_texts"], CFG["post_images"]
CAMP = CFG["campaign_repo"]
SLOT = {"linkedin": "07:30", "linkedin-company": "09:00"}
RULE = {0: "linkedin", 2: "linkedin", 4: "linkedin", 3: "linkedin-company"}      # weekday -> channel
STATUS = {"scheduled": "scheduled", "approved": "approved", "change": "change", "draft": "draft", "ready": "draft",
          "skipped": "skipped", "posted": "posted", "dropped": "dropped"}
PILLAR = {"foto-post": "personal", "grafik-post": "company", "opinion": "decision", "case": "case"}

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
    if not r.get("caption_ref"): return ""
    path = os.path.join(CAMP, r["caption_ref"])
    return open(path, encoding="utf-8").read().strip() if os.path.isfile(path) else ""

def hook(text, n=110):
    for ln in text.splitlines():
        if ln.strip(): return ln.strip()[:n] + ("…" if len(ln.strip()) > n else "")
    return ""

def find_image(asset):
    for m in re.findall(r"[\w./\-]+\.(?:jpg|jpeg|png)", asset or ""):
        for cand in (m, os.path.join(CAMP, m), os.path.join(IMG, os.path.basename(m))):
            if os.path.isfile(cand): return cand
    return None

def web_copy(src, dst_base):
    os.makedirs(os.path.join(BOARD_LOCAL, "img"), exist_ok=True)
    final = os.path.join(BOARD_LOCAL, "img", dst_base + "-final.jpg"); web = os.path.join(BOARD_LOCAL, "img", dst_base + ".jpg")
    if not (os.path.isfile(final) and os.path.isfile(web) and os.path.getmtime(final) >= os.path.getmtime(src)):
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im.save(final, "JPEG", quality=92); im.thumbnail((1600, 1600)); im.save(web, "JPEG", quality=85)
    im = Image.open(web)
    return {"url": "data/img/" + os.path.basename(web), "final": "data/img/" + os.path.basename(final), "w": im.width, "h": im.height}

def main():
    rows, _ = read_csv(PLAN)
    today = date.today(); now = datetime.now()
    cards, upcoming = [], []
    for r in rows:
        if r["channel"] not in SLOT: continue
        w = when(r); st = STATUS.get(r["status"], r["status"])
        if not w or st in ("posted", "dropped", "skipped") or w.date() < today: continue
        text = text_of(r); cid = card_id(r)
        upcoming.append({"id": cid, "when": w.isoformat(timespec="minutes"), "channel": chan(r), "lang": r["language"], "status": st,
                         "hook": hook(text) or r["slot"], "on_board": bool(text)})
        if not text: log("no text for", cid); continue
        img = find_image(r["asset"]); image = web_copy(img, cid) | {"id": os.path.basename(img)} if img else None
        cards.append({"id": cid, "channel": chan(r), "lang": r["language"], "slot": w.isoformat(timespec="minutes"),
                      "pillar": PILLAR.get(r["format"], r["format"]), "options": {"A": text}, "image": image, "status": st, "plan_row": r["id"],
                      "note": re.sub(r"^\[board [^\]]*\]\s*", "", r.get("notes", ""))[:0]})
    taken = {(u["when"][:10], u["channel"]) for u in upcoming}
    d = today
    while d <= today + timedelta(days=14):
        ch = RULE.get(d.weekday())
        if ch:
            slot_dt = datetime.strptime(f"{d} {SLOT[ch]}", "%Y-%m-%d %H:%M"); c = "company" if ch == "linkedin-company" else "personal"
            if (d.isoformat(), c) not in taken and slot_dt > now:
                upcoming.append({"id": "", "when": slot_dt.isoformat(timespec="minutes"), "channel": c, "lang": "en" if c == "company" else "de",
                                 "status": "open", "hook": "", "on_board": False})
        d += timedelta(days=1)
    upcoming.sort(key=lambda u: u["when"])
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
    jdump(os.path.join(BOARD_LOCAL, "cards.json"), cards)
    jdump(os.path.join(BOARD_LOCAL, "pipeline.json"), {"upcoming": upcoming, "published": published[:12], "generated": now.isoformat(timespec="seconds")})
    log(f"{len(cards)} cards: " + ", ".join(f"{c['id']}@{c['slot'][:16]}[{c['status']}]" for c in cards) + f"; {len(upcoming)} upcoming, {len(published)} published")

if __name__ == "__main__": main()
