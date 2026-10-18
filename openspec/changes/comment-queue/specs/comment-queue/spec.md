# Spec Delta

## Purpose
Hand Anton a short, expiring list of posts worth a personal comment, each with a drafted comment, so engagement is personal, timely and never automated.

## ADDED Requirements

### Requirement: Watch list
The system SHALL keep one watch list file with name, profile URL, company, role, reason, and added date; qualification SHALL only consider posts by watched people or posts on a pillar topic found by public search.

#### Scenario: Add a person
- **WHEN** a person comments on or reacts to one of Anton's posts
- **THEN** they are added to the watch list with reason "commented on <post id>" or "reacted to <post id>" unless already present; a comment ranks above a reaction

### Requirement: Post qualification
A post SHALL qualify when it is at most 24 hours old, has its own text (not a bare repost), and a question, added thought or concern can be drafted; congratulations and job-change posts SHALL NOT get a comment card.

#### Scenario: Bare repost
- **WHEN** a watched person reposts without text
- **THEN** no card is created

#### Scenario: Job change
- **WHEN** a watched person announces a new role
- **THEN** a message card with a one-line direct message draft is created instead of a comment card

### Requirement: Message card
A message card SHALL show who, the signal, the one-line draft, and the buttons Open profile and Copy; sending SHALL be Anton's action in LinkedIn, because LinkedIn offers no messaging API for members.

#### Scenario: Send a message
- **WHEN** Anton presses Open profile, then Copy, then pastes and sends in LinkedIn
- **THEN** the card is marked used with the time; three presses in total

### Requirement: Daily queue size
The queue SHALL hold 4–5 comment cards on an average day, never more than 7 and at most 2 message cards, ready by 07:00 on working days; the daily number SHALL follow how many cards Anton actually used in the last two weeks.

#### Scenario: Quiet day
- **WHEN** fewer than 4 posts qualify
- **THEN** the queue holds only those; nothing is padded

#### Scenario: Anton uses two a day
- **WHEN** Anton used on average 2 cards a day over the last 10 working days
- **THEN** the queue offers 3, the best-ranked ones, not 5

### Requirement: Skip reasons
Skip on a comment card SHALL offer two optional reasons, "not the topic" and "not the author"; Skip without a reason SHALL remain one press.

#### Scenario: Skip with reason
- **WHEN** Anton presses Skip and then "not the author"
- **THEN** the card closes and the reason is stored with the card id, author and topic

### Requirement: Learning from use and skips
The ranking SHALL raise authors and topics whose cards Anton used, lower topics skipped as "not the topic", and remove an author from the watch list after two "not the author" skips.

#### Scenario: Author dropped
- **WHEN** the same author was skipped twice with "not the author"
- **THEN** the author is removed from the watch list and listed in the weekly question as removed

#### Scenario: Topic cools down
- **WHEN** a topic was skipped as "not the topic" three times in two weeks
- **THEN** posts on that topic no longer qualify unless the author is a watched person

### Requirement: Weekly question
The system SHALL ask Anton at most one question per week, on the board, skippable, and only when it has a pattern to confirm; it SHALL never ask without a concrete observation.

#### Scenario: Pattern seen
- **WHEN** 4 of 5 skipped cards in a week came from consultancies
- **THEN** Monday's board shows one card "Drop consultancies from the watch list?" with Yes / No / Later, and no other question that week

#### Scenario: Nothing to ask
- **WHEN** no pattern reaches the threshold
- **THEN** no question card appears

### Requirement: Comment card
Each card SHALL show who, why now, the post's first line, the drafted comment, and the buttons Open post, Copy, Skip.

#### Scenario: Use a card
- **WHEN** Anton presses Open post and then Copy
- **THEN** the LinkedIn app opens on that post and the comment text is in the clipboard; the card is marked used

### Requirement: Comment tone
Drafted comments SHALL be two to four sentences and SHALL be a question, an added thought or a concern; praise and generic acknowledgement SHALL NOT be drafted.

#### Scenario: Draft check
- **WHEN** a draft contains only agreement or praise
- **THEN** it is rejected and redrafted before it reaches the queue

### Requirement: Clear all
The Comments screen SHALL have one Clear all button that empties today's queue without a note or reason.

#### Scenario: Busy day
- **WHEN** Anton presses Clear all
- **THEN** all remaining cards for today are deleted and the screen shows "nothing left today"

### Requirement: Expiry
Untouched cards SHALL be deleted at the expiry time, a setting with default 18:00 that Anton can change on the board; a card can be kept past expiry once with Keep, until the next day's expiry.

#### Scenario: Untouched at expiry
- **WHEN** the expiry time passes and cards remain
- **THEN** they are deleted and logged as expired; tomorrow's queue starts empty

#### Scenario: Keep one
- **WHEN** Anton presses Keep on a card
- **THEN** it survives today's expiry and is deleted at tomorrow's; a kept card cannot be kept again

#### Scenario: Change the time
- **WHEN** Anton sets expiry to 20:00 in the board settings
- **THEN** from the next day on cards expire at 20:00; the monthly ranking reports comment age at posting so the setting can be judged
