# Spec Delta

## Purpose
The board is the single place where Anton decides, from the phone or from the Mac, in as little time as possible: he sees each post as it will appear on LinkedIn and presses Post, writes what to change, or skips. He never picks pictures, never fills empty slots, never comes back for a post he has already commented on.

## ADDED Requirements

### Requirement: Private page on phone and desktop
The board SHALL be a single web page reachable via a private URL from Anton's phone and from any desktop browser on the Mac, usable without the Mac session running, and SHALL show three screens: Post, Comments, Photos.

#### Scenario: Open on the phone
- **WHEN** Anton opens the board bookmark on the phone
- **THEN** the Post screen for today loads within 3 seconds with no login beyond the private URL

#### Scenario: Open on the Mac
- **WHEN** Anton opens the same URL in Safari or Chrome on the Mac
- **THEN** the same screens and buttons work, laid out for the wider window

#### Scenario: Mac asleep
- **WHEN** the Mac is asleep or the session is closed
- **THEN** the board still loads and accepts button presses; they are applied at the next automated run

### Requirement: Post card = the post
The Post screen SHALL show every open card as the post will appear on LinkedIn: author line (Anton or AlpiType), slot, the full text and the image the system chose, with exactly three actions: Post as is, Post with these changes (a note), Skip. Cards that need a decision come first; cards without a decision due are one line each (slot, status, hook, Copy, Image, Show). The card SHALL NOT offer picture choice, text options or crop tools; the system picks the photo and a note changes it ("anderes Foto").

#### Scenario: Post as is
- **WHEN** Anton presses Post as is
- **THEN** the card's status becomes approved and shows "posts <slot>"; nothing else is asked

#### Scenario: Post with changes
- **WHEN** Anton writes a note (e.g. "kürzer, ohne den Harvard-Vergleich" or "anderes Foto") and presses Post with these changes
- **THEN** the status becomes change with the note, the card says "being updated", the next run (within 10 minutes) rewrites the text honouring the note (and swaps the photo when the note asks for it), keeps the old text as a version, and sets the status to approved; the card shows "updated per your note · posts <slot>"; Anton does not have to come back

#### Scenario: Note cannot be applied
- **WHEN** the rewrite breaks the rules gate or fails
- **THEN** the card stays open with "update failed · decide again" and the reason; nothing is approved

#### Scenario: Approved card at slot time, before API publishing exists
- **WHEN** the slot arrives and the linkedin-publishing capability is not live yet
- **THEN** the card shows "post it yourself · Copy text" with Copy text and Save image; Anton posts in LinkedIn and presses Mark posted (URL optional)

#### Scenario: Approved card at slot time, API publishing live
- **WHEN** the slot arrives and linkedin-publishing is live
- **THEN** the post is published without further action and the card shows "posted" with the URL

#### Scenario: Skip
- **WHEN** Anton presses Skip and optionally one of the two reasons "not the topic" / "not the form"
- **THEN** the card is removed, the slot is filled with a new draft by the next run, and the reason lowers that topic or form in the next ranking

#### Scenario: Veto after approval
- **WHEN** an approved (or updated) card is still before its slot and Anton presses Skip on it
- **THEN** it is skipped like a draft; nothing is published

### Requirement: Pipeline without gaps
The board SHALL show the next posts (14 days) and the last published posts with their numbers. Every listed slot SHALL carry a draft; a slot without a draft is not listed, because content-generation fills every slot in the horizon on each run. The list SHALL also show the material inventory counts per pillar and whether a voice memo is waiting.

#### Scenario: Open slot
- **WHEN** a slot in the next 14 days has no post (new week, a skip, a post moved)
- **THEN** the next run drafts one and the slot appears with its hook; the board never shows an empty slot

### Requirement: Shared decision state
Every decision SHALL be persisted in a shared state that automated runs read; the state SHALL record card id, decision, note, reason and timestamp.

#### Scenario: Next run reads decisions
- **WHEN** the sync run starts (every 10 minutes while the Mac is awake)
- **THEN** it reads all decisions since its last run and acts on each exactly once; the board shows the pressed state at once and drops its overlay once the Mac confirms

### Requirement: Record button
Every screen SHALL have a Record button; holding it records audio, releasing stops; the audio SHALL be stored in the board store with a timestamp and not in iCloud.

#### Scenario: Record a thought
- **WHEN** Anton presses Record, talks, presses again
- **THEN** the memo is uploaded, transcribed on the Mac at the next run, and becomes the material of the next personal draft (spec content-generation, Memo to draft); memos under 15 words are ignored as tests
