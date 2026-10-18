title: LinkedIn content system — technical overview
subtitle: Architecture, runtime, token budget and model choice · 18.10.2026 · companion to the OpenSpec changes
footer: AlpiType · Interner Plan · System overview · 18.10.2026

<style>table{page-break-inside:auto} tr{page-break-inside:avoid} svg{max-width:100%;height:auto;display:block;margin:6px 0 10px} .fig{font-size:9pt;color:#5a6b7a;margin:-4px 0 12px}</style>

## 1. Where this document belongs

OpenSpec holds behaviour (specs) and per-change design notes. It has no slot for the picture of the whole system, so that picture lives here, in `docs/system-overview.md` of the system repo, and the OpenSpec config points to it. Specs say what the system does; this document says what runs where, what it costs in tokens, and which model does which job.

## 2. Components and where they run

<div class="figwrap">
<svg viewBox="0 0 1000 470" xmlns="http://www.w3.org/2000/svg" font-family="-apple-system, Helvetica, Arial, sans-serif" font-size="12">
<defs><marker id="k" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#0f3a50"/></marker></defs>
<g stroke="#d6e2ea" fill="#f2f9fb"><rect x="10" y="10" width="200" height="200" rx="8"/><rect x="240" y="10" width="240" height="200" rx="8"/><rect x="510" y="10" width="480" height="300" rx="8"/><rect x="10" y="240" width="470" height="70" rx="8"/><rect x="10" y="330" width="980" height="130" rx="8"/></g>
<g fill="#0f3a50" font-weight="700" font-size="13"><text x="20" y="30">PHONE / MAC BROWSER</text><text x="250" y="30">BOARD (hosted page)</text><text x="520" y="30">MAC (nightly + slot jobs, launchd)</text><text x="20" y="260">CLOUD ROUTINE</text><text x="20" y="350">EXTERNAL</text></g>
<g stroke="#0f3a50" stroke-width="1.5" fill="#fff">
<rect x="20" y="45" width="180" height="60" rx="6"/><rect x="20" y="115" width="180" height="60" rx="6"/>
<rect x="250" y="45" width="220" height="60" rx="6"/><rect x="250" y="115" width="220" height="60" rx="6"/>
<rect x="520" y="45" width="140" height="60" rx="6"/><rect x="670" y="45" width="150" height="60" rx="6"/><rect x="830" y="45" width="150" height="60" rx="6"/>
<rect x="520" y="115" width="140" height="60" rx="6"/><rect x="670" y="115" width="150" height="60" rx="6"/><rect x="830" y="115" width="150" height="60" rx="6"/>
<rect x="520" y="185" width="140" height="60" rx="6"/><rect x="670" y="185" width="150" height="60" rx="6"/><rect x="830" y="185" width="150" height="60" rx="6"/>
<rect x="520" y="255" width="460" height="45" rx="6" fill="#BEF7FF"/>
<rect x="20" y="270" width="450" height="30" rx="6"/>
<rect x="20" y="365" width="180" height="80" rx="6"/><rect x="215" y="365" width="180" height="80" rx="6"/><rect x="410" y="365" width="180" height="80" rx="6"/><rect x="605" y="365" width="180" height="80" rx="6"/><rect x="800" y="365" width="180" height="80" rx="6"/>
</g>
<g fill="#1f2d3a" text-anchor="middle">
<text x="110" y="68" font-weight="600">Board UI</text><text x="110" y="86">home-screen web app</text><text x="110" y="100" fill="#5a6b7a" font-size="11">approve · comments · photos · record</text>
<text x="110" y="138" font-weight="600">LinkedIn app / site</text><text x="110" y="156">Anton posts, comments,</text><text x="110" y="170" fill="#5a6b7a" font-size="11">messages himself</text>
<text x="360" y="68" font-weight="600">Shared state</text><text x="360" y="86">decisions per day, settings</text><text x="360" y="100" fill="#5a6b7a" font-size="11">read by the Mac every night and at slots</text>
<text x="360" y="138" font-weight="600">File store</text><text x="360" y="156">photos, audio, rendered cards</text><text x="360" y="170" fill="#5a6b7a" font-size="11">working copies, compressed</text>
<text x="590" y="68" font-weight="600">board_sync</text><text x="590" y="86">state + files → library</text><text x="590" y="100" fill="#5a6b7a" font-size="11">02:00, Python, 0 tokens</text>
<text x="745" y="68" font-weight="600">photo_index</text><text x="745" y="86">EXIF, shoots, face crop</text><text x="745" y="100" fill="#5a6b7a" font-size="11">OpenCV, 0 tokens; tags: Haiku</text>
<text x="905" y="68" font-weight="600">transcribe</text><text x="905" y="86">memos → text</text><text x="905" y="100" fill="#5a6b7a" font-size="11">local Whisper, 0 tokens</text>
<text x="590" y="138" font-weight="600">gen_week</text><text x="590" y="156">topics, drafts, images</text><text x="590" y="170" fill="#5a6b7a" font-size="11">Sat 06:00; Opus for text</text>
<text x="745" y="138" font-weight="600">rules_check</text><text x="745" y="156">banned patterns, clients</text><text x="745" y="170" fill="#5a6b7a" font-size="11">regex + one Haiku pass</text>
<text x="905" y="138" font-weight="600">queue_build</text><text x="905" y="156">signals → cards</text><text x="905" y="170" fill="#5a6b7a" font-size="11">06:30; Haiku triage, Opus draft</text>
<text x="590" y="208" font-weight="600">publish</text><text x="590" y="226">approved → LinkedIn API</text><text x="590" y="240" fill="#5a6b7a" font-size="11">at slots, 0 tokens</text>
<text x="745" y="208" font-weight="600">metrics</text><text x="745" y="226">XLSX → posts-log, ranking</text><text x="745" y="240" fill="#5a6b7a" font-size="11">Python, 0 tokens; report: Opus</text>
<text x="905" y="208" font-weight="600">expire / rotate</text><text x="905" y="226">queue expiry, photo reuse</text><text x="905" y="240" fill="#5a6b7a" font-size="11">Python, 0 tokens</text>
<text x="750" y="282" font-weight="600" font-size="11">Library on disk: photos · memos · drafts · published · index.csv each</text>
<text x="245" y="290" font-size="11">Monday brief: web research → one page into the repo · Sonnet · no Mac needed</text>
<text x="110" y="388" font-weight="600">LinkedIn API</text><text x="110" y="406">posting scopes only</text><text x="110" y="424" fill="#5a6b7a" font-size="11">token by path, expiry tracked</text>
<text x="305" y="388" font-weight="600">Mailbox (read only)</text><text x="305" y="406">LinkedIn notification mails</text><text x="305" y="424" fill="#5a6b7a" font-size="11">cheapest signal source, 0 tokens</text>
<text x="500" y="388" font-weight="600">Anton's Chrome</text><text x="500" y="406">watch-list profiles, read only</text><text x="500" y="424" fill="#5a6b7a" font-size="11">only for people without mail signal</text>
<text x="695" y="388" font-weight="600">Web search</text><text x="695" y="406">public post URLs, brief</text><text x="695" y="424" fill="#5a6b7a" font-size="11">no login, no scraping tool</text>
<text x="890" y="388" font-weight="600">Model APIs</text><text x="890" y="406">Opus · Sonnet · Haiku</text><text x="890" y="424" fill="#5a6b7a" font-size="11">+ one non-Claude model in the test</text>
</g>
<g stroke="#0f3a50" stroke-width="1.5" fill="none" marker-end="url(#k)"><path d="M200,75 L250,75"/><path d="M470,75 L520,75"/><path d="M470,145 L520,145"/><path d="M200,145 L110,145" stroke-dasharray="4 3"/><path d="M590,245 L590,255"/></g>
</svg>
</div>
<p class="fig">Figure 1 — Components. Everything that costs tokens is named with its model; everything else is plain Python at zero tokens.</p>

**Why the Mac and not the cloud for most jobs.** The library, the photos, the memos and the campaign CSVs are on the Mac and never in git. Cloud routines see only the repo. So the Mac runs the jobs that touch content; the cloud runs the one job that only needs the web (the Monday brief). The Mac must be on at 02:00 and at the four slots; if it sleeps, the job runs at next wake and the card says "late".

## 3. Vertical slices, in build order

Your point stands: the specs are organised by capability (horizontal). The build is organised vertically, one thin end-to-end slice at a time, each usable on its own.

| Slice | End to end | Done |
|---|---|---|
| 1 · One post | Existing draft text → card on the board → Post → Copy text / Save image → you post → logged in posts-log | Mon 19.10. |
| 2 · Comments | Mail signals + 3 watched profiles → 4 cards → Open / Copy / Skip with reasons → expiry → log | Tue 20.10. |
| 3 · Photos | Add photo on the phone → index → crop → proposed on a card → used marking | Tue 20.10. |
| 4 · Memo to post | Record → transcribe → Friday draft → card | Fri 23.10. |
| 5 · Unattended week | gen_week runs Saturday, four cards without a prompt; metrics import Monday | Sat 25.10. |
| 6 · API publishing | Approved card publishes at slot; token expiry warning | Fri 06.11. |

## 4. Token budget — where tokens go, and where they do not

Assumptions: 4 posts and 2 redrafts a week; 25 comment candidates a day, 5 drafted; 10 photos a week; one brief a week; one ranking report a month. Stable context (CV v2, company context, rules, last 10 posts) is about 10k tokens and is cached, so each call pays it at the cache-read rate. Prices are Anthropic list prices as of October 2026 (Opus 5.5: $4 in / $20 out per million, cache read $0.20; Sonnet 5.5: $2 / $10; Haiku 5.5: $0.10 / $0.50).

| Job | Calls / month | Tokens per call (in cached · in new · out) | Model | Cost / month |
|---|---|---|---|---|
| Post drafting + redrafts | 26 | 10k · 3k · 2.5k | Opus 5.5 | ≈ $1.70 |
| Topic ranking (weekly) | 4 | 10k · 15k · 2k | Opus 5.5 | ≈ $0.40 |
| Comment triage (qualify candidates) | 22 days × 25 | 1k · 1.5k · 0.1k | Haiku 5.5 | ≈ $0.10 |
| Comment drafting | 22 × 5 | 6k · 2k · 0.4k | Opus 5.5 | ≈ $1.90 |
| Photo tags (vision) | 40 | 0 · 1.5k · 0.2k | Haiku 5.5 | ≈ $0.01 |
| Rules check (one model pass) | 30 | 2k · 1.5k · 0.2k | Haiku 5.5 | ≈ $0.01 |
| Monday brief (agentic web research) | 4 | ≈ 300k total per run | Sonnet 5.5 | ≈ $3–5 |
| Monthly ranking report | 1 | 10k · 30k · 4k | Opus 5.5 | ≈ $0.20 |
| Transcription, photo index, sync, publish, metrics, expiry | daily | 0 | local Python | $0 |
| **Running total** | | **≈ 2.5–3 M tokens a month, mostly cached or Haiku** | | **≈ $8–10 a month** |

Two things dominate and neither is in the table: **browser reading** and **the build**.

- **Browser reading of LinkedIn in a Claude Code session** costs roughly 5–10k tokens per profile page plus the session overhead of 20–30k tokens per turn. Ten profiles a day that way is 300–500k tokens a day, 7–10 M a month, on the subscription quota. That is why the design reads **LinkedIn notification mails first** (zero tokens, read-only via the mailbox you already allow) and opens the browser only for the few people who send no mail signal. To be verified on your account on Monday: LinkedIn's bell on a profile plus the "posts from people you follow" mail setting.
- **The build itself** (two weeks of Claude Code sessions) will use tens of millions of tokens on the subscription. That is one-off and is the price of the system, not of running it.

## 5. Which model for what — and a test instead of an opinion

| Job | Choice | Why |
|---|---|---|
| German post text, comments | **Blind test first.** Three models on the same three memos and the same rules: Claude Opus 5.5, the current GPT-5 generation, the current Gemini 3 generation; Mistral Large as a fourth if you want a European option. You rate six texts without names. | No benchmark covers German LinkedIn prose; vendor rankings disagree and none is German. The test costs an afternoon and under a dollar, and it is itself a "model tested on our tasks" post. |
| Qualifying candidates, tagging photos, rules pass | Haiku 5.5 | Classification at a tenth of a cent per call; quality difference is irrelevant for yes/no. |
| Monday brief | Sonnet 5.5 | Agentic search with many tool calls; Opus would double the cost for little gain on a one-page brief. |
| Monthly report, topic ranking | Opus 5.5 | One call a week or month, judgement matters, cost is cents. |
| Anything in a Claude Code session (build, debug, browser) | Whatever the session runs; keep sessions for building, not for operating | Session overhead per turn is larger than most of the calls above combined. |

**Claude Code headless (`claude -p`) as the engine?** It works and is allowed on a subscription: a prompt file in, JSON out, model chosen per call, `--max-turns 1` as a guard. Two facts to weigh. First, every call carries Claude Code's own system prompt and tool list, roughly 20–30k tokens, where the SDK call above carries 3–13k; for thirty calls a day that is the difference between about 1 M and about 0.3 M tokens a day. Second, whether `claude -p` draws from your normal plan limit or from a separate monthly pool was announced for June 2026 and then reported paused; check Settings → Usage before relying on it. Recommendation: the SDK for every scheduled job (cheap, cacheable, measurable per call via `usage`), `claude -p` only for a job that needs Claude Code's tools, and interactive sessions for building. If the blind test picks a non-Claude model for post text, that job calls that vendor's SDK and the rest stays as is.

## 6. Data at rest

| Data | Where | In git? |
|---|---|---|
| Specs, code, config, index files | system repo | yes |
| Photos (originals) | phone | no |
| Photos (working copies), audio, rendered cards | board file store | no |
| Library: photos, memos, drafts, published | Mac, `library/` | no (index files only) |
| content-plan.csv, posts-log.csv | campaign repo | yes (text only) |
| LinkedIn token, Graph credentials | by path in the existing secrets file | never |
| Comment log, skip reasons, weekly answers | `library/log/` | no |

## 7. Open checks before the build starts

1. Board hosting with shared state and file upload from the phone — verified on build day; the alternative is a small page on the Mac exposed only through the running session.
2. LinkedIn notification mails per watched person — verified in your account settings on Monday.
3. `claude -p` quota behaviour — read from Settings → Usage, not from blogs.
4. Blind model test for German text — Tuesday, three memos, six texts, your blind rating.
