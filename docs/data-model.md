# Data Model

Single SQLite database at `data/aios.db` (gitignored). Schema source of truth:
[`data/schema.sql`](../data/schema.sql), applied by `python3 scripts/db.py init`
(idempotent — safe to re-run after schema additions).

**Rule:** structured, queryable, append-heavy data lives here; narrative and
context live in Markdown (vault + `state/`). If you'd ever want to `GROUP BY`
it, it belongs in the DB.

All timestamps are UTC ISO-8601 (`2026-07-06T21:00:00Z`). All access goes
through `scripts/db.py`; raw SQL is allowed read-only via `db.py query "SELECT …"`.

## Tables

### tasks — the work queue
| Column | Notes |
|---|---|
| `status` | `open` → `in_progress` → `done` (or `dropped`) |
| `priority` | 1 (highest) … 5; default 3 |
| `project` | matches a `config/projects/<id>.json` id |
| `source` | provenance, e.g. `playtest:alpha-3`, `queue:morning-report` — lets you trace where work came from |
| `completed_at` | set by `task done`; queried by the daily-dev-log skill (`--completed-on`) |

### bugs — triaged defects
| Column | Notes |
|---|---|
| `severity` | S1 crash/blocker · S2 major · S3 impaired-with-workaround · S4 cosmetic |
| `status` | `open`, `needs-info`, `fixed` (sets `fixed_at`), `wontfix` |
| `report_count`, `last_seen` | duplicate reports bump these via `bug update <id> --seen` instead of creating new rows |
| `area` | gameplay / ui / audio / perf / save / build / other |

The Markdown ticket in `vault/10-projects/<project>/bugs/` carries the
narrative (investigation, fix); the row carries the queryable facts. The row
id is the ticket's `BUG-<id>` number — that's the join key.

### feedback — atomic playtest observations
One row per observation. `playtest` groups a session (e.g. `alpha-3`),
`category` ∈ bug/design/praise/confusion/request, `sentiment` ∈ −1/0/1,
`theme` is the cluster name assigned by the playtest-feedback skill.

### runs — automation & loop run history
Written by `automations/lib/common.sh` (`run start` → id → `run finish`).
`status` ∈ running/ok/failed. A row stuck in `running` means the script died
mid-run — the dashboard surfaces these.

### metrics — anything you want to chart
Free-form named time series (`build_time`, `devlog_written`, `test_count`, …).
`context` disambiguates (e.g. project id).

### sessions — Claude session records
Opened by `resume-session`, closed by `end-session` with a one-line summary.
The narrative counterpart lives in `state/session-log.md`.

## Adding a table

1. Add `CREATE TABLE IF NOT EXISTS` (+ indexes) to `data/schema.sql`.
2. Run `python3 scripts/db.py init` — existing data is untouched.
3. Add typed subcommands to `scripts/db.py` (copy an existing block).
4. Document it here; update the dashboard server if it should be visible.
