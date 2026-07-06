# Loop: draft-review-revise

**Entry criteria:** Producing prose or docs where quality matters — release
notes, design docs, READMEs, reports. Not for one-line answers.

**Max iterations:** 3 (draft + up to 2 revision passes; more revision than
that means requirements are unclear — go back to the user).

**Checkpoint:** the draft itself, written to its final destination path from
iteration 1 (e.g. the vault note or docs file). A separate
`state/draft-<slug>.md` is only needed if review notes must survive between
sessions; then it holds the current revision number and outstanding critique.

## Per-iteration steps

1. **Draft / revise** — write the full document (iteration 1) or apply the
   outstanding critique (2+). Always edit the file in place; the file is the state.
2. **Review as a different role** — re-read as the *audience*, not the author:
   - Release notes → a player who skipped the last version.
   - Docs → a new user with only the README.
   - Design docs → the implementer who has to build it.
   Produce concrete critique: unclear terms, unsourced claims, missing steps,
   buried leads.
3. **Verify facts** — every command, path, number, and name in the doc must be
   checked against reality (run it, open it, grep it) — not memory.
4. Decide: critique empty → exit. Otherwise next iteration with the critique
   as input.

## Exit criteria

- **Success:** a review pass produces no substantive critique and all facts
  verified. Deliver; clear the open-loop entry if one was registered.
- **Abort:** 3 iterations and the critique isn't shrinking → the requirements
  are ambiguous; present the two strongest variants to the user and ask.

## Verification step

Step 3 is non-negotiable: docs with untested commands are how trust dies.
