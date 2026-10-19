#!/usr/bin/env python3
"""Apply Anton's note to a card (spec approval-board: Post with note). A card with status change and a board note
gets a new text from the redraft model that honours the note; the old text is kept as a version; if the note asks for
another photo, the next eligible pool photo is taken. The result is approved: nothing to come back for."""
import json, os, re, shutil
from datetime import datetime
from common import CFG, LIB, read_csv, write_csv, resolve, log
from llm import llm_json
import photo_index as ph, rules_check
from draft import STYLE, render_graphic

PHOTO_WORDS = re.compile(r"foto|photo|bild|picture|image|anderes bild|other pic", re.I)
GRAPHIC_WORDS = re.compile(r"grafik|graphic|karte|card|visual", re.I)

def latest_note(notes):
    m = re.search(r"\[board [^\]]*? change: (.*?)\]", notes or "")
    return m.group(1).strip() if m else ""

def main():
    plan, fields = read_csv(CFG["content_plan"]); n = 0
    for r in plan:
        if r["status"] != "change" or not r["channel"].startswith("linkedin"): continue
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

Here is the current post and Anton's note on it. Apply the note exactly; change nothing he did not ask for.
Note: {note_for_text}

Current post:
{text}
{'The post also carries a 1200x1200 graphic with eyebrow/title/lines/footer; return a new "graphic" object only if the note concerns the graphic.' if channel == 'company' else ''}
Answer with one JSON object only: {{"text": "the full post incl. hashtags, newlines as \\n"{', "graphic": {...} (optional)' if channel == 'company' else ''}}}"""
            d = llm_json("redraft", prompt); new = d.get("text", "").strip(); v = rules_check.check(new, channel)
            if v: raise RuntimeError(f"rules: {v}")
            ver = len(meta.get("versions", [])) + 1; shutil.copy2(tp, f"{base}.v{ver}.txt")
            meta.setdefault("versions", []).append({"v": ver, "note": note, "ts": datetime.now().isoformat(timespec="seconds")})
            open(tp, "w", encoding="utf-8").write(new + "\n")
            if channel == "company" and d.get("graphic") and GRAPHIC_WORDS.search(note):
                meta["graphic"] = d["graphic"]; render_graphic(d["graphic"], os.path.basename(base))
            json.dump(meta, open(meta_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            r["status"] = "approved"; r["notes"] = f"[redraft {datetime.now():%Y-%m-%d %H:%M} applied: {note}] " + r.get("notes", ""); n += 1
            log("redrafted", r.get("caption_ref"), "->", "approved")
        except Exception as e:
            r["notes"] = f"[redraft failed {datetime.now():%Y-%m-%d %H:%M}: {str(e)[:120]}] " + r.get("notes", ""); log("redraft failed", r.get("caption_ref"), e)
    if n or True: write_csv(CFG["content_plan"], plan, fields)
    log(f"redrafts: {n}")

if __name__ == "__main__": main()
