#!/usr/bin/env bash
# Watch state/queue/ for trigger files dropped by the dashboard (or anything
# else) and surface them: log each pending trigger and, on macOS, raise a
# notification. Claude Code picks the actual work up at session start (see
# CLAUDE.md session protocol) — this watcher just makes sure you *notice*.
#
# Usage:
#   automations/watch-queue.sh --once        # single scan (for cron)
#   automations/watch-queue.sh               # poll loop every 30s (foreground)

set -u
source "$(dirname "$0")/lib/common.sh"
aios_init "watch-queue"

QUEUE_DIR="$AIOS_ROOT/state/queue"
SEEN_DIR="$QUEUE_DIR/.seen"
mkdir -p "$QUEUE_DIR" "$SEEN_DIR"

scan() {
  local n=0
  for f in "$QUEUE_DIR"/*.json; do
    [ -e "$f" ] || continue
    local base; base="$(basename "$f")"
    n=$((n + 1))
    if [ ! -e "$SEEN_DIR/$base" ]; then
      touch "$SEEN_DIR/$base"
      local action; action="$(aios_json_get "$f" action "unknown")"
      log_info "new trigger: $base (action: $action)"
      if command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"$action\" with title \"AIOS queue\"" 2>/dev/null || true
      fi
    fi
  done
  return $n
}

if [ "${1:-}" = "--once" ]; then
  scan; pending=$?
  log_info "scan complete: $pending pending trigger(s)"
  aios_finish ok "$pending pending"
else
  log_info "polling $QUEUE_DIR every 30s (ctrl-c to stop)"
  while true; do scan || true; sleep 30; done
fi
