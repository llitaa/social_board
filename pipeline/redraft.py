#!/usr/bin/env python3
"""Apply Anton's note to a card (spec approval-board: note loop). A card with status change and a board note
gets a new text from the redraft model that honours the note and his standing preferences (library/style-rules.txt);
the old text is kept as a version; if the note asks for another photo, the next eligible pool photo is taken.
The card then comes back to decide ("updated per your note"): Anton reads it, edits small things on the card, presses Post.
watch.py runs this within about a minute of the note, so he is usually still looking at the card."""
import json, os, re, shutil
from datetime import datetime
from common import CFG, LIB, read_csv, write_csv, resolve, log
from llm import llm_json
import photo_index as ph, rules_check, inventory as inv
from draft import STYLE, render_graphic, style_rules, positioning, book_phrases

PHOTO_WORDS = re.compile(r"foto|photo|bild|picture|image|anderes bild|other pic", re.I)
GRAPHIC_WORDS = re.compile(r"grafik|graphic|karte|card|visual", re.I)

def latest_note(notes):
    m = re.search(r"\[board [^\]]*? change: (.*?)\]", notes or "")
    return m.group(1).strip() if m else ""

def main():
    plan, fields = read_csv(CFG["content_plan"]); n = 0
    for r in plan:
        if r["status"] != "change" or not r["channel"].startswith("linkedin"): continue
        if r.get("notes", "").startswith("[redraft failed") and r["notes"].count("[redraft failed") >= 2: continue   # failed twice: waits for a new decision (board says so)
        note = latest_note(r.get("notes", "")); tp = resolve(r.get("caption_ref", ""))
        if not note or not os.path.isfile(tp): continue
        channel = "company" if r["channel"] == "linkedin-company" else "personal"
        text = open(tp, encoding="utf-8").read().strip(); base = os.path.splitext(tp)[0]
        meta_p = base + ".json"; meta = json.load(open(meta_p)) if os.path.isfile(meta_p) else {"versions": []}
        try:
            # 1. photo swap when asked
            if channel == "personal" and PHOTO_WORDS.search(note):
                cur = meta.get("photo", ""); ex = set(meta.get("photo_history", [])) | {cur}
                cands = ph.pick(datetime.strptime(r["planned"][:10], "%Y-%m-%d").date(), meta.get("neighbour_shoots", []), exclude_ids=ex)
                if cands:
                    p = cands[0]; meta["photo_history"] = sorted(ex); meta["photo"] = p["id"]
                    r["asset"] = f"{os.path.basename(p['file'])} (square: library/photos/square/{p['id']}_sq.png, {p['scene'][:60]})"
                    note_for_text = note + f"\n(The photo was changed; it now shows: {p['scene']})"
                else: note_for_text = note + "\n(No other photo is available; keep the text independent of the picture.)"
            else: note_for_text = note
            # 2. text
            prompt = f"""{STYLE[channel]}
{positioning() + book_phrases() if channel == 'personal' else ''}{style_rules()}
Here is the current post and Anton's note on it. Apply the note exactly; change nothing he did not ask for.
Note: {note_for_text}

Current post:
{text}
{('Facts you may use for anything new (nothing else):' + chr(10) + inv.cv_text()[:9000]) if channel == 'personal' else ''}
{'The post also carries a 1200x1200 graphic with eyebrow/title/lines/footer; return a new "graphic" object only if the note concerns the graphic.' if channel == 'company' else ''}
Answer with one JSON object only: {{"text": "the full post incl. hashtags, newlines as \\n"{', "graphic": {...} (optional)' if channel == 'company' else ', "card": {"kicker": "2-3 words", "headline": "the one sentence for under the photo, max 70 characters"}, "signals": {"lead": "sentence showing him leading or deciding, verbatim", "ai": "sentence showing his AI practice or position, verbatim"}'}}}"""
            d = llm_json("redraft", prompt); new = rules_check.fix_orthography(d.get("text", "").strip(), channel); v = rules_check.check(new, channel, d.get("signals"))
            if v: raise RuntimeError(f"rules: {v}")
            ver = len(meta.get("versions", [])) + 1; shutil.copy2(tp, f"{base}.v{ver}.txt")
            meta.setdefault("versions", []).append({"v": ver, "note": note, "ts": datetime.now().isoformat(timespec="seconds")})
            open(tp, "w", encoding="utf-8").write(new + "\n")
            if channel == "company" and d.get("graphic") and GRAPHIC_WORDS.search(note):
                meta["graphic"] = d["graphic"]; render_graphic(d["graphic"], os.path.basename(base))
            if channel == "personal":
                if d.get("card"): meta["card"] = d["card"]
                if d.get("signals"): meta["signals"] = d["signals"]
                if CFG.get("personal_card", {}).get("style", "off") != "off" and meta.get("card") and meta.get("photo"):
                    import personal_card
                    png = personal_card.render(os.path.join(LIB, "photos", "square", meta["photo"] + "_sq.png"), meta["card"], os.path.basename(base))
                    if png: r["asset"] = f"library/drafts/{os.path.basename(base)}.png (card: photo {meta['photo']} + headline, style {CFG['personal_card']['style']}; source library/drafts/{os.path.basename(base)}.html)"
            json.dump(meta, open(meta_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            r["status"] = "draft"; r["notes"] = f"[redraft {datetime.now():%Y-%m-%d %H:%M} applied: {note}] " + r.get("notes", ""); n += 1
            log("redrafted", r.get("caption_ref"), "-> back on the board to decide")
        except Exception as e:
            r["notes"] = f"[redraft failed {datetime.now():%Y-%m-%d %H:%M}: {str(e)[:120]}] " + r.get("notes", ""); log("redraft failed", r.get("caption_ref"), e)
    if n or True: write_csv(CFG["content_plan"], plan, fields)
    log(f"redrafts: {n}")

if __name__ == "__main__": main()
