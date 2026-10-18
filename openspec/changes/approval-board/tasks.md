# Tasks

## 1. Page and state
- [ ] 1.1 Build `local/board/board.html`: Post / Comments / Photos tabs, phone layout and desktop layout, private URL
- [ ] 1.2 Decision state read/write with card id, decision, option, image id, note, timestamp
- [ ] 1.3 Nightly sync script `board_sync.py` pulls state + files into `local/board/` and `local/resources/`

## 2. Post card
- [ ] 2.1 Render a card from `content-plan.csv` rows with status draft (text A/B from `local/reports/out/`, image from photo-pool)
- [ ] 2.2 Buttons Post / Change + note / Skip write decisions; card shows resulting status
- [ ] 2.4 Copy text / Save image on every card; "post it yourself" state at slot time
- [ ] 2.3 Redraft loop: change-requested cards get a new draft within the hour (hook into content-generation)

## 3. Record
- [ ] 3.1 Record button on every screen, audio compressed, stored with timestamp
- [ ] 3.2 Transcription on the Mac into `local/resources/voice/<ts>.txt`

## 4. Verify
- [ ] 4.1 Anton opens the board on the phone with the Mac asleep and on the Mac in Safari, presses Post on a test card, nightly run reads it
- [ ] 4.2 One memo recorded on the phone appears as text on the Mac the next morning
