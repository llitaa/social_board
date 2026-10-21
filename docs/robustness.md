# Robustness review, 21.10.2026

Trigger: the 07:30 post on 21.10. did not go out. Two faults stacked: a pull over ssh hung for 4.5 hours and held the run lock,
so nothing ran at 07:30; when the chain ran, LinkedIn answered 426 because the API version in the code was over a year old.
This review looked at the whole system again (own read plus an independent second read of the code).

## What the architecture bug was
Publishing sat at the end of a 15-step chain on a laptop. Any stall anywhere in the chain, or the laptop being asleep,
silently cancelled publishing, and nothing told Anton. The fix is structural: the always-on host publishes approved cards
at their slot by itself (`server/publish.php` in `~/board-worker`, cron every 5 minutes plus a tick from the board page
and from the Mac every minute). The Mac drafts, redrafts, transcribes, learns and folds results; if it is off, posts still
go out, drafts and notes wait.

## Found and fixed today (severity as found)
| # | Finding | Fix |
|---|---|---|
| C | Host cron ran in UTC: a 07:30 slot would have posted at 09:30 | `publish.php` sets Europe/Berlin |
| C | Cards that ever had a voice note, an uploaded image or "Next photo" kept a pending flag forever → the host would never publish them | flags carry their time, expire after 10 min, and any new decision clears them; the host also ignores overlay entries the Mac has already folded |
| C | Posts published by the host never reached `posts-log.csv` → invisible to metrics and Featured | `apply_decisions` creates the posts-log row when none exists |
| C | A crash or reboot during a run left the lock dir → every later run a no-op, for good | `run.sh` removes a lock older than 30 min with no run behind it |
| H | Drag-reorder could hand an approved card a slot in the past → posted at once | the API refuses such an order |
| H | An approved card with a past slot left the board and the host's view (never retried, no issue) | approved rows stay on the board until posted |
| H | Token expiry invisible: both warnings were gated on "connected" | a missing or expired token is itself a board issue; the host writes "token expired" on the card |
| H | A half-written decision line made the per-file counter skip the completed line | the counter stops at the first broken line and re-reads it |
| H | Overlay read-modify-write without a lock (page ticks, cron, taps at once) | one lock around read+write in api.php and publish.php |
| M | Lost answer from LinkedIn after the post was created → second post | an "attempt" marker before the call; no new attempt for 10 min |
| M | A permanent error retried every minute forever | five failures → "needs you" on the card, no further retries |
| M | A topic that can never pass the rules gate cost two Opus calls every 10 minutes | the topic is blocked after the failed attempt |
| M | Post ids could be reused after a plan row was deleted | the drafts folder counts too |
| M | Metrics from the API could never switch on (wrong key name for the granted scopes) | fixed |
| M | Every fast run reported rc=1 (last line of run.sh) → the daemon log was noise | `exit 0` |
| M | Health did not watch the token push, metrics steps | added |
| L | The host held the full token file incl. the client secret | only access token, expiry and URNs are pushed |
| L | Voice memos and decision files were downloadable with the URL | denied in .htaccess |
| L | Memo sidecar written after the audio → a pull in between could split them | sidecar first |
| L | A rejected upload stayed in the inbox and was retried every run | moved to `uploads/rejected/` |
| L | Private logs (decisions with transcripts, feedback) were in the public repo | out of git; the repo must still be set private |

## Still open, by choice or by design
- The LinkedIn token lasts 60 days (until 18.12.2026). Renewal needs a browser login on the Mac (`linkedin_auth.py`);
  the board warns 7 days ahead and the host writes "token expired" on the card. There is no automatic refresh.
- The browser shows slots in the phone's local time; outside Berlin the displayed time shifts (the host posts at Berlin time regardless).
- Whisper phantom sentences are filtered by a list; a new phantom phrase can still slip through once. A spoken note is only
  ever applied to a post as a rewrite that comes back to decide, so the damage is one review.
- Two people deciding on the same card: both presses are logged and applied in order, the later overlay write wins on the
  screen; nothing is lost, nothing warns. The board is built for one person.
- Exactly one worker Mac. A second worker would split the uploads (they are moved, not copied) and write two plans. Multiple
  phones or browsers on the same board are fine.
- The company page cannot publish until LinkedIn grants the Community Management API; `li-comp-12` (approved 19.10.) is
  back on the board as a visible card so it is not posted twice by surprise when the token arrives.

## Limits and scale
- Size: cards.json is about 2 KB per card; 17 cards = 34 KB per state poll. Images on the host: 18 MB, pruned 7 days after
  a slot. Decisions: one small file per day. Overlay: about 300 bytes per decision, never pruned (years of use stay under 1 MB).
- Load: one page polls every 60 s (every 5 s while it waits for the Mac), the Mac pings every 15 s and ticks every 60 s, cron
  every 5 min. Shared hosting copes with ten devices doing the same.
- Model calls: a draft is one Opus call (about 100 s, $0.15); a note is one Opus redraft plus one Sonnet learn call (about
  $0.10); transcription and photo indexing cost nothing. Nine ideas in one evening cost about $1.40. Drafting is sequential;
  parallel drafting would need the inventory and the plan to be written once at the end instead of after every draft.
- "How many agents": one worker, one LLM at a time, any number of board readers. Post volume is bounded by slots (4 per
  week), not by the system; 30 slots ahead would be 60 KB of cards and still fine.
