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
INK, CYAN, MUTED, SOFT = "#0f3a50", "#20B8D0", "#6b7f8c", "#e9fbfe"   # AlpiType: dark blue, cyan, tint; grey only for axes and captions
GREEN, BLUE, SKY, TINT = "#01BC56", "#00BEE6", "#08E3FB", "#BEF7FF"
GRAD = "linear-gradient(180deg,#42F45D 0%,#01BC56 30%,#00BEE6 65%,#08E3FB 100%)"

def esc(s): return html.escape(str(s or ""))

def frame(spec, body):
    title = esc(spec.get("title", "")).replace("\\n", "<br>"); light = spec.get("light", True)
    who = "" if light else '<div class="who"><b>Anton Lytvynenko</b>Software Architect, Technical Lead</div>'
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
    x0, x1, y0, y1 = 150, 1110, 1040, 440; ix0, ix1, iy0 = x0 + 40, x1 - 40, y0 - 30   # lines keep 40 px from the axes and the edge
    def pts(p): n = len(p) - 1; return [(ix0 + (ix1 - ix0) * i / n, iy0 - (iy0 - y1) * v) for i, v in enumerate(p)]
    A, B = pts(s["a"]["points"]), pts(s["b"]["points"]); gi = len(A) - 3   # the bracket near the end, where the gap is wide; the label stands to its right, between the lines
    path = smooth
    area = path(A) + " L" + " L".join(f"{x:.0f},{y:.0f}" for x, y in reversed(B)) + " Z"
    xl = s.get("x", ["", ""])
    return f"""<svg width="1200" height="1200" viewBox="0 0 1200 1200">
{f'<path d="{area}" fill="{SOFT}"/>' if s.get("area", False) else ""}
<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{MUTED}" stroke-width="3"/><line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1 - 30}" stroke="{MUTED}" stroke-width="3"/>
<path d="{path(B)}" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{path(A)}" fill="none" stroke="{CYAN}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
{legend([(CYAN, s["a"]["label"]), (INK, s["b"]["label"])], 96, y1 - 110)}
{f'<line x1="{A[gi][0]:.0f}" y1="{A[gi][1] + 14:.0f}" x2="{A[gi][0]:.0f}" y2="{B[gi][1] - 14:.0f}" stroke="{INK}" stroke-width="3"/><line x1="{A[gi][0] - 12:.0f}" y1="{A[gi][1] + 14:.0f}" x2="{A[gi][0] + 12:.0f}" y2="{A[gi][1] + 14:.0f}" stroke="{INK}" stroke-width="3"/><line x1="{A[gi][0] - 12:.0f}" y1="{B[gi][1] - 14:.0f}" x2="{A[gi][0] + 12:.0f}" y2="{B[gi][1] - 14:.0f}" stroke="{INK}" stroke-width="3"/><text x="{A[gi][0] + 28:.0f}" y="{(A[gi][1] + B[gi][1]) / 2 + 12:.0f}" font-size="30" text-anchor="start" font-weight="700">{esc(s["gap"])}</text>' if s.get("gap") else ""}
<text x="{x0}" y="{y0 + 48}" font-size="26" class="m">{esc(xl[0])}</text><text x="{x1}" y="{y0 + 48}" font-size="26" text-anchor="end" class="m">{esc(xl[1])}</text>
<text x="{x0 + 28}" y="{y1 - 34}" font-size="26" class="m">{esc(s.get("y", ""))}</text>{"".join(mark(A[m["at"]], m, y0) for m in s.get("marks", []))}</svg>"""

def smooth(P):
    """Catmull-Rom through the points as cubic beziers: a drawn curve, not a polyline."""
    if len(P) < 3: return "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in P)
    d = f"M{P[0][0]:.0f},{P[0][1]:.0f}"
    for i in range(len(P) - 1):
        p0 = P[i - 1] if i > 0 else P[i]; p1 = P[i]; p2 = P[i + 1]; p3 = P[i + 2] if i + 2 < len(P) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6); c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.0f},{c1[1]:.0f} {c2[0]:.0f},{c2[1]:.0f} {p2[0]:.0f},{p2[1]:.0f}"
    return d

def legend(items, x, y):
    """Swatches and labels on one row; the gap after a label is measured from its length, not a fixed column."""
    out = []
    for col, lab in items:
        out.append(f'<rect x="{x}" y="{y}" width="46" height="12" rx="6" fill="{col}"/><text x="{x + 62}" y="{y + 12}" font-size="28" class="m">{esc(lab)}</text>'); x += 62 + int(len(lab) * 15.5) + 60
    return "".join(out)

def mark(p, m, y0):
    """A point on line a with its label; pos = above | below | left | right (render() tries them in that order until the checker is clean)."""
    pos = m.get("pos") or ("above" if p[1] > y0 - 140 else "below")
    x, y, anchor = {"above": (p[0], p[1] - 84, "middle"), "below": (p[0], p[1] + 106, "middle"), "left": (p[0] - 70, p[1] + 12, "end"), "right": (p[0] + 70, p[1] + 12, "start"), "downleft": (p[0] - 60, p[1] + 86, "end"), "upright": (p[0] + 60, p[1] - 62, "start"), "upleft": (p[0] - 60, p[1] - 62, "end"), "downright": (p[0] + 60, p[1] + 86, "start")}[pos]
    lx = x if anchor == "middle" else (x + 10 if anchor == "end" else x - 10); ly = y - 12 if y < p[1] else y - 30   # a thin leader from the label towards the point
    return f'<line x1="{p[0]:.0f}" y1="{p[1]:.0f}" x2="{lx:.0f}" y2="{ly + (14 if y < p[1] else -2):.0f}" stroke="{MUTED}" stroke-width="2"/><text x="{x:.0f}" y="{y:.0f}" font-size="30" text-anchor="{anchor}" font-weight="700">{esc(m["label"])}</text>'

def shift(s):
    """s.bars: [{label, values:[...]}, {label, values:[...]}] (same length, sum ~100); s.segments: [labels]; dark to light from the bottom."""
    seg = s["segments"]; cols = [INK, BLUE, SKY, TINT, SOFT][:len(seg)]
    out = []; xs = [470, 860]; bw = 240; top, bottom = 380, 1000
    for (bar, x) in zip(s["bars"], xs):
        y = bottom; tot = sum(bar["values"]) or 1
        for v, c, lab in zip(bar["values"], cols, seg):
            h = (bottom - top) * v / tot; y -= h
            out.append(f'<rect x="{x}" y="{y:.0f}" width="{bw}" height="{h:.0f}" fill="{c}"/>')
            if h > 70: out.append(f'<text x="{x + bw / 2}" y="{y + h / 2 + 12:.0f}" font-size="30" text-anchor="middle" class="{"w" if c in (INK, BLUE) else ""}">{v:.0f}%</text>')
        out.append(f'<text x="{x + bw / 2}" y="{bottom + 54}" font-size="34" text-anchor="middle" font-weight="800">{esc(bar["label"])}</text>')
    ly = top + 10
    for c, lab in zip(cols, seg):   # legend on the left; a label wraps at "\n"
        parts = str(lab).split("\\n")
        out.append(f'<rect x="96" y="{ly}" width="34" height="34" rx="8" fill="{c}"/>' + "".join(f'<text x="144" y="{ly + 27 + 34 * j}" font-size="26" class="m">{esc(t)}</text>' for j, t in enumerate(parts))); ly += 48 + 34 * len(parts)
    out.append(f'<path d="M{xs[0] + bw + 30},{(top + bottom) / 2} L{xs[1] - 30},{(top + bottom) / 2}" stroke="{MUTED}" stroke-width="6" marker-end="url(#ar)"/>')
    return f'<svg width="1200" height="1200" viewBox="0 0 1200 1200"><defs><marker id="ar" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L5,2.5 L0,5 z" fill="{MUTED}"/></marker></defs>' + "".join(out) + "</svg>"

def beforeafter(s):
    """s.panels: [{label, lines:[{label, points, color:'ink'|'cyan'}]}] x2; a small line chart each, no axes numbers."""
    out = []; px = [96, 640]; pw = 470; top, bottom = 560, 900
    for p, x in zip(s["panels"], px):
        low = bottom - (bottom - top) * min(v for ln in p["lines"] for v in ln["points"])   # the panel ends 50 px under the lowest point, no empty tint
        out.append(f'<rect x="{x}" y="{top - 100}" width="{pw}" height="{low + 50 - (top - 100):.0f}" rx="18" fill="{SOFT}"/>')
        out.append(f'<text x="{x + 30}" y="{top - 46}" font-size="30" font-weight="700">{esc(p["label"])}</text>')
        for ln in p["lines"]:
            P = ln["points"]; n = len(P) - 1
            d = smooth([(x + 30 + (pw - 60) * i / n, bottom - (bottom - top) * v) for i, v in enumerate(P)])
            col = CYAN if ln.get("color") == "cyan" else INK
            out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"{" stroke-dasharray=\"2 22\"" if ln.get("dotted") else ""}/>')
        pass
    seen = []
    for ln in s["panels"][0]["lines"]:   # one legend for both panels, under the title
        col = CYAN if ln.get("color") == "cyan" else INK
        seen.append((col, ln["label"]))
    out.append(legend(seen, 96, top - 190))
    return f'<svg width="1200" height="1200" viewBox="0 0 1200 1200"><defs><marker id="ar" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L5,2.5 L0,5 z" fill="{MUTED}"/></marker></defs>' + "".join(out) + "</svg>"

def flow(s):
    """s.steps: [{label, sub, kind:'box'|'gate'|'end'}] left to right on one row (max 5); s.dead: {from: index, label, sub} drawn below as the dead end."""
    st = s["steps"]; n = len(st); out = []; y = 430; w = 200; h = 160; ext = 36   # a gate is a diamond w+2*ext wide
    widths = [w + 2 * ext if x.get("kind") == "gate" else w for x in st]; gap = (1110 - 96 - sum(widths)) / (n - 1)
    xs = []; cx = 96
    for i, x in enumerate(st): xs.append(cx + (ext if x.get("kind") == "gate" else 0)); cx += widths[i] + gap
    for i, (x, step) in enumerate(zip(xs, st)):
        k = step.get("kind", "box")
        if k == "gate": out.append(f'<path d="M{x + w / 2},{y - 40} L{x + w + 50},{y + h / 2} L{x + w / 2},{y + h + 40} L{x - 50},{y + h / 2} Z" fill="{CYAN}"/>')
        else: out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{INK if k == "box" else GREEN}"/>')
        parts = str(step["label"]).split("\\n"); fs = 30 if max(len(t) for t in parts) < 12 else 26; y0 = y + h / 2 + (0 if step.get("sub") else 12) - (len(parts) - 1) * fs * 0.6
        out.append("".join(f'<text x="{x + w / 2}" y="{y0 + j * fs * 1.2:.0f}" font-size="{fs}" text-anchor="middle" class="w">{esc(t)}</text>' for j, t in enumerate(parts)))
        if step.get("sub"): out.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 44}" font-size="26" text-anchor="middle" class="w" style="font-family:Open Sans;font-weight:400">{esc(step["sub"])}</text>')
        if i < n - 1:
            x1_, x2_ = x + w + (ext + 8 if k == "gate" else 10), xs[i + 1] - (ext + 14 if st[i + 1].get("kind") == "gate" else 16)
            out.append(f'<line x1="{x1_}" y1="{y + h / 2}" x2="{x2_}" y2="{y + h / 2}" stroke="{MUTED}" stroke-width="4" marker-end="url(#ar)"/>')
            if k == "gate": out.append(f'<text x="{(x1_ + x2_) / 2:.0f}" y="{y + h / 2 - 16}" font-size="26" text-anchor="middle" class="m">{esc(s.get("yes", "ja"))}</text>')
    d = s.get("dead")
    if d:
        x = xs[d["from"]] + w / 2; dy = y + h + 190
        out.append(f'<path d="M{x},{y + h + 54} L{x},{dy - 14}" stroke="{MUTED}" stroke-width="4" marker-end="url(#ar)"/><text x="{x + 18}" y="{(y + h + 54 + dy) / 2 + 8:.0f}" font-size="26" class="m">{esc(s.get("no", "nein"))}</text>')
        out.append(f'<rect x="{x - 250}" y="{dy}" width="500" height="136" rx="22" fill="none" stroke="{MUTED}" stroke-width="3" stroke-dasharray="8 8"/>')
        out.append(f'<text x="{x}" y="{dy + 58}" font-size="30" text-anchor="middle">{esc(d["label"])}</text><text x="{x}" y="{dy + 100}" font-size="26" text-anchor="middle" class="m">{esc(d.get("sub", ""))}</text>')
        if d.get("loop", True):   # the circle: from the dead end back to the first step
            bx0 = xs[0] + w / 2
            out.append(f'<path d="M{x - 250},{dy + 68} L{bx0},{dy + 68} L{bx0},{y + h + 18}" fill="none" stroke="{MUTED}" stroke-width="4" marker-end="url(#ar)"/>')
    return f'<svg width="1200" height="1200" viewBox="0 0 1200 1200"><defs><marker id="ar" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L5,2.5 L0,5 z" fill="{MUTED}"/></marker></defs>' + "".join(out) + "</svg>"

def matrix(s):
    """2x2: s.x = [left label, right label], s.y = [bottom label, top label]; s.quads = {tl, tr, bl, br: {label, sub}}; s.hot = the quadrant key drawn in cyan."""
    out = []; x0, y0, size = 330, 330, 370; names = {"tl": (0, 0), "tr": (1, 0), "bl": (0, 1), "br": (1, 1)}
    for k, (cx, cy) in names.items():
        q = s["quads"].get(k, {}); x = x0 + cx * size; y = y0 + cy * size; hot = k == s.get("hot"); dead = k == s.get("dead")
        fill = CYAN if hot else ("#f2f4f5" if dead else SOFT); col = "w" if hot else ""
        out.append(f'<rect x="{x + 13}" y="{y + 13}" width="{size - 26}" height="{size - 26}" rx="24" fill="{fill}"/>')
        parts = str(q.get("label", "")).split("\\n"); fs = 36 if max(len(t) for t in parts) < 14 else 29
        out.append("".join(f'<text x="{x + size / 2}" y="{y + size / 2 - 10 + (j - (len(parts) - 1) / 2) * fs * 1.2:.0f}" font-size="{fs}" text-anchor="middle" font-weight="800" class="{col}">{esc(t)}</text>' for j, t in enumerate(parts)))
        if q.get("sub"): out.append(f'<text x="{x + size / 2}" y="{y + size / 2 + 50 + (len(parts) - 1) * fs * 0.6:.0f}" font-size="26" text-anchor="middle" class="{"w" if hot else "m"}" style="font-family:Open Sans;font-weight:400">{esc(q["sub"])}</text>')
    xl, yl = s.get("x", ["", ""]), s.get("y", ["", ""])
    out.append(f'<text x="{x0 + size / 2}" y="{y0 + 2 * size + 56}" font-size="28" text-anchor="middle">{esc(xl[0])}</text><text x="{x0 + size * 1.5}" y="{y0 + 2 * size + 56}" font-size="28" text-anchor="middle">{esc(xl[1])}</text>')
    out.append(f'<text x="{x0 - 24}" y="{y0 + size * 1.5 + 10}" font-size="28" text-anchor="end">{esc(yl[0])}</text><text x="{x0 - 24}" y="{y0 + size / 2 + 10}" font-size="28" text-anchor="end">{esc(yl[1])}</text>')
    return '<svg width="1200" height="1200" viewBox="0 0 1200 1200">' + "".join(out) + "</svg>"

def phases(s):
    """Grouped horizontal bars: one row per phase (label 30 px at the left), two bars per row (first row = INK, second = CYAN), legend under the title."""
    out = []; ph = s["phases"]; rows = s["rows"]; n = len(ph)
    top, bottom = 460, 1080; lx, bx, bw_max = 96, 420, 600; rh = (bottom - top) / n; bh = min(40, rh / 3)
    mx = max(max(r["values"]) for r in rows) or 1
    out.append(legend([(INK, rows[0]["label"]), (CYAN, rows[1]["label"])], lx, top - 120))
    hot = s.get("hot", -1)
    for i, lab in enumerate(ph):
        y = top + i * rh
        out.append(f'<text x="{lx}" y="{y + rh / 2 + 10:.0f}" font-size="30" font-weight="{800 if i == hot else 600}" class="{"" if i == hot else "m"}">{esc(lab)}</text>')
        for j, (r, col) in enumerate(zip(rows, ((INK, CYAN) if i == hot else ("#9fb3c0", TINT)))):
            w = bw_max * r["values"][i] / mx; yy = y + rh / 2 - bh - 4 + j * (bh + 8)
            out.append(f'<rect x="{bx}" y="{yy:.0f}" width="{w:.0f}" height="{bh:.0f}" rx="6" fill="{col}"/><text x="{bx + w + 16:.0f}" y="{yy + bh - 10:.0f}" font-size="26" class="m">{r["values"][i]:.0f}%</text>')
    return '<svg width="1200" height="1200" viewBox="0 0 1200 1200">' + "".join(out) + "</svg>"


KINDS = {"phases": phases, "curves": curves, "shift": shift, "beforeafter": beforeafter, "flow": flow, "matrix": matrix}

CHECK_JS = """<script>
window.addEventListener('load',()=>{setTimeout(()=>{
  const R=[];const els=[...document.querySelectorAll('svg text, h1, .eyebrow, .who, .note')].filter(e=>(e.textContent||'').trim());
  const box=e=>{const b=e.getBoundingClientRect();return {l:b.left,t:b.top,r:b.right,b:b.bottom,s:(e.textContent||'').trim().slice(0,30)}};
  const T=els.map(box);
  const hit=(a,b,pad)=>a.l<b.r+pad&&b.l<a.r+pad&&a.t<b.b+pad&&b.t<a.b+pad;
  const cnt=document.querySelectorAll('svg text').length;if(cnt>20)R.push('too many labels: '+cnt);
  const stacked=(a,b)=>(Math.abs((a.l+a.r)/2-(b.l+b.r)/2)<3||Math.abs(a.l-b.l)<3)&&(Math.abs(a.b-b.t)<14||Math.abs(b.b-a.t)<14);
  for(let i=0;i<T.length;i++)for(let j=i+1;j<T.length;j++)if(hit(T[i],T[j],4)&&!stacked(T[i],T[j]))R.push('text/text: "'+T[i].s+'" × "'+T[j].s+'"');
  for(const t of T){if(t.l<60||t.r>1180||t.b>1180||t.t<40)R.push('margin: "'+t.s+'"')}
  for(const e of els){const fs=parseFloat(getComputedStyle(e).fontSize);if(fs<26&&!e.classList.contains('eyebrow'))R.push('small text '+Math.round(fs)+'px: "'+(e.textContent||'').trim().slice(0,30)+'"')}
  if(document.querySelector('svg circle, svg ellipse'))R.push('dots: circle markers present');
  const F=[...document.querySelectorAll('svg rect, svg path[fill]:not([fill="none"])')].filter(e=>!e.closest('marker')).map(e=>e.getBoundingClientRect());
  for(const t of T){const cx=(t.l+t.r)/2,cy=(t.t+t.b)/2;const host=F.find(f=>f.width>60&&f.height>60&&cx>f.left&&cx<f.right&&cy>f.top&&cy<f.bottom);
    if(host&&(t.l<host.left+6||t.r>host.right-6))R.push('text wider than its box: "'+t.s+'"')}
  const S=[...document.querySelectorAll('svg rect, svg path[fill]:not([fill="none"])')].filter(e=>!e.closest('marker')&&e.getBoundingClientRect().width>60&&e.getBoundingClientRect().height>60).map(e=>e.getBoundingClientRect());
  for(let i=0;i<S.length;i++)for(let j=i+1;j<S.length;j++){const a=S[i],b=S[j];const inside=(a.left>=b.left&&a.right<=b.right&&a.top>=b.top&&a.bottom<=b.bottom)||(b.left>=a.left&&b.right<=a.right&&b.top>=a.top&&b.bottom<=a.bottom)||(Math.abs(a.left-b.left)<2&&Math.abs(a.width-b.width)<2);
    if(!inside&&a.left<b.right+20&&b.left<a.right+20&&a.top<b.bottom+20&&b.top<a.bottom+20)R.push('shapes closer than 20px: '+Math.round(a.width)+'x'+Math.round(a.height)+' / '+Math.round(b.width)+'x'+Math.round(b.height))}
  for(const p of document.querySelectorAll('svg path, svg line')){
    const st=getComputedStyle(p);if(st.fill!=='none'&&st.fill!=='rgba(0, 0, 0, 0)'&&p.tagName==='path'&&!p.getAttribute('stroke'))continue;
    if(p.getAttribute('fill')&&p.getAttribute('fill')!=='none'&&!p.getAttribute('stroke'))continue;
    if(p.closest('marker'))continue;
    let L=0;try{L=p.getTotalLength()}catch(e){continue}
    const svg=p.ownerSVGElement.getBoundingClientRect();
    for(let d=0;d<=L;d+=6){const q=p.getPointAtLength(d);const x=q.x+svg.left,y=q.y+svg.top;
      const t=T.find(t=>x>t.l-2&&x<t.r+2&&y>t.t-2&&y<t.b+2);if(t){R.push('text/line: "'+t.s+'"');break}}
  }
  const words=els.map(e=>e.textContent.trim().split(/\\s+/).length).reduce((a,b)=>a+b,0);
  if(words>40)R.push('too much text: '+words+' words (max 40)');
  const pre=document.createElement('pre');pre.id='__check';pre.textContent=JSON.stringify([...new Set(R)]);document.body.appendChild(pre);
},300)});
</script>"""

def check(html_path):
    """Geometry check of a rendered page: text over text, text over a line, text outside the margins, too many words. Returns a list of findings."""
    import re
    r = subprocess.run([CFG["chrome"], "--headless=new", "--disable-gpu", "--window-size=1200,1200", "--virtual-time-budget=6000", "--dump-dom", "file://" + html_path], capture_output=True, text=True, timeout=60)
    m = re.search(r'<pre id="__check">(.*?)</pre>', r.stdout, re.S)
    if not m: return ["check did not run"]
    return json.loads(html.unescape(m.group(1)))

def render(spec, out_base, out_dir=None, verbose=True):
    """Renders the PNG and runs the checker; findings are printed and returned via render.last_check."""
    out_dir = out_dir or DRAFTS; os.makedirs(out_dir, exist_ok=True)
    doc = frame(spec, KINDS[spec["kind"]](spec)).replace("</body>", CHECK_JS + "</body>")
    hp = os.path.abspath(os.path.join(out_dir, out_base + ".html")); png = os.path.abspath(os.path.join(out_dir, out_base + ".png"))
    open(hp, "w", encoding="utf-8").write(doc)
    subprocess.run([CFG["chrome"], "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,1200", "--virtual-time-budget=5000", f"--screenshot={png}", "file://" + hp], capture_output=True, timeout=60)
    render.last_check = check(hp)
    for _ in range(8):   # a mark label on the line: try the next position
        bad = [m for m in spec.get("marks", []) if any(f.startswith('text/') and m["label"][:30] in f for f in render.last_check)]
        if not bad: break
        order = ["above", "below", "left", "right", "downleft", "upright", "upleft", "downright"]
        for m in bad: m["pos"] = order[(order.index(m.get("pos", "above")) + 1) % len(order)] if m.get("pos") in order else "below"
        doc = frame(spec, KINDS[spec["kind"]](spec)).replace("</body>", CHECK_JS + "</body>"); open(hp, "w", encoding="utf-8").write(doc)
        subprocess.run([CFG["chrome"], "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,1200", "--virtual-time-budget=5000", f"--screenshot={png}", "file://" + hp], capture_output=True, timeout=60)
        render.last_check = check(hp)
    if verbose: print(f"  check {out_base}: " + ("ok" if not render.last_check else "; ".join(render.last_check)), file=sys.stderr)
    return png if os.path.isfile(png) else None
render.last_check = []

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1], encoding="utf-8")); print(render(spec, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
