# Skill: daily-dev-log

**Description:** Write the day's dev log from evidence (git commits, completed
tasks, session logs) instead of memory. Also runs headlessly via
`automations/daily-dev-log.sh`, which pre-collects the raw data.

**Trigger phrases:** "write my dev log", "what did I do today", "dev log for
yesterday"

## Inputs

| Input | Required | Source |
|---|---|---|
| date | no | default today |
| raw activity | auto | git log of each repo in `config/projects/*.json`; `db.py task list --completed-on <date>`; `state/session-log.md` entries for the date; automation pre-collect at `state/devlog-raw-<date>.md` if present |

## Procedure

1. If `state/devlog-raw-<date>.md` exists (written by the automation), start
   from it. Otherwise collect: for each project config, `git -C <path> log
   --since "<date> 00:00" --until "<date> 23:59" --oneline --stat`; completed
   tasks from the DB; the date's session-log entries.
2. Draft the note from `vault/90-system/templates/daily-note.md`:
   - **Shipped** — user-meaningful outcomes (not commit messages verbatim)
   - **In progress** — open loops touched today
   - **Blocked / decisions needed**
   - **Tomorrow** — top 1–3 intentions, pulled from open tasks
3. Write to `vault/00-inbox/daily/<YYYY-MM-DD>.md` (Obsidian daily-note
   compatible). If a note already exists, merge — never overwrite hand-written
   content.
4. Record: `db.py metric add devlog_written 1`.
5. Verify: every "Shipped" bullet traces to a commit, task, or session entry.

## Outputs

- `vault/00-inbox/daily/<date>.md`
- `devlog_written` metric row

## Example

> User: "write my dev log"
>
> Result: `vault/00-inbox/daily/2026-07-06.md` — 3 shipped items from 9
> commits across 2 repos, 1 blocker, tomorrow's top task.

## Failure modes

- **No activity found** → still write the note saying so; a gap is information.
- **Repo path in config doesn't exist on this machine** → skip it with a note
  in the log entry, don't abort the whole log.
- **Existing note has same-name sections** → append under them with a
  `*(auto)*` marker.

## State & logging

- Reads `state/devlog-raw-<date>.md` if the automation ran; deletes it after
  merging.
- DB records: `metrics`
