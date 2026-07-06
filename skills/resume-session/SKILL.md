# Skill: resume-session

**Description:** Reconstruct full working context from disk at the start of a
session, so work continues as if nothing was forgotten.

**Trigger phrases:** "resume", "resume where we left off", "where were we",
"continue" (as a session opener)

## Inputs

| Input | Required | Source |
|---|---|---|
| none | — | everything comes from `state/`, the DB, and the vault |

## Procedure

1. Read `state/current-focus.md` → the active project/goal and why.
2. Read `state/open-loops.json` → for each open loop, read its checkpoint file
   (path is in the entry) to know the exact iteration it stopped at.
3. Read the last 1–2 entries of `state/session-log.md` → how the previous
   session ended, decisions made, and its "next step" line.
4. Check `state/queue/` for unprocessed trigger files (dashboard actions);
   list them.
5. `python3 scripts/db.py task list --status open --limit 10` → current task
   stack. `db.py run list --limit 5` → recent automation health.
6. Register the session: `db.py session start --focus "<from current-focus>"`
   and remember the returned id for `end-session`.
7. Brief the user in ≤10 lines: **Focus / Open loops (with next action each) /
   Queue items / Notable since last session.** End with a recommended next
   action — the previous session's declared next step unless something in the
   queue outranks it.
8. Then wait for the user; do not start executing the next step unprompted
   unless the user's message was explicitly "resume and keep going".

## Outputs

- Context briefing in chat; new `sessions` row (open).

## Example

> User: "resume where we left off"
>
> Result: "Focus: alpha-3 stabilization. Open loop: build-test-fix on mygame,
> iteration 3/5, next = fix `SaveSlot` null-ref. Queue: morning-report
> requested 08:02. Recommend continuing the BTF loop."

## Failure modes

- **`state/` files missing/empty** → say so plainly, offer to initialize them
  from the `.example` files; never invent prior context.
- **Checkpoint file referenced in open-loops.json doesn't exist** → mark that
  loop `stale` in the JSON and tell the user it needs a restart.
- **DB missing** → `python3 scripts/db.py init`, note that history is empty.

## State & logging

- Reads all of `state/`; writes only the `sessions` row.
