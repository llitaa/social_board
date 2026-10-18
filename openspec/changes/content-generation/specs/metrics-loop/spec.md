# Spec Delta

## Purpose
Replace guessing with Anton's own numbers: a weekly brief in, an analytics export in, a monthly ranking out that shapes the next month's drafts.

## ADDED Requirements

### Requirement: Monday brief
A one-page brief SHALL be in the repo by Monday 06:00: hiring moves at the target employers, model and tool releases, three post ideas with the pillar each fits.

#### Scenario: Brief delivered
- **WHEN** it is Monday 06:00
- **THEN** `local/reports/brief/YYYY-MM-DD.md` exists and the board links it from the Post screen

### Requirement: Analytics import
When Anton drops the LinkedIn analytics export into `local/resources/analytics/`, the system SHALL fill impressions, reactions and comments for every post in posts-log.csv it can match by date and hook.

#### Scenario: Export dropped
- **WHEN** a new XLSX appears in the folder
- **THEN** posts-log.csv is updated within the next run and unmatched rows are listed in the run log

### Requirement: Monthly ranking
On the first working day of the month the system SHALL rank last month's posts by pillar, hook form and slot, apply the ranking to the next weekly runs by itself, and put at most one Yes / No / Later card on the board when a change needs Anton's say.

#### Scenario: Ranking applied without Anton
- **WHEN** the month ends
- **THEN** the ranking report exists and the next weekly run weights pillars and hook forms by it; nothing is asked

#### Scenario: A change that needs his say
- **WHEN** the ranking suggests dropping a pillar or changing a slot time
- **THEN** one card "Move Thursday company post to Tuesday? Yes / No / Later" appears; No or no answer keeps everything as is
