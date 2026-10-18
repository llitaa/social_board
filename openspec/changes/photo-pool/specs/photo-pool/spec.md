# Spec Delta

## Purpose
Keep every usable photo of Anton in one indexed pool that the phone feeds and the post pipeline reads, with the previous-shoot rule enforced automatically.

## ADDED Requirements

### Requirement: Upload from the phone
The Photos screen SHALL offer Add photo that opens the phone's picker (camera roll or camera), accepts 1–10 photos with no text required, and stores copies with EXIF kept; originals SHALL remain on the phone.

#### Scenario: Upload three photos
- **WHEN** Anton selects three photos and presses Upload
- **THEN** three thumbnails appear with status new; nothing is written to iCloud and nothing else is asked

### Requirement: The system reads the picture
For each photo the system SHALL derive what is in it (place, setting, objects, whether Anton's face is visible) and tag it; Anton MAY add one line only when the photo carries an idea the picture alone does not show.

#### Scenario: No note
- **WHEN** a photo of a harbour is uploaded without text
- **THEN** it is tagged harbour, ship, outdoor, no face, and offered for posts where such a scene fits

#### Scenario: Note with an idea
- **WHEN** Anton adds "sunk ship → legacy code" to a photo
- **THEN** the note becomes a topic link and content-generation proposes that photo for the next legacy-code post

### Requirement: Crop only
Photos SHALL only be cropped and scaled; no retouching, no generated or added pixels, no filters, so that no post has to be marked as AI-generated imagery.

#### Scenario: Face partly outside the square
- **WHEN** the best square cannot include the whole face
- **THEN** the system proposes a different square or the full photo with letterbox, never an extended or generated background

### Requirement: Shoot detection
Photos SHALL be grouped into shoots by EXIF date and GPS (same calendar day, within 500 m, within 3 hours); without GPS, by calendar day and note.

#### Scenario: Same evening
- **WHEN** four photos were taken within 20 minutes at the same place
- **THEN** they form one shoot with one id and one folder

### Requirement: Square crop
Each photo SHALL get a 1200×1200 crop proposal centred on a detected face, or on the image centre when no face is found; Anton's Crop adjustment SHALL be stored and re-rendered.

#### Scenario: Move the crop
- **WHEN** Anton drags and zooms the square on the post card and taps OK
- **THEN** the crop box is saved in the index and the 1200×1200 file is cut again from the original copy

### Requirement: Index as the truth
One index file SHALL hold id, file, taken, shoot, note, status (new, ready, used, deleted), used_in and crop; every screen and every run SHALL read and write only through it.

#### Scenario: Status after posting
- **WHEN** a post with photo id X is published
- **THEN** X and every photo of its shoot are set to used with used_in = post id

### Requirement: Previous-shoot rule
The proposed image for a post SHALL never come from the shoot used by the previous published personal post.

#### Scenario: Only the previous shoot has photos
- **WHEN** all ready photos belong to the previous post's shoot
- **THEN** the post card proposes a graphic or No photo and says why

### Requirement: Photos screen controls
Per shoot the screen SHALL offer Use Friday, Mark shoot used and Delete; Delete SHALL remove the board copy and mark the index entry deleted.

#### Scenario: Delete a photo
- **WHEN** Anton presses Delete on a photo
- **THEN** it disappears from the board and the Mac copy is removed at the next sync

### Requirement: Existing photos
The seven unused photos already on the Mac and the used-up list SHALL be imported into the index on first run.

#### Scenario: First run
- **WHEN** the pool is created
- **THEN** Stanford and the six October photos appear as ready shoots and the used-up shoots appear as used
