#!/bin/zsh
# The sync chain, every 10 minutes from launchd. One run at a time (lock dir).
# Every step is logged to library/log/steps.jsonl (step, start, seconds, rc, last stderr line);
# health.py turns that into board/data/health.json, and the board shows a red line when something is wrong.
cd /Users/anton/dev/linkedin-system || exit 1
LOCK=library/log/.run.lock; STEPS=library/log/steps.jsonl
if ! mkdir "$LOCK" 2>/dev/null; then echo "$(date +%H:%M) another run is active"; exit 0; fi
trap 'rmdir "$LOCK"' EXIT
P=/opt/anaconda3/bin/python3
echo "=== $(date '+%Y-%m-%d %H:%M')"
step() {  # step <name> <command...>
  local name=$1; shift; local t0=$(date +%s); local err=$(mktemp)
  "$@" 2> >(tee "$err" >&2); local rc=$?
  local last=$(tail -n 1 "$err" | tr -d '"\\' | cut -c1-200); rm -f "$err"
  printf '{"step":"%s","ts":"%s","seconds":%d,"rc":%d,"last":"%s"}\n' "$name" "$(date '+%Y-%m-%dT%H:%M:%S')" $(( $(date +%s) - t0 )) $rc "$last" >> "$STEPS"
  return $rc
}
step pull        $P pipeline/board_sync.py pull || { $P pipeline/health.py; exit 1; }
step apply       $P pipeline/apply_decisions.py
step transcribe  $P pipeline/transcribe.py
step photos      $P pipeline/photo_index.py
step redraft     $P pipeline/redraft.py
step draft       $P pipeline/draft.py
step cards       $P pipeline/cards.py
step health      $P pipeline/health.py
step push        $P pipeline/board_sync.py push
