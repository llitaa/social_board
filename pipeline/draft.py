#!/usr/bin/env python3
"""Keep every post slot in the next horizon_days filled with a board-ready draft (spec content-generation).
Slot rule from config (Mon/Wed/Fri personal 07:30 DE, Thu company 09:00 EN); a week holds at most 3 personal and
1 company post, so a post Anton scheduled himself on another weekday counts for that week.
Per open slot: pillar (least used in the surrounding 14 days; a fresh voice memo comes first) -> topic from the
inventory -> photo from the pool (personal) or a 1200x1200 graphic from the template (company) -> one text
(draft model) -> rules gate -> library/drafts/<id>.{txt,json,png} and a content-plan.csv row with status draft.
"""
import base64, html, json, os, re, subprocess
from datetime import date, datetime, timedelta
from common import CFG, LIB, ROOT, CAMP, read_csv, write_csv, resolve, log
from llm import llm_json, MODELS
import photo_index as ph, inventory as inv, rules_check

DRAFTS = os.path.join(LIB, "drafts"); os.makedirs(DRAFTS, exist_ok=True)
WD = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
SLOTS = CFG["slots"]; HORIZON = int(CFG.get("horizon_days", 14))
CHAN = {"personal": "linkedin", "company": "linkedin-company"}
STYLE = {"personal": """Du schreibst als Anton Lytvynenko auf seinem persönlichen LinkedIn-Profil, auf Deutsch, Sie-Form, als Softwarearchitekt mit 13 Jahren C++.
Form: 900-1600 Zeichen. Erster Satz = Hook (konkret, kein Clickbait). Kurze Absätze, keine Aufzählungszeichen-Orgie, keine Emojis. Ein Gedanke pro Post.
Immer eine Frage als letzter Satz vor den Hashtags, dann genau 3 Hashtags.
Verboten: Zielgruppen-Ansprache ("richtet sich an", "für alle, die"), Freelance- oder Jobsuche-Hinweise, AlpiType, erfundene Zahlen oder Projekte, Kundennamen Infineon, Leica, Siemens, Reiser (sag "ein Halbleiterhersteller", "ein Messtechnik-Hersteller"), Werbesprache.
Wenn ein Foto beschrieben ist, darf der erste Satz es leicht aufgreifen (wie "Dieses Schiff fährt noch? Legacy-Code auch?"), muss aber nicht.""",
         "company": """You write for the AlpiType company page on LinkedIn, in English, as the company ("we").
Form: 900-1500 characters. First sentence = hook with a concrete scene or number from the material. Short paragraphs, no emojis. One idea per post.
AlpiType builds automation as code inside the client's own environment (Microsoft 365, or software next to the machine); the machine does 70 percent, a person approves the 30 percent of exceptions; who trains, who controls, who is accountable stays written down.
Always end with a question, then exactly 3 hashtags including #7030. Allowed CTA at most once: the book as free PDF alpitype.de/buch-en, or "30 minutes with an engineer".
Forbidden: addressing an audience ("for everyone who"), naming clients, invented numbers, claims not in the company context."""}

def positioning():
    """Who the personal posts are for and what must stick with the reader (library/positioning.md, Anton edits it)."""
    f = os.path.join(LIB, "positioning.md")
    return ("\nPositionierung (gilt für jeden persönlichen Post):\n" + open(f, encoding="utf-8").read().strip() + "\n") if os.path.isfile(f) else ""

def book_phrases():
    """One sentence per chapter of Anton's book (library/sources/book-phrases.md): his own wording for hooks and card headlines."""
    f = os.path.join(LIB, "sources", "book-phrases.md")
    return ("\nSätze aus Antons Buch \"Das KI-System 70/30\", ein Satz pro Kapitel. Das ist seine Sprache: nimm einen davon als Hook oder Karten-Headline, wenn er zum Thema passt (wörtlich), sonst schreibe in diesem Ton:\n" + open(f, encoding="utf-8").read().strip() + "\n") if os.path.isfile(f) else ""

def style_rules():
    """Anton's standing preferences, learned from his notes, edits and skip reasons on the board (learn.py)."""
    f = os.path.join(LIB, "style-rules.txt")
    rules = [l.strip() for l in open(f, encoding="utf-8")] if os.path.isfile(f) else []
    rules = [l for l in rules if l and not l.startswith("#")]
    return ("\nAnton's standing preferences from his notes on earlier posts (apply them):\n" + "\n".join("- " + l.split("\t")[-1] for l in rules[-40:]) + "\n") if rules else ""

def planned(channel, slot_day, days=28):
    """Hooks of posts posted or planned within +/- days of the slot: the draft must not reuse their facts or angle."""
    plan, _ = read_csv(CFG["content_plan"]); out = []
    for r in plan:
        d = (r.get("planned") or "")[:10]
        if r["channel"] != CHAN[channel] or len(d) != 10 or r["status"] in ("dropped", "skipped", "idea") or abs((date.fromisoformat(d) - slot_day).days) > days: continue
        t = text_of_row(r)
        if t: out.append(f"{d}: {t.splitlines()[0][:140]}")
    return out

def text_of_row(r):
    t = resolve(r.get("caption_ref", ""))
    return open(t, encoding="utf-8").read().strip() if t and os.path.isfile(t) else ""

def examples(channel, n=3):
    plan, _ = read_csv(CFG["content_plan"]); out = []
    for r in sorted(plan, key=lambda r: r.get("planned") or "", reverse=True):
        if r["channel"] == CHAN[channel] and r["status"] in ("posted", "scheduled") and r.get("caption_ref"):
            t = resolve(r["caption_ref"])
            if os.path.isfile(t): out.append(open(t, encoding="utf-8").read().strip())
        if len(out) >= n: break
    return out

def next_ids(plan):
    n = {"post": 12, "comp": 12}
    for r in plan:
        for k, v in re.findall(r"li-(post|comp)-(\d+)", r.get("caption_ref", "") + " " + r.get("asset", "")): n[k] = max(n[k], int(v))
    return n

def week(d): return d.isocalendar()[:2]

def open_slots(plan, today):
    taken = {}; per_week = {}
    for r in plan:
        if r["channel"] not in CHAN.values() or r["status"] in ("dropped", "skipped", "idea", "blocked"): continue
        d = (r.get("planned") or "")[:10]
        if len(d) != 10: continue
        c = "company" if r["channel"] == "linkedin-company" else "personal"; dd = date.fromisoformat(d)
        taken[(d, c)] = r; per_week[(week(dd), c)] = per_week.get((week(dd), c), 0) + 1
    out = []; d = today
    while d <= today + timedelta(days=HORIZON):
        for c, s in SLOTS.items():
            if d.strftime("%a") in s["days"] and (d.isoformat(), c) not in taken and per_week.get((week(d), c), 0) < (1 if c == "company" else 3):
                dt = datetime.strptime(f"{d} {s['time']}", "%Y-%m-%d %H:%M")
                if dt > datetime.now() + timedelta(hours=2): out.append((dt, c)); per_week[(week(d), c)] = per_week.get((week(d), c), 0) + 1
        d += timedelta(days=1)
    return sorted(out)

def pillar_counts(plan, around, days=14):
    c = {}
    for r in plan:
        d = (r.get("planned") or "")[:10]
        if r["channel"] != "linkedin" or len(d) != 10 or abs((date.fromisoformat(d) - around).days) > days: continue
        m = re.search(r"pillar=([\w-]+)", r.get("notes", "")); c[m.group(1) if m else "unknown"] = c.get(m.group(1) if m else "unknown", 0) + 1
    return c

def fresh_memo():
    rows, _ = read_csv(os.path.join(LIB, "memos", "index.csv"))
    for r in rows:
        if r["status"] == "new" and int(r.get("words") or 0) >= 15:
            t = os.path.join(LIB, os.path.splitext(r["file"])[0] + ".txt")
            if os.path.isfile(t): return r, open(t, encoding="utf-8").read().strip()
    return None, ""

def neighbour_shoots(plan, slot_day, idx):
    """Shoots of the personal posts just before and after slot_day (so the picked photo is not from the same trip)."""
    pi = ph.plan_images(); by_date = []
    for pid, uses in pi.items():
        for cid, d, st in uses:
            if d and st not in ("skipped", "dropped"): by_date.append((d, idx.get(pid, {}).get("shoot", pid)))
    before = [s for d, s in by_date if d < slot_day.isoformat()]; after = [s for d, s in by_date if d > slot_day.isoformat()]
    out = []
    if before: out.append(max((d, s) for d, s in by_date if d < slot_day.isoformat())[1])
    if after: out.append(min((d, s) for d, s in by_date if d > slot_day.isoformat())[1])
    return out

def render_graphic(g, cid):
    tpl = open(os.path.join(ROOT, "pipeline", "templates", "company-card.html"), encoding="utf-8").read()
    logo = base64.b64encode(open(os.path.expanduser(CFG["logo"]), "rb").read()).decode()
    lines = g.get("lines", [])[:4]
    lh = "".join(f'<div class="line{" last" if i == len(lines) - 1 else ""}"><div class="n">{i + 1}</div><div>{html.escape(l)}</div></div>' for i, l in enumerate(lines))
    doc = tpl.replace("{{LOGO}}", logo).replace("{{EYEBROW}}", html.escape(g.get("eyebrow", ""))).replace("{{TITLE}}", html.escape(g.get("title", "")).replace("\\n", "<br>")) \
             .replace("{{LINES}}", lh).replace("{{FOOTER}}", html.escape(g.get("footer", "70 / 30")))
    hp = os.path.join(DRAFTS, cid + ".html"); png = os.path.join(DRAFTS, cid + ".png"); open(hp, "w", encoding="utf-8").write(doc)
    subprocess.run([CFG["chrome"], "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,1200", f"--screenshot={png}", "file://" + hp],
                   capture_output=True, timeout=60)
    return png if os.path.isfile(png) else None

def draft_one(dt, channel, plan, idx, memo=None):
    today = date.today(); slot_day = dt.date()
    if memo: pillar, topic = "memo", None
    else:
        cnt = pillar_counts(plan, slot_day); order = ["case", "decision", "trend", "model-test"] if channel == "personal" else ["company"]
        cands = [(cnt.get(p, 0), i, p) for i, p in enumerate(order) if inv.take(p)]
        if not cands: log("no unused topic for", channel); return None
        pillar = min(cands)[2]; topic = inv.take(pillar)
    photo = None; nb = []
    if channel == "personal":
        nb = neighbour_shoots(plan, slot_day, idx)
        cands = ph.pick(slot_day, nb, topic_tags=(topic["tags"].split() if topic else ()), friday=slot_day.weekday() == 4)
        if not cands: log("no eligible photo for", slot_day); return None
        photo = cands[0]
    ex = examples(channel)
    material = f"Voice memo (Anton's own words, keep his thought, clean spelling and structure only, add nothing he did not say):\n{memo[1]}" if memo else \
               f"Topic: {topic['topic']}\nAngle: {topic['angle']}\nSource: {topic['source']}\nPillar: {pillar} = {inv.PILLARS[pillar]}"
    facts = inv.cv_text() if channel == "personal" else open(os.path.expanduser(CFG["company_context"]), encoding="utf-8").read()
    img = f"\nPhoto that will be posted with the text: {photo['scene'] or photo['note'] or 'Anton, ' + photo['tags']}\n" if photo else \
          "\nThe post gets a 1200x1200 graphic: give eyebrow (2-3 words), title (max 8 words, may contain one \\n), 3-4 numbered lines (max 9 words each) and a 1-3 word footer.\n"
    prompt = f"""{STYLE[channel]}
{positioning() + book_phrases() if channel == 'personal' else ''}{style_rules()}
Slot: {dt.strftime('%A %d.%m.%Y %H:%M')}
{material}
{img}
Posts already posted or planned within four weeks of this slot. Do not reuse their angle and do not repeat a fact or number they already carry (one fact, one post):
{chr(10).join(planned(channel, slot_day)) or '-'}

Three of Anton's recent posts on this channel, for voice and length only (do not repeat their content):
---
{chr(10) + '---' + chr(10)}{(chr(10) + '---' + chr(10)).join(ex)}
---
Facts you may use (nothing else):
{facts[:9000]}

Answer with one JSON object only: {{"text": "the full post incl. hashtags, newlines as \\n"{', "graphic": {"eyebrow": "", "title": "", "lines": [""], "footer": ""}' if channel == 'company' else ', "card": {"kicker": "2-3 words, the field (e.g. Legacy C++)", "headline": "the one sentence of the post that should stand under the photo, max 70 characters"}, "signals": {"lead": "the sentence of the post that shows him leading or deciding, copied verbatim", "ai": "the sentence that shows his own AI practice or position, copied verbatim"}'}}}"""
    d = llm_json("draft", prompt); text = rules_check.fix_orthography(d.get("text", "").strip(), channel)
    v = rules_check.check(text, channel, d.get("signals"))
    if v:
        d = llm_json("draft", prompt + f"\n\nYour previous answer broke these rules: {v}. Fix them and answer again with the JSON object only.\nPrevious text:\n{text}")
        text = rules_check.fix_orthography(d.get("text", "").strip(), channel); v = rules_check.check(text, channel, d.get("signals"))
        if v: log("rules fail", dt, channel, v); return None
    ids = next_ids(plan); kind = "post" if channel == "personal" else "comp"; num = ids[kind] + 1
    slug = re.sub(r"[^a-z0-9]+", "-", (topic["topic"] if topic else "memo").lower()).strip("-")[:28]
    cid = f"li-{kind}-{num:02d}"; base = f"{cid}-{slug}"
    open(os.path.join(DRAFTS, base + ".txt"), "w", encoding="utf-8").write(text + "\n")
    asset = ""
    if photo:
        asset = f"{os.path.basename(photo['file'])} (square: library/photos/square/{photo['id']}_sq.png, {photo['scene'][:60]})"
        if CFG.get("personal_card", {}).get("style", "off") != "off" and d.get("card"):
            import personal_card
            png = personal_card.render(ph.square_of(photo), d["card"], base)
            if png: asset = f"library/drafts/{base}.png (card: photo {photo['id']} + headline, style {CFG['personal_card']['style']}; source library/drafts/{base}.html)"
    else:
        png = render_graphic(d.get("graphic", {}), base)
        asset = f"library/drafts/{base}.png (1200x1200 graphic; source library/drafts/{base}.html)" if png else ""
    meta = {"id": cid, "channel": channel, "pillar": pillar, "topic": topic["id"] if topic else "", "memo": memo[0]["id"] if memo else "", "photo": photo["id"] if photo else "",
            "neighbour_shoots": nb, "model": MODELS["draft"], "created": datetime.now().isoformat(timespec="seconds"), "versions": [], "graphic": d.get("graphic"), "card": d.get("card"), "signals": d.get("signals")}
    json.dump(meta, open(os.path.join(DRAFTS, base + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    row = {"id": str(max(int(r["id"]) for r in plan if r["id"].isdigit()) + 1), "campaign": "linkedin-anton" if channel == "personal" else "linkedin-alpitype",
           "channel": CHAN[channel], "slot": slug, "asset": asset, "format": "foto-post" if photo else "grafik-post", "language": SLOTS[channel]["lang"],
           "caption_ref": f"library/drafts/{base}.txt", "planned": dt.strftime("%Y-%m-%d %H:%M"), "status": "draft",
           "notes": f"[draft {today.isoformat()} pillar={pillar} topic={topic['id'] if topic else 'memo'} photo={photo['id'] if photo else '-'}] {topic['angle'] if topic else 'from voice memo ' + memo[0]['id']}"}
    plan.append(row)
    if topic: inv.set_status(topic["id"], "drafted", cid)
    if memo:
        rows, f = read_csv(os.path.join(LIB, "memos", "index.csv"))
        for r in rows:
            if r["id"] == memo[0]["id"]: r["status"], r["used_in"] = "drafted", cid
        write_csv(os.path.join(LIB, "memos", "index.csv"), rows, f)
    log(f"drafted {cid} {channel} {dt:%a %d.%m. %H:%M} pillar={pillar} photo={photo['id'] if photo else '-'}")
    return row

def main(limit=8):
    plan, fields = read_csv(CFG["content_plan"]); today = date.today()
    idx = {r["id"]: r for r in ph.read_index()}
    slots = open_slots(plan, today)
    if not slots: log("all slots filled"); return
    memo = fresh_memo(); n = 0
    for dt, c in slots[:limit]:
        m = memo if (c == "personal" and memo[0]) else None
        try:
            if draft_one(dt, c, plan, idx, m): n += 1; write_csv(CFG["content_plan"], plan, fields)
            if m: memo = (None, "")
        except Exception as e: log("draft failed", dt, c, repr(e)[:300])
    log(f"drafts written: {n} of {len(slots)} open slots")

if __name__ == "__main__": main()
