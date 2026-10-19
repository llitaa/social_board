#!/usr/bin/env python3
"""The system learns from Anton's notes. Every note on a card, every text he edited on the card and every skip reason
is read once; a small model decides whether it carries a preference that holds for future posts (not a one-off fix)
and states it in one line. Those lines live in library/style-rules.txt and go into every draft and redraft prompt.
Cost: one Sonnet call per note, about a cent. Lines Anton does not want can be deleted from the file by hand."""
import json, os
from datetime import datetime
from common import LIB, BOARD_LOCAL, read_csv, jload, jdump, resolve, log
from llm import llm_json

RULES = os.path.join(LIB, "style-rules.txt"); STATE = os.path.join(LIB, "log", ".learned.json")
DEC = os.path.join(LIB, "log", "post-decisions.csv")

def rules():
    return [l.rstrip("\n") for l in open(RULES, encoding="utf-8") if l.strip() and not l.startswith("#")] if os.path.isfile(RULES) else []

def previous_text(cid):
    """The text before the edit/note, from the latest version file of the draft."""
    for c in jload(os.path.join(BOARD_LOCAL, "cards.json"), []):
        if c["id"] == cid: break
    else: return "", ""
    drafts = os.path.join(LIB, "drafts"); vs = sorted(f for f in os.listdir(drafts) if f.startswith(cid + "-") and ".v" in f and f.endswith(".txt")) if os.path.isdir(drafts) else []
    cur = [f for f in os.listdir(drafts) if f.startswith(cid + "-") and f.endswith(".txt") and ".v" not in f] if os.path.isdir(drafts) else []
    old = open(os.path.join(drafts, vs[-1]), encoding="utf-8").read().strip() if vs else ""
    new = open(os.path.join(drafts, cur[0]), encoding="utf-8").read().strip() if cur else c.get("text", "")
    return old, new

def main():
    rows, _ = read_csv(DEC); st = jload(STATE, {"done": 0}); n = 0; have = rules()
    for d in rows[st["done"]:]:
        what = ""
        if d["decision"] == "change" and d.get("note"): what = f"Anton's note on the post: {d['note']}"
        elif d["decision"] == "skip" and d.get("reason"): what = f"Anton skipped the post with the reason: {d['reason']}"
        elif d.get("edited") == "yes":
            old, new = previous_text(d["card_id"])
            if old and new: what = f"Anton edited the post himself before posting.\nBefore:\n{old}\n\nAfter:\n{new}"
        if not what: continue
        prompt = f"""Anton Lytvynenko reviews LinkedIn post drafts on a board. Below is one of his reactions.
Decide whether it clearly states a preference that should hold for ALL FUTURE posts (tone, structure, words to avoid, kinds of topics or photos),
or whether it fixes only this one post. Default to a one-off: a note about this post's length, facts, wording or photo is a one-off unless
it says so in general terms ("immer", "nie", "generell", "grundsätzlich", "in Zukunft", "always", "never", "from now on") or names a habit of the writer.
Known preferences already recorded:
{chr(10).join('- ' + l.split(chr(9))[-1] for l in have[-40:]) or '- none yet'}

Reaction:
{what}

Answer with one JSON object only: {{"rule": "one imperative line in English for the writer, or an empty string if it is a one-off or already recorded"}}"""
        try:
            r = llm_json("learn", prompt).get("rule", "").strip()
        except Exception as e: log("learn failed", d["card_id"], str(e)[:120]); r = ""
        if r:
            line = f"{datetime.now():%Y-%m-%d}\t{d['card_id']}\t{r}"; have.append(line)
            with open(RULES, "a", encoding="utf-8") as f: f.write(line + "\n")
            n += 1; log("learned:", r)
    st["done"] = len(rows); jdump(STATE, st)
    log(f"learn: {n} new rule(s), {len(have)} total")

if __name__ == "__main__": main()
