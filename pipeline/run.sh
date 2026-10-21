#!/bin/zsh
# The sync chain. watch.py starts it: `run.sh fast` as soon as a press reaches the server (pull, decisions,
# learn, redraft, cards, push: a note is applied within about a minute), `run.sh full` every 10 minutes
# (plus memos, photos, slot filling). One run at a time (lock dir); `run.sh` by hand = full.
# Every step is logged to library/log/steps.jsonl (step, start, seconds, rc, last stderr line);
# health.py turns that into board/data/health.json, and the board shows a red line when something is wrong.
cd "$(dirname "$0")/.." || exit 1
LOCK=library/log/.run.lock; STEPS=library/log/steps.jsonl
if [ -d "$LOCK" ] && [ -z "$(find "$LOCK" -maxdepth 0 -mmin -30)" ] && ! pgrep -f "pipeline/run.sh" | grep -qv $$; then rmdir "$LOCK"; echo "$(date +%H:%M) stale lock removed"; fi   # a crash or reboot must not stop the chain for good
if ! mkdir "$LOCK" 2>/dev/null; then echo "$(date +%H:%M) another run is active"; exit 0; fi
trap 'rmdir "$LOCK"' EXIT
P=${PYTHON:-$( [ -x /opt/anaconda3/bin/python3 ] && echo /opt/anaconda3/bin/python3 || command -v python3 )}   # the worker: any machine with the requirements in docs/worker.md
echo "=== $(date '+%Y-%m-%d %H:%M')"
step() {  # step <name> <command...>
  local name=$1; shift; local t0=$(date +%s); local err=$(mktemp)
  "$@" 2> >(tee "$err" >&2); local rc=$?
  local last=$(tail -n 1 "$err" | tr -d '"\\' | cut -c1-200); rm -f "$err"
  printf '{"step":"%s","ts":"%s","seconds":%d,"rc":%d,"last":"%s"}\n' "$name" "$(date '+%Y-%m-%dT%H:%M:%S')" $(( $(date +%s) - t0 )) $rc "$last" >> "$STEPS"
  return $rc
}
MODE=${1:-full}
step pull        $P pipeline/board_sync.py pull || { $P pipeline/health.py; exit 1; }
step transcribe  $P pipeline/transcribe.py          # before apply: a spoken note on a card becomes a change decision in this run
step apply       $P pipeline/apply_decisions.py
step learn       $P pipeline/learn.py
if [ "$MODE" = full ]; then
step photos      $P pipeline/photo_index.py
step mail        $P pipeline/mail_watch.py
step metrics     $P pipeline/metrics_import.py
step metrics_api $P pipeline/metrics_fetch.py
else
step photos      $P pipeline/photo_index.py fast
fi
step redraft     $P pipeline/redraft.py
step publish     $P pipeline/publish.py
[ "$MODE" = full ] && step draft $P pipeline/draft.py
step cards       $P pipeline/cards.py
step health      $P pipeline/health.py
step push        $P pipeline/board_sync.py push
[ "$MODE" = full ] && step worker $P pipeline/board_sync.py worker
exit 0
