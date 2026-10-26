# linkedin-system

Anton's LinkedIn content system: board (phone/desktop approval page), pipeline (Mac jobs), library (content on disk, not in git), openspec (behaviour specs).

- Specs: `openspec/changes/*` (active), `openspec/specs/*` (archived truth). Commands: `/opsx:*`.
- One-page architecture (data flow, storage, feedback, measured tokens): `docs/architecture.md`. Longer background: `docs/system-overview.md`.
- Sync chain (launchd, every 10 min): pull → transcribe (whisper, local) → apply_decisions → photo_index → cards → push. Deploy code: `python3 pipeline/board_sync.py deploy`.
- Model calls (drafts, redrafts on notes, learning, photo tags) do NOT run in the background (`llm.auto: false` since 26.10.). Run them when you are at the Mac: `python3 pipeline/process.py` shows what waits, asks, runs the chain with model calls, and prints what it produced. `--status` only shows, `--yes` skips the question. The board says "waiting for process.py" meanwhile.
- Statuses live in `content-plan.csv` (`planned` may carry a time: `2026-10-19 09:45`; `scheduled` = scheduled inside LinkedIn, nothing to do on the board).
- Campaign CSVs stay in `~/dev/campaign` and are referenced by path in `config.yaml`.
