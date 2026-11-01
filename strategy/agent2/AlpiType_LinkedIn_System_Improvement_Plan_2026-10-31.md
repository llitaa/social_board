# AlpiType — LinkedIn system: what to change, why, and how

**Decision memo and implementation brief | 31 October 2026**

> **Decision:** Keep the existing three-posts-per-week LinkedIn system. Make a small, evidence-based editorial improvement. Do **not** build a speculative lead-generation funnel. Run warm-client follow-ups and referral requests as a separate sales process.

## 1. What changed: actual client evidence

| Observed fact | What it means for the system |
|---|---|
| Seven opportunities; **zero sourced from LinkedIn**. All came through warm contacts or referrals. | Do not optimize the posting pipeline for an unproven direct-lead channel. |
| Bogner had already built an AI assistant but still spent roughly 1.5 hours per evening on administration. | Explain the gap between a working AI demo and an integrated, dependable business process. |
| ZAMM chose an option linked to a concrete VAT-related financial risk; funding/signature still pending. | Illustrate business consequences, not generic AI features. Do not claim delivered results. |
| Blauth responded to visual process canvases; IP and budget certainty remained obstacles. | Use visual workflows to make system ownership, boundaries and decisions understandable. |
| Existing followers are largely engineers, architects, CTOs and recruiters. | Treat them as actual readers, potential technical buyers and referrers—not as imaginary nontechnical founders. |

**Interpretation, not proven fact:** The existing technical network may generate referrals when contacts recognize that a business needs engineering beyond prompts and isolated automations. This is a hypothesis to test, not a proven acquisition channel.

## 2. Exact changes to the existing LinkedIn pipeline

| Component | Change now | Why / acceptance test |
|---|---|---|
| **Topic selection and drafting** | Add three lightweight metadata fields per proposed post: `primary_reader`, `core_insight_and_evidence`, `why_worth_discussing`. | No unsupported buyer assumptions. Fields visible in board or draft metadata. |
| **Editorial guidance** | Prefer (a) engineering and AI judgment, (b) prototype-to-business-system lessons, (c) technical ownership and leadership. **Not fixed quotas.** | Topics remain grounded in voice notes, real experience or cited research. |
| **Graphics** | For system posts, suggest a simple before/after workflow or decision diagram **only when useful**. | Reuse existing graphics generator; no invented client outcomes. |
| **Claims and anonymization** | Do not name current clients or reveal sensitive project details without explicit permission. Label illustrative scenarios. | No unapproved client references, confidential details or fabricated numbers. |
| **Review board** | Display reader, key claim and rationale for any graphic beside each draft. | Anton can assess drafts quickly, without extra workflow steps. |
| **Measurement** | Record real post engagement where available and manually noted relevant inbound/referrals. Mark missing data explicitly. | No invented reach, buyer segmentation or revenue attribution. |

**Preserve without changes:** Voice memo → transcription → drafting → board review → publishing; three posts/week; existing visual generator; explicit model calls via `pipeline/process.py` (no background LLM calls).

**Implementation constraint:** The other agent must inspect the actual repository before choosing files or designing schema migrations. The metadata names above are suggested fields, not claims about existing code.

## 3. What changes in Anton's weekly workflow

| When | Anton does | System / result |
|---|---|---|
| Existing drafting session | Records spontaneous voice notes as usual and reviews drafts on the board. | Claude proposes posts and, where useful, visuals, with a clear reader and evidence. |
| Before publishing | Checks technical accuracy, confidentiality and whether the text sounds like Anton. | Publishes normally. **No mandatory sales CTA.** |
| Separate sales slot | Follows up Bogner, Blauth and ZAMM; asks for a few warm introductions when appropriate. | Real sales conversations, not imaginary LinkedIn automation. |
| Short weekly review | Notes relevant DMs, introductions and meetings, with actual source. | Simple categories: LinkedIn / referral / existing relationship / unknown. |

**Net new burden:** Only a brief review of the additional draft context and a short factual note on any inbound lead. Do not require Anton to research every post or invent personal experiences.

## 4. What not to build yet

Do **not** add a newsletter, new landing page, lead magnet, automated connection requests, contact scraping, LinkedIn-to-revenue attribution model, forced CTA on every post or unvalidated workshop pricing. Those need separate evidence and commercial decisions.

## 5. Sales actions outside the LinkedIn repository

1. **Bogner:** Prepare a visual walkthrough of his working day, Debuxx integration limitations, legacy data and funding scenarios before the requested two-hour discussion. Clarify meeting scope and whether it is paid before committing.
2. **Blauth:** Check whether the revised offer was sent and what decision remains. Address delivery confidence, IP ownership and price certainty—not another generic AI pitch.
3. **ZAMM:** Follow the funding/signing sequence. Request a referral or testimonial only at an appropriate stage; no public case study without permission.
4. **Referral test:** Ask a small number of trusted contacts for introductions to owners with complex, repetitive workflows that simple AI tools have not solved. Track introductions and qualified conversations, not follower counts.

These are **separate commercial actions**. Do not silently convert them into LinkedIn pipeline tasks.

## 6. Instructions for the other agent

Inspect `~/dev/linkedin-system` and return a **minimal diff plan**, including:

- Exact existing files and stages to modify, after verifying the repository.
- Minimal metadata schema and where each field is generated/stored.
- Specific board display changes that do not add a new approval step.
- Claim/confidentiality safeguards for unpublished client work.
- One before/after example showing how a real draft improves.
- Clear separation of **must implement now**, **optional later** and **do not implement**.

**Do not** implement a CRM, outreach automation or a new publishing architecture as part of this task.

## 7. Success criteria and open questions

**Six-week criterion:** The system reliably produces accurate, recognizable engineering content with minimal extra effort. Record any inbound opportunities honestly. Assess sales progress separately via follow-ups, introductions, meetings and signed work. No guaranteed conversion-rate targets.

**Known unknowns:** LinkedIn analytics after 10 September are incomplete; audience buyer composition is unmeasured; there is no DACH consultant competitor benchmark; Bogner meeting terms and current Blauth status remain unresolved. None may be silently treated as known.

**Evidence basis:** `client-context-2026-10-31.md` (seven opportunity dossiers and constraints), the existing LinkedIn-system handover, and our discussion. Recommendations and hypotheses are distinguished from observed results.
