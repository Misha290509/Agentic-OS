# Changelog

All notable changes to AIOS. Format follows
[Keep a Changelog](https://keepachangelog.com); versions follow semver.

## [Unreleased]

## [0.1.0] — 2026-07-06

Initial release: the full 4-level system.

### Added
- **Level 1:** `skills/` (build-test-fix, bug-triage, playtest-feedback,
  daily-dev-log, release-notes, resume/end-session, onboarding + template),
  `loops/` (build-test-fix, research, draft-review-revise, triage),
  `automations/` (daily-dev-log, watch-queue, backup-state + cron/launchd/
  Task Scheduler setup), root `CLAUDE.md` operating manual.
- **Level 2:** SQLite schema + `scripts/db.py` CLI (tasks, bugs, feedback,
  runs, metrics, sessions), `state/` session protocol (current-focus,
  session-log, open-loops, queue), Obsidian vault structure + note templates.
- **Level 3:** local web dashboard (`scripts/serve_dashboard.py` +
  `dashboard/`) with quick actions that queue triggers for Claude,
  `config/ui.json` customization, Obsidian Home/Weekly Review/project
  dashboards fed by `scripts/sync_vault_views.py`.
- **Level 4:** `install.sh` / `install.ps1`, getting-started guide,
  onboarding skill, MIT license, contributing guide.
