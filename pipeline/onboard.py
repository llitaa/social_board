#!/usr/bin/env python3
"""Self-onboarding of another person's board (03.11.2026). The person types their website and a few sentences on the board
(api.php a=profile) and may attach a document; the request lands in uploads/profile/ and is pulled here. One model call turns
website text + document + their words into a profile proposal (library/profile.json, confirmed: false) that the board shows for
correction. After "Passt" (apply_decisions: profile_confirm) the facts become library/profile.md and positioning.md, and the
topic inventory is built from them (one more call). Nothing is invented: unsure points are listed, not filled.
Nothing to do on Anton's board (his facts are the CV and the company context)."""
import html, json, os, re, subprocess, sys, urllib.request
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CFG, LIB, BOARD_LOCAL, USER, jload, jdump, log, read_csv

REQ = os.path.join(BOARD_LOCAL, "uploads", "profile")

def fetch(url, limit=40000):
    """Visible text of a public web page (the person named it); errors return ''."""
    if not re.match(r"^https?://", url): url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AlpiType board onboarding)"})
        with urllib.request.urlopen(req, timeout=25) as r: raw = r.read(600000).decode(r.headers.get_content_charset() or "utf-8", "ignore")
    except Exception as e: log("website fetch failed:", url, str(e)[:120]); return ""
    raw = re.sub(r"(?is)<(script|style|nav|footer|svg|noscript).*?</\1>", " ", raw)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", raw)); txt = re.sub(r"[ \t\r\f\v]+", " ", txt); txt = re.sub(r"\n\s*\n+", "\n", txt)
    return txt.strip()[:limit]

def doc_text(path, limit=40000):
    if not path or not os.path.isfile(path): return ""
    if path.lower().endswith(".pdf"):
        try: return subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, timeout=60).stdout[:limit]
        except Exception as e: log("pdftotext failed:", e); return ""
    try: return open(path, encoding="utf-8", errors="ignore").read()[:limit]
    except OSError: return ""

def propose(req):
    from llm import llm_json
    from common import profile
    who = profile(); de = who["lang"] == "de"
    site = fetch(req.get("website", "")) if req.get("website") else ""
    doc = doc_text(os.path.join(REQ, req["doc"])) if req.get("doc") else ""
    words = (req.get("words") or "").strip()
    if not (site or doc or words): log("profile request without content"); return None
    prompt = f"""Build a LinkedIn posting profile for {who['name']} from the material below. Use only what is there; where something is unclear, say so under "uncertain" instead of guessing. Write every field in {'German' if de else 'English'}, short and concrete, in the third person except "facts".
Answer with one JSON object only:
{{"role": "one line: what they do, as they would say it", "company": "company name or empty", "website": "the site as given or empty",
 "audience": "one line: who should read their posts (a role and a situation, not 'everyone')", "offer": "one line: what the reader should take away or ask for",
 "topics": ["6-10 short post topics from the material, each with a concrete angle"],
 "tone": "one line: how they write or speak (from their own words if present)",
 "audiences": ["3-5 reader groups as short chips, 2-5 words each, concrete (for example: Eltern kurzsichtiger Kinder)"],
 "tone_samples": {"locker": "two sentences in a casual, direct voice, built from the facts, as a post opening", "sachlich": "two sentences, calm and factual, from the facts", "persoenlich": "two sentences, personal, told as a small story from the facts"},
 "facts": "10-25 lines of facts a post may use: services, methods, places, years, typical clients described without names, results that are stated. One fact per line, nothing invented.",
 "uncertain": ["points the material does not settle"]}}

=== Their own words ===
{words or '-'}

=== Website text ===
{site or '-'}

=== Document ===
{doc or '-'}
"""
    d = llm_json("profile", prompt)
    pr = jload(os.path.join(LIB, "profile.json"), {})
    pr.update({"role": str(d.get("role", ""))[:200], "company": str(d.get("company", ""))[:120], "website": str(d.get("website") or req.get("website", ""))[:200],
               "audience": str(d.get("audience", ""))[:300], "offer": str(d.get("offer", ""))[:300], "topics": [str(t)[:160] for t in d.get("topics", [])][:12],
               "tone": str(d.get("tone", ""))[:300], "facts": str(d.get("facts", ""))[:6000], "uncertain": [str(u)[:200] for u in d.get("uncertain", [])][:10],
               "audiences": [str(a)[:60] for a in (d.get("audiences") or [])][:6], "tone_samples": {k: str(v)[:400] for k, v in (d.get("tone_samples") or {}).items() if k in ("locker", "sachlich", "persoenlich")},
               "linkedin": str(req.get("linkedin", ""))[:200],
               "words": words[:4000], "proposed": datetime.now().isoformat(timespec="minutes"), "confirmed": False})
    pr.setdefault("name", who["name"]); pr.setdefault("lang", who["lang"])
    jdump(os.path.join(LIB, "profile.json"), pr); jdump(os.path.join(BOARD_LOCAL, "profile.json"), pr)
    log(f"profile proposed for {who['name']}: {len(pr['topics'])} topics, {len(pr['uncertain'])} open points")
    return pr

def write_facts(pr):
    """profile.md (facts for drafts) and positioning.md (who reads, what must stick) from the confirmed profile."""
    lines = [f"# {pr.get('name', '')}", pr.get("role", ""), f"Firma: {pr['company']}" if pr.get("company") else "", f"Website: {pr['website']}" if pr.get("website") else "", "",
             "## Fakten", pr.get("facts", ""), "", "## In eigenen Worten", pr.get("words", ""), "", "## Themen"] + [f"- {t}" for t in pr.get("topics", [])]
    open(os.path.join(LIB, "profile.md"), "w", encoding="utf-8").write("\n".join(l for l in lines if l is not None) + "\n")
    pos = [f"Leser: {pr.get('audience', '')}", f"Was hängen bleiben soll: {pr.get('offer', '')}", f"Was der Leser danach tun soll: {pr['goal']}" if pr.get("goal") else "", f"Ton: {pr.get('tone', '')}" if pr.get("tone") else "",
           ("Nie als Thema, auch nicht am Rand: " + "; ".join(pr["avoid"])) if pr.get("avoid") else ""]
    open(os.path.join(LIB, "positioning.md"), "w", encoding="utf-8").write("\n".join(l for l in pos if l) + "\n")
    ex = os.path.join(LIB, "examples.md")   # posts the person likes (Mein Profil): tone reference for draft.py, never copied
    if (pr.get("examples") or "").strip(): open(ex, "w", encoding="utf-8").write(pr["examples"].strip() + "\n")
    elif os.path.isfile(ex): os.remove(ex)

def main():
    if not USER: return
    f = os.path.join(REQ, "request.json")
    if os.path.isfile(f):
        req = jload(f, {})
        try:
            if propose(req) is not None: os.remove(f)
        except Exception as e: log("profile proposal failed:", repr(e)[:300])
    pr = jload(os.path.join(LIB, "profile.json"), {})
    if pr.get("confirmed") and not os.path.isfile(os.path.join(LIB, "profile.md")): write_facts(pr)
    inv, _ = read_csv(os.path.join(LIB, "inventory.csv"))
    if pr.get("confirmed") and not any(r.get("status") == "unused" for r in inv):
        import inventory
        try: inventory.build()
        except Exception as e: log("inventory failed:", repr(e)[:300])

if __name__ == "__main__": main()
