# Spec Delta

## Purpose
The board is the single place where Anton decides, from the phone or from the Mac, in as little time as possible: he sees each post as it will appear on LinkedIn and presses Post, writes what to change and sees the new text within about a minute, fixes a word directly in the text, or skips. He never picks pictures, never fills empty slots, and the system learns his preferences from what he writes.

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
The Post screen SHALL show every open card as the post will appear on LinkedIn: author line (Anton or AlpiType), slot, the full text and the image the system chose, with these actions, the same on every card: Post now, Schedule (date and time, prefilled with the slot), Update the post (a note), Drop; under the image: Next photo from the pool (personal) and Upload another image. The text of a card to decide is editable in place (tap, type); Post now and Schedule take the text as shown. A scheduled card offers Post now and Unschedule (back to decide). A post Anton scheduled himself in the LinkedIn app shows "scheduled by you in the LinkedIn app" and only Unschedule, with the note that he must cancel it in LinkedIn first. Copy text and Download image appear only when he has to post by hand (channel not connected). Cards that need a decision come first; cards without a decision due are one line each (slot, status, hook, Copy, Image, Show). The card SHALL NOT offer picture choice, text options or crop tools; the system picks the photo and a note changes it ("anderes Foto").

#### Scenario: Post now
- **WHEN** Anton presses Post now
- **THEN** the row's time becomes now, the worker publishes it within about 20 seconds when the channel is connected (card: "posting now …", then gone, under Published with its URL); when the channel is not connected the card says "post it yourself now · Copy text · Download image" with Mark posted; the original slot is free and gets a new draft

#### Scenario: Schedule
- **WHEN** Anton picks a date and time (prefilled with the slot) and presses Schedule
- **THEN** the row moves to that time with status approved, the card says "scheduled · posts itself <time>" (or "scheduled <time>" plus "not connected: you post it then"); Post now and Unschedule stay available until then

#### Scenario: Unschedule
- **WHEN** Anton presses Unschedule on a scheduled card
- **THEN** it is back to decide, nothing is posted; for a post he scheduled in the LinkedIn app the card tells him to cancel it there first, because the board cannot reach it

#### Scenario: Drop
- **WHEN** Anton presses Drop (optionally with "not the topic" / "not the form")
- **THEN** the post is removed for good (text stays in the drafts library), the slot gets a new draft at the next full run, the reason goes through learning

#### Scenario: Another picture
- **WHEN** Anton presses "Next photo from the pool" or uploads an image on the card
- **THEN** within about 20 seconds the card shows the next ranked pool photo (never one it had before) or the uploaded image (square crop for personal posts, as is for company cards); the text does not change; the uploaded image is marked used by that post and never offered elsewhere

#### Scenario: Post with a small edit
- **WHEN** Anton changes a word in the card's text and presses Post
- **THEN** the edited text is what gets approved; the worker writes it into the draft file and keeps the previous text as a version; no model call

#### Scenario: Update the post
- **WHEN** Anton writes a note (e.g. "kürzer, ohne den Harvard-Vergleich" or "anderes Foto") and presses Update the post
- **THEN** the status becomes change with the note and the card says "being updated · about a minute"; the worker, triggered by the press (not by a timer), rewrites the text honouring the note and Anton's learned preferences, swaps the photo when the note asks for it, keeps the old text as a version, and puts the card back to decide with "updated per your note · read · edit · Post"; the page refreshes itself every 5 seconds meanwhile, so Anton reads the new text without reloading, edits if needed and presses Post (measured 19.10.: 60–70 s from press to new text)

#### Scenario: Note cannot be applied
- **WHEN** the rewrite breaks the rules gate or fails
- **THEN** the card stays open with "update failed · decide again" and the reason; nothing is approved; a note that failed twice is not retried until Anton decides again

#### Scenario: The system learns from a note
- **WHEN** a note, an edit or a skip reason states a preference that holds for future posts ("immer", "nie", "generell", a tone or word to avoid)
- **THEN** one line is added to the preference list (`library/style-rules.txt`) and every later draft and redraft prompt carries it; a one-off fix ("ohne die Zahl im ersten Satz") adds nothing; the system line shows the count; a line deleted from the file is forgotten

#### Scenario: Approved card due on a channel without API
- **WHEN** the slot arrives (or Post now was pressed) and that channel is not connected to the API
- **THEN** the card counts and sorts as a decision at the top of the Post screen: "waits for you: post it by hand", numbered sequence Copy text, Download image, post in LinkedIn, Mark posted (URL optional), plus Back to decide; the header shows "n to post by hand" and the system line names the post

#### Scenario: Post scheduled in LinkedIn by Anton
- **WHEN** a row has status scheduled and its time has passed
- **THEN** the worker sets it to posted, the card leaves the board and the post appears under Published; the board never shows a published post as open

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

#### Scenario: A press starts the worker
- **WHEN** a press, an upload or a memo reaches the server
- **THEN** the worker's watch loop (polling a change stamp every 15 seconds, no model call) starts the fast chain at once: pull, decisions into the CSV, learn, redraft, cards, push; it reads all decisions since its last run and acts on each exactly once; the board shows the pressed state at once and drops its overlay once the worker confirms

#### Scenario: Full run
- **WHEN** 10 minutes have passed since the last full run
- **THEN** the worker also transcribes memos, scans photos and fills open slots

### Requirement: Record button
Every screen SHALL have a Record button; holding it records audio, releasing stops; the audio SHALL be stored in the board store with a timestamp and not in iCloud.

#### Scenario: Record a thought
- **WHEN** Anton presses Record, talks, presses again
- **THEN** the memo is uploaded, transcribed on the Mac at the next run, and becomes the material of the next personal draft (spec content-generation, Memo to draft); memos under 15 words are ignored as tests

### Requirement: Spoken note on a card
Every card to decide SHALL have "Record a note" next to "Update the post". The recording goes to the server with the card id; the worker's fast chain transcribes it locally (whisper, zero tokens), writes it as a change decision into its own folder (`board/data/decisions-local/`, never into the server mirror) and applies it in the same run like a typed note: redraft within about a minute, the card comes back to decide, `learn.py` reads the note and keeps a general remark as a rule for all posts. While the note travels the card shows "voice note on its way · about a minute". The chain runs transcription before decisions in both modes, so a spoken note never waits for the 10-minute full run.

#### Scenario: Spoken "kürzer"
- **WHEN** Anton records "kürzer, und nie mit einer Zahl anfangen" on a card and presses Stop
- **THEN** within about a minute the card shows the shorter text as "updated per your note", and `library/style-rules.txt` gains "nie mit einer Zahl anfangen"

#### Scenario: Discard before sending
- **WHEN** a recording runs (round button or Record a note)
- **THEN** a bar at the bottom shows the running time with ✕ (discard) and ✓ (send); nothing leaves the phone until ✓ or the round button is pressed; ✕ throws the recording away with "recording discarded"

#### Scenario: Recorder buttons
- **WHEN** Anton taps the round record button or "Record a note" on the phone
- **THEN** nothing inside the button can be selected or long-press-highlighted; the button only starts and stops

### Requirement: No redundant explanations
Action buttons carry no explanation line when the label says it all (Schedule has none; "Post now" keeps its one line because by-hand posting differs).

### Requirement: Overview tiles and order
The Post tab SHALL open with a tile per upcoming post (square thumbnail, day, status dot: orange decide, green scheduled, blue scheduled in LinkedIn, company marked "A"); a tap opens the card. "Reorder" turns the tiles into an edit mode with ◀ ▶ per tile; Done sends the new sequence per channel, and the posts take the channel's existing slots in that sequence, at once on the board (overlay) and in the plan on the next run. Rows Anton scheduled in the LinkedIn app are shown locked and never moved. A new thought can thus be moved to the front instead of waiting at the end.

#### Scenario: Thought to the front
- **WHEN** Anton moves the newest thought tile to the first position and presses Done
- **THEN** that post carries the earliest personal slot, the others shift back one slot each, and the plan shows "[board … reordered to …]" on every moved row

### Requirement: Notes for the builder
A memo that addresses the board or the system (e.g. "generic note", "feedback", "zum Board") SHALL go to `library/feedback.md` and is shown on the board as "n spoken notes for the builder"; it never becomes a post idea.
