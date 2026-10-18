# Proposal

## Why
An approved card should publish at its slot without a second click. Until the API app is approved, Anton posts from the card with Copy text and Save image.

## What Changes
- LinkedIn developer app in Anton's name; member posting scope for the personal profile; organisation scope for the company page after LinkedIn's review.
- Scheduler publishes approved cards at their slot with text and image; logs the post URL into posts-log.csv.
- No fallback path: a card always has Copy text and Save image; if the API cannot publish, the card says so and why. Token expiry is tracked and warned 7 days ahead.
- Hard rule: only cards with status approved are ever published; nothing else touches LinkedIn.
- Out of scope: comments, likes, messages, analytics reads (closed API).

## Capabilities

### New Capabilities
- `linkedin-publishing`: authorisation, scheduled publishing of approved cards, logging, health and token-expiry warnings.

### Modified Capabilities
(none)

## Impact
New secrets (token) stored by path only, never printed. A self-hosted open-source scheduler or an own script; decision in design. Plan done-date: Fri 06.11.
