# Workflow Audit

> **Status:** Derived from the owner's kickoff brief (2026-07-06). The interactive
> interview could not complete in the build session, so assumptions are flagged
> with ⚠️. Edit this file directly, or run the `onboarding` skill to redo the
> interview — skills and automations read nothing from this file at runtime, so
> it is safe to rewrite.

## Profile

| Field | Value |
|---|---|
| Primary work | Game development, software development, software testing |
| Existing tools | Obsidian, Notion, VS Code |
| OS | macOS (primary), Windows (available) |
| Technical comfort | Intermediate |
| Engine/stack | ⚠️ Assumed mixed/multiple — all build skills are engine-agnostic and read commands from `config/projects/*.json` |

## Ranked Workflows (by automation ROI)

ROI = (frequency × time saved × error reduction) ÷ setup cost.

### 1. Build–Test–Fix Loop — skill: `build-test-fix`
- **Trigger:** "run build-test-fix", after any significant code change, before a commit/release.
- **Inputs:** project id (from `config/projects/`), optional scope (test filter).
- **Steps:** build → run tests → parse failures → diagnose → apply smallest fix → re-run → repeat.
- **Outputs:** green build, fix log entry, run record in `data/aios.db`.
- **Frequency:** many times daily. **Pain point:** babysitting the loop manually; losing track of what was already tried.

### 2. Bug Triage & Reporting — skill: `bug-triage`
- **Trigger:** "triage bugs", new items land in `vault/00-inbox/bugs/` or are pasted in.
- **Inputs:** raw bug reports, crash logs, tester messages.
- **Steps:** parse → deduplicate against `bugs` table → classify severity/area → write structured tickets.
- **Outputs:** rows in `bugs` table, one Markdown ticket per bug in the project's vault folder.
- **Frequency:** daily during active testing. **Pain point:** duplicates and inconsistent severity calls.

### 3. Playtest Feedback Processing — skill: `playtest-feedback`
- **Trigger:** "process playtest feedback", after a playtest session.
- **Inputs:** raw notes/transcripts/survey exports dropped in `vault/00-inbox/playtests/`.
- **Steps:** ingest → cluster into themes → separate bugs (→ bug-triage) from design feedback → extract actionables.
- **Outputs:** themed summary note in vault, `feedback` rows, new tasks for actionables.
- **Frequency:** per playtest (⚠️ assumed ~weekly). **Pain point:** raw feedback piles up unread; signal gets lost.

### 4. Daily Dev Log — skill: `daily-dev-log` (+ automation `daily-dev-log.sh`)
- **Trigger:** "write my dev log", or scheduled at end of day.
- **Inputs:** git activity across configured project repos, session logs in `state/`, completed tasks.
- **Steps:** collect commits/tasks/sessions for the day → summarize → write daily note.
- **Outputs:** `vault/10-projects/<project>/devlog/` or daily note in `00-inbox` per template.
- **Frequency:** daily. **Pain point:** never gets written when done manually.

### 5. Release Notes Generation — skill: `release-notes`
- **Trigger:** "generate release notes for <version>", at release time.
- **Inputs:** git range (last tag → HEAD), closed bugs, completed tasks, dev logs for the period.
- **Steps:** collect → group (features / fixes / balance / known issues) → draft player-facing + internal notes.
- **Outputs:** `vault/10-projects/<project>/releases/<version>.md`, `CHANGELOG` fragment.
- **Frequency:** per release. **Pain point:** reconstructing what changed from memory.

### 6–8. Supporting workflows (built because the system needs them)
- **Session resume/end** — skills `resume-session` / `end-session`: reconstruct context from `state/` at start; checkpoint at end. Frequency: every session.
- **Morning report** — dashboard quick action → queue task: state of tasks, open loops, overnight automation runs.
- **Onboarding** — skill `onboarding`: runs this audit interview for a new user (Level 4).

## Open questions for the owner
1. Engine(s) and real build/test commands per project → fill in `config/projects/*.json`.
2. Existing Obsidian vault path (if you want to use it instead of `vault/`) → set `vault_path` in `config/aios.json`.
3. Playtest cadence and feedback sources (Discord? forms? in-person notes?) → affects `playtest-feedback` ingestion.
4. Notion: currently out of scope; everything is file/SQLite based. Say the word if you want a sync.
