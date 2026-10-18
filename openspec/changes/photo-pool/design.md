# Design

## Context
Phone photos are HEIC with EXIF/GPS. The Mac has Python with Pillow/OpenCV available; face detection runs locally. The board store holds the compressed copy until the nightly sync.

## Goals / Non-Goals
**Goals:** phone → pool with no manual copy; index.csv as truth; rule enforcement. **Non-Goals:** editing beyond crop, filters, iCloud, video.

## Decisions
- Phone-side compression to ≤ 2 MB JPEG (EXIF preserved) before upload.
- Naming: `inbox/YYYY-MM-DD_HHMM_<id4>.jpg`, `shoots/YYYY-MM-DD_<slug>/`, `square/<id4>_sq.png`.
- Face detection: OpenCV Haar/DNN on the Mac; crop = largest face centred, 1:1, max size inside the frame.
- Import of existing pool: `local/resources/anton-photos/square/` files and the used-up list in memory become index rows.

## Risks / Trade-offs
- No GPS on some photos → shoot by day+note only; acceptable.
- Face detection misses → centre crop; Anton's Crop fixes it in 10 s.
