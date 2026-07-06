#!/usr/bin/env bash
# Collect the day's raw dev activity so the `daily-dev-log` skill (or you)
# can turn it into a dev log without hunting for data.
#
# What it does:
#   1. For every project in config/projects/*.json, collect today's git log.
#   2. Append completed tasks for the day from the DB (if present).
#   3. Write everything to state/devlog-raw-<YYYY-MM-DD>.md.
#
# Usage: automations/daily-dev-log.sh [YYYY-MM-DD]   (default: today)
# Schedule: nightly, see automations/schedule/README.md

set -u
source "$(dirname "$0")/lib/common.sh"
aios_init "daily-dev-log"

DATE="${1:-$(date +%Y-%m-%d)}"
OUT="$AIOS_ROOT/state/devlog-raw-$DATE.md"
mkdir -p "$AIOS_ROOT/state"

{
  echo "---"
  echo "generated: $(_aios_ts)"
  echo "date: $DATE"
  echo "source: automations/daily-dev-log.sh"
  echo "---"
  echo
  echo "# Raw dev activity for $DATE"
} > "$OUT"

found_any=0
for cfg in "$AIOS_ROOT"/config/projects/*.json; do
  [ -e "$cfg" ] || continue
  name="$(aios_json_get "$cfg" name "$(basename "$cfg" .json)")"
  path="$(aios_json_get "$cfg" path "")"
  if [ -z "$path" ] || [ ! -d "$path/.git" ]; then
    log_warn "project '$name': path '$path' missing or not a git repo, skipping"
    continue
  fi
  log_info "collecting git log for '$name' ($path)"
  {
    echo
    echo "## Project: $name"
    echo '```'
    git -C "$path" log --since "$DATE 00:00" --until "$DATE 23:59" \
      --pretty=format:'%h %ad %s' --date=format:'%H:%M' --stat 2>&1 \
      || echo "(git log failed)"
    echo
    echo '```'
  } >> "$OUT"
  found_any=1
done
[ "$found_any" = 1 ] || echo -e "\n_No project repos configured or reachable._" >> "$OUT"

if [ -f "$AIOS_ROOT/data/aios.db" ]; then
  {
    echo
    echo "## Tasks completed $DATE"
    echo '```'
    python3 "$AIOS_DB_CLI" task list --completed-on "$DATE" 2>&1 || echo "(db query failed)"
    echo '```'
  } >> "$OUT"
fi

log_info "wrote $OUT"
aios_finish ok "$OUT"
