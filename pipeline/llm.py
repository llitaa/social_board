"""One function for every model call: llm(step, prompt, ...). Backend = `claude -p` on the subscription (default)
or the API (config llm.backend: api, needs ANTHROPIC_API_KEY). Which model runs which step is config, not code.
Every call is logged to library/log/llm-calls.csv with tokens and cost, so the monthly bill is a one-liner."""
import csv, json, os, re, subprocess, time
from datetime import datetime
from common import CFG, LIB, log

L = CFG.get("llm", {})
MODELS = {"draft": "claude-opus-5-5", "redraft": "claude-opus-5-5", "inventory": "claude-opus-5-5",
          "tags": "claude-haiku-5-5", "comment": "claude-sonnet-5-5", "learn": "claude-sonnet-5-5"} | L.get("models", {})
CALLS = os.path.join(LIB, "log", "llm-calls.csv")

def claude_bin():
    """The claude CLI: config llm.claude, else PATH, else the usual install places (launchd/cron have a short PATH)."""
    import glob, shutil
    c = os.path.expanduser(L.get("claude", "")) or shutil.which("claude")
    if c and os.path.isfile(c): return c
    for pat in ("~/.claude/local/claude", "~/.local/bin/claude", "/opt/homebrew/bin/claude", "/usr/local/bin/claude", "~/.nvm/versions/node/*/bin/claude"):
        for f in sorted(glob.glob(os.path.expanduser(pat)), reverse=True):
            if os.path.isfile(f): return f
    raise RuntimeError("claude CLI not found: set llm.claude in config.yaml (docs/worker.md)")

def _log(step, model, ms, u, cost, ok):
    os.makedirs(os.path.dirname(CALLS), exist_ok=True); new = not os.path.isfile(CALLS)
    with open(CALLS, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new: w.writerow(["ts", "step", "model", "ms", "input", "cache_read", "cache_create", "output", "cost_usd", "ok"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), step, model, ms, u.get("input_tokens", 0), u.get("cache_read_input_tokens", 0),
                    u.get("cache_creation_input_tokens", 0), u.get("output_tokens", 0), f"{cost:.4f}", "yes" if ok else "no"])

def llm(step, prompt, system=None, files=False, model=None, timeout=300):
    """Returns the model's text. files=True lets the model Read files named in the prompt (images, documents)."""
    model = model or MODELS.get(step, MODELS["draft"])
    if L.get("backend", "claude-p") == "api": return _api(step, prompt, system, model)
    cmd = [claude_bin(), "-p", "--model", model, "--output-format", "json", "--no-session-persistence", "--disable-slash-commands"]
    cmd += ["--allowedTools", "Read", "--max-turns", "6"] if files else ["--tools", "", "--max-turns", "1"]
    if system: cmd += ["--system-prompt", system]
    t = time.time()
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
    ms = int((time.time() - t) * 1000)
    try: d = json.loads(r.stdout)
    except json.JSONDecodeError: _log(step, model, ms, {}, 0, False); raise RuntimeError(f"claude -p failed: {r.stderr[-300:]} {r.stdout[-300:]}")
    _log(step, model, ms, d.get("usage", {}), float(d.get("total_cost_usd") or 0), not d.get("is_error"))
    if d.get("is_error"): raise RuntimeError(d.get("result", "")[:300])
    return d.get("result", "")

def _api(step, prompt, system, model):
    import anthropic
    t = time.time(); c = anthropic.Anthropic()
    m = c.messages.create(model=model, max_tokens=4000, system=system or anthropic.NOT_GIVEN, messages=[{"role": "user", "content": prompt}])
    u = m.usage; _log(step, model, int((time.time() - t) * 1000), {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens}, 0, True)
    return "".join(b.text for b in m.content if b.type == "text")

def llm_json(step, prompt, **kw):
    """Same, but the answer must be one JSON object; fences and prose around it are tolerated."""
    out = llm(step, prompt, **kw)
    m = re.search(r"\{.*\}", out, re.S)
    if not m: raise RuntimeError("no JSON in answer: " + out[:200])
    return json.loads(m.group(0))

if __name__ == "__main__":
    import sys; print(llm(sys.argv[1] if len(sys.argv) > 1 else "tags", sys.stdin.read()))
