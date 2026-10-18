# Proposal

## Why
Posts with Anton's face perform best, but photos sit on his phone and iCloud is full. Copying files to the Mac by hand means no photo, or the wrong one.

## What Changes
- Add photo on the board: pick 1–10 from the camera roll or camera, optional one-line note; originals stay on the phone.
- Nightly: sync to the Mac, shoot detection (same day and place), face-aware square crop, index.csv updated.
- Photos screen: thumbnails grouped by shoot, status new / ready / used, Use Friday, Mark shoot used, Delete.
- Post card: Other (swipe proposals), Crop (move/zoom the square), No photo.
- Rule enforcement: never a photo from the same shoot as the previous post.
- Out of scope: graphics rendering for company posts (content-generation), iCloud of any kind.

## Capabilities

### New Capabilities
- `photo-pool`: upload, organisation, cropping, status and the previous-shoot rule.

### Modified Capabilities
(none)

## Impact
New folder `local/resources/anton-photos/{inbox,shoots,square}` and `index.csv`; the existing used-up list and seven unused photos are imported. Board gets the Photos screen and the image controls on the post card. Plan done-date: Tue 20.10.
