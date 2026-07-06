# Contributing

AIOS is a framework plus a personal layer. Contributions belong to the
framework; the personal layer (`state/`, `data/*.db`, `config/aios.json`,
vault content) is gitignored and must stay that way.

## Ground rules

1. **Nothing undocumented.** A new skill, automation, or config key ships with
   its docs (SKILL.md, README table row, or docs/ page) in the same PR.
2. **Stdlib only.** `scripts/` and `automations/` must run on a fresh macOS/
   Linux box with bash + python3 — no pip installs, no npm.
3. **Never leak personal data.** No real paths, names, or project details in
   examples — extend the `.example` files instead. Run
   `git status --ignored` before committing if unsure.
4. **Test what you add.** Run the script/skill and paste its output in the PR.

## Adding a skill

1. `cp -r skills/_template skills/<name>` and fill every section — trigger
   phrases, procedure with exact paths/commands, failure modes.
2. Add a row to `skills/README.md`.
3. If it's multi-step, reference (or add) a loop spec in `loops/`.

## Adding an automation

1. Follow the pattern in `automations/README.md` (`aios_init`/`aios_finish`,
   log to `logs/`, idempotent).
2. Add it to the automations table and, if schedulable, to
   `automations/schedule/` (all three OSes or a note on which it supports).

## Schema changes

Additive only (`CREATE TABLE IF NOT EXISTS` / new columns via migration note);
`db.py init` must remain safe on existing databases. Update
`docs/data-model.md` in the same commit.

## Commit style

Present-tense summary line, body explaining *why*. One logical change per
commit. Update `CHANGELOG.md` under "Unreleased" for user-visible changes.
