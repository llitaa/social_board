#!/usr/bin/env python3
"""Build board/data/cards.json from content-plan.csv rows that are scheduled or draft.
Text comes from the row's caption_ref file; the image from the asset column (first existing path).
Images are copied as web copies (max 1600 px) + final file into board/data/img/.
"""
import os, re, shutil
from datetime import datetime
from PIL import Image, ImageOps
from common import CFG, BOARD_LOCAL, read_csv, jload, jdump, log

PLAN, OUT, IMG = CFG["content_plan"], CFG["post_texts"], CFG["post_images"]
CAMP = CFG["campaign_repo"]
SLOT = {"linkedin": "07:30", "linkedin-company": "09:00"}
PILLAR = {"foto-post": "personal", "grafik-post": "company", "opinion": "decision", "case": "case"}

def find_image(asset: str):
    for m in re.findall(r"[\w./\-]+\.(?:jpg|jpeg|png)", asset):
        for cand in (m, os.path.join(CAMP, m), os.path.join(IMG, os.path.basename(m))):
            if os.path.isfile(cand): return cand
    return None

def web_copy(src, dst_base):
    os.makedirs(os.path.join(BOARD_LOCAL, "img"), exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    final = os.path.join(BOARD_LOCAL, "img", dst_base + "-final.jpg")
    im.save(final, "JPEG", quality=92)
    im.thumbnail((1600, 1600)); web = os.path.join(BOARD_LOCAL, "img", dst_base + ".jpg")
    im.save(web, "JPEG", quality=85)
    return {"url": "data/img/" + os.path.basename(web), "final": "data/img/" + os.path.basename(final), "w": im.width, "h": im.height}

def main():
    rows, _ = read_csv(PLAN)
    existing = {c["id"]: c for c in jload(os.path.join(BOARD_LOCAL, "cards.json"), [])}
    cards = []
    for r in rows:
        if r["status"] not in ("scheduled", "draft", "ready"): continue
        if r["channel"] not in SLOT or not r.get("planned"): continue
        if r["planned"] < datetime.now().strftime("%Y-%m-%d"): continue   # past slots never become cards
        pid = os.path.basename(r["caption_ref"]).split("-anton-")[0].split("-")[0:3]
        cid = "-".join(os.path.basename(r["caption_ref"]).split("-")[0:3]) if r["caption_ref"] else f"row-{r['id']}"
        txt_path = os.path.join(CAMP, r["caption_ref"]) if r["caption_ref"] else None
        text = open(txt_path, encoding="utf-8").read().strip() if txt_path and os.path.isfile(txt_path) else ""
        if not text: log("no text for", cid); continue
        slot = f"{r['planned']}T{SLOT[r['channel']]}:00"
        img = find_image(r["asset"]); image = web_copy(img, cid) | {"id": os.path.basename(img)} if img else None
        card = {"id": cid, "channel": "company" if r["channel"] == "linkedin-company" else "personal", "lang": r["language"],
                "slot": slot, "pillar": PILLAR.get(r["format"], r["format"]), "options": {"A": text}, "image": image,
                "status": existing.get(cid, {}).get("status", "draft"), "plan_row": r["id"]}
        cards.append(card)
    jdump(os.path.join(BOARD_LOCAL, "cards.json"), cards)
    log(f"{len(cards)} cards:", ", ".join(f"{c['id']}@{c['slot'][:10]}" for c in cards))

if __name__ == "__main__": main()
