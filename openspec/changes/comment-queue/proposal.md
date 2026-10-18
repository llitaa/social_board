# Proposal

## Why
Engagement on LinkedIn only counts when it is personal and timely. Automating it violates LinkedIn's terms; doing it by hand costs Anton an hour of browsing. The queue removes the browsing and keeps the human post.

## What Changes
- A watch list of about 50 people in one CSV (hiring managers and heads of software at the 40 target employers, ten authors on AI in engineering and software product decisions, people who commented on Anton's posts).
- A daily scan that finds qualifying posts and drafts a comment per post (question, added thought or concern).
- Comment cards on the board's Comments screen with Open post, Copy, Skip, and a Clear all button.
- Expiry (setting, default 18:00; Keep once per card): untouched cards are deleted, nothing carries over.
- Learning: Skip with two optional reasons (not the topic / not the author); ranking adapts; at most one question a week on the board, only with a concrete pattern.
- Up to 2 message cards a day for signals that warrant a direct message (job change, new role). No messaging API exists for members: Open profile + Copy, Anton sends.
- Out of scope: posting the comment (always Anton), liking, following, any automation on LinkedIn.

## Capabilities

### New Capabilities
- `comment-queue`: watch list, qualification rules, drafting, the queue's lifecycle (07:00 ready, 18:00 expiry, Clear all).

### Modified Capabilities
(none)

## Impact
New files: `watchlist.csv`, `local/queue/YYYY-MM-DD.json`. Uses the board (approval-board) for display. Reads Anton's own browser (Chrome with the extension) for watch-list activity, a few profiles a day. Plan done-date: Tue 20.10. (queue), Wed 21.10. (watch list).
