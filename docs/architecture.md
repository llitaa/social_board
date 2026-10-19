title: LinkedIn system — architecture on one page
subtitle: Data flow with token plugs, hosting, storage, feedback · state 19.10.2026 · measured, not estimated
footer: AlpiType · Intern · Architecture · 19.10.2026

<style>table{page-break-inside:auto} tr{page-break-inside:avoid} svg{max-width:100%;height:auto;display:block;margin:4px 0 8px} td,th{font-size:9pt} h2{margin-top:14px}</style>

## 1. Data flow (what runs where, and where tokens are spent)

Everything is local and free except the four orange boxes. Grey = your devices and the server, blue = the Mac jobs.

<div class="figwrap">
<svg viewBox="0 0 1000 470" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, Helvetica, Arial, sans-serif" font-size="12">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#0f3a50"/></marker></defs>
<g stroke="#d6e2ea" fill="#f8fafb"><rect x="10" y="10" width="190" height="450" rx="8"/><rect x="220" y="10" width="200" height="450" rx="8"/></g>
<rect x="440" y="10" width="550" height="450" rx="8" stroke="#d6e2ea" fill="#f2f9fb"/>
<g fill="#0f3a50" font-weight="700" font-size="13"><text x="20" y="30">YOU · phone or Mac browser</text><text x="230" y="30">SERVER · alpitype.de/board/…</text><text x="450" y="30">WORKER (today: the Mac) · watch.py: a press → run.sh fast in ~1 min, full every 10 min</text></g>
<g fill="#5a6b7a" font-size="11"><text x="20" y="46">nothing installed</text><text x="230" y="46">PHP, rsync target, 7 MB</text><text x="450" y="46">any always-on machine: python, ffmpeg+whisper.cpp, OpenCV, Chrome, claude CLI · see docs/worker.md</text></g>
<g stroke="#0f3a50" stroke-width="1.5" fill="#fff">
<rect x="20" y="62" width="170" height="60" rx="6"/><rect x="20" y="134" width="170" height="60" rx="6"/><rect x="20" y="206" width="170" height="60" rx="6"/><rect x="20" y="278" width="170" height="60" rx="6"/>
<rect x="230" y="62" width="180" height="60" rx="6"/><rect x="230" y="134" width="180" height="60" rx="6"/><rect x="230" y="206" width="180" height="60" rx="6"/><rect x="230" y="278" width="180" height="60" rx="6"/>
<rect x="450" y="62" width="255" height="60" rx="6"/><rect x="720" y="62" width="260" height="60" rx="6" fill="#fff3e0" stroke="#e08a00"/>
<rect x="450" y="134" width="255" height="60" rx="6"/><rect x="720" y="134" width="260" height="60" rx="6" fill="#fff3e0" stroke="#e08a00"/>
<rect x="450" y="206" width="255" height="60" rx="6"/><rect x="720" y="206" width="260" height="60" rx="6" fill="#fff3e0" stroke="#e08a00"/>
<rect x="450" y="278" width="255" height="60" rx="6"/><rect x="720" y="278" width="260" height="60" rx="6" fill="#fff3e0" stroke="#e08a00"/>
<rect x="450" y="350" width="530" height="44" rx="6" fill="#BEF7FF"/>
<rect x="20" y="404" width="390" height="44" rx="6" stroke-dasharray="4 3"/><rect x="450" y="404" width="530" height="44" rx="6" stroke-dasharray="4 3"/>
</g>
<g fill="#1f2d3a" text-anchor="middle">
<text x="105" y="84" font-weight="600">Board: the post</text><text x="105" y="100" font-size="11">Post as is · with changes · Skip</text><text x="105" y="114" font-size="11">Copy text · Save image</text>
<text x="105" y="156" font-weight="600">Photos: don't use</text><text x="105" y="172" font-size="11">the only photo decision</text>
<text x="105" y="228" font-weight="600">Record</text><text x="105" y="244" font-size="11">browser microphone → m4a</text>
<text x="105" y="300" font-weight="600">Add photo</text><text x="105" y="316" font-size="11">camera roll, original stays</text>
<text x="320" y="84" font-weight="600">cards · pipeline · photos</text><text x="320" y="100" font-size="11">JSON written by the Mac</text><text x="320" y="114" font-size="11">web copies of card images</text>
<text x="320" y="156" font-weight="600">decisions/*.jsonl</text><text x="320" y="172" font-size="11">every press, append only</text>
<text x="320" y="228" font-weight="600">uploads/memos · photos</text><text x="320" y="244" font-size="11">≤ 10 min, then moved to the worker</text>
<text x="320" y="300" font-weight="600">overlay.json</text><text x="320" y="316" font-size="11">a press shows before the Mac confirms</text>
<text x="577" y="84" font-weight="600">apply_decisions → content-plan.csv</text><text x="577" y="100" font-size="11">approved / change+note / skipped</text><text x="577" y="114" font-size="11">the truth, git in ~/dev/campaign</text>
<text x="850" y="84" font-weight="600" fill="#8a4b00">redraft.py · Opus · ~$0.09</text><text x="850" y="100" font-size="11">note + current text → new text</text><text x="850" y="114" font-size="11">version kept, back to you to Post</text>
<text x="577" y="156" font-weight="600">transcribe.py · whisper.cpp</text><text x="577" y="172" font-size="11">ffmpeg → 16 kHz wav → ggml-small (466 MB)</text><text x="577" y="186" font-size="11">local CPU/GPU, 1–20 s, 0 tokens</text>
<text x="850" y="156" font-weight="600" fill="#8a4b00">draft.py · Opus · ~$0.15 per post</text><text x="850" y="172" font-size="11">slot + pillar + topic + photo scene</text><text x="850" y="186" font-size="11">+ CV or company context → text</text>
<text x="577" y="228" font-weight="600">photo_index.py · OpenCV YuNet</text><text x="577" y="244" font-size="11">EXIF, face, square crop, shoots,</text><text x="577" y="258" font-size="11">90-day reuse, pick() · 0 tokens</text>
<text x="850" y="228" font-weight="600" fill="#8a4b00">tags · Haiku · $0.002 per photo</text><text x="850" y="244" font-size="11">thumbnail → scene, tags, who is in it</text><text x="850" y="258" font-size="11">once per photo</text>
<text x="577" y="300" font-weight="600">cards.py · rules_check.py</text><text x="577" y="316" font-size="11">CSV → cards, pipeline, material</text><text x="577" y="330" font-size="11">banned patterns gate · 0 tokens</text>
<text x="850" y="300" font-weight="600" fill="#8a4b00">inventory.py · Opus · $0.34 once</text><text x="850" y="316" font-size="11">CV + context + published → topics</text><text x="850" y="330" font-size="11">re-run only adds</text>
<text x="715" y="368" font-weight="600">library/ on the Mac</text><text x="715" y="384" font-size="11">photos · memos · drafts (texts, versions, graphics) · published · inventory.csv · log/llm-calls.csv</text>
<text x="215" y="422" font-weight="600">LinkedIn</text><text x="215" y="438" font-size="11">today: Copy text + Save image, you post or schedule · from 06.11.: API</text>
<text x="715" y="422" font-weight="600">not built: comment queue (slice 2)</text><text x="715" y="438" font-size="11">watch list read by a local browser script, 0 tokens · drafts Sonnet ~$0.03 each</text>
</g>
<g stroke="#0f3a50" stroke-width="1.5" fill="none" marker-end="url(#a)">
<path d="M190 100 L228 156"/><path d="M190 164 L228 164"/><path d="M190 236 L228 236"/><path d="M190 308 L228 244"/><path d="M228 84 L192 84"/>
<path d="M410 164 L448 92"/><path d="M410 228 L448 164"/><path d="M410 244 L448 236"/><path d="M448 300 L412 100"/>
<path d="M705 92 L718 92"/><path d="M705 164 L718 164"/><path d="M705 236 L718 236"/>
</g>
<g fill="#5a6b7a" font-size="10" text-anchor="middle"><text x="208" y="78">push</text><text x="208" y="126">press</text><text x="436" y="214">push</text></g>
</svg>
</div>

**Voice memo, step by step:** Record in the browser (MediaRecorder, m4a) → `api.php` stores it under `uploads/memos/` → the next run moves it to the Mac (`library/memos/`) → `ffmpeg` converts to 16 kHz mono wav → `whisper-cli` (whisper.cpp, model ggml-small, 466 MB on disk, runs on the Mac's CPU/GPU) writes the transcript → `library/memos/<ts>.txt` + `index.csv`. No model tokens anywhere in that path; your 4-second test took 1.4 s. Tokens are spent only afterwards, when `draft.py` turns a memo of 15+ words into the next personal post (one Opus call). Memos under 15 words are marked short and ignored.

## 1a. Where compute runs, and why

| Component | Needs | Runs today | Could run on |
|---|---|---|---|
| Board page + API | PHP, a few MB | Hostinger shared hosting (alpitype.de) | stays; it is only a mailbox |
| Memo transcription | ffmpeg, whisper.cpp, 466 MB model, ≈ 1 GB RAM, CPU seconds (1.4 s for your 4 s memo on the M-series; a shared-hosting CPU would need a minute and may be killed; the plan allows no binaries and no long-running processes) | the Mac, 0 tokens | any PC or a VPS (≈ 5 € / month) |
| Photo pool (EXIF, YuNet face crop, shoots, pick) | OpenCV, pillow-heif | the Mac, 0 tokens | any PC |
| Drafts, redrafts, inventory, tags | `claude -p` on the subscription (or API key) | the Mac | any machine logged in to the subscription; a server is simpler with the API key |
| Company graphics | headless Chrome | the Mac | any PC with Chromium |
| Cards, pipeline, health, sync | python, rsync, ssh key | the Mac: `watch.py` polls the board every 15 s, a press starts the fast chain, the full chain runs every 10 min | any PC |
| Learning from your notes | Sonnet, one call per note / edit / skip reason (≈ 1–2 ct) | the Mac | same worker |
| LinkedIn publishing (when the app exists) | python, token file | the Mac at slot time | same worker |

The Mac is one role, "the worker", not an architecture decision: everything in `pipeline/` is plain python and shell, the state is files, and the server never calls the worker. Moving the role to your other PC is a checklist (`docs/worker.md`): clone the two repos, install the table above, copy `library/` and the two `config.local.*` files and the ssh key, run `watch.py` as a service, stop the Mac job. Two workers must never run at once. The AWS machine would add uptime the board does not need; presses wait on the server until the worker's next run, so a PC that sleeps at night is enough.

## 2. Hosting and storage

All nine domains (alpitype.de, alpitype.com, alpitype.ai, alpi-m.de, aux-valley.*, ki-*.de) sit on **one** Hostinger account and one disk; dropping alpitype.com saves the domain fee, not hosting. The board was therefore moved on 19.10. to **alpitype.de/board/<token>/** (beside WordPress; real directories bypass its rewrite, PHP and the CDN pass it as dynamic). alpitype.com now redirects every path to alpitype.de, so the old bookmark lands on the new board.

| | Today | Growth | Rule |
|---|---|---|---|
| Whole account | 1.7 GB (alpitype.de WordPress 687 MB, alpi-m 358 MB, aux-valley.com 303 MB, ki-aktiv 289 MB) | — | plan limit 100 GB (Premium) / 200 GB (Business); check in hPanel once |
| Board | 7 MB | ≈ 10 MB per month if nothing is deleted (one card = web copy 0.3 MB + final 0.3–1.9 MB; a thumbnail 30 KB) | card images are deleted 7 days after the slot; thumbnails only for photos still in the pool; `board_sync push` mirrors with delete; a warning in the log above 200 MB |
| Mac `library/` | 1.1 GB (whisper model 466 MB, pool 43 photos) | ≈ 50 MB per month (photos + memos) | nothing to delete; media never in git |

## 3. Where things live

| What | Lives on | Copy on the server | In git |
|---|---|---|---|
| Post texts and graphics | `library/drafts/<id>.txt/.json/.png` (new drafts, versions `.v1.txt`), `library/published/` (everything posted so far, copied 19.10.) | web copy of the current cards only | texts yes, images no |
| Topic inventory | `library/inventory.csv` (39 topics, status unused/drafted/published) | counts in pipeline.json | yes |
| Status, slot, reasons, numbers | `content-plan.csv`, `posts-log.csv` in `~/dev/campaign` | cards.json, pipeline.json (derived, read only) | yes |
| Photos | originals on the phone or in `~/Downloads`; copy in `library/photos/shoots/`, square crop in `square/`, `index.csv` with scene, tags, used_at | 400 px thumbnails of available photos | index only, never media |
| Voice memos | `library/memos/<ts>.m4a` + `.txt` transcript + `index.csv` | nothing after the next pull | index only |
| Every press on the board | `decisions/*.jsonl` on the server, folded into `library/log/*.csv` | stays (small, append only) | log CSVs yes |
| Secrets | board token `config.local.token`; Graph creds in alpi_marketer; LinkedIn token later | none | never |

## 4. How your feedback is applied

1. A press writes one JSON line on the server and an overlay entry, so the page shows the new state at once.
2. The worker's `watch.py` asks the server for a change stamp every 15 seconds (a few bytes, no model). The stamp moves, the fast chain starts: pull → `apply_decisions.py` writes the line into `content-plan.csv` (status approved / change / skipped / posted, the reason or note in front of the row's notes) and into `posts-log.csv` → learn → redraft → cards → push. Measured 19.10.: a note is back on the board as a new text after 60–70 seconds (15 s poll, 12–25 s Opus, 4 s push); Post or Skip are folded in after about 20 s. `applied.json` tells the server which overlay entries are now in the CSV. The server cannot call the worker (shared hosting, no outbound hook), so polling is the whole trick; the full chain (memos, photos, slot filling) still runs every 10 minutes.
3. **Update the post (a note):** `redraft.py` rewrites the text with the note (Opus: current text, your note, your standing preferences, nothing else), swaps the photo when the note says so ("anderes Foto" → next ranked photo), keeps the old text as `<id>.v1.txt`, runs the rules gate and puts the card **back to you**: "updated per your note · read · edit · Post". You read it while it is still on your screen (the page refreshes every 5 s while a card is being updated), fix a word directly in the text if needed, press Post. A note that fails twice waits for a new decision; the card says so.
3a. **Post with an edit:** the text on a card to decide is editable (tap, type). Post sends what you see; `apply_decisions.py` writes it into the draft file and keeps the previous text as the next `.vN.txt`. No model call.
3b. **The system learns:** `learn.py` reads every note, every edited text (before/after) and every skip reason once and asks Sonnet whether it states a preference for all future posts or fixes only this post (default: one-off). A preference becomes one line in `library/style-rules.txt` (date, card, rule); every draft and redraft prompt carries those lines. The board's system line shows how many were learned; delete a line from the file to forget it. Test 19.10.: "kürzer, maximal 700 Zeichen" became a rule (too eager, prompt tightened), an edit that added one word was correctly left alone.
4. **Skip:** the slot opens again; `draft.py` fills it with the next topic in the next full run. The reason ("not the topic" / "not the form") goes through the same learning step.
4a. **Scheduled in LinkedIn:** a post you scheduled yourself (status scheduled, time in `planned`) becomes posted on the worker once its time has passed; the card leaves the board and the post appears under Published (the Schiff post did on 19.10. 14:47).
5. `cards.py` rebuilds the cards from the CSV, so the board and the CSV never disagree for more than one cycle.
6. "Don't use these" on a shoot goes into `photos/index.csv` (status hold); the shoot disappears from the available list at once and is never picked.

## 4a. How a slot gets its post

`draft.py` runs in every sync. For each weekday slot in the next 14 days without a post (max 3 personal + 1 company per week, posts you scheduled yourself count): pillar = the one least used in the surrounding 14 days that still has material (a fresh voice memo comes first) → topic = strongest unused row of `library/inventory.csv` → photo = `photo_index.pick()` (never used before re-used, taken within 24 months before older, newest first, solo photos first, never the shoot of the post before or after, 90 days until a used photo is free again) or, for company posts, a 1200×1200 graphic from `pipeline/templates/company-card.html` rendered by headless Chrome → one text from Opus with the CV (personal) or the company context (company) as the only facts and three recent posts as voice → `rules_check.py` (banned patterns, question at the end, length) → `library/drafts/` + a content-plan row with status draft. 19.10.: 5 drafts in about 9 minutes.

## 5. Logs and the watchdog

Every run of the chain writes one line per step to `library/log/steps.jsonl` (step, time, seconds, exit code, last log line); full output is in `library/log/board-sync.err`, model calls in `llm-calls.csv`, board presses in `post-decisions.csv` / `board-events.csv`. `health.py` is the agent: after each run it reads those lines plus the content state (posts planned in the next 14 days, stuck notes, unused topics, failed model calls) and writes `health.json` to the server. The board's first line is that report: green "system ok · last run n min ago · 9 posts planned · $1.21 this month", or a red block per problem with the failing step, its last log line and the fix command. The page adds "Mac not seen for n min" from the timestamp itself, so a sleeping Mac shows without any process on the server. Shared hosting cannot run a daemon; this needs none.

**Why transcription runs on the Mac, not the server:** whisper.cpp needs ffmpeg, a 466 MB model, about 1 GB RAM and real CPU time (your 4 s memo took 1.4 s on the M-series chip; on the shared Hostinger CPU it would be a minute and may be killed). The hosting plan allows no long-running processes and no binaries we install. A VPS could do it for about 5 € a month; the Mac does it for nothing, and the Mac runs anyway for the drafts.

## 6. LinkedIn API: what exists, what you have to do once

**Connected 19.10. 15:40** with the existing app "AlpiType Analytics" (scopes openid, profile, w_member_social; token until 18.12., the board warns 7 days before; company page scope waits for LinkedIn's Community Management review). `watch.py` starts the fast chain when an approved card's slot arrives, so a post goes out within about 20 seconds of its slot; a failure stays on the row, the board shows it in red with "post it yourself". `pipeline/linkedin_auth.py` (one-time authorisation in your browser; I never sign in for you) and `pipeline/publish.py` (approved cards → Posts API at the slot, image upload, URL into posts-log, `--dry` to preview) are written and wait for an app: create it at linkedin.com/developers under the AlpiType page, add "Share on LinkedIn" and "Sign In with LinkedIn using OpenID Connect", redirect URL `http://localhost:8765/callback`, put client id and secret into `config.local.linkedin.json`, run the auth script. Personal posts work from that moment. The company page needs the "Community Management API" product, which LinkedIn reviews (days to weeks); until then company cards keep Copy text and Save image.

**What the system knows about your previous posts, honestly:** 22 posts since 30.07. in `posts-log.csv`, numbers for 6 of them (li-post-02 19 reactions, li-post-06 3121 impressions / 16 reactions, li-comp-05 7 / 4, li-comp-06 147 impressions, li-post-01 847, li-post-06-legacy 263); the LinkedIn data export on the Mac (31.07.) has your comments, reactions and 17 media uploads but no posts file. Nothing was read from LinkedIn itself; there is no API read scope and the browser profile is not logged in. `metrics_import.py` now takes LinkedIn's analytics exports (page: Analytics → Content → Export; personal: post → analytics → Export) from `library/metrics/inbox/` into posts-log, matched by date and hook.

## 7. Tokens: measured today, and the decision

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
| Redraft on a note (text + note → text) | Opus 5.5 | 3 | 12–25 s, $0.06–0.09 | $0.23 |
| Learning (note / edit / skip reason → rule or nothing) | Sonnet 5.5 | 3 | 4–9 s, $0.02 | $0.06 |

Text-only steps run with the tool list switched off, so the context is the job itself (5k), not the 22k of the Claude Code system prompt. **Monthly:** 16 drafts + ≈ 8 redrafts (Opus, ≈ $3.50), ≈ 10 learning calls (Sonnet, $0.20), tags for new photos (cents), comment drafts later ≈ 100 (Sonnet, ≈ $3). The 15-second polling costs nothing: it is one HTTP request of 60 bytes, no model. At list prices through the API: **$6–8 per month**; through `claude -p`: **0 € extra**. Which model runs which step is `config.yaml` (`llm.models`), the backend too (`llm.backend: claude-p | api`).

**Decision for you, with my recommendation:** stay with `claude -p` on the subscription; it is what runs now. The API key becomes the backend only if the quota collides with your own sessions or the volume grows tenfold. That is a config line, not a second path in the code.

**Dropped:** the LinkedIn notification-mail idea. You do not need to care about it. The queue's signal source will be a local browser script reading the watch list in your own logged-in Chrome profile, once a day, zero tokens; the model only drafts. You log in to LinkedIn in that Chrome profile once.
