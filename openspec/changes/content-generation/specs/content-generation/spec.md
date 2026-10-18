# Spec Delta

## Purpose
Turn Anton's voice memos, our documented work and the weekly brief into four board-ready post cards a week that obey his content rules.

## ADDED Requirements

### Requirement: Weekly cadence
The system SHALL produce cards for four slots per week: Mon 07:30, Wed 07:30, Fri 07:30 personal DE and Thu 09:00 company EN; the cards for the coming week SHALL exist on the board by the review time, a setting with default Saturday 08:00.

#### Scenario: Weekend review
- **WHEN** the weekly run completes before Saturday 08:00
- **THEN** four cards with status draft exist in content-plan.csv and on the board, reviewable on the weekend or on Monday

#### Scenario: Review time changed
- **WHEN** Anton sets the review time to Monday 06:00
- **THEN** from the next week on the run completes before that time

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
Each card SHALL carry two text options at most, hashtags, the slot, and an image: a pool photo for personal posts or a 1200×1200 graphic in the post style for company posts.

#### Scenario: Personal post image
- **WHEN** a personal card is drafted
- **THEN** its image is a ready pool photo obeying the previous-shoot rule, or a graphic with the reason stated

### Requirement: Rules check
Before a card reaches the board it SHALL pass: facts only from CV v2 and the company context, no audience address, no freelance CTA, no AlpiType on personal posts, no assistant credited as author, no client that must not be named.

#### Scenario: Banned pattern
- **WHEN** a draft contains "richtet sich an" or "#Freelance" or names Infineon, Leica, Siemens or Reiser
- **THEN** the draft is rejected and redrafted; the card is not created until it passes

### Requirement: Redraft on note
When a card is change-requested with a note, a new draft honouring the note SHALL replace it within one hour during 07:00–20:00.

#### Scenario: Note at 07:10
- **WHEN** Anton writes "kürzer, ohne den Harvard-Vergleich" at 07:10
- **THEN** a new option set is on the card by 08:10 and the old one is kept as history

### Requirement: Memo to draft
A voice memo recorded by 20:00 SHALL appear as a draft card the next morning, in Anton's words cleaned for spelling and structure only; nothing SHALL be added that he did not say.

#### Scenario: Memo with one idea
- **WHEN** a 90-second memo describes one thought
- **THEN** the draft contains that thought and a closing question, no invented facts
