# Proposal: boards for other people (multi-user)

## Why
Anton's content system worked for one person. Since 03.11.2026 a second person (first pilot: Andreas Bentele-Krickl, BNI Gilching) gets their own board: own link and password, own memos, photos, drafts and publishing, and the system may lay material another board has shared under their draft ("Das System holt, was passt"). Setup must be done by an admin page, not by hand on the Mac.

## What changes
- A board = a directory on the host (`board/<token>/`, same code, own `data/`) and a directory on the worker (`users/<slug>/`: library, campaign CSVs, mirror, token, config). `BOARD_USER=<slug>` switches every pipeline script (common.py); Anton's board is the default and unchanged.
- Login: `data/auth.json` with a password hash makes a board private; session cookie 30 days (HttpOnly, Secure, SameSite), five wrong passwords lock 15 minutes, first login forces a new password. No auth.json = open board behind its link (Anton).
- Admin page `board/admin/` (own password, `users.py admin`): create a board, reset a password, disable. Registry `~/board-worker/users.json`; the worker's `users.py sync` creates `users/<slug>/` and deploys code.
- Onboarding on the board: website, own words, optional document -> one model call -> profile proposal -> the person corrects and confirms -> facts (`profile.md`), positioning, topic inventory, first draft. Nothing invented; open points listed.
- Sharing: a photo can be marked `share: network` on the Photos tab (single or whole series), withdrawable. Shared photos are never posted by themselves.
- Matching: `match.py` offers at most one shared photo of another board under an open draft (word overlap shortlist, one small model call per card); "Ja, nehmen" copies it into the pool, puts it on the card and adds "Foto: <owner>"; the owner sees the use on their board. "Nein" or "nothing fits" is remembered.
- Groups: every board has a group (default bni-gilching); sharing and proposals happen only inside a group. A second chapter or a client team is a second group, same code.
- Board UI in German, du-Form, for everyone (03.11. late); the admin page too.
- Groups (04.11.): a board is in one or more groups; only boards with a common group get each other's shared material. Admin sets them at creation and per row later; the worker carries them into `users/<slug>/config.yaml`.
- Profil tab (04.11.): the person shapes the model without seeing a prompt: facts, topics, never-topics, tone as three choices plus own words and example posts, sharing default, password. Saved as one decision; the worker rewrites profile.md, positioning.md and examples.md and puts new topics into the inventory.
- Publishing per board: `server/publish.php` uses `linkedin-<slug>.json`; without a token the card says "post it yourself" (Copy text) as before.

## Decisions taken (03.11.2026)
- Model calls on another person's board run in the background (`llm.auto: true` in `users/<slug>/config.yaml`): self-onboarding needs it. Anton's board keeps `llm.auto: false`.
- The worker stays the Mac for every board; a user's memo is transcribed when the Mac runs.
- Board UI stays English except the new parts (login, onboarding, sharing, proposal), which are German, du-Form.

## Out of scope
LinkedIn OAuth through the server (a user connects LinkedIn later, on the Mac with Anton), memo and text sharing (photos only), teams, pricing, Google login.
