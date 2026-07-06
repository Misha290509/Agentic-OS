# Skill: release-notes

**Description:** Generate release notes for a version from git history, closed
bugs, completed tasks, and dev logs — in two voices: player-facing and internal.

**Trigger phrases:** "generate release notes for <version>", "draft the vX.Y
patch notes"

## Inputs

| Input | Required | Source |
|---|---|---|
| project id | yes | user or single config |
| version | yes | user (e.g. "v0.4.0") |
| git range | no | default: last tag → HEAD in the project repo |

## Procedure

Follow `loops/draft-review-revise-loop.md` for the writing phase.

1. Collect, for the range/period:
   - `git -C <path> log <last-tag>..HEAD --oneline`
   - `db.py bug list --project <id> --status fixed --since <last-release-date>`
   - `db.py task list --project <id> --completed --since <last-release-date>`
   - dev logs in `vault/00-inbox/daily/` for the period (skim for context)
2. Group into: **New**, **Improved**, **Fixed**, **Balance/Tuning**,
   **Known issues** (open S1/S2 bugs).
3. Draft two documents:
   - *Player-facing*: plain language, no internal jargon, no bug IDs, leads
     with the most exciting change.
   - *Internal*: same grouping but with bug IDs, commit refs, and migration or
     QA notes.
4. Review pass (per the loop): every claim must trace to a commit/bug/task;
   cut anything you can't source.
5. Write both to `vault/10-projects/<project>/releases/<version>.md`
   (player-facing first, internal below a `---` divider) and append the
   player-facing section to the project's `CHANGELOG.md` if it has one.
6. Verify with the user before anything is published anywhere external.

## Outputs

- `vault/10-projects/<project>/releases/<version>.md`
- Optional CHANGELOG fragment in the project repo (uncommitted).

## Example

> User: "generate release notes for v0.4.0"
>
> Result: 4 new features, 12 fixes (incl. BUG-7 save corruption), 2 known
> issues; player + internal notes written to the vault.

## Failure modes

- **No tags in repo** → ask for a start commit or date; suggest tagging this
  release afterwards.
- **Commit messages too cryptic to summarize** → cross-reference the dev logs
  for that day; if still unclear, list under internal notes only.
- **Fixed-bug list disagrees with git history** → trust git, flag the DB
  mismatch to the user.

## State & logging

- Checkpoint: draft lives in the vault from step 3 onward (the note *is* the state).
- DB records: none written; reads `bugs`, `tasks`.
