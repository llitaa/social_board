"""The gate before the board: Anton's content rules as patterns. Returns a list of violations (empty = pass).
Since 20.10.2026 a personal post must also carry a leadership signal and an AI signal (library/positioning.md): the model
names the two sentences, check() verifies they are really in the text. Swiss orthography (ss for ß) is applied, not checked."""
import re
try:
    from common import CFG
except ImportError: CFG = {}

def fix_orthography(text, channel):
    return text.replace("ß", "ss") if channel == "personal" and CFG.get("orthography", "ch") == "ch" else text

def _in(text, sent):
    s = re.sub(r"\W+", " ", (sent or "").replace("ß", "ss")).strip().lower()[:40]
    return bool(s) and len(s) > 12 and s in re.sub(r"\W+", " ", text.replace("ß", "ss")).lower()

BANNED_ALL = [r"richtet sich an", r"für alle, die", r"for everyone who", r"#Freelance", r"\bInfineon\b", r"\bLeica\b", r"\bSiemens\b", r"\bReiser\b",
              r"\bClaude\b", r"\bChatGPT\b", r"KI-generiert", r"AI-generated", r"\bMBit\b"]
BANNED_PERSONAL = [r"AlpiType", r"alpitype\.", r"\bFreelanc", r"freiberuflich", r"Festanstellung", r"Jobsuche"]

def check(text, channel, signals=None):
    v = [p for p in BANNED_ALL if re.search(p, text, re.I)]
    if channel == "personal": v += [p for p in BANNED_PERSONAL if re.search(p, text, re.I)]
    if channel == "personal" and signals is not None:
        if not _in(text, (signals or {}).get("lead")): v.append("no leadership signal (a sentence where he leads, decides, coordinates or sets up a practice; quote it verbatim in signals.lead)")
        if not _in(text, (signals or {}).get("ai")): v.append("no AI signal (a sentence with his own agent practice or position on AI in software work; quote it verbatim in signals.ai)")
    if not text.strip().rstrip("#").strip(): v.append("empty")
    body = re.sub(r"(\s*#\w+)+\s*$", "", text.strip())
    if "?" not in body[-220:]: v.append("no question at the end")
    n = len(body)
    if n < 500: v.append(f"too short ({n} chars)")
    if n > 2200: v.append(f"too long ({n} chars)")
    return v

if __name__ == "__main__":
    import sys; print(check(open(sys.argv[1], encoding="utf-8").read(), sys.argv[2] if len(sys.argv) > 2 else "personal"))
