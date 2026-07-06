#!/usr/bin/env bash
# Snapshot everything gitignored-but-precious (state/, data/, vault/, config/)
# into backups/aios-backup-<timestamp>.tar.gz and keep the newest 14.
#
# Usage: automations/backup-state.sh
# Schedule: daily, see automations/schedule/README.md

set -u
source "$(dirname "$0")/lib/common.sh"
aios_init "backup-state"

BACKUP_DIR="$AIOS_ROOT/backups"
mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$BACKUP_DIR/aios-backup-$STAMP.tar.gz"

targets=()
for d in state data vault config; do
  [ -d "$AIOS_ROOT/$d" ] && targets+=("$d")
done
if [ "${#targets[@]}" -eq 0 ]; then
  aios_finish failed "nothing to back up"
fi

if tar -czf "$OUT" -C "$AIOS_ROOT" "${targets[@]}" 2>>"$LOG_FILE"; then
  log_info "wrote $OUT ($(du -h "$OUT" | cut -f1))"
else
  aios_finish failed "tar failed"
fi

# Retention: keep newest 14
ls -1t "$BACKUP_DIR"/aios-backup-*.tar.gz 2>/dev/null | tail -n +15 | while read -r old; do
  rm -f "$old" && log_info "pruned $old"
done

aios_finish ok "$OUT"
