#!/usr/bin/env python3
"""Diagram posts (Anton, 30.10.): the picture carries the point, the text is a caption. Four reusable kinds, each a 1200x1200
inline-SVG page in the house style (stripe left, name top right, short title, one big drawing), rendered with headless Chrome:
  curves       two lines over time and the gap between them (e.g. generation vs verification)
  shift        two stacked bars, before and after (e.g. where the week goes, 2014 vs 2026)
  beforeafter  two small panels with a line each (e.g. invoice vs production, licence vs usage pricing)
  flow         boxes with arrows, an optional gate and a dead end (e.g. PoC -> pilot -> gate -> operations, graveyard)
Usage: render(spec, out_base, out_dir) -> png path. spec = {"kind": ..., "eyebrow": ..., "title": ..., "note": ..., ...kind fields}.
python3 pipeline/graphics.py spec.json out_base [out_dir]"""
import html, json, os, subprocess, sys
from common import CFG, LIB

DRAFTS = os.path.join(LIB, "drafts")
INK, CYAN, MUTED, SOFT = "#1f4a63", "#20B8D0", "#6b7f8c", "#eaf7fa"
GRAD = "linear-gradient(180deg,#42F45D 0%,#01BC56 30%,#00BEE6 65%,#08E3FB 100%)"

def esc(s): return html.escape(str(s or ""))

def frame(spec, body):
    title = esc(spec.get("title", "")).replace("\\n", "<br>"); light = spec.get("light", True)
    who = "" if light else '<div class="who"><b>Anton Lytvynenko</b>Software Architect · Technical Lead</div>'
    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><title>graphic</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Open+Sans:wght@400;600&display=block" rel="stylesheet">
<style>*{{box-sizing:border-box;margin:0}}html,body{{background:#fff}}
body{{font-family:"Montserrat","Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased;color:{INK}}}
.canvas{{width:1200px;height:1200px;position:relative;overflow:hidden;background:#fff}}
.stripe{{position:absolute;left:0;top:0;width:{12 if light else 24}px;height:100%;background:{GRAD}}}
.who{{position:absolute;right:72px;top:64px;text-align:right;font-family:"Open Sans",sans-serif;font-size:22px;color:{MUTED}}}
.who b{{display:block;font-weight:600;color:{INK};font-size:25px}}
.eyebrow{{position:absolute;left:96px;top:72px;font-family:"Open Sans",sans-serif;font-size:22px;letter-spacing:.22em;text-transform:uppercase;color:{CYAN};font-weight:600}}
h1{{position:absolute;left:96px;top:{118 if light else 124}px;width:900px;font-size:{50 if light else 58}px;line-height:1.12;font-weight:{700 if light else 800};letter-spacing:-1px}}
svg{{position:absolute;left:0;top:0}}
.note{{position:absolute;left:96px;bottom:60px;right:72px;font-family:"Open Sans",sans-serif;font-size:22px;color:{MUTED};line-height:1.35}}
svg text{{font-family:"Montserrat","Helvetica Neue",Arial,sans-serif;font-weight:600;fill:{INK}}}
svg .m{{fill:{MUTED};font-family:"Open Sans",sans-serif;font-weight:400}}
svg .c{{fill:{CYAN}}} svg .w{{fill:#fff}}
</style></head><body><div class="canvas"><div class="stripe"></div>
{who}
<div class="eyebrow">{esc(spec.get("eyebrow", ""))}</div><h1>{title}</h1>
{body}
<div class="note">{esc(spec.get("note", ""))}</div></div></body></html>"""

def curves(s):
    """s.a / s.b: {label, points:[y0..yn in 0..1]}; s.gap: label of the shaded area; s.x: [first, last] axis labels."""
    x0, x1, y0, y1 = 150, 1110, 1000, 430
    def pts(p): n = len(p) - 1; return [(x0 + (x1 - x0) * i / n, y0 - (y0 - y1) * v) for i, v in enumerate(p)]
    A, B = pts(s["a"]["points"]), pts(s["b"]["points"])
    path = lambda P: "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in P)
    area = path(A) + " L" + " L".join(f"{x:.0f},{y:.0f}" for x, y in reversed(B)) + " Z"
    xl = s.get("x", ["", ""])
    return f"""<svg width="1200" height="1200" viewBox="0 0 1200 1200">
{f'<path d="{area}" fill="{SOFT}"/>' if s.get("area", True) else ""}
<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{MUTED}" stroke-width="3"/><line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1 - 30}" stroke="{MUTED}" stroke-width="3"/>
<path d="{path(B)}" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{path(A)}" fill="none" stroke="{CYAN}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="{x0 - 50}" y="{y1 - 120}" width="46" height="12" rx="6" fill="{CYAN}"/><text x="{x0 + 12}" y="{y1 - 108}" font-size="28" class="m">{esc(s["a"]["label"])}</text>
<rect x="{x0 + 420}" y="{y1 - 120}" width="46" height="12" rx="6" fill="{INK}"/><text x="{x0 + 482}" y="{y1 - 108}" font-size="28" class="m">{esc(s["b"]["label"])}</text>
<text x="{(x0 + x1) / 2 + 120:.0f}" y="{(A[-2][1] + B[-2][1]) / 2 + 12:.0f}" font-size="40" text-anchor="middle" font-weight="800" style="paint-order:stroke;stroke:#fff;stroke-width:12px;stroke-linejoin:round">{esc(s.get("gap", ""))}</text>
<text x="{x0}" y="{y0 + 48}" font-size="26" class="m">{esc(xl[0])}</text><text x="{x1}" y="{y0 + 48}" font-size="26" text-anchor="end" class="m">{esc(xl[1])}</text>
<text x="{x0 - 20}" y="{y1 - 30}" font-size="26" class="m">{esc(s.get("y", ""))}</text>{"".join(f'<circle cx="{A[m["at"]][0]:.0f}" cy="{A[m["at"]][1]:.0f}" r="16" fill="{CYAN}" stroke="#fff" stroke-width="5"/><text x="{A[m["at"]][0]:.0f}" y="{A[m["at"]][1] + (64 if (m.get("below", True) and A[m["at"]][1] < y0 - 110) else -34):.0f}" font-size="30" text-anchor="middle" font-weight="800" style="paint-order:stroke;stroke:#fff;stroke-width:10px;stroke-linejoin:round">{esc(m["label"])}</text>' for m in s.get("marks", []))}</svg>"""

def shift(s):
    """s.bars: [{label, values:[...]}, {label, values:[...]}] (same length, sum ~100); s.segments: [labels]; dark to light from the bottom."""
    seg = s["segments"]; cols = [INK, "#2d6a8a", CYAN, "#9fdde8", "#d7eef3"][:len(seg)]
    out = []; xs = [470, 860]; bw = 240; top, bottom = 380, 1000
    for (bar, x) in zip(s["bars"], xs):
        y = bottom; tot = sum(bar["values"]) or 1
        for v, c, lab in zip(bar["values"], cols, seg):
            h = (bottom - top) * v / tot; y -= h
            out.append(f'<rect x="{x}" y="{y:.0f}" width="{bw}" height="{h:.0f}" fill="{c}"/>')
            if h > 44: out.append(f'<text x="{x + bw / 2}" y="{y + h / 2 + 12:.0f}" font-size="30" text-anchor="middle" class="{"w" if c in (INK, "#2d6a8a", CYAN) else ""}">{v:.0f}%</text>')
        out.append(f'<text x="{x + bw / 2}" y="{bottom + 54}" font-size="34" text-anchor="middle" font-weight="800">{esc(bar["label"])}</text>')
    ly = top + 10
    for c, lab in zip(cols, seg):   # legend on the left; a label wraps at "\n"
        parts = str(lab).split("\\n")
        out.append(f'<rect x="96" y="{ly}" width="34" height="34" rx="8" fill="{c}"/>' + "".join(f'<text x="144" y="{ly + 26 + 30 * j}" font-size="24" class="m">{esc(t)}</text>' for j, t in enumerate(parts))); ly += 44 + 30 * len(parts)
    out.append(f'<path d="M{xs[0] + bw + 30},{(top + bottom) / 2} L{xs[1] - 30},{(top + bottom) / 2}" stroke="{MUTED}" stroke-width="6" marker-end="url(#ar)"/>')
    return f'<svg width="1200" height="1200" viewBox="0 0 1200 1200"><defs><marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>' + "".join(out) + "</svg>"

def beforeafter(s):
    """s.panels: [{label, lines:[{label, points, color:'ink'|'cyan'}]}] x2; a small line chart each, no axes numbers."""
    out = []; px = [96, 640]; pw = 470; top, bottom = 420, 900
    for p, x in zip(s["panels"], px):
        out.append(f'<rect x="{x}" y="{top - 70}" width="{pw}" height="{bottom - top + 130}" rx="18" fill="{SOFT}"/>')
        out.append(f'<text x="{x + 30}" y="{top - 20}" font-size="32" font-weight="800">{esc(p["label"])}</text>')
        out.append(f'<line x1="{x + 30}" y1="{bottom}" x2="{x + pw - 30}" y2="{bottom}" stroke="{MUTED}" stroke-width="3"/>')
        for ln in p["lines"]:
            P = ln["points"]; n = len(P) - 1
            d = "M" + " L".join(f"{x + 30 + (pw - 60) * i / n:.0f},{bottom - (bottom - top) * v:.0f}" for i, v in enumerate(P))
            col = CYAN if ln.get("color") == "cyan" else INK
            out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"{" stroke-dasharray=\"2 22\"" if ln.get("dotted") else ""}/>')
        pass
    seen = []
    for ln in s["panels"][0]["lines"]:   # one legend for both panels, under the title
        col = CYAN if ln.get("color") == "cyan" else INK; lx = 96 + 260 * len(seen)
        out.append(f'<rect x="{lx}" y="{top - 130}" width="46" height="10" rx="5" fill="{col}"/><text x="{lx + 60}" y="{top - 118}" font-size="26" class="m">{esc(ln["label"])}</text>'); seen.append(ln)
    out.append(f'<path d="M{px[0] + pw + 14},{(top + bottom) / 2} L{px[1] - 14},{(top + bottom) / 2}" stroke="{MUTED}" stroke-width="6" marker-end="url(#ar)"/>')
    return f'<svg width="1200" height="1200" viewBox="0 0 1200 1200"><defs><marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>' + "".join(out) + "</svg>"

def flow(s):
    """s.steps: [{label, sub, kind:'box'|'gate'|'end'}] left to right on one row (max 5); s.dead: {from: index, label, sub} drawn below as the dead end."""
    st = s["steps"]; n = len(st); out = []; y = 480; w = 190; gap = (1030 - 96 - n * w) / (n - 1); h = 150
    xs = [96 + i * (w + gap) for i in range(n)]
    for i, (x, step) in enumerate(zip(xs, st)):
        k = step.get("kind", "box")
        if k == "gate": out.append(f'<path d="M{x + w / 2},{y - 40} L{x + w + 50},{y + h / 2} L{x + w / 2},{y + h + 40} L{x - 50},{y + h / 2} Z" fill="{CYAN}"/>')
        else: out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{INK if k == "box" else "#1a9c4a"}"/>')
        parts = str(step["label"]).split("\\n"); fs = 30 if max(len(t) for t in parts) < 12 else 24; y0 = y + h / 2 + (0 if step.get("sub") else 12) - (len(parts) - 1) * fs * 0.6
        out.append("".join(f'<text x="{x + w / 2}" y="{y0 + j * fs * 1.2:.0f}" font-size="{fs}" text-anchor="middle" class="w">{esc(t)}</text>' for j, t in enumerate(parts)))
        if step.get("sub"): out.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 40}" font-size="20" text-anchor="middle" class="w" style="font-family:Open Sans;font-weight:400">{esc(step["sub"])}</text>')
        if i < n - 1: out.append(f'<line x1="{x + w + (52 if k == "gate" else 4)}" y1="{y + h / 2}" x2="{xs[i + 1] - (56 if st[i + 1].get("kind") == "gate" else 8)}" y2="{y + h / 2}" stroke="{MUTED}" stroke-width="6" marker-end="url(#ar)"/>')
    d = s.get("dead")
    if d:
        x = xs[d["from"]] + w / 2; dy = y + h + 150
        out.append(f'<path d="M{x},{y + h + 44} L{x},{dy - 10}" stroke="{MUTED}" stroke-width="6" stroke-dasharray="14 12" marker-end="url(#ar)"/>')
        out.append(f'<rect x="{x - 220}" y="{dy}" width="440" height="130" rx="22" fill="none" stroke="{MUTED}" stroke-width="5" stroke-dasharray="14 12"/>')
        out.append(f'<text x="{x}" y="{dy + 58}" font-size="30" text-anchor="middle">{esc(d["label"])}</text><text x="{x}" y="{dy + 98}" font-size="22" text-anchor="middle" class="m">{esc(d.get("sub", ""))}</text>')
    return f'<svg width="1200" height="1200" viewBox="0 0 1200 1200"><defs><marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>' + "".join(out) + "</svg>"

def matrix(s):
    """2x2: s.x = [left label, right label], s.y = [bottom label, top label]; s.quads = {tl, tr, bl, br: {label, sub}}; s.hot = the quadrant key drawn in cyan."""
    out = []; x0, y0, size = 210, 320, 335; names = {"tl": (0, 0), "tr": (1, 0), "bl": (0, 1), "br": (1, 1)}
    for k, (cx, cy) in names.items():
        q = s["quads"].get(k, {}); x = x0 + cx * size; y = y0 + cy * size; hot = k == s.get("hot"); dead = k == s.get("dead")
        fill = CYAN if hot else ("#f3f5f6" if dead else SOFT); col = "w" if hot else ""
        out.append(f'<rect x="{x + 6}" y="{y + 6}" width="{size - 12}" height="{size - 12}" rx="24" fill="{fill}"/>')
        parts = str(q.get("label", "")).split("\\n"); fs = 36 if max(len(t) for t in parts) < 14 else 29
        out.append("".join(f'<text x="{x + size / 2}" y="{y + size / 2 - 10 + (j - (len(parts) - 1) / 2) * fs * 1.2:.0f}" font-size="{fs}" text-anchor="middle" font-weight="800" class="{col}">{esc(t)}</text>' for j, t in enumerate(parts)))
        if q.get("sub"): out.append(f'<text x="{x + size / 2}" y="{y + size / 2 + 50 + (len(parts) - 1) * fs * 0.6:.0f}" font-size="21" text-anchor="middle" class="{"w" if hot else "m"}" style="font-family:Open Sans;font-weight:400">{esc(q["sub"])}</text>')
    xl, yl = s.get("x", ["", ""]), s.get("y", ["", ""])
    out.append(f'<text x="{x0 + size / 2}" y="{y0 + 2 * size + 50}" font-size="26" text-anchor="middle" class="m">{esc(xl[0])}</text><text x="{x0 + size * 1.5}" y="{y0 + 2 * size + 50}" font-size="26" text-anchor="middle" class="m">{esc(xl[1])}</text>')
    out.append(f'<text transform="translate({x0 - 44},{y0 + size * 1.5}) rotate(-90)" font-size="26" text-anchor="middle" class="m">{esc(yl[0])}</text><text transform="translate({x0 - 44},{y0 + size / 2}) rotate(-90)" font-size="26" text-anchor="middle" class="m">{esc(yl[1])}</text>')
    return '<svg width="1200" height="1200" viewBox="0 0 1200 1200">' + "".join(out) + "</svg>"

def phases(s):
    """Two rows of phase blocks, block width = share of effort. s.phases: [labels]; s.rows: [{label, values}] x2; s.hot: index of the phase to colour."""
    out = []; x0, w = 96, 1010; ys = [440, 760]; h = 150; hot = s.get("hot", -1)
    for row, y in zip(s["rows"], ys):
        tot = sum(row["values"]) or 1; x = x0; under_prev = False
        out.append(f'<text x="{x0}" y="{y - 22}" font-size="26" class="m">{esc(row["label"])}</text>')
        for i, (v, lab) in enumerate(zip(row["values"], s["phases"])):
            bw = w * v / tot
            out.append(f'<rect x="{x + 3}" y="{y}" width="{max(bw - 6, 4):.0f}" height="{h}" rx="14" fill="{CYAN if i == hot else SOFT}" stroke="{CYAN if i == hot else "#cfe3ea"}" stroke-width="2"/>')
            fits = bw > 34 + 15 * len(lab)   # label inside when it fits, otherwise under the block
            if fits: out.append(f'<text x="{x + bw / 2:.0f}" y="{y + h / 2 + 10}" font-size="26" text-anchor="middle" class="{"w" if i == hot else ""}">{esc(lab)}</text>')
            else: out.append(f'<text x="{x + bw / 2:.0f}" y="{y + h + (62 if under_prev else 34)}" font-size="20" text-anchor="middle" class="m">{esc(lab)}</text>')   # two narrow neighbours: second label one line lower
            under_prev = not fits and not under_prev; x += bw
    out.append(f'<path d="M{x0 + w / 2},{ys[0] + h + 60} L{x0 + w / 2},{ys[1] - 56}" stroke="{MUTED}" stroke-width="4" marker-end="url(#ar)"/>')
    return f'<svg width="1200" height="1200" viewBox="0 0 1200 1200"><defs><marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>' + "".join(out) + "</svg>"

KINDS = {"phases": phases, "curves": curves, "shift": shift, "beforeafter": beforeafter, "flow": flow, "matrix": matrix}

def render(spec, out_base, out_dir=None):
    out_dir = out_dir or DRAFTS; os.makedirs(out_dir, exist_ok=True)
    doc = frame(spec, KINDS[spec["kind"]](spec))
    hp = os.path.abspath(os.path.join(out_dir, out_base + ".html")); png = os.path.abspath(os.path.join(out_dir, out_base + ".png"))
    open(hp, "w", encoding="utf-8").write(doc)
    subprocess.run([CFG["chrome"], "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,1200", "--virtual-time-budget=5000", f"--screenshot={png}", "file://" + hp], capture_output=True, timeout=60)
    return png if os.path.isfile(png) else None

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8")); print(render(spec, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
