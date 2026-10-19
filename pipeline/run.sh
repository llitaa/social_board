#!/bin/zsh
# The sync chain, every 10 minutes from launchd. One run at a time (lock dir); each step is logged.
cd /Users/anton/dev/linkedin-system || exit 1
LOCK=library/log/.run.lock
if ! mkdir "$LOCK" 2>/dev/null; then echo "$(date +%H:%M) another run is active"; exit 0; fi
trap 'rmdir "$LOCK"' EXIT
P=/opt/anaconda3/bin/python3
echo "=== $(date '+%Y-%m-%d %H:%M')"
$P pipeline/board_sync.py pull      || exit 1   # decisions, uploads, memos from the server
$P pipeline/apply_decisions.py                  # board presses -> content-plan.csv / logs
$P pipeline/transcribe.py                       # memos -> text (whisper.cpp, local)
$P pipeline/photo_index.py                      # uploads + sources -> pool, tags, eligibility
$P pipeline/redraft.py                          # "Post with changes" notes -> new text, approved
$P pipeline/draft.py                            # every slot in the next 14 days gets a draft
$P pipeline/cards.py                            # cards.json + pipeline.json from the CSVs
$P pipeline/board_sync.py push                  # back to the server
