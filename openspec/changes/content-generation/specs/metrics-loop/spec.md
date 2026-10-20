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

### Requirement: Numbers from the API
Once the Community Management API is granted to the app "AlpiType Board" (scopes `r_member_postAnalytics` for Anton's posts, `r_organization_social` for the page), the full chain SHALL fetch impressions, reactions and comments for every post of the last 90 days that has a LinkedIn URN in posts-log.csv (`metrics_fetch.py`, at most every 6 hours per post, zero tokens). Posts published by hand get their URN when Anton pastes the post URL on the board (Mark posted). Until the scope exists the script states so once per run and the export path stays: files in `library/metrics/inbox/` are imported by `metrics_import.py` in the same chain.

#### Scenario: Scope granted
- **WHEN** `linkedin_auth.py --org` has stored a token with `r_member_postAnalytics`
- **THEN** the next full run fills the numbers of every post with a URN and the board shows them under Published

### Requirement: Featured candidates
The board SHALL show, under Published, the three personal posts of the last 90 days with the most impressions as the posts that belong in the profile's Featured section; Anton pins them by hand. When three or more published posts older than 3 days have no numbers, the board says so and names the export path.

#### Scenario: Numbers present
- **WHEN** impressions exist for last month's posts
- **THEN** the line "Featured on your profile should be: …" lists the top three with their impressions

### Requirement: Monthly ranking
On the first working day of the month the system SHALL rank last month's posts by pillar, hook form and slot, apply the ranking to the next weekly runs by itself, and put at most one Yes / No / Later card on the board when a change needs Anton's say.

#### Scenario: Ranking applied without Anton
- **WHEN** the month ends
- **THEN** the ranking report exists and the next weekly run weights pillars and hook forms by it; nothing is asked

#### Scenario: A change that needs his say
- **WHEN** the ranking suggests dropping a pillar or changing a slot time
- **THEN** one card "Move Thursday company post to Tuesday? Yes / No / Later" appears; No or no answer keeps everything as is
