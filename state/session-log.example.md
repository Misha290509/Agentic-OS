# Session Log

Newest entries at the top. Written by the `end-session` skill; read by
`resume-session`. Keep entries short — the vault holds the long-form story.

## 2026-07-06 16:45 — Save crash root-caused, fix in progress
- Did: reproduced BUG-1 on macOS; root cause = SaveSlot deserializing v2
  saves with v3 schema; wrote failing test
- Decided: migrate old saves on load rather than versioning the schema
  (smaller blast radius pre-alpha)
- Next: implement `SaveMigrator.from_v2()`, then run build-test-fix on the
  save-system scope — checkpoint at state/btf-example-game.md

## 2026-07-05 11:20 — Playtest prep
- Did: processed alpha-2 feedback (5 themes, 6 bugs triaged, 4 tasks)
- Decided: alpha-3 focuses on stability, not content
- Next: fix BUG-1 (S1) first
