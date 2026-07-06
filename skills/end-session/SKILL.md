# Skill: end-session

**Description:** Checkpoint everything before a session ends so the next
session (or another machine) can resume cold. The counterpart of `resume-session`.

**Trigger phrases:** "wrap up", "end session", "checkpoint", "save state" —
also run proactively when context is about to run out.

## Inputs

| Input | Required | Source |
|---|---|---|
| session id | no | from `resume-session` step 6 if it ran; otherwise skip the DB close-out |

## Procedure

1. **Session log:** append to `state/session-log.md` (newest at top):

   ```markdown
   ## 2026-07-06 14:30 — <one-line summary>
   - Did: <bullet per significant outcome>
   - Decided: <decisions made, with rationale one-liners>
   - Next: <the single next action, specific enough to execute cold>
   ```

2. **Open loops:** update `state/open-loops.json` — add loops started this
   session (with checkpoint path + next action), remove completed ones, bump
   `updated` timestamps. Ensure every referenced checkpoint file actually
   exists and reflects reality.
3. **Current focus:** rewrite `state/current-focus.md` if the focus shifted;
   update its `updated:` frontmatter either way.
4. **Queue hygiene:** move processed trigger files to `state/queue/done/`.
5. **DB:** `python3 scripts/db.py session end <id> --summary "<one-liner>"`;
   mark finished tasks `db.py task done <id>`.
6. **Vault views:** `python3 scripts/sync_vault_views.py` so the Obsidian
   dashboards show this session's end state.
7. Verify (the whole point): re-read the three state files and confirm a
   stranger could resume from them alone. If the "Next:" line requires chat
   context to understand, rewrite it.
8. Tell the user what was checkpointed in 2–3 lines.

## Outputs

- Updated `state/session-log.md`, `state/open-loops.json`,
  `state/current-focus.md`; closed `sessions` row.

## Example

> User: "wrap up"
>
> Result: session logged ("fixed save bug, started release notes"), 1 loop
> closed, 1 added (release-notes draft, next = review pass), focus unchanged.

## Failure modes

- **Interrupted mid-wrap-up** → order matters: session-log first (it's the
  narrative), then open-loops, then focus. Partial wrap-up still resumable.
- **No session id (resume-session never ran)** → still do steps 1–4 and 6;
  create-and-close a sessions row with `db.py session start … && session end …`.

## State & logging

- Writes all of `state/`; closes the `sessions` row.
