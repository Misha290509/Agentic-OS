# Skill: onboarding

**Description:** Personalize a fresh AIOS clone for a new user: interview them
(the Level-1 workflow audit), write their config and state, and map their
workflows onto skills.

**Trigger phrases:** "onboard me", "set up my AIOS", "personalize this",
first session in a repo where `docs/workflow-audit.md` still carries the
template owner's data

## Inputs

| Input | Required | Source |
|---|---|---|
| the user's answers | yes | interactive interview (below) |

## Procedure

1. **Precheck.** If `./install.sh` hasn't run (no `state/current-focus.md` or
   no `data/aios.db`), run it with the user (`./install.sh`) before anything else.
2. **Interview — one topic at a time, not a wall of questions:**
   a. What's your primary work? Typical day/week?
   b. Which tools/engines/languages? (per project: how do you build? how do
      you test? — exact commands)
   c. Which workflows repeat most? For each: trigger, inputs, steps, outputs,
      frequency, pain points. Push for 5–10.
   d. What should never be automated? (their "human-only" list)
   e. Obsidian: existing vault to point at (`vault_path`), or the bundled `vault/`?
3. **Write the audit:** rewrite `docs/workflow-audit.md` with *their* profile
   and ranked workflows (ROI = frequency × time saved ÷ setup cost). This
   file describes the owner — replacing it is the point.
4. **Write config:** update `config/aios.json` (owner, vault_path, timezone);
   create `config/projects/<id>.json` per project with the real build/test
   commands from 2b.
5. **Map workflows → skills.** For each audited workflow: name the existing
   skill that covers it, or create a new one from `skills/_template/`
   (add it to `skills/README.md`). Game-dev defaults cover: build-test-fix,
   bug-triage, playtest-feedback, daily-dev-log, release-notes.
6. **Initialize state:** rewrite `state/current-focus.md` with their actual
   current focus (from the interview); reset `state/session-log.md` with an
   "onboarded" first entry; empty `state/open-loops.json` loops array.
7. **Verify — run one real skill end-to-end** (usually `daily-dev-log`
   against one of their repos) and show the output.
8. **Tour:** show them the three sentences (`resume…`, `run my … skill`,
   `wrap up`), the dashboard command, and `docs/getting-started.md`.

## Outputs

- Personalized `docs/workflow-audit.md`, `config/aios.json`,
  `config/projects/*.json`, `state/*`; possibly new skills.

## Example

> User: "onboard me"
>
> Result: 15-minute interview → audit with 7 ranked workflows, 2 project
> configs, 1 new custom skill (`localization-check`), dev-log skill
> demonstrated on their repo.

## Failure modes

- **User unsure about workflows** → walk through "yesterday, hour by hour"
  instead of asking abstractly.
- **Build/test commands unknown** → create the project config with `TODO`
  placeholders and a task (`db.py task add "Fill in build/test commands for <id>"`).
- **Existing vault has a different folder scheme** → don't restructure it;
  set `vault_path` and record their scheme in `docs/workflow-audit.md` so
  skills write to the right places.

## State & logging

- This skill rewrites the personal layer by design; it must never touch
  framework files except to *add* skills.
- DB records: initial tasks from the interview's pain points.
