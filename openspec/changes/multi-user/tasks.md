# Tasks

## 1. Tenant
- [x] 1.1 `common.py`: BOARD_USER, users/<slug>/ paths, config merge (slots replaced, rest merged), `boards()`, `profile()`
- [x] 1.2 `run.sh`, `watch.py`, `process.py --user`: chain per board, Anton first; mail and metrics only on Anton's board
- [x] 1.3 `users.py sync | add | admin | list`; `server/publish.php` per board (token file, memory, lock; CLI loops all boards)

## 2. Login and admin
- [x] 2.1 `board/auth.php`: password, sessions, lock-out, forced change; `index.php` gate, `api.php` 401, logout, password actions
- [x] 2.2 `board/admin/index.php`: create, reset, disable; registry and code copy in ~/board-worker

## 3. Onboarding
- [x] 3.1 Board: request form (website, words, document), waiting view, proposal form with confirm
- [x] 3.2 `onboard.py`: website + document + words -> profile.json proposal; after confirm: profile.md, positioning.md, inventory
- [x] 3.3 `draft.py`, `inventory.py`, `rules_check.py`: the person's name, role and facts instead of Anton's; text-only posts when the pool is empty

## 4. Sharing and matching
- [x] 4.1 `photo_index.py`: share/owner columns, share and unshare decisions (single photo or series); Photos tab buttons
- [x] 4.2 `match.py`: proposals.json; card block "Passt das zu deinem Entwurf?"; `apply_decisions.py` accept -> pool, card image, credit line, owner notice
- [x] 4.3 `cards.py` notices ("dein Foto ist in einem Post von ...")

## 5. Open
- [ ] 5.1 LinkedIn connection for a user through the server (OAuth callback on alpitype.de); until then Copy text
- [ ] 5.2 Memo and text sharing; a user's own uploads marked "für das Netzwerk" at upload time
- [ ] 5.3 Measurement per board: time to first draft, proposals offered / taken, posts, inquiries (events.csv)
- [x] 5.4 German UI for the whole board (du-Form), 03.11. late
- [x] 5.5 Groups: a board belongs to one or more groups (04.11.: `groups` list in users.json, users/<slug>/config.yaml and root config; admin creates with a comma list and edits per row); match.py proposes only between boards with a common group; `network.json` per board (my groups, members, shared counts)
- [x] 5.6 Proposal feed on the Post tab ("Für dich gefunden") with Ja / Nein / Post ansehen, badge on the tile; share at upload time (checkbox)
- [x] 5.8 Profil tab (04.11.): network, about, topics and never-topics, tone (register, length, question at the end, own words, example posts), facts, sharing default, password change. api `profile_save` -> decision `profile_save` -> apply_decisions: profile.json, profile.md, positioning.md (incl. "Nie"), examples.md, new topics straight into the inventory (no model call); draft.py reads register/length/question/examples, rules_check.py length and question per profile, inventory.py never-topics
- [x] 5.9 Invite from any board (04.11.): `board/boards.php` (create, registry, self, network), api `invite` (new board in one of my teams or a new team, 20 per day, one-time text with link + start password, WhatsApp / mail / copy / share), api `team` (join, leave), state `board`, `network` from the registry (immediate), `invites` with login state; admin uses the same library and shows "eingeladen von"; Anton is registry entry `anton`, `users/.registry.json` is the worker's copy and wins for his groups
- [x] 5.7 Phone layout: nothing in the pipeline column may exceed the screen (long buttons pushed the Published rows off-screen)
