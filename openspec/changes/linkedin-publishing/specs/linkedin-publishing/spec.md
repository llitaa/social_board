# Spec Delta

## Purpose
Publish only what Anton approved, at the slot he approved, through LinkedIn's official API, and record what was published.

## ADDED Requirements

### Requirement: Approved cards only
The system SHALL publish a post only when its card status is approved; draft, change-requested, skipped or expired cards SHALL never be published.

#### Scenario: Draft at slot time
- **WHEN** the slot arrives and the card is still draft
- **THEN** nothing is published and the card shows "missed slot, not approved"

### Requirement: Publish at slot
An approved personal card SHALL be published to Anton's profile at its slot (or at once after Post now) with its text and image; an approved company card SHALL be published to the company page once the organisation scope exists. The worker's watch loop SHALL notice a due slot without waiting for the 10-minute run.

#### Scenario: Monday 07:30
- **WHEN** it is 07:30 and the Monday card is approved
- **THEN** the post is live within about 20 seconds and the post URL is written to posts-log.csv; the card leaves the board and appears under Published

#### Scenario: Post now
- **WHEN** Anton presses Post now on a connected channel
- **THEN** the row's time becomes now and the same publish step runs in the next fast chain

#### Scenario: Posts Anton scheduled in the LinkedIn app
- **WHEN** a row has status scheduled because Anton scheduled it in LinkedIn himself
- **THEN** the system never publishes it (LinkedIn does) and marks it posted after its time; the card says "scheduled by you in the LinkedIn app" and only offers Unschedule

### Requirement: Authorisation
Publishing SHALL use tokens Anton authorised once in his own LinkedIn account; tokens SHALL be stored by path only and never printed in logs or documents. Done 19.10.2026 with the existing app "AlpiType Analytics" (scopes openid, profile, w_member_social; token until 18.12.2026; `docs/linkedin-setup.md`). The company page scope (w_organization_social) waits for LinkedIn's Community Management API review.

#### Scenario: Token rejected
- **WHEN** the token is rejected
- **THEN** the card shows "not published: token rejected" and the Post screen shows the re-authorise warning

### Requirement: API health and token expiry
The system SHALL check the API and token daily, warn on the board 7 days before a token expires and immediately when a publish fails, naming the reason; it SHALL never silently switch to another path.

#### Scenario: Token expires in a week
- **WHEN** the token's expiry is 7 days away
- **THEN** the Post screen shows "LinkedIn token expires on <date>, re-authorise" until it is renewed

#### Scenario: Publish fails
- **WHEN** a publish call fails at the slot
- **THEN** the card shows "not published: <reason>" and keeps Copy text and Save image, which are always present on every card

#### Scenario: Company scope not granted yet
- **WHEN** the organisation scope is not yet granted and a company card is approved and due (Post now, or its slot arrived)
- **THEN** the card moves to the top of the Post screen as a decision, "waits for you: post it by hand · company page not connected to the API", with the sequence Copy text, Download image, post in LinkedIn as AlpiType, Mark posted, plus Back to decide; the header counts it ("1 to post by hand") and the system line names it; nothing disappears (19.10.: the alarm-flow post did disappear into a compact row, which is why this scenario exists)

### Requirement: No other LinkedIn actions
The publishing component SHALL perform no action on LinkedIn other than creating Anton's own approved posts.

#### Scenario: Scope audit
- **WHEN** the granted scopes are listed
- **THEN** only posting scopes are present; no read, comment, like or message scope

### Requirement: Publishing does not depend on the Mac
Approved cards SHALL be published by the always-on host at their slot: `server/publish.php` in `~/board-worker` (outside the web root) reads the board's cards and overlay, posts text and image through the LinkedIn Posts API, writes the result into the overlay (posted + URL, or publish_error) and a `posted` decision the Mac folds into the CSVs. It runs from a 5-minute cron in hPanel and whenever the board page or the Mac calls `api.php?a=tick` (at most once a minute, locked). The Mac's `publish.py` only publishes with `--force`. The LinkedIn-Version header is computed (two months back) so it never ages out. A due post not published 30 minutes after its slot is a board issue. A hung sync on the Mac is killed after 25 minutes.

#### Scenario: Mac asleep at 07:30
- **WHEN** a personal post is approved for 07:30 and the Mac is closed
- **THEN** the cron posts it by 07:35, the card shows "posted by the server" with the link, and the Mac records it in posts-log.csv when it wakes

#### Scenario: LinkedIn rejects the call
- **WHEN** the API answers an error
- **THEN** the card shows "publishing failed: …", the attempt is retried every 5 minutes, and nothing is posted twice (published.json)

#### Scenario: Lost answer, permanent error
- **WHEN** LinkedIn creates the post but the answer never arrives, or answers the same error five times
- **THEN** no second post is made within 10 minutes of the attempt, and after five failures the card says "needs you" and the host stops retrying

#### Scenario: Pending change
- **WHEN** a voice note or an image change is still being applied by the Mac
- **THEN** the host waits, but never longer than 10 minutes; an approved card with a past slot stays on the board until it is out
