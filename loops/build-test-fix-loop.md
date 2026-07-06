# Loop: build-test-fix

**Entry criteria:** A project has (or is suspected to have) a red build or
failing tests, and the user wants it green. Requires a project config with
`build_cmd` and `test_cmd`.

**Max iterations:** 5 (raise only if the user explicitly says so).

**Checkpoint file:** `state/btf-<project>.md`

```markdown
---
loop: build-test-fix
project: <id>
started: <ISO timestamp>
iteration: <n>
---
## Failure set (current)
- <test/error name>: <one-line diagnosis or "undiagnosed">

## Attempt log
### Iteration <n> — <timestamp>
- Intent: <fix being attempted, written BEFORE applying it>
- Result: <what the re-run showed>
```

## Per-iteration steps

1. **Checkpoint intent** — append the iteration header and the fix you intend
   to try. If your intended fix already appears in the attempt log with a
   failed result, choose differently or escalate to the user.
2. **Build** — run `build_cmd`. Compile errors become the failure set (skip tests).
3. **Test** — run `test_cmd` (scoped if the user scoped it). Parse the failure list.
4. **Diagnose one root cause** — the first/most fundamental failure. Read the
   actual error and the actual code; no fixes based on the test name alone.
5. **Fix minimally** — smallest change addressing the root cause. Forbidden
   without explicit user approval: deleting/skipping tests, loosening
   assertions, catching-and-ignoring exceptions.
6. **Verify** — re-run the scoped tests. Record the result in the attempt log.

## Exit criteria

- **Success:** scoped tests pass **and** a final full unscoped `test_cmd`
  passes. Then: remove the loop from `state/open-loops.json`, delete the
  checkpoint file, `db.py run finish` with status ok, summarize fixes.
- **Abort:** max iterations reached, or the same failure survives two
  different fixes, or a fix would require an architectural change. Then: keep
  the checkpoint file, leave the loop in `open-loops.json` with next-action
  set, report honestly.

## Verification step (every iteration)

The test run *is* the verification. Never mark an iteration successful from
reading code — only from a passing run.
