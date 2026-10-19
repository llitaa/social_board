# Spec Delta

## Purpose
Keep every usable photo of Anton in one indexed pool that the phone, the Mac's photo folders and the past feed, and from which the system picks the picture for each post. Anton never picks; he only adds photos or removes what should never appear.

## ADDED Requirements

### Requirement: Upload from the phone
The Photos screen SHALL offer Add photo that opens the phone's picker (camera roll or camera), accepts 1–10 photos with no text required, and stores copies with EXIF kept; originals SHALL remain on the phone.

#### Scenario: Upload three photos
- **WHEN** Anton selects three photos and presses Upload
- **THEN** three thumbnails appear with status new; nothing is written to iCloud and nothing else is asked

### Requirement: Photo sources
Besides phone uploads the pool SHALL be fed from configured folders on the Mac (default `~/Downloads`) and the legacy photo folder: every camera photo (EXIF date and camera model, at least 300 KB) with a detected face is copied into the pool; originals stay where they are; copies and derived files are never re-imported. Document scans, screenshots, memes and photos of other people (child present, woman only) SHALL be purged with every copy, never shown.

#### Scenario: Scan of the Downloads folder
- **WHEN** the run scans `~/Downloads` with 90 camera photos
- **THEN** the photos with a face join the pool as ready with their shoot, square crop and thumbnail; passport scans and family photos are deleted from the pool again after tagging

### Requirement: The system reads the picture
For each photo the system SHALL derive what is in it (scene line, tags, who is in it, LinkedIn-suitable or not) once with the small tags model on the 400 px thumbnail; Anton MAY add one line only when the photo carries an idea the picture alone does not show.

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
One index file SHALL hold id, file, taken, gps, shoot, note, status (new, ready, used, hold, deleted), used_in, used_at, crop, face, faces, scene, tags, people, label, src; every screen and every run SHALL read and write only through it.

#### Scenario: Status after posting
- **WHEN** a post with photo id X is posted, scheduled or approved
- **THEN** X and every photo of its shoot are set to used with used_in = post id and used_at = the post date

### Requirement: Reuse after 90 days
A used photo SHALL become eligible again 90 days after used_at (setting `photo_reuse_days`); the board shows "free from <date>" on used photos and the next free date in the pool summary.

#### Scenario: Pool runs dry
- **WHEN** no never-used photo is eligible for a slot
- **THEN** the oldest-used eligible photo (used_at + 90 days in the past) is picked, newest taken first

### Requirement: The system picks the photo
For a personal post the system SHALL rank eligible photos: never-used before re-used; photos taken within 24 months before older ones (setting `photo_fresh_months`, older ones only when nothing newer is eligible); then newest first; a tag match with the topic moves a photo up; a Friday label moves it up on Friday slots. Photos from the shoot of the neighbouring posts (the post before and the post after the slot), or from a shoot within 3 days of them, SHALL never be picked.

#### Scenario: Neighbouring post is fixed
- **WHEN** Friday's slot is drafted and Monday's post (already scheduled in LinkedIn) uses the Las Vegas photo of 22.05.
- **THEN** Friday's photo comes neither from 22.05. nor from the Horseshoe Bend shoot of 20.05.

#### Scenario: Other photo by note
- **WHEN** Anton writes "anderes Foto" on the card
- **THEN** the next-ranked eligible photo replaces it and the text is adjusted to the new picture if it referred to the old one

### Requirement: Photos screen
The Photos screen SHALL show Add photo, one summary line (available, used with next free date, held back) and the available shoots as thumbnails with their scene line; used and held shoots sit behind one toggle. Per available shoot there is one control, "don't use these" (status hold); uploads not yet fetched can be deleted. No picking, no Friday, no crop.

#### Scenario: Hold a shoot
- **WHEN** Anton presses "don't use these" on a shoot
- **THEN** it disappears from the available list at once and is never picked

### Requirement: Existing photos
The photos already on the Mac (legacy folder, Downloads) and the used-up list from the content plan SHALL be imported into the index on first run.

#### Scenario: First run (done 19.10.2026)
- **WHEN** the pool is created
- **THEN** 43 camera photos with a face are indexed, 16 marked used from the content plan with their post dates, 6 purged, 17 available
