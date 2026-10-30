# Spec Delta

## Purpose
Diagram posts for founders without a technical background that lead to a conversation with Anton.

## ADDED Requirements

### Requirement: The diagram is the post
An engagement post SHALL consist of one 1200x1200 diagram in the house style (stripe left, Anton's name top right, one title, one drawing, one note line) and a caption of at most three sentences plus one question. The diagram SHALL be one of the kinds in `pipeline/graphics.py` (curves, shift, beforeafter, flow, matrix) rendered from a JSON spec; no photo, no AlpiType logo, no list of sentences as a picture.

#### Scenario: Episode rendered
- **WHEN** a spec JSON is rendered
- **THEN** a PNG and its HTML source exist in library/drafts and the caption carries the series name and episode number

### Requirement: Two candidates, one yes
For every topic Anton gives (one sentence by memo, chat or terminal) the system SHALL answer with exactly two candidates: diagram kind, title, labels and caption each, rendered as PNG, and SHALL ask yes/no. Only the chosen one goes on the board, as a draft for the next Monday or Friday slot. No model call runs in the background for this.

#### Scenario: Topic given
- **WHEN** Anton says "Thema: Piloten, die nie Betrieb werden"
- **THEN** he sees two rendered candidates and says A, B or no; the chosen draft appears on the board with the caption

### Requirement: Reader locates himself
Every caption SHALL end with a question that asks the reader where he stands on the drawing (which quadrant, which point of the curve, which box). Addressing an audience ("für Gründer, die"), job-search wording and offers are forbidden; the series name and episode number are required.

#### Scenario: Caption check
- **WHEN** the caption is checked by rules_check
- **THEN** it passes only with a question in the last sentence and without banned phrases

### Requirement: Conversion is answered, not posted
Comments and DMs on an episode SHALL be logged per episode (count only, in posts-log) and are the measure of the series; impressions are secondary. The answer to a comment is Anton's, one line; the Betriebs-Check offer and the checklist live in the DM, never in the post.

#### Scenario: Episode without comments
- **WHEN** 48 hours after publishing an episode has no comment
- **THEN** the board shows it under Published with "no comment yet" and Anton adds the sharpest line of the caption as his own comment
