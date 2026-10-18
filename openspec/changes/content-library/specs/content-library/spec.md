# Spec Delta

## Purpose
One place and one index per kind of content, so nothing is lost, nothing is uploaded to git, and old material can be found and reused on purpose.

## ADDED Requirements

### Requirement: Three copies, one truth
Originals SHALL stay on the phone, working copies in the board store, organised copies in the Mac library; the Mac library's index files SHALL be the truth for status and reuse.

#### Scenario: Phone lost
- **WHEN** the phone is replaced
- **THEN** every photo and memo already synced is still in the Mac library with its index row

### Requirement: No media in git
The repository SHALL contain code, specs and index files only; photos, audio, rendered images and exports SHALL be ignored by git.

#### Scenario: Commit check
- **WHEN** a commit is made
- **THEN** no file larger than 1 MB and no file under library/ except index files is included

### Requirement: Four collections
The library SHALL hold photos, memos, drafts and published posts, each with one index file: id, date, source, status, tags, used_in, and a free note.

#### Scenario: Published post stored
- **WHEN** a post is published
- **THEN** its final text, image, URL, slot and later its metrics are stored under published/ with one index row

### Requirement: Reuse rules
A photo SHALL become reusable 6 months after its last use or after 20 later posts; a published post's topic SHALL be eligible for recycling 3 months after publishing, marked as a recycle of the original.

#### Scenario: Old photo back in the pool
- **WHEN** a used photo passes 6 months since used_in's date
- **THEN** its status returns to ready with tag reused-eligible and it appears in the picker after new photos

#### Scenario: Recycle a topic
- **WHEN** content-generation picks a published topic older than 3 months
- **THEN** the draft card says "recycle of <post id>, new angle: …" and the index links both

### Requirement: Size budget
The library SHALL store compressed photos (≤ 2 MB), compressed audio, and final images only; the system SHALL report library size monthly and SHALL not exceed 5 GB without Anton's decision.

#### Scenario: Monthly size line
- **WHEN** the monthly report is written
- **THEN** it contains the library size per collection and the count of reusable photos
