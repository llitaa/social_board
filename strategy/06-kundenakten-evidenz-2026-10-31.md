# AlpiType — client evidence for the conversion question

**Date:** 2026-10-31
**For:** the agent working on "LinkedIn → paying customers" (reply to `alpitype_linkedin_conversion_new_context_2026-10-31.md`)
**From:** the agent running the LinkedIn system and the client dossiers in `~/dev/ai-automation/business/`
**Scope:** only what the repositories and Anton's statements actually show about real opportunities. No prices or rates invented; every number below is one that was offered, paid, or said by the client. Where a fact comes from Anton verbally and is not in a file, it is marked "per Anton".

---

## 0. The short version

- Seven real opportunities since June 2026. One won (ZAMM, 11.870 €), one offer sent and waiting for funding (Bogner, 19.960 €), one offer parked (Fixmer, 7.560 €), one large offer in its seventh version and not closed (Blauth platform, 93.750 €), one large offer drafted and never sent (Promeda, 23.970 / 56.960 €), two leads with concept only (Ponholzer, Blauth holding).
- **All seven came warm**: BNI chapter (Fixmer, Ponholzer), personal network and WhatsApp (ZAMM, Bogner), referral through an intermediary (Promeda via Dennis Hundt), a personal contact (Blauth). **Zero came from LinkedIn**, zero from a cold channel. The cold-call list for Handwerk (20 firms, prepared 12.10.) has not been dialled: every row is still "neu".
- The buyer in every case is the owner. Every owner said the same sentence in the first call: the office work lands on them in the evening (Aeneas, Andre, Philipp). That sentence, not "AI", is what sold.
- The friction the other agent asks about is visible in three dossiers: **the client cannot picture the result** (Bogner asked for two hours before signing; Blauth misread the IP clause as "you will sell my platform to competitors" and could not tell whether the price would end at 100 k; Promeda's managing director anchored on 25 k from a phone estimate and then added requirements worth +33 k in the next call).
- Two forces drive every price: **Digitalbonus Bayern** (50 % grant, Standard cap 7.500 €, Plus from 15.000 € eligible spend) and **the owner pre-financing the whole amount**. Without the grant none of the Handwerk deals would have been priced as they were.

---

## 1. The opportunities, one by one

### 1.1 ZAMM (Z.A.M.M. GmbH Malermeisterbetrieb, Fürstenfeldbruck) — won
- Owner Aeneas Zimmermann, painter business, ~30 e-mails a day, two managing directors read one shared inbox. Contact via WhatsApp and voice messages, "Du".
- What was bought: Microsoft 365 e-mail automation (draft replies for approval), invoice handling, VAT monitor. **Option 2, 11.870 € net**, own share 5.935 € after Digitalbonus Standard. Maintenance 199 €/year optional.
- **What sold it:** a surprise VAT payment of about 10 k€ in the month he had planned a machine purchase. The VAT monitor turned a vague "e-mail automation" into a thing with a visible loss attached. Note: the pain was money, not time.
- Boundaries he insisted on: no chatbot, no bank integration, no filing of the VAT return (preparation only).
- Path: analysis June 2026 → concept with options August → chose Option 2 → Digitalbonus application window Mo 02.11.2026 10:00 (October quota was exhausted; the GmbH is new, so figures are estimated "nach Treu und Glauben"). Contract signed only after the funding confirmation. Nothing delivered yet.
- Anton's own view (10.10.): 11.870 € was a pilot price; future projects should be ≥ 15 k€.
- Files: `zamm/notes.md`, `zamm/offers/ZAMM-Angebot-AN-2026-001_2026-08.pdf`, `zamm/funding/`.

### 1.2 Andre Bogner (Bogner Schädlingsbekämpfung, Oberhaching) — offer sent 08.10., waiting for the funding window; **asked for two hours of consultancy before signing** (per Anton, 31.10.; not yet in the dossier)
- Solo pest-control business, 2 to 4 jobs a day, recurring property-management clients. Systems: Debuxx (industry tool, 180 €/month, no API), IONOS mailbox, Google Calendar, ChatGPT Pro.
- Telling detail: **he had already built his own automation** with ChatGPT Pro ("Second Brain" project, a browser agent that fills Debuxx from the e-mail subject). Still 1.5 hours of admin every evening. So this buyer is not AI-illiterate; he hit the ceiling of what prompting gives him.
- Budget history: first call August **"about 5.000 € total"**. September analysis priced step 1 on n8n at 4.970 €. After Anton decided against GUI automation and n8n, and after Andre wrote his own target picture (voice note after the job → invoice draft → approve → send), the offer became **19.960 € in four positions, Digitalbonus Plus 50 % → own share 9.980 €**. Anton's reading: the ticket grew when it stopped being "a helper" and became "his digital back office". The Handwerk plan records this as "ticket readiness comes from ambition, not from company size".
- Risk recorded: Digitalbonus Plus requires demonstrated innovation; the FAQ says individual programming is "per se nicht innovativ". If only Standard is granted (7.500 € cap), the own share roughly doubles. Anton promised to "talk" in that case, no number in writing.
- Send set 08.10.: project sketch (4 pages, "Vom Einsatz zur Rechnung in zwei Minuten"), offer, 6-page Digitalbonus application manual with every form field pre-filled. Application window Mo 02.11.2026 10:00.
- **The two-hour request** is the test case the other agent asks about. What the dossier suggests he still lacks, in order of likelihood: (1) a picture of his own working day with the system, step by step, not a feature list; (2) certainty about what happens to Debuxx and his 280 old invoices; (3) what he is on the hook for if the grant is Standard, not Plus. Open: whether he expects the two hours free. The repo has no answer; Anton decides.
- Files: `bogner/README.md` (file map and status), `bogner/Bogner-Kontext-Stand-intern_2026-10-07.md` (the handover context), `bogner/offers/`, `bogner/funding/`.

### 1.3 Fixmer GmbH (Haus- und Objektbetreuung, Gilching; BNI) — offer ready since 21.08., parked by Anton on 17.10.
- Father and son, both managing directors, both on sites all day. Pain: 30 to 40 phone calls a day, each interrupts; a second pain, the mechanics' "I'll be there in 45 minutes" calls that must be answered or the appointment dies.
- Offer: AI phone assistant (triage incoming calls, emergencies put through, rest as ticket; mechanic calls checked against Outlook and confirmed by SMS). **7.560 € fixed, ≈ 3.780 € after Digitalbonus**, running costs about 115 to 130 €/month (fonio.ai plus Azure/SMS). Budget he named: 3 to 10 k€.
- Market check in the dossier: ready-made trade phone assistants exist from 99 €/month (Foncall, Vokaro); classic phone services 200 to 400 €/month. AlpiType's difference as written: emergency logic with his property-management context, a case list instead of loose messages, operation by AlpiType.
- Status: send set never recorded as sent; parked 17.10. Reason not in the file.
- Files: `fixmer/notes.md`, `fixmer/offers/`, `fixmer/funding/`.

### 1.4 Promeda Hausverwaltung GmbH, Berlin (via Dennis Hundt) — offer drafted 03.09., not sent; **rejected / budget 5 to 15 k€** (per Anton via the other agent's brief; the rejection is not in the dossier)
- 4.350 units, haussoft (on-prem SQL Server ERP), facilioo (portal, Gen2 API), Microsoft 365. Managing director and decision maker Marcel Kurzke; Dennis Hundt is co-shareholder and the AI sponsor. 25 to 30 incoming invoices per working day.
- What they wanted: four modules on one data basis (e-mail assistant with context from both systems, invoice intake into haussoft, knowledge base with chat, phone later). Their own paper said: EU cloud in Promeda's name, AVV with AlpiType, source code and documentation part of the delivery, haussoft and facilioo stay.
- Price history, the most instructive in the folder:
  - Call 02.09.: Anton named **≈ 25.000 €** for platform plus e-mail assistant, PoC included; chat later 12 to 25 k€. Marcel accepted the number twice.
  - Same call: quality bar "a new colleague could answer from the draft" (history, resolutions, contracts) → document index needed already in the e-mail module → requirements worth about 15 k€ added in the call, about 5.6 k€ own corrections (identity resolution, tests, staging).
  - Internal calculation v3 at 919 €/PT with 30 % buffer reached 67.870 / 89.470 € for the two context levels. Anton then cut back to **Option 1 "as discussed" 23.970 € / Option 2 "after the call" 56.960 €**, LP0 analysis 3.990 € first for both, knowledge base 12.990 / 24.990 as non-binding estimate.
  - The offer (8 pages, 20+ review rounds on 03.09.) was final and **never sent**. Per the other agent's brief the client later signalled 5 to 15 k€. That is a 4× to 10× gap between what a 4.350-unit property manager pictured and what the stated requirements cost.
- Lessons already written in the dossier: the 25 k anchor was a Stage-1 spot estimate; the client's own quality demand defined Stage 3; nobody priced a buffer before v3; a second developer would be needed for a solo duration of 28 weeks.
- Files: `hundt-hausverwaltung/README.md` (the full map), `notes.md`, `differenz-25-25-2026-09-03.md`, `offers/Promeda-Angebot-202603091-AlpiType_2026-09-03.pdf`.

### 1.5 Sven Blauth — Immobilienvisionäre GmbH / Blauth & Team Versicherungsvisionäre GmbH (Kaiserslautern) — platform offer, seven versions, not closed
- Property developer and insurance broker, about 12 staff, 400 customer records, target 3.000 to 5.000. Vision: a "real estate investment platform" for private investors buying 1 to 4 flats; USP simplicity; later a licence product for other brokers. CRM today: onOffice.
- Price history: v2 60.000 € (22 weeks) → v3 75.000 € (Anton: 60 k left no room for iteration) → v4 same, funding corrected to Rhineland-Palatinate → v5 75.000 € in M0 gate plus M1 to M5, sent 27.09. → **call 28.09.: disappointed**. Two reasons in his words: the IP clause ("no exclusivity, re-use in similar solutions") read as "you will sell my platform to competitors"; and the two-step price with a gate adjustment read as "I do not know whether it ends at 100 k". Funding was irrelevant to him. He was willing to go above 75 k.
- v7 = "Version 2" for Sven, 29.09.: **93.750 € fixed**, budget frame max. 103.250 € under named assumptions, one contract, signature covers M0 (8.500 €) with M1 to M6 prices fixed, IP clause "the platform is your product", about 9 months. E-mail drafted 29.09. Current status after that date: not in the notes.
- The credibility point from the other agent's brief ("sole proprietor") appears in the dossier as: his adviser Leo said 75 k is too low for a product and recommended building on HubSpot; the internal concept v5 lists "Risikomassnahmen Einzelunternehmer"; the contract has a clause for transferring it to a company Anton may found. Delivery needs a second developer (Oleksandr Lytvynenko is being onboarded with a Ukrainian context document).
- Second lead from the same client, 02.10.: AI assistance across the holding (insurance, property sales, property management), e-mail reply drafts, shared knowledge, companies must remain separable. No concept yet. They are M365 users and mentioned Copilot themselves.
- Files: `~/dev/blauth-immobilienplattform/notes.md` (long, chronological), `docs/Blauth-Angebot-v7-2026-09.pdf`, `docs/intern/M0-Analyse-Risiken-Preis-2026-09-28.md`; `~/dev/blauth-holding-automation/notes.md`.

### 1.6 Dr. Florian Ponholzer (law firm, Planegg; BNI) — concept sent August, no reply recorded
- Use case: fill foreclosure applications from client documents. Professional secrecy (§ 203 StGB) → on-premise server recommended. GbR of lawyers → **no Digitalbonus**.
- Concept priced in ranges, deliberately: hardware 3.000 to 5.500 € (dealer), AlpiType application 6.000 to 12.000 €, IT setup by his IT provider. ROI left as a formula with his own numbers (applications per month × minutes per application); the dossier records why: an invented example volume would be a trust risk.
- Market check: law-firm software with a foreclosure module fills forms only from manually maintained master data; no "documents in, application out" product found. That was meant to be the ROI core.
- Outcome: the e-mail ended with "it depends on two numbers". No numbers came back. Reading: a concept with a clean argument and no deadline does not move a lawyer who never asked for a meeting.
- Files: `ponholzer/notes.md`, `ponholzer/offers/Ponholzer-Loesungskonzept-2026-08.pdf`.

### 1.7 Handwerk cold outreach (plan 12.10., evaluation 10.10.)
- Goal set 09.10.: one more Handwerk project (≥ 15 k€, Digitalbonus) by 31.12.2026, phone first (60-second permission ask), e-mail only after a spoken yes (cold B2B e-mail is unlawful under § 7 UWG), 1 hour a day, max. 4 touches.
- ICP derived from the three wins: owner does the office in the evening; recurring B2B customers (property managers, trade, developers); Elektro, SHK, roofing first; 5 to 25 staff; Bavaria within 60 km; already somewhat digital.
- Market data in the evaluation: 1 to 9-person firms average 3.3 people and 266 k€ revenue; Bitkom: 84 % "KI kein Thema"; 15 k€ fits 10 to 49-person Elektro/SHK and property managers. Critic's risks: price frame in the mail, warm offers not sent, delivery collides with Anton's running contract, owner reach per dial 25 to 35 %.
- **Status: 20 firms listed, 0 calls made.** Fixmer parked 17.10. The referral ask to the four existing clients ("who in your circle drowns in office work the same way?") is in the plan, not recorded as done.
- Files: `~/dev/campaign/handwerk/plan.md`, `evaluation-handwerk.html`, `calls.csv`.

---

## 2. What the seven cases say about the brief's questions

### 2.1 Audience and reach (brief §2A, §6.4)
- Fact: no client came from LinkedIn. The LinkedIn system has published 24 posts since July; the only post with real reach (3.121 impressions, 16 reactions, 04.09.) was a personal freelance-availability post to a developer audience. Metrics for everything after 10.09. are missing because the analytics API is not available on Anton's token and no export has been done.
- Fact: every client was an owner of a 1 to 15-person firm or a developer with 12 staff, reached through BNI, WhatsApp, a referral or a personal contact. The "founder without engineering" category the LinkedIn series targets since 30.10. does not appear among the seven; the closest is Sven Blauth, and he came through a personal contact, not content.
- Consequence for the other agent: treat LinkedIn as a trust layer for people who already heard the name (every one of the seven can look at the profile before the second call), not as a lead source, until an export shows otherwise.

### 2.2 Why interested people do not buy (brief §2B, §6.3)
Observed, not hypothesised:
1. **The client's picture of the price is formed before the requirements are** (Promeda 25 k → 57 k; Bogner 5 k → 20 k; Blauth 60 k → 94 k). In two of three cases the number moved up because the client's own quality demand grew in the second conversation. The one that closed (ZAMM) had options with fixed prices in a concept document before the decision call.
2. **The client cannot read a software offer as a day in their life.** Bogner wrote his own target picture as a PDF and still wants two hours. Blauth rejected a text-heavy big-picture document; the visual canvas with four boards ("Customer Journey", "Kampagne → CRM", "Sales-Dashboard", "Kunden-Dashboard") is what made him say "we want the offer" on 21.09. Fixmer's send set includes a two-page "So funktioniert es" with the two call flows as pictures, written for the father.
3. **Contract language scares more than price.** Blauth's two objections were the IP clause and the open-ended gate, not 75 k. Promeda's own paper demanded AVV, source code and documentation before any price was discussed.
4. **Funding is the real calendar.** ZAMM and Bogner both wait for the first working day of a month at 10:00. Nothing is signed before the funding confirmation. A sales motion that ignores the Digitalbonus window is out of step with how these owners decide.
5. **Capacity doubt is real and comes from advisers, not from the owner.** Leo at Blauth; Dennis Hundt at Promeda asked for an "honest assessment" of n8n and RPA proposals from third parties. Both times a second opinion sat next to the owner.

### 2.3 Competition (brief §2C, §6.2)
- The dossiers contain three concrete market checks, all against ready-made products, none against other consultants: trade phone assistants from 99 €/month (Fixmer), law-firm software with foreclosure module (Ponholzer), haussoft's own "Rechnungsdatenimport" and "Rechnungseingang Plus" modules (Promeda), onOffice and HubSpot (Blauth), Debuxx and Lexware Office (Bogner).
- In every case the written differentiation is the same three things: **the client's context in the logic** (which property manager, which object, what counts as an emergency), **a case list with approval instead of loose outputs**, and **code in the client's environment with an exit** (EU cloud in the client's name, source code handed over, no platform rented). Bogner's history is the sharpest proof available: he had the "prompt expert" solution himself and still had 1.5 hours of evening work.
- No DACH competitor comparison exists in the repositories. That research is genuinely open.

### 2.4 Pricing facts the other agent may use (no invention needed)
| Item | Value | Source |
|---|---|---|
| Internal target day rate | 919 €/PT (Promeda, Bogner); 870 to 950 €/PT effective (Blauth) | calculations |
| Buffer | 30 % inside every price since 03.09. (none before) | Promeda v3 |
| Position prices end on …90 | house rule | business/CLAUDE.md |
| Maintenance package | 199 €/year (2 h), further hours 114,90 €/h | ZAMM, Fixmer, Bogner |
| Operation packages (platform) | 790 €/month (6 h) and 1.890 €/month (12 h) | Blauth v7 |
| Analysis / entry phase | LP0 3.990 € (Promeda), M0 8.500 € (Blauth) | offers |
| Smallest and largest fixed prices offered | 7.560 € (Fixmer) to 93.750 € (Blauth) | offers |
| Digitalbonus | Standard 50 % up to 7.500 €, Plus 50 % up to 30.000 € from 15.000 € eligible spend, one per company, application before order, owner pre-finances | digitalbonus.bayern, verified 06.10. |
| Rejected invented prices | 290 to 490 € workshop, 1.500 to 3.000 € scoping | Anton, 31.10. |
What is missing for the "offer design" question: delivery margins per project (only Promeda and Blauth have an effort-vs-price table), and the real subcontractor rate for the second developer (open assumption 55 to 80 €/h in the Blauth calculation).

### 2.5 Delivery capacity (brief §6.1)
- Anton has a running engineering contract through 31.12.2026 that takes most of the week (confidential, do not name), a job search for an engineering-manager role, and no employed developer. Oleksandr Lytvynenko is being onboarded as developer for the automation cluster. The Handwerk evaluation names this collision as a top risk.
- Shared code base exists: `~/dev/ai-automation/m365-automation` (mail, voice, documents, calendar, client knowledge, approval, cloud deployment), meant to make the small projects repeatable. Anton's rule: custom code on that core, not n8n; low-code only where the client must maintain it inside Microsoft.

---

## 3. Rules the other agent must respect
- Prices are Anton's. Propose ranges only from the table above or from new research with sources.
- Client names: ZAMM, Bogner, Fixmer, Ponholzer, Promeda, Blauth are internal; none has a reference release. Publicly nameable past clients are only Rheinmetall (project via Normalis), Brainlab, FlashCut CNC, Udikon; never Infineon, Leica, Siemens, Reiser. Warden Robotics: "arbeiten zusammen", not a client.
- The workshop on alpitype.de was never delivered; only offered.
- No AI attribution in any document. Client documents are by Anton Lytvynenko / AlpiType, built with `~/.claude/templates/alpitype_doc.py`.
- No background model calls in the LinkedIn system; model work only via `pipeline/process.py` in a terminal.
- Anton wants short documents: decision first, one line of why, separate small action docs.

---

## 4. Open questions only Anton can answer (please collect them in one list, not one by one)
1. Bogner's two hours: paid or free, and what exactly he said he cannot picture.
2. Promeda: what was said when they signalled 5 to 15 k€, and whether the LP0 at 3.990 € was ever put to them.
3. Blauth: status since 29.09. (Version 2 sent? reply?), and whether the holding project is alive.
4. Fixmer: why parked on 17.10.
5. Whether the referral ask to ZAMM, Bogner, Fixmer, Blauth has been made.
6. Whether the Handwerk calls will happen at all, given the contract until year end.

---

## 5. Where everything lives
- Pipeline overview (one row per client, partly stale for Bogner): `~/dev/ai-automation/business/pipeline.md`
- Client folders: `~/dev/ai-automation/business/{zamm,bogner,fixmer,hundt-hausverwaltung,ponholzer}/` (README = file map, notes = chronology, offers, funding)
- Blauth: `~/dev/blauth-immobilienplattform/`, `~/dev/blauth-holding-automation/`
- Handwerk outreach: `~/dev/campaign/handwerk/`
- Company facts and naming rules: `~/.claude/alpitype/company-context.md`
- LinkedIn system handover (all posts, pipeline, board): `~/dev/linkedin-system/docs/handover/handover-2026-10-31.md`
