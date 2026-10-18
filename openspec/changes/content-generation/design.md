# Design

## Context
Drafting, image templates and logs exist in the repo today but run only when prompted. Routines run in the cloud on the GitHub repo; files under `local/` are gitignored, so the nightly Mac job must push the needed inputs or the routine must run on the Mac.

## Goals / Non-Goals
**Goals:** unattended Sunday run, brief, metrics, redraft loop. **Non-Goals:** publishing, engagement, Instagram.

## Decisions
- Sunday run and redraft loop run on the Mac (they need `local/` inputs and the photo pool); the Monday brief runs as a cloud routine (web research only) and writes into the repo.
- Topic ranking: score = pillar balance (each pillar at least once in two weeks) × last-month performance of the hook form × freshness of the source.
- Rules check as a script `rules_check.py` with the banned patterns list; it is the gate before the board.
- Posts-log matching by date ± 1 day and first 30 characters of the hook.

## Risks / Trade-offs
- Mac asleep on Sunday night → run again on Monday 05:00; cards may be late once.
- Model test posts need real runs; if no run happened, Wednesday falls back to a decision helper.
