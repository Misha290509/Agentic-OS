# AIOS — Operating Manual for Claude Code

You are operating inside a personal **Agentic OS**. Everything you need is on
disk; assume you have zero memory of previous sessions. This file tells you how
to behave here. Read it fully before doing anything else.

## Prime directives

1. **Behavior lives in skills.** Before improvising a workflow, check
   `skills/README.md`. If the user's request matches a skill's trigger phrases,
   follow that `SKILL.md` exactly. If you build a new repeatable workflow,
   encode it as a new skill from `skills/_template/`.
2. **State lives in files, never in chat.** Anything the next session needs
   must be written to `state/`, the vault, or the database before you finish.
3. **Loops over one-shots.** For multi-step work, pick a loop spec from
   `loops/` and follow its checkpoint discipline.
4. **Log what you do.** Automations and long-running work log to `logs/` and
   record runs in the database (see Logging below).

## Session protocol

**At session start** (always, before the user's first task):
1. Read `state/current-focus.md` — what the owner is working on and why.
2. Read `state/open-loops.json` — unfinished multi-step work; each entry says
   which loop it follows and where its checkpoint file lives.
3. Skim the last entry of `state/session-log.md` — how the previous session ended.
4. Check `state/queue/` for pending trigger files (JSON tasks dropped by the
   dashboard or automations). Process or acknowledge them.
5. If the user says "resume" / "resume where we left off" / "continue", run the
   `resume-session` skill.

**At session end** (when the user says "wrap up", "end session", or asks for a
summary — and proactively before context runs out):
- Run the `end-session` skill: append to `state/session-log.md`, update
  `state/current-focus.md` and `state/open-loops.json`, record the session in
  the DB.

## Where things live

| Path | Purpose |
|---|---|
| `skills/` | One folder per workflow; `SKILL.md` is the contract. Index: `skills/README.md`. |
| `loops/` | Agentic loop patterns (entry/exit criteria, checkpointing). |
| `automations/` | Scripts that run without Claude (cron/launchd/Task Scheduler). |
| `state/` | Machine-readable working state. Gitignored; `.example` files show shape. |
| `state/queue/` | Trigger files (JSON) awaiting pickup. Move to `state/queue/done/` after processing. |
| `vault/` | Obsidian vault = long-term memory. Human notes, dev logs, tickets, dashboards. |
| `data/aios.db` | SQLite: tasks, bugs, feedback, runs, metrics, sessions. Use `scripts/db.py`, never raw sqlite3 writes. |
| `logs/` | `logs/<name>/YYYY-MM-DD.log`, timestamped lines. |
| `config/` | `aios.json` (user config, gitignored; example provided) and `projects/*.json` (per-project build/test commands). |
| `dashboard/` | Local web UI. Start with `python3 scripts/serve_dashboard.py`. |
| `docs/` | Human documentation for every part of the system. |

## Vault conventions

- Folders: `00-inbox` (unprocessed input), `10-projects`, `20-areas`,
  `30-resources`, `40-archive`, `90-system` (templates, dashboards).
- Every note gets YAML frontmatter: `title, created, updated, tags, status, related`.
  Templates live in `vault/90-system/templates/`.
- Skills write their outputs into the vault (see each SKILL.md for exact paths).
- The vault path is `vault/` by default; if `config/aios.json` sets
  `vault_path`, use that instead everywhere.

## Database

- Query/update via `python3 scripts/db.py <subcommand>` — run
  `python3 scripts/db.py --help` for the full CLI. Common:
  - `db.py task add "title" --project X --priority 2`
  - `db.py task list --status open`
  - `db.py bug add "title" --severity S2 --project X`
  - `db.py run start <automation>` / `db.py run finish <run_id> --status ok`
  - `db.py metric add <name> <value>`
  - `db.py session start --focus "..."` / `db.py session end <id> --summary "..."`
  - `db.py query "SELECT ..."` (read-only escape hatch)
- Schema documented in `docs/data-model.md`. If `data/aios.db` is missing, run
  `python3 scripts/db.py init` (idempotent).

## Picking a loop

| Situation | Loop |
|---|---|
| Code change must end in green tests | `loops/build-test-fix-loop.md` |
| Open-ended question needing sources | `loops/research-loop.md` |
| Writing anything longer than a paragraph that matters | `loops/draft-review-revise-loop.md` |
| Pile of unstructured items to classify | `loops/triage-loop.md` |

Every loop iteration checkpoints to a file named in `state/open-loops.json`, so
a dead session can be resumed by any future session.

## Logging conventions

- Automations: source `automations/lib/common.sh`, use `log_info`/`log_error`;
  they write to `logs/<automation-name>/YYYY-MM-DD.log` and register runs in the DB.
- Claude sessions: significant actions go in the session-log entry at wrap-up,
  not scattered files.
- Log lines are `ISO-8601 timestamp | LEVEL | message`. Grep-friendly, no JSON blobs.

## Safety rules

- Never commit `state/`, `logs/`, `data/*.db`, `config/aios.json`, or personal
  vault content. The `.gitignore` enforces this — do not weaken it.
- Automations must be idempotent and safe to re-run.
- When a skill's instructions and the user's explicit request conflict, the
  user wins; note the deviation in the session log.
