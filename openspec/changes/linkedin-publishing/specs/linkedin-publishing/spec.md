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
An approved personal card SHALL be published to Anton's profile at its slot with the chosen text option and image; an approved company card SHALL be published to the company page.

#### Scenario: Monday 07:30
- **WHEN** it is 07:30 and the Monday card is approved
- **THEN** the post is live within 5 minutes and the post URL is written to posts-log.csv

### Requirement: Authorisation
Publishing SHALL use tokens Anton authorised once in his own LinkedIn account; tokens SHALL be stored by path only and never printed in logs or documents.

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
- **WHEN** the organisation scope is not yet granted
- **THEN** company cards show "company page: no API yet" and Anton posts them from the card with Copy text and Save image

### Requirement: No other LinkedIn actions
The publishing component SHALL perform no action on LinkedIn other than creating Anton's own approved posts.

#### Scenario: Scope audit
- **WHEN** the granted scopes are listed
- **THEN** only posting scopes are present; no read, comment, like or message scope
