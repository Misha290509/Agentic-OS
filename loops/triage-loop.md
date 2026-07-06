# Loop: triage

**Entry criteria:** A pile of unstructured items (bug reports, feedback,
inbox notes) needs classifying into a structured destination (DB rows,
tickets, themed notes). Used by `bug-triage` and `playtest-feedback`.

**Iteration unit:** a batch of ≤10 items (not a fixed max — the pile defines
the total; the batch size bounds the blast radius of an interruption).

**Checkpoint file:** `state/triage-checkpoint.md` (only needed when the pile
exceeds one batch)

```markdown
---
loop: triage
source: <inbox path or description>
started: <ISO timestamp>
total_items: <n>
processed: <n>
---
## Batches
- batch 1: items 1–10 — done (<X> new, <Y> dupes)
## Classification decisions worth remembering
- <edge case> → <how it was ruled>  (keeps later batches consistent)
```

## Per-batch steps

1. **Checkpoint** — record which items this batch covers *before* processing.
2. **Classify each item** against the skill's schema (severity/area for bugs,
   category/theme for feedback). Consult the "decisions worth remembering"
   list so batch 5 rules like batch 1.
3. **Deduplicate** against the DB before creating anything new.
4. **Write outputs** (DB rows via `scripts/db.py`, tickets/notes in the vault).
5. **Archive inputs** — move processed source files to `vault/40-archive/…`
   so the inbox only ever contains unprocessed items.
6. **Verify** — outputs created == items classified; nothing dropped. Update
   the checkpoint counts.

## Exit criteria

- **Success:** inbox/source empty, `processed == total_items`. Delete the
  checkpoint, report the summary table (new/dupes/breakdown).
- **Abort:** items that can't be classified go to a `needs-info` state (bugs)
  or a "parking lot" section (feedback) — the loop still completes; unclassifiable
  ≠ stuck.

## Verification step

Count in, count out. Every raw item must be findable afterwards as a DB row, a
ticket, a theme member, or an explicit parking-lot entry.
