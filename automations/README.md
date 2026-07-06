# Automations

Scripts that run without Claude. All of them:
- source `lib/common.sh` for logging and run-tracking,
- log to `logs/<name>/YYYY-MM-DD.log` (`timestamp | LEVEL | message`),
- register start/finish in the `runs` table when `data/aios.db` exists
  (they degrade to file-only logging when it doesn't),
- are idempotent — safe to re-run.

| Script | What it does | Suggested schedule |
|---|---|---|
| `daily-dev-log.sh [date]` | Collects the day's git activity + completed tasks into `state/devlog-raw-<date>.md` for the `daily-dev-log` skill | nightly 21:00 |
| `watch-queue.sh [--once]` | Surfaces new dashboard trigger files in `state/queue/` (log + macOS notification) | every 5 min (`--once`) or run as a foreground poller |
| `backup-state.sh` | Tars `state/ data/ vault/ config/` into `backups/`, keeps newest 14 | daily 21:30 |

Scheduling setup for macOS (launchd), Linux (cron), and Windows (Task
Scheduler) lives in [`schedule/README.md`](schedule/README.md).

## Writing a new automation

1. Copy the header pattern from `daily-dev-log.sh` (comment block: what, usage, schedule).
2. `source lib/common.sh`, call `aios_init "<name>"` first and `aios_finish ok|failed` last.
3. Never write outside `state/`, `logs/`, `backups/`, or the vault.
4. Add it to the table above and to your scheduler.
