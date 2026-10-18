# Proposal

## Why
Anton needs to approve posts, comments and photos in two minutes a day, from the phone or the Mac, without a Claude session open. Today drafts live in repo files he has to open on the Mac; nothing reaches the phone.

## What Changes
- A private web page ("the board"), phone-sized and desktop-usable, with three screens: post card, comment queue, photo pool.
- Post card: text (option A/B), square image, slot, buttons Post / Change + note / Skip.
- A Record button on every screen's top bar for voice memos (audio into the board store, no iCloud).
- Shared state: every decision is readable by the next automated run without the Mac session.
- Out of scope: comment cards content (comment-queue), photo processing (photo-pool), drafting (content-generation), publishing (linkedin-publishing).

## Capabilities

### New Capabilities
- `approval-board`: the page, its post card, its record button, Copy text / Save image on every card, and the shared decision state other capabilities read.

### Modified Capabilities
(none)

## Impact
New: board page + store, decision state file read by content-generation and linkedin-publishing. Phone: home-screen bookmark. Mac: nightly sync reads the store. Plan done-date: Mon 19.10. evening.
