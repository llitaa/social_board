# Spec Delta

## Purpose
The board is the single place where Anton decides, from the phone or from the Mac: approve or change a post, work the comment queue, manage photos, record a thought.

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

### Requirement: Post card
The Post screen SHALL show one card per scheduled post: channel, slot, text option A and B, the proposed square image, and the buttons Post, Change + note, Skip.

#### Scenario: Approve
- **WHEN** Anton presses Post
- **THEN** the card's status becomes approved with the chosen option and image, and the card shows "approved for <slot>"

#### Scenario: Approved card at slot time, before API publishing exists
- **WHEN** the slot arrives and the linkedin-publishing capability is not live yet
- **THEN** the card shows "approved, post it yourself" with Copy text and Save image, which every card has at all times; Anton posts in LinkedIn

#### Scenario: Approved card at slot time, API publishing live
- **WHEN** the slot arrives and linkedin-publishing is live
- **THEN** the post is published without further action and the card shows "posted" with the URL

#### Scenario: Change with note
- **WHEN** Anton types a note and presses Change + note
- **THEN** the status becomes change-requested with the note, and a redraft replaces the card within one hour during working hours

#### Scenario: Skip
- **WHEN** Anton presses Skip
- **THEN** the card is removed for that slot and the slot is left empty; nothing is published

#### Scenario: Skip with reason
- **WHEN** Anton presses Skip and then one of the two optional reasons, "not the topic" or "not the form"
- **THEN** the reason is stored with the card and content-generation lowers that topic or form in the next ranking

### Requirement: Shared decision state
Every decision SHALL be persisted in a shared state that automated runs read; the state SHALL record card id, decision, option, image id, note and timestamp.

#### Scenario: Next run reads decisions
- **WHEN** the nightly run starts
- **THEN** it reads all decisions since its last run and acts on each exactly once

### Requirement: Record button
Every screen SHALL have a Record button; holding it records audio, releasing stops; the audio SHALL be stored in the board store with a timestamp and not in iCloud.

#### Scenario: Record a thought
- **WHEN** Anton holds Record, talks, releases
- **THEN** the memo appears in a memo list with duration and time, and is available to the next nightly run
