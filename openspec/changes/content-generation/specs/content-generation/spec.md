# Spec Delta

## Purpose
Turn Anton's voice memos, our documented work and the weekly brief into four board-ready post cards a week that obey his content rules.

## ADDED Requirements

### Requirement: Slots are always filled
The slot rule is config: Mon, Wed, Fri 07:30 personal DE and Thu 09:00 company EN (`slots` in config.yaml). Every run (each 10-minute sync) SHALL draft a post for every slot in the next 14 days that has none, at most 3 personal and 1 company post per ISO week counting posts Anton scheduled himself on other weekdays. There is no review time: drafts are on the board as soon as a slot opens.

#### Scenario: Monday morning
- **WHEN** Anton opens the board on any day
- **THEN** every slot of the next 14 days shows a draft or a scheduled post; nothing is empty

#### Scenario: Post scheduled by Anton on a Friday
- **WHEN** a company post is scheduled in LinkedIn for Friday 23.10.
- **THEN** no company draft is made for Thursday 22.10. (one company post per week)

### Requirement: Unreviewed cards
A card not approved by its slot SHALL not be published; it SHALL move once to the next slot of the same kind, and if still unreviewed, SHALL go to the drafts library with status unused.

#### Scenario: Nothing reviewed by Tuesday
- **WHEN** Monday's card was not approved by Mon 07:30
- **THEN** it becomes the card for Wed 07:30 and Wednesday's draft moves to the following week; nothing is posted and no reminder is sent

### Requirement: Pillar mix
Over any two weeks the personal slots SHALL contain at least one case from practice, one decision helper or model test and one post from a voice memo when memos exist; within that, each slot SHALL take whichever pillar has the strongest material, not a fixed weekday.

#### Scenario: No memo this week
- **WHEN** no voice memo was recorded in the last 7 days
- **THEN** the memo slot is filled from the inventory and the card says "no memo this week"

#### Scenario: Cases run low
- **WHEN** fewer than 3 unused case topics remain in the inventory
- **THEN** the weekly run says so on the board and the mix shifts to decision helpers and memos until Anton adds material

### Requirement: Material inventory
The system SHALL keep an inventory of candidate topics per pillar with source, status (unused, drafted, published, recycled) and a one-line angle, visible on the board, so Anton can see how much material exists.

#### Scenario: Inventory on day one
- **WHEN** the inventory is first built from CV v2, the company context, the published posts and this repo's work
- **THEN** it lists every candidate with its angle and the count per pillar; cases from the CV count each distinct angle once, not each project once

### Requirement: Draft content
Each card SHALL carry one text with hashtags, the slot, and an image: a pool photo chosen by photo-pool for personal posts or a 1200×1200 graphic rendered from the company template (eyebrow, title, 3–4 numbered lines, footer; headless Chrome) for company posts. Drafts live in `library/drafts/<id>.{txt,json,png}`; the content plan row carries status draft and the pillar, topic and photo id in its notes.

#### Scenario: Personal post image
- **WHEN** a personal card is drafted
- **THEN** its image is a ready pool photo obeying the previous-shoot rule, or a graphic with the reason stated

### Requirement: Rules check
Before a card reaches the board it SHALL pass: facts only from CV v2 and the company context, no audience address, no freelance CTA, no AlpiType on personal posts, no assistant credited as author, no client that must not be named.

#### Scenario: Banned pattern
- **WHEN** a draft contains "richtet sich an" or "#Freelance" or names Infineon, Leica, Siemens or Reiser
- **THEN** the draft is rejected and redrafted; the card is not created until it passes

### Requirement: Redraft on note
When a card carries a note (Post with these changes), the next run SHALL rewrite the text honouring the note and nothing else, keep the old text as a version, swap the photo when the note asks for it, pass the rules gate and set the card to approved. No second decision is asked.

#### Scenario: Note at 07:10
- **WHEN** Anton writes "kürzer, ohne den Harvard-Vergleich" at 07:10
- **THEN** by 07:20 the card shows the shorter text, "updated per your note", status approved, and `<id>.v1.txt` holds the old text

### Requirement: Which model does what
Model calls go through one function (`llm(step, prompt)`), the backend is config (`claude -p` on the subscription by default, API key as a switch), the model per step is config: draft and redraft Opus, inventory Opus, photo tags Haiku, comment drafts Sonnet. Every call is logged with tokens and cost to `library/log/llm-calls.csv`.

#### Scenario: Monthly cost
- **WHEN** Anton asks what the system cost
- **THEN** the log answers per step: calls, seconds, dollars (19.10. measured: tags 44 calls $0.08, inventory 1 call $0.34, a draft about $0.15)

### Requirement: Memo to draft
A voice memo recorded by 20:00 SHALL appear as a draft card the next morning, in Anton's words cleaned for spelling and structure only; nothing SHALL be added that he did not say.

#### Scenario: Memo with one idea
- **WHEN** a 90-second memo describes one thought
- **THEN** the next open personal slot gets that thought as its draft (pillar memo) with a closing question, no invented facts; memos under 15 words are ignored
