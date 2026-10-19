# linkedin-system

Anton's LinkedIn content system: board (phone/desktop approval page), pipeline (Mac jobs), library (content on disk, not in git), openspec (behaviour specs).

- Specs: `openspec/changes/*` (active), `openspec/specs/*` (archived truth). Commands: `/opsx:*`.
- One-page architecture (data flow, storage, feedback, measured tokens): `docs/architecture.md`. Longer background: `docs/system-overview.md`.
- Sync chain (launchd, every 10 min): pull → apply_decisions → cards → photo_index → transcribe → push. Deploy code: `python3 pipeline/board_sync.py deploy`.
- Statuses live in `content-plan.csv` (`planned` may carry a time: `2026-10-19 09:45`; `scheduled` = scheduled inside LinkedIn, nothing to do on the board).
- Campaign CSVs stay in `~/dev/campaign` and are referenced by path in `config.yaml`.
