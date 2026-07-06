#!/usr/bin/env bash
# Shared helpers for AIOS automations.
# Usage in an automation script:
#   source "$(dirname "$0")/lib/common.sh"
#   aios_init "my-automation"
#   log_info "doing things"
#   aios_finish ok        # or: aios_finish failed "reason"
#
# Logging convention: logs/<name>/YYYY-MM-DD.log, lines are
#   ISO-8601 | LEVEL | message
# Runs are also registered in data/aios.db via scripts/db.py when the DB
# layer exists; if it doesn't yet (Level 1 install), we log to file only.

set -u

AIOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AIOS_DB_CLI="$AIOS_ROOT/scripts/db.py"
AIOS_RUN_ID=""
AUTOMATION_NAME=""
LOG_FILE=""

_aios_ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }

_aios_log() { # LEVEL message...
  local level="$1"; shift
  local line
  line="$(_aios_ts) | ${level} | $*"
  echo "$line" >> "$LOG_FILE"
  echo "$line" >&2
}

log_info()  { _aios_log INFO "$@"; }
log_warn()  { _aios_log WARN "$@"; }
log_error() { _aios_log ERROR "$@"; }

aios_init() { # name
  AUTOMATION_NAME="$1"
  local log_dir="$AIOS_ROOT/logs/$AUTOMATION_NAME"
  mkdir -p "$log_dir"
  LOG_FILE="$log_dir/$(date +%Y-%m-%d).log"
  log_info "=== $AUTOMATION_NAME started (pid $$) ==="
  if [ -f "$AIOS_DB_CLI" ] && [ -f "$AIOS_ROOT/data/aios.db" ]; then
    AIOS_RUN_ID="$(python3 "$AIOS_DB_CLI" run start "$AUTOMATION_NAME" --quiet 2>/dev/null || true)"
  fi
}

aios_finish() { # status [detail]
  local status="${1:-ok}"; local detail="${2:-}"
  if [ -n "$AIOS_RUN_ID" ]; then
    python3 "$AIOS_DB_CLI" run finish "$AIOS_RUN_ID" --status "$status" ${detail:+--detail "$detail"} --quiet 2>/dev/null || true
  fi
  log_info "=== $AUTOMATION_NAME finished: $status ${detail:+($detail)} ==="
  [ "$status" = "ok" ] || exit 1
}

# Read a key from an AIOS json file: aios_json_get <file> <dotted.key> [default]
aios_json_get() {
  python3 - "$1" "$2" "${3:-}" <<'PY'
import json, sys
path, key, default = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    obj = json.load(open(path))
    for part in key.split('.'):
        obj = obj[part]
    print(obj)
except Exception:
    print(default)
PY
}
