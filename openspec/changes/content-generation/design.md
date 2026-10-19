# Design

## Context
Drafting, image templates and logs exist in the repo today but run only when prompted. Routines run in the cloud on the GitHub repo; files under `local/` are gitignored, so the nightly Mac job must push the needed inputs or the routine must run on the Mac.

## Goals / Non-Goals
**Goals:** unattended Sunday run, brief, metrics, redraft loop. **Non-Goals:** publishing, engagement, Instagram.

## Decisions
- No weekly run: `draft.py` is part of every sync run and fills whatever is open in the next 14 days; `redraft.py` runs before it. Both on the Mac (they need the pool, the CV, the drafts).
- Inventory (`inventory.py`, `library/inventory.csv`): one Opus call over CV + company context + published hooks; statuses unused/drafted/published; re-runs only add. Pillar per slot = the pillar least used in the surrounding 14 days that still has material; a fresh memo takes the next personal slot first.
- Facts for the model: personal = the CV text; company = the company context file. Three recent posts of the channel as voice examples.
- Rules check as `rules_check.py` (banned patterns, question at the end, 500–2200 chars); one retry with the violations named, then the slot stays open and the log says why.
- Company graphic: `pipeline/templates/company-card.html` + headless Chrome screenshot (1.8 s); no image generation.
- Posts-log matching by date ± 1 day and first 30 characters of the hook.

## Risks / Trade-offs
- Mac asleep on Sunday night → run again on Monday 05:00; cards may be late once.
- Model test posts need real runs; if no run happened, Wednesday falls back to a decision helper.
