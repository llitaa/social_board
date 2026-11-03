#!/bin/zsh
# The sync chain. watch.py starts it: `run.sh fast` as soon as a press reaches the server (pull, decisions,
# learn, redraft, cards, push: a note is applied within about a minute), `run.sh full` every 10 minutes
# (plus memos, photos, slot filling). One run at a time (lock dir); `run.sh` by hand = full.
# Every step is logged to library/log/steps.jsonl (step, start, seconds, rc, last stderr line);
# health.py turns that into board/data/health.json, and the board shows a red line when something is wrong.
cd "$(dirname "$0")/.." || exit 1
P=${PYTHON:-$( [ -x /opt/anaconda3/bin/python3 ] && echo /opt/anaconda3/bin/python3 || command -v python3 )}   # the worker: any machine with the requirements in docs/worker.md
# BOARD_USER empty = Anton's board; BOARD_USER=<slug> = users/<slug>/ (common.py). Lock and step log live in that board's library.
export BOARD_USER PYTHONPATH=pipeline
LIBD=$($P -c "from common import LIB; print(LIB)" 2>/dev/null) || { echo "no board for BOARD_USER=$BOARD_USER"; exit 1; }
mkdir -p "$LIBD/log"; LOCK=$LIBD/log/.run.lock; STEPS=$LIBD/log/steps.jsonl
if [ -d "$LOCK" ] && [ -z "$(find "$LOCK" -maxdepth 0 -mmin -30)" ] && ! pgrep -f "pipeline/run.sh" | grep -qv $$; then rmdir "$LOCK"; echo "$(date +%H:%M) stale lock removed"; fi   # a crash or reboot must not stop the chain for good
if ! mkdir "$LOCK" 2>/dev/null; then echo "$(date +%H:%M) another run is active"; exit 0; fi
trap 'rmdir "$LOCK"' EXIT
echo "=== $(date '+%Y-%m-%d %H:%M') ${BOARD_USER:-anton}"
step() {  # step <name> <command...>
  local name=$1; shift; local t0=$(date +%s); local err=$(mktemp)
  "$@" 2> >(tee "$err" >&2); local rc=$?
  local last=$(tail -n 1 "$err" | tr -d '"\\' | cut -c1-200); rm -f "$err"
  printf '{"step":"%s","ts":"%s","seconds":%d,"rc":%d,"last":"%s"}\n' "$name" "$(date '+%Y-%m-%dT%H:%M:%S')" $(( $(date +%s) - t0 )) $rc "$last" >> "$STEPS"
  return $rc
}
MODE=${1:-full}
# model calls: only when config llm.auto is true or process.py started this run (LLM_INTERACTIVE=1); otherwise those steps are
# logged as deferred and health.py counts what waits. Transcription (whisper, local) and everything else still run.
AUTO=$($P -c "from common import CFG; print(str(CFG.get('llm', {}).get('auto', True)).lower())" 2>/dev/null)
if [ "$AUTO" = true ] || [ "${LLM_INTERACTIVE:-0}" = 1 ]; then MODELS=1; else MODELS=0; fi
export LLM_INTERACTIVE
mstep() {  # a step that calls a model: runs only when MODELS=1
  if [ $MODELS = 1 ]; then step "$@"; else printf '{"step":"%s","ts":"%s","seconds":0,"rc":0,"last":"deferred: model calls run from the terminal (python3 pipeline/process.py)"}\n' "$1" "$(date '+%Y-%m-%dT%H:%M:%S')" >> "$STEPS"; fi
}
[ -z "$BOARD_USER" ] && [ "$MODE" = full ] && step users $P pipeline/users.py sync   # new boards created in the admin page get their users/<slug>/ here
step pull        $P pipeline/board_sync.py pull || { $P pipeline/health.py; exit 1; }
step transcribe  $P pipeline/transcribe.py          # before apply: a spoken note on a card becomes a change decision in this run
step apply       $P pipeline/apply_decisions.py
mstep learn      $P pipeline/learn.py
if [ "$MODE" = full ]; then
step photos      $P pipeline/photo_index.py
if [ -z "$BOARD_USER" ]; then   # Anton's mailbox and LinkedIn exports; a user has neither
step mail        $P pipeline/mail_watch.py
step metrics     $P pipeline/metrics_import.py
step metrics_api $P pipeline/metrics_fetch.py
fi
else
step photos      $P pipeline/photo_index.py fast
fi
mstep onboard    $P pipeline/onboard.py        # a user's website or document -> profile proposal (one call); nothing to do for Anton
mstep redraft    $P pipeline/redraft.py
step publish     $P pipeline/publish.py
[ "$MODE" = full ] && mstep draft $P pipeline/draft.py
mstep match      $P pipeline/match.py          # shared material of the other boards that fits an open draft -> proposal on the card
step cards       $P pipeline/cards.py
step health      $P pipeline/health.py
step push        $P pipeline/board_sync.py push
[ "$MODE" = full ] && step worker $P pipeline/board_sync.py worker
exit 0
