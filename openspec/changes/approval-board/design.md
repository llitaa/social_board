# Design

## Context
The board must work from the phone and from the Mac without a Claude session. The Mac holds the repo and does the heavy lifting at night. No push: cards are always ready at 07:00 on working days, Anton knows that. A web page, not a native app: home-screen web apps on iOS give full screen, icon, camera-roll upload and microphone; a native app would add a developer account, builds and distribution for no behaviour this system needs.

## Goals / Non-Goals
**Goals:** one URL, three screens, decisions persisted server-side, record button, Copy text / Save image on every card.
**Non-Goals:** user accounts, multi-user, editing post text on the phone beyond a note, analytics on the board.

## Decisions
- Hosting: PHP page + JSON API on **alpitype.de** under a secret path (`board/<token>/`), beside the WordPress site (a real directory bypasses its rewrite; Hostinger CDN treats PHP as dynamic, images carry `?v=mtime`), one shared-hosting plan for all domains; alpitype.com redirects to it. The worker syncs with rsync: `pipeline/watch.py` (launchd KeepAlive) polls `api.php?a=ping` every 15 s and starts `run.sh fast` on a change, `run.sh full` every 10 min. The server cannot call the worker (shared hosting), so polling is the only way to react to a press within a minute; the ping is 60 bytes.
- Storage rule: the server holds only the current cards' images and the pool thumbnails; card images are pruned 7 days after the slot and the push mirrors with delete; a log warning above 200 MB. Expected growth without the rule ≈ 10 MB/month, plan limit 100–200 GB.
- State model: decisions appended as JSONL per day on the server, pulled to `board/data/decisions/`, folded into `content-plan.csv` by `apply_decisions.py`; the CSV is the truth, the board shows an overlay until the Mac confirms (`applied.json`).
- Card = post preview (author line, text, image), three actions. A note is an instruction: `redraft.py` applies it within about a minute and hands the card back to decide (Anton asked 19.10. to read the result, fix small things in place, then Post). The text of a card to decide is `contenteditable`; Post sends the text only when it differs. No option A/B, no crop, no photo choice on the card.
- Learning: `learn.py` turns notes, edits (before/after) and skip reasons into one-line preferences via Sonnet (default one-off, so the list stays short); `library/style-rules.txt` is plain text Anton can prune; drafts and redrafts carry the last 40 lines.
- A post Anton scheduled in LinkedIn himself is promoted to posted by `apply_decisions.py` once its time has passed, so the board does not show it as open (19.10.: the Schiff post stayed visible after 09:45).
- Record: browser MediaRecorder → `uploads/memos/` → moved to the Mac → whisper.cpp → `library/memos/<ts>.txt` → next personal draft.
- Copy text and Save image on every card, always; at slot time an approved card says "post it yourself" until linkedin-publishing is live.
- Desktop ≥ 960 px: cards left with the action column beside the preview, pipeline right; phone: one column, pipeline under the cards.

## Risks / Trade-offs
- Mac asleep: presses are stored on the server and applied at the next run; a note waits until then. Known and accepted.
- A note the model misreads: the card comes back to decide, Anton sees it and notes again or edits; nothing is approved unseen.
- The worker must be awake for the one-minute loop; asleep, the press waits and the card says "being updated" until it wakes (the system line shows "Mac not seen for n min").
