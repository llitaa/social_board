# Design

## Context
Today: photos under campaign/local/resources/anton-photos, used-up list in agent memory, post texts in local/reports/out, posts-log.csv in the campaign repo. The campaign repo also carries the book campaign and Handwerk; the LinkedIn system would be a fourth thing in it.

## Goals / Non-Goals
**Goals:** one library, one index per collection, no media in git, reuse on purpose. **Non-Goals:** cloud backup (Anton's iCloud is full; a backup decision is his), DAM tooling.

## Decisions
- Separate repo `~/dev/linkedin-system`: `openspec/`, `board/`, `pipeline/`, `library/` (gitignored except `library/*/index.csv`). The campaign repo stays the home of `posts-log.csv` and `content-plan.csv` and is referenced by a path in `config.yaml`; the system writes those files, nothing else there.
- Library layout: `library/photos/{inbox,shoots,square}` + `index.csv` (as in photo-pool), `library/memos/<ts>.{m4a,txt}` + `index.csv`, `library/drafts/<post-id>/` (option A/B, image candidates, notes history) + `index.csv`, `library/published/<post-id>/` (final text, final image, url, metrics.json) + `index.csv`.
- Rotation: a monthly step flips eligible photos back to ready and lists recyclable topics for content-generation.
- Migration: move photo-pool folders and the seven unused photos; import the used-up list; fill published/ from posts-log.csv and local/reports/out.

## Risks / Trade-offs
- Two repos mean one cross-repo path; kept in one config line.
- Board store as "working copy" has provider limits; the nightly sync is what makes the Mac library complete.
