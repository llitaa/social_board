# Design

## Context
The board must work from the phone and from the Mac without a Claude session. The Mac holds the repo and does the heavy lifting at night. No push: cards are always ready at 07:00 on working days, Anton knows that. A web page, not a native app: home-screen web apps on iOS give full screen, icon, camera-roll upload and microphone; a native app would add a developer account, builds and distribution for no behaviour this system needs.

## Goals / Non-Goals
**Goals:** one URL, three screens, decisions persisted server-side, record button, Copy text / Save image on every card.
**Non-Goals:** user accounts, multi-user, editing post text on the phone beyond a note, analytics on the board.

## Decisions
- Hosting: a published artifact page with shared-state and file-store capabilities (verify on build day); fallback: a small static page on the Mac exposed only via the Claude session (Remote Control) until the artifact path is confirmed.
- State model: one JSON document per day (`decisions/YYYY-MM-DD.json`) mirrored into the repo at `local/board/` by the nightly sync; the repo copy is the truth after sync.
- Record: browser MediaRecorder → audio file in the board store → nightly sync → `local/resources/voice/`; transcription on the Mac (local Whisper), never cloud.
- Copy text and Save image on every card, always; at slot time an approved card says "post it yourself" until linkedin-publishing is live.

## Risks / Trade-offs
- Artifact file-store limits (size per file) → compress audio and photos on the phone before upload.
- If shared state is unavailable, decisions fall back to Remote Control replies; the day still works, slower.
