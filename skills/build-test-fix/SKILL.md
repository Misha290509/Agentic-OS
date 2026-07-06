# Skill: build-test-fix

**Description:** Drive a project to a green build by looping build → test →
diagnose → fix until everything passes. Engine/language-agnostic: the actual
commands come from the project's config file.

**Trigger phrases:** "run build-test-fix", "get the build green", "fix the
failing tests", "run the BTF loop on <project>"

## Inputs

| Input | Required | Source |
|---|---|---|
| project id | yes | user, or the single entry in `config/projects/` if only one exists |
| scope/filter | no | user (e.g. "only the inventory tests") |
| max iterations | no | default 5 (from loop spec) |

Project config `config/projects/<id>.json` must define `path`, `build_cmd`,
`test_cmd`, and optionally `test_filter_flag`, `log_hints`.

## Procedure

Follow `loops/build-test-fix-loop.md`. Summary:

1. Read `config/projects/<id>.json`. If missing, ask the user for build/test
   commands and offer to save them as a new project config.
2. Register the run: `python3 scripts/db.py run start build-test-fix --detail "<project>"`.
3. Create checkpoint `state/btf-<project>.md` (from the loop spec's template)
   listing: iteration, failures seen, fixes attempted.
4. **Loop (max 5 iterations):**
   a. Run `build_cmd` in `path`. On build failure, treat compile errors as the
      failure set.
   b. Run `test_cmd` (with filter if scoped). Parse failures.
   c. If zero failures → exit loop.
   d. Diagnose the *first* root cause, not every symptom. Check the checkpoint
      file — never retry an already-failed fix unchanged.
   e. Apply the smallest fix that addresses the root cause. Never weaken or
      delete a test to make it pass without explicit user approval.
   f. Append iteration record to the checkpoint file.
5. Verify: full unfiltered `test_cmd` passes at the end even if the loop ran scoped.
6. Close out: `db.py run finish <run_id> --status ok|failed`, delete the
   checkpoint file on success (leave it on failure — it's the handoff),
   summarize fixes for the user.

## Outputs

- Code changes in the project working tree (uncommitted unless asked).
- Run record in `runs` table; fix summary in chat and, if a session wrap-up
  happens, in the session log.

## Example

> User: "run build-test-fix on mygame, just the save-system tests"
>
> Result: 2 iterations, fixed null-check in `SaveSlot.cs`, 47/47 tests green.

## Failure modes

- **Max iterations reached** → stop, leave checkpoint file, report the
  remaining failures and what was tried. Do not thrash.
- **Same test flips pass/fail across runs** → flag as flaky, record it as a bug
  via `db.py bug add`, don't chase it in this loop.
- **Build command itself not found** → fix the config with the user; don't
  guess alternate toolchains.

## State & logging

- Checkpoint: `state/btf-<project>.md` (one per project, overwritten per run)
- DB records: `runs`
