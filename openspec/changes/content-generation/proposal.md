# Proposal

## Why
Four posts a week with zero writing from Anton requires the drafting, image, rules check and logging to run without a prompt, from the sources he actually produces: voice memos, our work, a weekly brief and last month's numbers.

## What Changes
- Weekly cadence: Mon/Wed/Fri personal DE (case, decision helper or model test, personal), Thu company EN.
- Sunday-night run: topic candidates per slot ranked by last month's numbers and pillar balance, draft text (two options), image (photo from the pool or 1200² graphic), rules check, card on the board.
- Monday brief at 06:00: one page (hiring, releases, trends) with three post ideas.
- Metrics loop: Monday analytics export dropped by Anton → posts-log filled → monthly ranking by pillar, hook, slot.
- Redraft within the hour on Change + note.
- Out of scope: publishing (linkedin-publishing), the board itself.

## Capabilities

### New Capabilities
- `content-generation`: topic selection, drafting, image choice, rules check, redraft, weekly cadence.
- `metrics-loop`: Monday brief, analytics import, monthly ranking that feeds the next plan.

### Modified Capabilities
(none)

## Impact
Reads `local/resources/voice/`, the work log, the brief, `posts-log.csv`; writes `content-plan.csv` rows and `local/reports/out/<id>.txt` + PNG. Runs as scheduled routines. Plan done-dates: Sun 25.10. (routine), Mon 26.10. (brief, metrics), Fri 30.10. (phase 1 done).
