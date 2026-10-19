# Tasks

## 1. Page and state
- [x] 1.1 Build `local/board/board.html`: Post / Comments / Photos tabs, phone layout and desktop layout, private URL
- [x] 1.2 Decision state read/write with card id, decision, option, image id, note, timestamp
- [x] 1.3 Nightly sync script `board_sync.py` pulls state + files into `local/board/` and `local/resources/`

## 2. Post card
- [x] 2.1 Render a card from `content-plan.csv` rows (text from `library/drafts/` or `library/published/`, image from the row's asset)
- [x] 2.2 Buttons Post as is / Post with these changes / Skip write decisions; card shows resulting status (19.10.: card = post preview, no picture choice, no options)
- [x] 2.4 Copy text / Save image on every card; "post it yourself" state at slot time
- [x] 2.3 Note loop: `redraft.py` applies the note, keeps versions, hands the card back to decide; `watch.py` triggers the fast chain within 15 s of a press; page polls every 5 s while updating (19.10., measured 60–70 s)
- [x] 2.6 Editable text on the card, Post sends the edit; `apply_decisions.py` writes it with a version (19.10., tested through the server API)
- [x] 2.7 `learn.py`: notes, edits, skip reasons → `library/style-rules.txt` → draft and redraft prompts (19.10.)
- [x] 2.8 Scheduled rows past their time become posted (19.10.)
- [x] 2.9 Compact rows: explicit grid columns (19.10.: tools were auto-placed into the date column)
- [x] 2.5 Pipeline list: next 14 days without empty slots, published with numbers, material counts (19.10.)

## 3. Record
- [x] 3.1 Record button on every screen, audio stored with timestamp (compression: later)
- [x] 3.2 Transcription on the Mac into `local/resources/voice/<ts>.txt`

## 4. Verify
- [ ] 4.1 Anton opens the board on the phone with the Mac asleep and on the Mac in Safari, presses Post on a test card, the next run reads it
- [x] 4.2 One memo recorded on the phone appears as text on the Mac (19.10. 11:21: "Test message one two three", 1.4 s whisper)
