"""The gate before the board: Anton's content rules as patterns. Returns a list of violations (empty = pass)."""
import re

BANNED_ALL = [r"richtet sich an", r"für alle, die", r"for everyone who", r"#Freelance", r"\bInfineon\b", r"\bLeica\b", r"\bSiemens\b", r"\bReiser\b",
              r"\bClaude\b", r"\bChatGPT\b", r"KI-generiert", r"AI-generated", r"\bMBit\b"]
BANNED_PERSONAL = [r"AlpiType", r"alpitype\.", r"\bFreelanc", r"freiberuflich", r"Festanstellung", r"Jobsuche"]

def check(text, channel):
    v = [p for p in BANNED_ALL if re.search(p, text, re.I)]
    if channel == "personal": v += [p for p in BANNED_PERSONAL if re.search(p, text, re.I)]
    if not text.strip().rstrip("#").strip(): v.append("empty")
    body = re.sub(r"(\s*#\w+)+\s*$", "", text.strip())
    if "?" not in body[-220:]: v.append("no question at the end")
    n = len(body)
    if n < 500: v.append(f"too short ({n} chars)")
    if n > 2200: v.append(f"too long ({n} chars)")
    return v

if __name__ == "__main__":
    import sys; print(check(open(sys.argv[1], encoding="utf-8").read(), sys.argv[2] if len(sys.argv) > 2 else "personal"))
