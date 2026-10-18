# Proposal

## Why
Content (photos, voice memos, drafts, published posts and their numbers) has no home: it sits in the phone, in scattered repo folders and in a used-up list in memory. Anton wants one organisation, no upload of media into git, and the freedom to reuse old material.

## What Changes
- One content library on the Mac, outside git, with four indexed collections: photos, memos, drafts, published posts (text + image + metrics).
- Phone holds originals; the board store holds the working copies; the Mac library holds the organised copies. Git holds only code, specs and index files, never media.
- Reuse rules: a photo may be reused after 6 months or 20 posts; a published post's topic may be recycled after 3 months with a new angle, tracked in the index.
- The system's code and specs move to their own repo; the campaign repo keeps the campaign CSVs and is read by path.
- Out of scope: Handwerk files, the book, anything not produced for LinkedIn.

## Capabilities

### New Capabilities
- `content-library`: where content lives, how it is indexed, what may be reused when, and the size budget.

### Modified Capabilities
(none)

## Impact
New repo `~/dev/linkedin-system` (code, openspec, index files). Library at `~/dev/linkedin-system/library/` (gitignored). photo-pool's folders become the photos collection of the library. Plan done-date: Mon 19.10. (repo and folders), Sun 25.10. (published-posts collection filled from posts-log).
