#!/usr/bin/env python3
"""Personal post image = pool photo + headline block (what thought leaders do: every post recognisable in the feed).
Styles live in templates/personal-card.html: bottom (square, full photo, headline alone at the foot over a soft fade,
Anton's choice 20.10.), band (dark blue block under the photo), light (4:5, white block with the cyan bar), overlay. config.yaml personal_card.style picks one;
off = plain photo as before. Palette = AlpiType colours only, no logo, no company name (personal posts never name it).
Fonts = the website's: Montserrat for the headline, Open Sans for kicker and bottom line (Google Fonts, loaded by Chrome at
render time). The headline never ends in a full stop. The bottom line is config personal_card.who: name | role | none.
Rendered with headless Chrome, zero tokens. `python3 personal_card.py <square.png> "<headline>" [kicker] [style] [out_base] [who]`."""
import html, os, subprocess, sys
from common import CFG, LIB, ROOT, log

TPL = os.path.join(ROOT, "pipeline", "templates", "personal-card.html")
DRAFTS = os.path.join(LIB, "drafts")
NAME, ROLE = "Anton Lytvynenko", "Software Architect & Technical Lead"
SIZES = {"band": (1200, 1200, 760), "light": (1080, 1350, 1000), "overlay": (1200, 1200, 1200), "bottom": (1200, 1200, 1200)}   # width, height, photo height

def headline_size(h, style):
    n = len(h); base = {"band": 60, "light": 54, "overlay": 64, "bottom": 58}[style]
    return base if n <= 45 else base - 8 if n <= 60 else base - 14 if n <= 78 else base - 20

def render(photo_png, card, out_base, style=None, out_dir=DRAFTS, who=None, rule=None):
    """card = {"kicker": ..., "headline": ...}; returns the PNG path or None."""
    style = style or CFG.get("personal_card", {}).get("style", "band"); who = who or CFG.get("personal_card", {}).get("who", "name")
    if style not in SIZES or not os.path.isfile(photo_png): return None
    w, h, ph = SIZES[style]; head = (card.get("headline") or "").strip().rstrip(".").strip(); kick = (card.get("kicker") or "").strip()
    photo = "file://" + os.path.abspath(photo_png)      # by path, not embedded: the .html stays small (media never in git)
    extra = {"band": '<div class="seam"></div>', "light": "", "overlay": '<div class="shade"></div>', "bottom": '<div class="shade"></div>'}[style]
    rule = CFG.get("personal_card", {}).get("rule", True) if rule is None else rule
    doc = (open(TPL, encoding="utf-8").read().replace("{{W}}", str(w)).replace("{{H}}", str(h)).replace("{{PH}}", str(ph)).replace("{{HS}}", str(headline_size(head, style)))
           .replace("{{STYLE}}", style + ("" if rule else " norule")).replace("{{PHOTO}}", photo).replace("{{EXTRA}}", extra).replace("{{BAR}}", '<div class="bar"></div>' if style == "light" else "")
           .replace("{{KICKER}}", html.escape(kick)).replace("{{HEADLINE}}", html.escape(head)).replace("{{NAME}}", NAME).replace("{{ROLE}}", ROLE).replace("{{WHO}}", who)
           .replace('<div class="overlay-rule"></div>', ""))
    if style in ("overlay", "bottom"): doc = doc.replace('<h1>', '<div class="rule"></div><h1>', 1)
    os.makedirs(out_dir, exist_ok=True)
    hp, png = os.path.join(out_dir, out_base + ".html"), os.path.join(out_dir, out_base + ".png")
    open(hp, "w", encoding="utf-8").write(doc)
    subprocess.run([CFG["chrome"], "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}", "--virtual-time-budget=8000", f"--screenshot={png}", "file://" + hp], capture_output=True, timeout=60)
    if os.path.isfile(png): log(f"card {out_base}.png ({style}, {w}x{h})"); return png
    return None

if __name__ == "__main__":
    a = sys.argv[1:]
    print(render(a[0], {"headline": a[1], "kicker": a[2] if len(a) > 2 else ""}, a[4] if len(a) > 4 else "card-preview", a[3] if len(a) > 3 else None, who=a[5] if len(a) > 5 else None, rule=(a[6] != "norule") if len(a) > 6 else None))
