# Design

## Context
LinkedIn offers no read API for members' posts (r_member_social closed). Scraping tooling was ruled out in rep_v05/06. The only compliant sources are Anton's own browser and public search.

## Goals / Non-Goals
**Goals:** find, qualify, draft, expire. **Non-Goals:** posting, liking, following, tracking replies to comments automatically.

## Decisions
- Source A: watch-list profiles opened in Anton's Chrome via the browser extension in a morning session, read-only, max ~10 profiles/day, randomised order and time.
- Source B: web search restricted to linkedin.com/posts for pillar keywords; public post pages only.
- Drafting rules file `local/queue/rules.md` with the tone rule and banned phrases ("great post", "thanks for sharing", "fully agree").
- Queue file per day; the board renders it; expiry is a scheduled 18:00 step that rewrites the file and logs `expired`.
- Signal log: every used card writes `comment-log.csv` (date, person, post url, signal, used/skipped/expired) so "proven signals" can be measured monthly.

## Risks / Trade-offs
- Browser reading depends on Anton's session being logged in; if not, the day's queue comes from Source B only.
- Over-drafting makes comments sound alike; cap at 7 and rotate the opening form (question / thought / concern).
