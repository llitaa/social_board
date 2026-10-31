title: LinkedIn-System: Verbesserungsplan, Review
subtitle: Plan des zweiten Agenten vom 31.10.2026, geprüft gegen das Repository, mit Ergänzungen und offenen Entscheidungen
footer: AlpiType · Intern · Review Verbesserungsplan · 31.10.2026

## 1. Verdict

The plan is right in its core and I would implement it: keep the memo → board → publish chain, no lead funnel, no new architecture, sales follow-ups as a separate process. Four things need correcting before it becomes a work order: the cadence it assumes is wrong, the metadata it proposes half exists already, it drops the series decided on 30.10. without saying so, and it treats the missing metrics as a known unknown instead of the first task. Implementation of the "must now" part is about half a day and costs no model tokens.

## 2. Facts to correct in the plan

| Plan says | Repository says | Consequence |
|---|---|---|
| "three posts per week" | `config.yaml`: personal Mon, Wed, Fri 07:30 plus company Thu 09:00 = four slots; Mon and Fri take an engagement pillar first | Keep four. The company page is missing from the plan entirely; it stays as is (EN, by hand until the API exists). |
| Add fields `primary_reader`, `core_insight_and_evidence`, `why_worth_discussing` | Every draft JSON already carries `pillar`, `topic`, `memo`, `photo`, `card` and `signals` (a lead signal and an AI signal, which is the evidence). `rules_check.py` already checks banned phrases and orthography. | Add two fields, not three: `reader` and `why`. Evidence is the existing `signals`, renamed on the board. |
| "editorial guidance, not fixed quotas" | `library/positioning.md` (30.10.) defines the series "Nach dem Go-live", Mon and Fri, diagram instead of photo, four pillars, target "founders without a technical background". Six candidates are rendered and wait for Anton's yes. | A silent conflict. Either the series runs as a six-episode test or it is dropped. That is Anton's call, see section 4. |
| Analytics "incomplete, a known unknown" | No numbers for any post since 10.09. The API is not available; the pipeline reads LinkedIn exports from ~/Downloads, none has been dropped there. | Without one export now, the six-week criterion cannot be judged. Export is task zero. |
| "Record inbound and referrals" | `posts-log.csv` has no source column; there is no inbound log at all. | New small file `inbound-log.csv` in ~/dev/campaign, four columns, filled by hand weekly. |
| ZAMM: "funding and signature pending" | Correct. Application window Mo 02.11.2026 10:00, contract after confirmation. | No case study, no numbers in posts. |

## 3. My input to each proposed change

| Proposal | Input | Decision |
|---|---|---|
| Metadata per post | Yes. `reader` (one line: who this is for) and `why` (one line: why it is worth their comment) go into the draft prompt in `draft.py`, into the JSON, onto the card via `cards.py`, and the board shows them in small type under the hook. No new step, no new approval. | implement now |
| Editorial guidance (engineering and AI judgment, prototype to business system, ownership and leadership) | Agree with the three themes; they are the technical reading of the four pillars already in positioning.md. The wording "founders without a technical background" should become "people who carry software responsibility, with or without a team": the evidence says the readers are engineers, architects, CTOs; the buyers so far were owners who found Anton through people exactly like those readers. One sentence changed in positioning.md, the rest stays. | Anton confirms wording |
| Graphics only when useful | Agree for the Wed photo posts. For Mon and Fri the series is the test of whether a diagram earns comments; six episodes, then judge by comments and DMs, not impressions. The renderer and checker exist; the missing piece is `episode.py` (topic in, two candidates out), roughly one day. | Anton: run the six-episode test, or not |
| Claims and anonymization | Already in positioning.md and rules_check. Add the client names ZAMM, Bogner, Fixmer, Promeda, Hundt, Blauth, Ponholzer, Debuxx, haussoft, facilioo to the banned list in `rules_check.py`, so a draft cannot leak them by accident. Illustrative scenarios get the word "Beispiel" in the text. | implement now |
| Review board | Show `reader`, `why` and the existing signals beside each draft. Ten lines in `board/index.php`, data already flows through cards.json. | implement now |
| Measurement | Two parts. (a) `inbound-log.csv`: date, source (LinkedIn, referral, existing relationship, unknown), who, what, next step. Anton fills it in the weekly review; the board shows the last five rows under Published. (b) One LinkedIn export every two weeks into ~/Downloads; the pipeline writes the numbers into posts-log by itself. | implement (a) now; (b) is Anton's habit |
| What not to build | Agree with the whole list. I add: no Betriebs-Check page and no checklist PDF until the series has produced one DM that asks for it. | agreed |
| Sales actions | Agree. Concrete additions in section 5. | Anton |

### Before and after on a real draft

li-post-20 (draft for 02.11., "Der Mensch reagiert, die KI initiiert", pillar thought, topic t042). Today the board shows: status, channel, pillar, slot, hook, text, photo. After the change it also shows:

> **Reader:** a team lead who has one or two developers working with agents and sees the humans becoming passive.
> **Evidence:** the lead signal already in the draft: "Für die Arbeitsteilung habe ich daraus eine Regel gemacht …" (the rule Anton set in his own team).
> **Why worth a comment:** the question at the end asks who in the reader's team still initiates; a CTO can answer that from memory.

Text and photo unchanged. If `reader` cannot be written in one line, the draft is not ready; that is the whole point of the field.

## 4. Decisions for Anton

1. **Target wording** in positioning.md: "people who carry software responsibility, with or without a team" instead of "founders without a technical background". Yes or no.
2. **Series test:** six episodes of "Nach dem Go-live" on Mon and Fri, judged by comments and DMs. If yes: E or F for the first one.
3. **Inbound log** as a CSV filled weekly by hand. Yes or no.
4. **LinkedIn export** every two weeks into Downloads. The only way to numbers.
5. **Bogner two hours:** paid or free, and what he said he cannot picture. Decides what the walkthrough document must show.
6. **Referral ask** to ZAMM, Bogner, Fixmer, Blauth (the sentence is in the Handwerk plan, step 6). This week or not.

## 5. Sales actions outside the repository, made concrete

- **Bogner walkthrough.** Two pages in the house style on the Fixmer pattern ("So funktioniert es"): his day with the system as a picture (voice note after the job, draft on the phone, approve, invoice and treatment record sent), what happens to Debuxx and the 280 old invoices, what changes if only Digitalbonus Standard is granted. Built from the existing offer and sketch, half a day, before the two hours. The two hours then become the review of that document, not a lecture.
- **Blauth.** One question to Anton: was Version 2 (29.09.) sent, and what did Sven say. Only then a next step.
- **ZAMM.** 02.11. 09:55 screen share with Ines and Aeneas is already in the dossier. Referral or testimonial request only after the contract is signed.
- **Referral test.** Four contacts, one sentence each, logged in inbound-log.csv with source "referral". Measured by qualified conversations in four weeks, not by replies.

## 6. Implementation plan for the LinkedIn system

**Must now (half a day, no model cost)**
- `pipeline/draft.py`: prompt asks for `reader` and `why` as one line each; both stored in the draft JSON next to `signals`.
- `pipeline/import_draft.py`: accepts both fields for drafts written outside the pipeline.
- `pipeline/cards.py`: passes `reader`, `why`, `signals` to cards.json.
- `board/index.php`: three small lines under the hook of every draft; last five inbound rows under Published.
- `pipeline/rules_check.py`: client names and tool names added to the banned list.
- `~/dev/campaign/inbound-log.csv`: created with header; `cards.py` reads it.
- Redrafts of existing drafts are not needed: the two fields are added by the next `process.py` run for the drafts that lack them.

**Optional later**
- `pipeline/episode.py` for the series (one day). Only after decision 2.
- Comment and DM counts per episode in posts-log and the "no comment yet" line on the board (openspec task 2.2).

**Do not implement**
- Newsletter, landing page, lead magnet, connection automation, scraping, attribution model, forced CTA, workshop pricing, Betriebs-Check page before a DM asks for it.

## 7. Six-week criterion, made checkable

- Every draft on the board carries `reader` and `why` in one line each, or it is not approved.
- posts-log has numbers for every post of the period, from two exports.
- inbound-log.csv has an honest row for every DM, introduction and meeting, including "none".
- If the series runs: comments per episode, written next to the episode. No target number; the comparison is against the Wed photo posts.
- Sales progress is read from the dossiers (Bogner contract, Blauth answer, ZAMM confirmation, referral conversations), not from LinkedIn.
