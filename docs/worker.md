# The worker: what it needs, and how to move it off the Mac

The server (Hostinger) is only a mailbox: it stores presses, uploads and the JSON the board reads. All processing
runs on **one worker machine** that is awake most of the day. Today that is the Mac. Any Linux box, a Windows PC with
WSL, or a cloud VM can take the role; the server does not care which machine syncs with it.

## Requirements

| Need | Why | Install (Linux/WSL) | macOS |
|---|---|---|---|
| python3 ≥ 3.10 with pillow, pillow-heif, opencv-python-headless, pyyaml, openpyxl, numpy | pipeline | `pip install pillow pillow-heif opencv-python-headless pyyaml openpyxl numpy` | anaconda has them |
| ffmpeg + whisper.cpp (`whisper-cli`) + `pipeline/models/ggml-small.bin` (466 MB) | memo transcription; ~1 GB RAM, 1–20 s per memo on CPU, no GPU needed | `apt install ffmpeg`; build whisper.cpp; download the model | `brew install ffmpeg whisper-cpp` |
| YuNet model `face_detection_yunet_2023mar.onnx` | face crop | from the opencv_zoo repo | same |
| Chrome or Chromium (path in `config.yaml: chrome`) | company graphics (headless screenshot) | `apt install chromium` | Google Chrome |
| pdftotext (poppler) | CV text for the inventory | `apt install poppler-utils` | `brew install poppler` |
| `claude` CLI, logged in to the subscription (`claude login`), or `ANTHROPIC_API_KEY` with `llm.backend: api` | draft, redraft, tags, inventory | npm install -g @anthropic-ai/claude-code | same |
| ssh key for the Hostinger alias (`~/.ssh/config` entry `hostinger-alpitype`) + rsync | sync | copy the key | exists |
| the two repos: `linkedin-system` and `campaign` (content-plan.csv, posts-log.csv) | truth files | git clone both | exist |
| `config.local.token`, `config.local.linkedin.json`, `library/` (photos, memos, drafts) | secrets and content, not in git | copy once from the Mac (`rsync -a library/ config.local.* newhost:~/linkedin-system/`) | — |

Scheduling: launchd on macOS (`~/Library/LaunchAgents/com.alpitype.board-sync.plist`), on Linux a cron line
`*/10 * * * * /home/anton/linkedin-system/pipeline/run.sh >> library/log/board-sync.out 2>> library/log/board-sync.err`,
on Windows WSL the same cron inside WSL or Task Scheduler. `run.sh` finds python3 on PATH (`PYTHON=` to override).

## Moving the role

1. Stop the Mac job: `launchctl bootout gui/$(id -u)/com.alpitype.board-sync` (two machines must never sync at once).
2. On the new worker: clone both repos, install the table above, copy `library/`, `config.local.*`, the ssh key, set `chrome:` in `config.yaml`.
3. Run `pipeline/run.sh` once by hand, read `library/log/board-sync.err`, open the board: the system line must say "system ok".
4. Add the cron line. The Mac keeps its copy as a cold spare; commit the CSVs from whichever machine runs.

## Cloud instead of a PC

A small AWS instance (t3.small, ≈ 17 € a month) runs everything in the table; `claude -p` on a subscription needs a one-time
`claude login` from that box (device flow), otherwise use the API key (≈ 6–8 $ a month at today's volume). It buys nothing
over a PC at home except uptime; the board does not need uptime, presses wait on the server. A PC at home is the cheaper
answer; the AWS box is not needed and can go.
