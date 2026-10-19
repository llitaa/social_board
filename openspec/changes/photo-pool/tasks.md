# Tasks

## 1. Store and sync
- [x] 1.1 Add photo on the Photos screen with phone-side compression and note
- [x] 1.2 Nightly sync into `local/resources/anton-photos/inbox/`

## 2. Processing
- [x] 2.1 `photo_index.py`: EXIF read, shoot clustering, folder move, index.csv write
- [x] 2.2 Face-aware square crop → `square/<id>_sq.png`; re-render on crop change
- [x] 2.3 Import existing photos (legacy + Downloads scan, 19.10.: 43 indexed, 6 purged) and used-up list with dates
- [x] 2.4 Tags/scene/people per photo (Haiku, once); purge filter for documents and other people
- [x] 2.5 `pick()`: 90-day reuse, 24-month freshness, neighbour-shoot rule, tag match

## 3. Board controls
- [x] 3.1 Photos screen: summary line, available shoots with scene, "don't use these", used/held behind a toggle (19.10.)
- [x] 3.2 Post card: "anderes Foto" as a note swaps the photo in `redraft.py`; "Next photo from the pool" and "Upload another image" per card in `photo_index.card_images()` (19.10., exercised through the server API)
- [x] 3.3 Neighbour-shoot rule in `draft.py` (shoots of the post before and after the slot, ±3 days)

## 4. Verify
- [ ] 4.1 Tue 20.10.: three photos uploaded from the phone appear as one shoot with crops the next morning
