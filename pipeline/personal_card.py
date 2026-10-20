#!/usr/bin/env python3
"""Personal post image = pool photo + headline block (what thought leaders do: every post recognisable in the feed).
Styles live in templates/personal-card.html: band (square, dark blue block under the photo), light (4:5, white block
with the cyan bar of the documents), overlay (square, headline on the photo). config.yaml personal_card.style picks one;
off = plain photo as before. Palette = AlpiType colours only, no logo, no company name (personal posts never name it).
Rendered with headless Chrome, zero tokens. `python3 personal_card.py <square.png> "<headline>" [kicker] [style] [out_base]`."""
import html, os, subprocess, sys
from common import CFG, LIB, ROOT, log

TPL = os.path.join(ROOT, "pipeline", "templates", "personal-card.html")
DRAFTS = os.path.join(LIB, "drafts")
NAME, ROLE = "Anton Lytvynenko", "Software Architect & Technical Lead"
SIZES = {"band": (1200, 1200, 760), "light": (1080, 1350, 1000), "overlay": (1200, 1200, 1200)}   # width, height, photo height

def headline_size(h, style):
    n = len(h); base = {"band": 64, "light": 56, "overlay": 68}[style]
    return base if n <= 45 else base - 8 if n <= 60 else base - 14

def render(photo_png, card, out_base, style=None, out_dir=DRAFTS):
    """card = {"kicker": ..., "headline": ...}; returns the PNG path or None."""
    style = style or CFG.get("personal_card", {}).get("style", "band")
    if style not in SIZES or not os.path.isfile(photo_png): return None
    w, h, ph = SIZES[style]; head = (card.get("headline") or "").strip(); kick = (card.get("kicker") or "").strip()
    photo = "file://" + os.path.abspath(photo_png)      # by path, not embedded: the .html stays small (media never in git)
    extra = {"band": '<div class="seam"></div>', "light": "", "overlay": '<div class="shade"></div>'}[style]
    doc = (open(TPL, encoding="utf-8").read().replace("{{W}}", str(w)).replace("{{H}}", str(h)).replace("{{PH}}", str(ph)).replace("{{HS}}", str(headline_size(head, style)))
           .replace("{{STYLE}}", style).replace("{{PHOTO}}", photo).replace("{{EXTRA}}", extra).replace("{{BAR}}", '<div class="bar"></div>' if style == "light" else "")
           .replace("{{KICKER}}", html.escape(kick)).replace("{{HEADLINE}}", html.escape(head)).replace("{{NAME}}", NAME).replace("{{ROLE}}", ROLE)
           .replace('<div class="overlay-rule"></div>', ""))
    if style == "overlay": doc = doc.replace('<h1>', '<div class="rule"></div><h1>', 1)
    os.makedirs(out_dir, exist_ok=True)
    hp, png = os.path.join(out_dir, out_base + ".html"), os.path.join(out_dir, out_base + ".png")
    open(hp, "w", encoding="utf-8").write(doc)
    subprocess.run([CFG["chrome"], "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}", f"--screenshot={png}", "file://" + hp], capture_output=True, timeout=60)
    if os.path.isfile(png): log(f"card {out_base}.png ({style}, {w}x{h})"); return png
    return None

if __name__ == "__main__":
    a = sys.argv[1:]
    print(render(a[0], {"headline": a[1], "kicker": a[2] if len(a) > 2 else ""}, a[4] if len(a) > 4 else "card-preview", a[3] if len(a) > 3 else None))
