# Tasks

## 1. Slot filling (19.10.)
- [x] 1.1 `draft.py`: open slots from config + plan, pillar per slot, topic from `inventory.py`
- [x] 1.2 One text per slot into `library/drafts/<id>.txt`; photo via `photo_index.pick()` or graphic via template + Chrome
- [x] 1.3 `rules_check.py` gate with banned patterns and client list
- [x] 1.4 Write content-plan.csv rows (status draft); cards.py shows them
- [x] 1.5 `llm.py`: one function, backend and model per step in config, call log with cost

## 2. Redraft and memos
- [x] 2.1 `redraft.py`: notes applied at the next run, versions kept, approved (19.10.)
- [x] 2.2 Memo transcripts → next personal draft, cleaned only (19.10.; first real memo pending)

## 3. Metrics loop
- [ ] 3.1 Monday brief routine (cloud) → `local/reports/brief/`
- [x] 3.2 Analytics XLSX import → posts-log.csv (`metrics_import.py`, in the full chain since 20.10.)
- [x] 3.3 API numbers: `metrics_fetch.py` (member post analytics + page share statistics), dormant until the Community Management API is granted (20.10.)
- [x] 3.4 Featured candidates + "numbers missing" line on the board (20.10.)
- [ ] 3.5 Monthly ranking report + proposed decision

## 5. Positioning and card (20.10.)
- [x] 5.1 `library/positioning.md` in draft + redraft prompts; `signals` check in `rules_check.py`; Swiss orthography switch
- [x] 5.2 `personal_card.py` + template with styles band / light / overlay; `personal_card.style` in config (off until Anton approves a style)
- [x] 5.3 li-post-13..17 redrafted with the positioning note (versions kept); li-post-18 from Anton's thought "a prompt is a sentence in a conversation" with the band card
- [x] 5.4 Style decided 20.10.: bottom (full photo, dark fade at the foot, white Montserrat headline, no kicker, no name); Montserrat/Open Sans = website fonts
- [x] 5.5 Pillar thought: phrases from memos (< 60 words) and chat → inventory, hook + headline verbatim, at least one per week (`make_room_for_thoughts`); book phrase bank `library/book-phrases.md` in the prompts
- [ ] 5.6 Anton picks a style → config → next drafts carry the card; check the first post's numbers against the plain-photo posts after 2 weeks

## 4. Verify
- [ ] 4.1 Tue 20.10.: every slot until 02.11. shows a draft on the board without a prompt; Anton's first note comes back approved
- [ ] 4.2 Mon 26.10.: brief present, export imported, 15 missing metrics filled where matchable
