# Design

## Context
Member posting via the self-serve "Share on LinkedIn" product needs no review; company-page posting needs the Community Management product and LinkedIn's review. Self-hosted open-source schedulers (e.g. Postiz) wrap both but add services to run.

## Goals / Non-Goals
**Goals:** approved → live at slot, logged; minimal scopes. **Non-Goals:** analytics via API, any engagement, Instagram/YouTube connectors even if the scheduler offers them.

## Decisions
- Start with an own script against the Posts API for the personal profile (smallest surface, no extra services); evaluate the scheduler only if company-page posting or media handling makes the script heavy.
- Token storage: `~/dev/alpi_marketer/server/src/system/config/secrets.json`-style path, referenced by path only.
- Scheduler trigger: the Mac's launchd at slot times; cloud routine as backup if the Mac is asleep (needs the token in the cloud environment, decide at build).
- Logging: posts-log.csv row updated with post URL and `posted` status.

## Risks / Trade-offs
- LinkedIn review for organisation scope can take weeks → company posts stay manual meanwhile.
- API changes/versions → pin the version header; Copy text / Save image on every card is the permanent manual route, not a fallback mode.
