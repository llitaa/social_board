# Design

## Context
The board must work from the phone and from the Mac without a Claude session. The Mac holds the repo and does the heavy lifting at night. No push: cards are always ready at 07:00 on working days, Anton knows that. A web page, not a native app: home-screen web apps on iOS give full screen, icon, camera-roll upload and microphone; a native app would add a developer account, builds and distribution for no behaviour this system needs.

## Goals / Non-Goals
**Goals:** one URL, three screens, decisions persisted server-side, record button, Copy text / Save image on every card.
**Non-Goals:** user accounts, multi-user, editing post text on the phone beyond a note, analytics on the board.

## Decisions
- Hosting: PHP page + JSON API on alpitype.com under a secret path (`board/<token>/`), shared hosting, no accounts; the Mac syncs with rsync every 10 minutes (`pipeline/run.sh`, launchd).
- State model: decisions appended as JSONL per day on the server, pulled to `board/data/decisions/`, folded into `content-plan.csv` by `apply_decisions.py`; the CSV is the truth, the board shows an overlay until the Mac confirms (`applied.json`).
- Card = post preview (author line, text, image), three actions. A note is an instruction, not a conversation: `redraft.py` applies it and approves. No option A/B, no crop, no photo choice on the card.
- Record: browser MediaRecorder → `uploads/memos/` → moved to the Mac → whisper.cpp → `library/memos/<ts>.txt` → next personal draft.
- Copy text and Save image on every card, always; at slot time an approved card says "post it yourself" until linkedin-publishing is live.
- Desktop ≥ 960 px: cards left with the action column beside the preview, pipeline right; phone: one column, pipeline under the cards.

## Risks / Trade-offs
- Mac asleep: presses are stored on the server and applied at the next run; a note waits until then. Known and accepted.
- A note the model misreads is approved without Anton seeing it: the updated card stays visible until the slot and can be skipped; the rules gate blocks the worst cases.
