# Skill: playtest-feedback

**Description:** Digest raw playtest feedback (notes, transcripts, survey
exports) into clustered themes, separated bugs, and actionable tasks — so no
tester signal is lost.

**Trigger phrases:** "process playtest feedback", "what did testers say",
"digest the playtest", user drops files in `vault/00-inbox/playtests/`

## Inputs

| Input | Required | Source |
|---|---|---|
| raw feedback | yes | `vault/00-inbox/playtests/` and/or pasted text |
| playtest label | yes | user (e.g. "alpha-3"), or derive from filenames/date |
| project id | yes | user or config |

## Procedure

1. Ingest all sources; split into atomic feedback items (one observation each).
2. Tag each item: `bug` / `design` / `praise` / `confusion` / `request`, plus
   sentiment (+/0/-).
3. **Bugs exit here:** hand `bug` items to the `bug-triage` skill procedure
   (dedupe → DB → tickets). Don't duplicate that logic.
4. Cluster the rest into themes (aim for 3–8; merge singletons into "misc").
   For each theme record: item count, sentiment lean, representative quotes (≤3).
5. Store items: `python3 scripts/db.py feedback add "<text>" --playtest
   <label> --category design --sentiment -1 --theme "<theme>"` for each.
6. Write the summary note
   `vault/10-projects/<project>/playtests/<label>.md` using
   `vault/90-system/templates/playtest-summary.md`: themes ranked by
   count×severity, quotes, and an **Actionables** section.
7. For each actionable: `db.py task add "<action>" --project <id> --source
   playtest:<label>`.
8. Archive raw files to `vault/40-archive/playtests/YYYY-MM/`.
9. Verify: every ingested item exists in the DB (`db.py feedback list
   --playtest <label>` count matches); summary links to created tasks/bugs.

## Outputs

- Summary note in vault; `feedback` rows; `tasks` rows for actionables; bugs
  routed through bug-triage.

## Example

> User: "process playtest feedback for alpha-3"
>
> Result: 42 items → 5 themes (top: "tutorial confusion", 11 items, negative),
> 6 bugs triaged, 4 tasks created, summary at `…/playtests/alpha-3.md`.

## Failure modes

- **Contradictory feedback** ("too hard" vs "too easy") → keep both in the
  theme, note the split explicitly; never average it away.
- **Feedback about out-of-scope features** → collect under a "parking lot"
  section in the summary, no tasks.
- **Large corpus (>100 items)** → process per-source, checkpoint counts to
  `state/playtest-<label>.md` between sources.

## State & logging

- Checkpoint: `state/playtest-<label>.md` (large batches only)
- DB records: `feedback`, `tasks`, `bugs` (via bug-triage)
