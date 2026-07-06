# Skills Index

Each skill is a folder with a `SKILL.md` contract. When a user request matches
a trigger phrase, follow that file exactly. Add new skills by copying
`_template/`.

| Skill | Invoke when the user says… | Output |
|---|---|---|
| [`build-test-fix`](build-test-fix/SKILL.md) | "run build-test-fix", "get the build green", "fix the failing tests" | Green build + fix log + DB run record |
| [`bug-triage`](bug-triage/SKILL.md) | "triage bugs", "process the bug inbox", pastes raw bug reports | Deduped `bugs` rows + Markdown tickets in vault |
| [`playtest-feedback`](playtest-feedback/SKILL.md) | "process playtest feedback", "what did testers say" | Themed summary note + `feedback` rows + tasks |
| [`daily-dev-log`](daily-dev-log/SKILL.md) | "write my dev log", "what did I do today" | Daily note in vault from git + tasks + sessions |
| [`release-notes`](release-notes/SKILL.md) | "generate release notes for vX.Y" | Player-facing + internal notes in vault |
| [`resume-session`](resume-session/SKILL.md) | "resume", "where were we", session start | Reconstructed context briefing |
| [`end-session`](end-session/SKILL.md) | "wrap up", "end session" | Updated `state/` + session DB record |
| [`onboarding`](onboarding/SKILL.md) | "onboard me", first run for a new user | Personalized config, audit, and vault |

## Conventions all skills follow

- Read config from `config/aios.json` (fall back to `config/aios.example.json` defaults).
- Write vault outputs with the standard YAML frontmatter (see `CLAUDE.md`).
- Touch the DB only through `scripts/db.py`.
- Multi-step skills checkpoint under `state/` so any session can resume them.
