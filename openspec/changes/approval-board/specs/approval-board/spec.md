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
The Post screen SHALL show every open card as the post will appear on LinkedIn: author line (Anton or AlpiType), slot, the full text and the image the system chose, with exactly three actions: Post, Update the post (a note), Skip. The text of a card to decide is editable in place (tap, type); Post takes the text as shown. Cards that need a decision come first; cards without a decision due are one line each (slot, status, hook, Copy, Image, Show). The card SHALL NOT offer picture choice, text options or crop tools; the system picks the photo and a note changes it ("anderes Foto").

#### Scenario: Post
- **WHEN** Anton presses Post
- **THEN** the card's status becomes approved and shows "posts itself <slot>" when LinkedIn is connected, otherwise "approved · you post it <slot>" with "LinkedIn not connected"; nothing else is asked

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

#### Scenario: Approved card at slot time, before API publishing exists
- **WHEN** the slot arrives and the linkedin-publishing capability is not live yet
- **THEN** the card shows "approved · post it yourself now · Copy text" with Copy text and Save image; Anton posts in LinkedIn and presses Mark posted (URL optional)

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
