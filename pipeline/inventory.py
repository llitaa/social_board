#!/usr/bin/env python3
"""Material inventory: candidate topics per pillar with a one-line angle (library/inventory.csv).
Built from the CV, the company context and the published posts with one model call; re-running keeps statuses
(unused / drafted / published / skipped) and only adds new candidates. Shown on the board as counts per pillar."""
import os, re, subprocess
from datetime import datetime, date
from common import CFG, LIB, read_csv, write_csv, log, resolve
from llm import llm_json

INV = os.path.join(LIB, "inventory.csv")
FIELDS = ["id", "pillar", "channel", "topic", "angle", "source", "tags", "status", "used_in", "added"]
PILLARS = {"network": "a post built on material a teammate shared (a photo, a published post, a memo): the author's own angle on it, the teammate named in the text, credit line at the end",
           "thought": "a phrase Anton recorded or wrote himself (memo or chat): the post is built around that sentence, it is the hook and the card headline, verbatim",
           "case": "a case from Anton's own practice (CV): situation, what he did, what it cost or saved, one lesson",
           "decision": "a decision helper for a CIO / Entwicklungsleiter: a choice they face this year, the two or three options, what tips it",
           "model-test": "a model or tool test from Anton's daily work with coding agents on legacy C++: setup, result, verdict",
           "trend": "a trend in AI-in-engineering / software products with Anton's own position, no news summary, no model or hardware names",
           "transformation": "engagement post with graphic: what shifts in software development, from code to product (roles, work, responsibility), told from Anton's own projects",
           "money": "engagement post with graphic: how software earns or saves money, a real mechanism from a project (new market, new pricing, less downtime)",
           "learning": "engagement post with graphic: a reading or learning list for people who are responsible for software without writing it; only real books and sources, one sentence why each",
           "company": "AlpiType company post (EN): industrial or office automation built as code in the client's own environment, 70/30, who approves"}

def cv_text():
    if not CFG.get("cv_pdf"):   # another person's board: the facts are their confirmed profile (library/profile.md, from onboard.py)
        f = os.path.join(LIB, "profile.md"); return open(f, encoding="utf-8").read() if os.path.isfile(f) else ""
    out = os.path.join(LIB, "sources", "cv-en.txt"); pdf = os.path.expanduser(CFG["cv_pdf"])
    if not os.path.isfile(out) or os.path.getmtime(out) < os.path.getmtime(pdf):
        os.makedirs(os.path.dirname(out), exist_ok=True); subprocess.run(["pdftotext", "-layout", pdf, out], check=True)
    return open(out, encoding="utf-8").read()

def published():
    plog, _ = read_csv(CFG["posts_log"]); plan, _ = read_csv(CFG["content_plan"])
    hooks = [f"{r['date']} {r['channel']}: {r['hook'][:120]}" for r in plog if r.get("hook")]
    for r in plan:
        if r.get("status") in ("scheduled", "approved", "draft", "change") and r.get("caption_ref"):
            t = resolve(r["caption_ref"]); first = open(t, encoding="utf-8").readline().strip()[:120] if os.path.isfile(t) else r["slot"]
            hooks.append(f"{(r.get('planned') or '')[:10]} {r['channel']} ({r['status']}): {first}")
    return hooks

def load(): rows, _ = read_csv(INV); return rows
def save(rows): write_csv(INV, rows, FIELDS)

def build_user():
    """Topic inventory for another person's board: facts only from their confirmed profile, personal pillars only, no company page."""
    from common import profile
    who = profile(); rows = load(); have = {r["topic"].lower() for r in rows}; facts = cv_text()
    if not facts.strip(): log("no profile.md yet, no inventory"); return
    de = who["lang"] == "de"
    prompt = f"""You build a topic inventory for the LinkedIn posts of {who['name']}{(' (' + who['role'] + ')') if who.get('role') else ''}. Facts may only come from the profile below; invent nothing, no numbers or clients that are not there.
Pillars: case = a concrete situation from their work, what was done, what came out; decision = a position or rule they hold, with the reason; trend = a development in their field with their own view.
Rules: posts on their personal profile, in {'German' if de else 'English'}, first person; no audience addressing ("richtet sich an", "für alle, die"); no job search; one angle per topic.
Already published or planned (do not repeat): {chr(10).join(published()) or '-'}
Existing inventory topics (do not repeat): {sorted(have) or 'none'}
{('Never, not even in passing (the person ruled these out): ' + '; '.join(who['avoid'])) if who.get('avoid') else ''}
Produce 8-10 case topics, 5-6 decision topics, 4 trend topics, strongest first within a pillar.
Answer with one JSON object only: {{"topics": [{{"pillar": "case|decision|trend", "topic": "4-8 words in {'German' if de else 'English'}", "angle": "one sentence, the concrete hook", "source": "profile: <section or fact>", "tags": "3-6 lowercase words"}}]}}

=== Profile ===
{facts[:12000]}
"""
    d = llm_json("inventory", prompt); n = 0
    for t in d.get("topics", []):
        if t.get("topic", "").lower() in have or t.get("pillar") not in ("case", "decision", "trend"): continue
        rows.append({"id": f"t{len(rows) + 1:03d}", "pillar": t["pillar"], "topic": t["topic"][:80], "angle": t.get("angle", "")[:300], "source": t.get("source", "")[:120], "tags": t.get("tags", "")[:80], "status": "unused", "used_in": "", "added": date.today().isoformat()}); n += 1
    save(rows); log(f"inventory: {n} new topics, {len(rows)} total"); return n

def build():
    if not CFG.get("cv_pdf"): return build_user()
    rows = load(); have = {r["topic"].lower() for r in rows}
    ctx = open(os.path.expanduser(CFG["company_context"]), encoding="utf-8").read()
    prompt = f"""You build a topic inventory for Anton Lytvynenko's LinkedIn posts. Facts may only come from the CV and the company context below; invent nothing.
Pillars and what they mean:
{chr(10).join(f'- {k}: {v}' for k, v in PILLARS.items())}
Rules: personal pillars (case, decision, model-test, trend) are posts on Anton's own profile in German: never mention AlpiType, never a freelance or job-search angle, never name the clients Infineon, Leica, Siemens or Reiser (say "a semiconductor manufacturer", "a measurement-technology manufacturer"); Brainlab, Rheinmetall (as "Rheinmetall project") may be named. Company topics are for the AlpiType page in English.
Already published or planned (do not repeat these angles; list them in "covered" with the matching topic if an inventory topic is clearly the same):
{chr(10).join(published())}
Existing inventory topics (do not repeat): {sorted(have) or 'none'}

Produce 8-12 case topics, 6-8 decision topics, 3-4 model-test topics, 4-6 trend topics, 8-10 company topics. Each distinct angle once, strongest first within a pillar.
Answer with one JSON object only: {{"topics": [{{"pillar": "case|decision|model-test|trend|company", "topic": "4-8 words", "angle": "one sentence, the concrete hook", "source": "CV: <project> | context: <section> | own position", "tags": ["3-5 lowercase words for photo matching, e.g. outdoor, lake, book, desk"]}}], "covered": ["topics already published"]}}

=== CV (EN) ===
{cv_text()}

=== Company context ===
{ctx}
"""
    d = llm_json("inventory", prompt)
    n0 = len(rows); nid = max([int(r["id"][1:]) for r in rows if r["id"][1:].isdigit()] or [0])
    for t in d.get("topics", []):
        if t.get("topic", "").lower() in have or t.get("pillar") not in PILLARS: continue
        nid += 1
        rows.append({"id": f"t{nid:03d}", "pillar": t["pillar"], "channel": "company" if t["pillar"] == "company" else "personal", "topic": t["topic"],
                     "angle": t.get("angle", ""), "source": t.get("source", ""), "tags": " ".join(t.get("tags", [])), "status": "unused", "used_in": "",
                     "added": datetime.now().isoformat(timespec="seconds")})
    save(rows); log(f"inventory: {len(rows)} topics ({len(rows) - n0} new); covered: {d.get('covered', [])}")

def counts():
    rows = load(); c = {}
    for r in rows:
        c.setdefault(r["pillar"], {"unused": 0, "drafted": 0, "published": 0})
        c[r["pillar"]][r["status"] if r["status"] in c[r["pillar"]] else "published"] += 1
    return c

def take(pillar):
    """The strongest unused topic of a pillar (file order = model order), or None."""
    for r in load():
        if r["pillar"] == pillar and r["status"] == "unused": return r
    return None

def set_status(tid, status, used_in=""):
    rows = load()
    for r in rows:
        if r["id"] == tid: r["status"] = status; r["used_in"] = used_in or r["used_in"]
    save(rows)

if __name__ == "__main__":
    build(); print(counts())
