# Design

## Context
Phone photos are HEIC with EXIF/GPS. The Mac has Python with Pillow/OpenCV available; face detection runs locally. The board store holds the compressed copy until the nightly sync.

## Goals / Non-Goals
**Goals:** phone → pool with no manual copy; index.csv as truth; rule enforcement. **Non-Goals:** editing beyond crop, filters, iCloud, video.

## Decisions
- Phone-side compression to ≤ 2 MB JPEG (EXIF preserved) before upload.
- Naming: `inbox/YYYY-MM-DD_HHMM_<id4>.jpg`, `shoots/YYYY-MM-DD_<slug>/`, `square/<id4>_sq.png`.
- Face detection: OpenCV Haar/DNN on the Mac; crop = largest face centred, 1:1, max size inside the frame.
- Import of existing pool: legacy folder + `~/Downloads` scan (config `photo_sources`); used-up state comes from `content-plan.csv` assets (IMG numbers) with the post date as `used_at`.
- Tagging: one Haiku call per photo on the thumbnail (measured 19.10.: 44 photos, 4.7 s and $0.0017 each), once; identity is not asked (the model refuses), a face + camera EXIF + the purge filter stand in for it.
- Reuse: `photo_reuse_days` 90, `photo_fresh_months` 24; picking in `photo_index.pick()`; neighbours from the plan's assets.

## Risks / Trade-offs
- No GPS on some photos → shoot by day+note only; acceptable.
- Face detection misses → centre crop; Anton's Crop fixes it in 10 s.
