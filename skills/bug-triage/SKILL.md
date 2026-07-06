# Skill: bug-triage

**Description:** Turn raw bug reports (tester messages, crash logs, screenshots
descriptions) into deduplicated, severity-classified, structured tickets.

**Trigger phrases:** "triage bugs", "process the bug inbox", "here are some bug
reports", user pastes raw crash logs

## Inputs

| Input | Required | Source |
|---|---|---|
| raw reports | yes | pasted by user, or files in `vault/00-inbox/bugs/` |
| project id | yes | user, or inferable from report content |

## Severity scale

- **S1** crash/data loss/blocker — fix before anything else
- **S2** major feature broken, no workaround
- **S3** feature impaired, workaround exists
- **S4** cosmetic/polish

## Procedure

Follow `loops/triage-loop.md` (batch classification loop). Per report:

1. Gather sources: every file in `vault/00-inbox/bugs/` plus anything pasted.
2. Parse each into: symptom, repro steps (if any), platform, build/version.
3. **Deduplicate:** `python3 scripts/db.py bug list --project <id> --status open`
   and compare symptoms. A match increments `report_count` and updates
   `last_seen` (`db.py bug update <id> --seen`) instead of creating a new bug.
4. New bugs: classify severity (scale above) and area (gameplay/UI/audio/
   perf/save/build), then `db.py bug add "<title>" --severity S2 --area ui
   --project <id> --repro "<steps>"`.
5. Write one ticket per new bug to
   `vault/10-projects/<project>/bugs/BUG-<id>-<slug>.md` using
   `vault/90-system/templates/bug-ticket.md`.
6. Move processed inbox files to `vault/40-archive/bugs/YYYY-MM/`.
7. Verify: ticket count == new-bug count; inbox empty.
8. Report a triage summary table (new/dupes/severity breakdown) to the user.

## Outputs

- Rows in `bugs` table (new or updated `report_count`).
- Markdown tickets in `vault/10-projects/<project>/bugs/`.
- Archived raw reports; empty inbox.

## Example

> User: "triage bugs" (6 files in inbox)
>
> Result: 4 new bugs (1×S1, 2×S3, 1×S4), 2 duplicates of BUG-12, inbox archived.

## Failure modes

- **Report too vague to classify** → create the bug at S3 with status
  `needs-info`, list the missing details in the ticket; never silently drop a report.
- **Can't tell if duplicate** → treat as new but add `related:` link to the
  suspected twin in both tickets.
- **Huge batch (>25 reports)** → process in chunks of 10, checkpointing to
  `state/triage-checkpoint.md` between chunks.

## State & logging

- Checkpoint: `state/triage-checkpoint.md` (only for large batches)
- DB records: `bugs`
