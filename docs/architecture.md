title: LinkedIn system — architecture on one page
subtitle: Data flow, storage, feedback, tokens · state 19.10.2026 evening · measured, not estimated
footer: AlpiType · Intern · Architecture · 19.10.2026

<style>table{page-break-inside:auto} tr{page-break-inside:avoid} svg{max-width:100%;height:auto;display:block;margin:4px 0 8px} td,th{font-size:9pt} h2{margin-top:14px}</style>

## 1. Data flow (what runs where)

<div class="figwrap">
<svg viewBox="0 0 1000 400" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, Helvetica, Arial, sans-serif" font-size="12">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#0f3a50"/></marker></defs>
<g stroke="#d6e2ea" fill="#f2f9fb"><rect x="10" y="10" width="220" height="380" rx="8"/><rect x="260" y="10" width="300" height="380" rx="8"/><rect x="590" y="10" width="400" height="380" rx="8"/></g>
<g fill="#0f3a50" font-weight="700" font-size="13"><text x="20" y="30">PHONE or MAC BROWSER</text><text x="270" y="30">SERVER alpitype.com (PHP)</text><text x="600" y="30">MAC, launchd every 10 min</text></g>
<g fill="#5a6b7a" font-size="11"><text x="20" y="46">nothing installed, nothing stored</text><text x="270" y="46">/board/&lt;secret&gt;/ · data/ not readable from web</text><text x="600" y="46">python, whisper.cpp, OpenCV · zero tokens</text></g>
<g stroke="#0f3a50" stroke-width="1.5" fill="#fff">
<rect x="20" y="60" width="200" height="54" rx="6"/><rect x="20" y="124" width="200" height="54" rx="6"/><rect x="20" y="188" width="200" height="54" rx="6"/><rect x="20" y="252" width="200" height="54" rx="6"/>
<rect x="270" y="60" width="280" height="54" rx="6"/><rect x="270" y="124" width="280" height="54" rx="6"/><rect x="270" y="188" width="280" height="54" rx="6"/><rect x="270" y="252" width="280" height="54" rx="6"/>
<rect x="600" y="60" width="380" height="54" rx="6" fill="#BEF7FF"/><rect x="600" y="124" width="180" height="54" rx="6"/><rect x="790" y="124" width="190" height="54" rx="6"/><rect x="600" y="188" width="180" height="54" rx="6"/><rect x="790" y="188" width="190" height="54" rx="6"/><rect x="600" y="252" width="380" height="54" rx="6"/>
<rect x="20" y="326" width="530" height="54" rx="6" stroke-dasharray="4 3"/><rect x="600" y="326" width="380" height="54" rx="6" stroke-dasharray="4 3"/>
</g>
<g fill="#1f2d3a" text-anchor="middle">
<text x="120" y="82" font-weight="600">Board page</text><text x="120" y="98" font-size="11">Post · Comments · Photos · Record</text>
<text x="120" y="146" font-weight="600">Decision press</text><text x="120" y="162" font-size="11">Post as is / Post with changes / Skip</text>
<text x="120" y="210" font-weight="600">Add photo</text><text x="120" y="226" font-size="11">camera roll, original stays on phone</text>
<text x="120" y="274" font-weight="600">Record</text><text x="120" y="290" font-size="11">MediaRecorder, m4a</text>
<text x="410" y="82" font-weight="600">cards.json · pipeline.json · photos.json</text><text x="410" y="98" font-size="11">read only, written by the Mac</text>
<text x="410" y="146" font-weight="600">decisions/YYYY-MM-DD.jsonl</text><text x="410" y="162" font-size="11">append only + overlay.json for instant UI</text>
<text x="410" y="210" font-weight="600">uploads/photos/</text><text x="410" y="226" font-size="11">waits ≤10 min, then moved off</text>
<text x="410" y="274" font-weight="600">uploads/memos/</text><text x="410" y="290" font-size="11">waits ≤10 min, then moved off</text>
<text x="790" y="82" font-weight="600">apply_decisions → content-plan.csv · posts-log.csv</text><text x="790" y="98" font-size="11">the truth; status, reason, URL; git in ~/dev/campaign</text>
<text x="690" y="146" font-weight="600">cards.py</text><text x="690" y="162" font-size="11">CSV → cards, pipeline, material</text>
<text x="885" y="146" font-weight="600">photo_index.py</text><text x="885" y="162" font-size="11">Downloads scan, tags, 90-day reuse, pick</text>
<text x="690" y="210" font-weight="600">transcribe.py</text><text x="690" y="226" font-size="11">whisper.cpp, 1–20 s, local</text>
<text x="885" y="210" font-weight="600">library/</text><text x="885" y="226" font-size="11">photos · memos · drafts · log</text>
<text x="790" y="274" font-weight="600">draft.py · redraft.py · inventory.py · llm.py</text><text x="790" y="290" font-size="11">fill every slot 14 days ahead (Opus) · apply notes · tags (Haiku)</text>
<text x="285" y="348" font-weight="600">LinkedIn</text><text x="285" y="364" font-size="11">today: Copy text + Save image, post or schedule by hand · from 06.11.: API</text>
<text x="790" y="348" font-weight="600">Signals for the comment queue (slice 2)</text><text x="790" y="364" font-size="11">local browser script on the watch list, once a day, zero tokens</text>
</g>
<g stroke="#0f3a50" stroke-width="1.5" fill="none" marker-end="url(#a)">
<path d="M270 87 L222 87"/><path d="M220 151 L268 151"/><path d="M220 215 L268 215"/><path d="M220 279 L268 279"/>
<path d="M552 151 L598 151"/><path d="M552 215 L598 215"/><path d="M552 279 L598 279"/><path d="M598 87 L552 87"/>
</g>
<g fill="#0f3a50" font-size="10" text-anchor="middle"><text x="575" y="80">push</text><text x="575" y="144">pull</text><text x="575" y="208">pull</text><text x="575" y="272">pull</text><text x="245" y="80">GET</text><text x="245" y="144">POST</text><text x="245" y="208">POST</text><text x="245" y="272">POST</text></g>
</svg>
</div>

## 2. Where things live

| What | Lives on | Copy on the server | In git |
|---|---|---|---|
| Post texts and graphics | `library/drafts/<id>.txt/.json/.png` (new drafts, versions `.v1.txt`), `library/published/` (everything posted so far, copied 19.10.) | web copy of the current cards only | texts yes, images no |
| Topic inventory | `library/inventory.csv` (39 topics, status unused/drafted/published) | counts in pipeline.json | yes |
| Status, slot, reasons, numbers | `content-plan.csv`, `posts-log.csv` in `~/dev/campaign` | cards.json, pipeline.json (derived, read only) | yes |
| Photos | originals on the phone or in `~/Downloads`; copy in `library/photos/shoots/`, square crop in `square/`, `index.csv` with scene, tags, used_at | 400 px thumbnails of available photos | index only, never media |
| Voice memos | `library/memos/<ts>.m4a` + `.txt` transcript + `index.csv` | nothing after the next pull | index only |
| Every press on the board | `decisions/*.jsonl` on the server, folded into `library/log/*.csv` | stays (small, append only) | log CSVs yes |
| Secrets | board token `config.local.token`; Graph creds in alpi_marketer; LinkedIn token later | none | never |

## 3. How your feedback is applied

1. A press writes one JSON line on the server and an overlay entry, so the page shows the new state at once.
2. Within 10 minutes the Mac pulls the line and writes it into `content-plan.csv` (status approved / change / skipped / posted, the reason or note in front of the row's notes) and into `posts-log.csv` (posted date, URL). `applied.json` tells the server which overlay entries are now folded in.
3. **Post with these changes:** `redraft.py` reads the note, rewrites the text with it (Opus, the current text and your note, nothing else), swaps the photo when the note says so ("anderes Foto" → next ranked photo), keeps the old text as `<id>.v1.txt`, runs the rules gate and sets the row to **approved**. The card shows "updated per your note · posts <slot>". You do not come back; you can still Skip it until the slot.
4. **Skip:** the slot opens again; `draft.py` fills it with the next topic in the same run. The reason ("not the topic" / "not the form") is stored with the row and in `library/log/post-decisions.csv`; the drafting prompt gets the last reasons as rules (next step).
5. `cards.py` rebuilds the cards from the CSV, so the board and the CSV never disagree for more than one cycle.
6. "Don't use these" on a shoot goes into `photos/index.csv` (status hold); the shoot disappears from the available list at once and is never picked.

## 3a. How a slot gets its post

`draft.py` runs in every sync. For each weekday slot in the next 14 days without a post (max 3 personal + 1 company per week, posts you scheduled yourself count): pillar = the one least used in the surrounding 14 days that still has material (a fresh voice memo comes first) → topic = strongest unused row of `library/inventory.csv` → photo = `photo_index.pick()` (never used before re-used, taken within 24 months before older, newest first, solo photos first, never the shoot of the post before or after, 90 days until a used photo is free again) or, for company posts, a 1200×1200 graphic from `pipeline/templates/company-card.html` rendered by headless Chrome → one text from Opus with the CV (personal) or the company context (company) as the only facts and three recent posts as voice → `rules_check.py` (banned patterns, question at the end, length) → `library/drafts/` + a content-plan row with status draft. 19.10.: 5 drafts in about 9 minutes.

## 4. Tokens: measured today, and the decision

`claude -p` works from a script on your subscription for all three models. Measured 19.10., one comment draft (a realistic 180-word prompt), Mac, no session open:

| Model | Wall time | Context per call | Output | List price per call | Quality of the draft |
|---|---|---|---|---|---|
| Haiku 5.5 | 2.5 s | 22k (11k cached) | 4 | $0.002 | n/a (trivial prompt) |
| Sonnet 5.5 | 4.5 s | 22k (15k cached) | 182 | $0.030 | usable, specific question at the end |
| Opus 5.5 | 10.5 s | 24k (all cached) | 430 incl. 263 thinking | $0.013 | better: names the process, not the model |

The 22k context is the Claude Code system prompt and tool list that `claude -p` always carries; the job itself is 300 tokens. It is almost entirely cache reads, which is why Opus is cheaper than Sonnet here. On the subscription this counts against the 5-hour usage window, not against money.

**Built 19.10. and measured with real jobs** (`library/log/llm-calls.csv` logs every call):

| Step | Model | Calls 19.10. | Per call | Cost 19.10. |
|---|---|---|---|---|
| Photo tags (scene, tags, who) | Haiku 5.5, image | 44 | 4.7 s, $0.002 | $0.08 |
| Topic inventory (CV + context → 39 topics) | Opus 5.5 | 1 | 96 s, $0.34 | $0.34 |
| Post draft (CV or context + 3 examples → text) | Opus 5.5 | 5 | ≈ 100 s, ≈ $0.15 | ≈ $0.75 |

Text-only steps run with the tool list switched off, so the context is the job itself (5k), not the 22k of the Claude Code system prompt. **Monthly:** 16 drafts + ≈ 8 redrafts (Opus, ≈ $3.50), tags for new photos (cents), comment drafts later ≈ 100 (Sonnet, ≈ $3). At list prices through the API: **$6–8 per month**; through `claude -p`: **0 € extra**. Which model runs which step is `config.yaml` (`llm.models`), the backend too (`llm.backend: claude-p | api`).

**Decision for you, with my recommendation:** stay with `claude -p` on the subscription; it is what runs now. The API key becomes the backend only if the quota collides with your own sessions or the volume grows tenfold. That is a config line, not a second path in the code.

**Dropped:** the LinkedIn notification-mail idea. You do not need to care about it. The queue's signal source will be a local browser script reading the watch list in your own logged-in Chrome profile, once a day, zero tokens; the model only drafts. You log in to LinkedIn in that Chrome profile once.
