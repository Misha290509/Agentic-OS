# File Structure

```
Agentic-OS/
├── CLAUDE.md                  # Operating manual every Claude session reads first
├── README.md                  # Project overview + quickstart
├── install.sh / install.ps1   # Interactive installers (Level 4)
├── skills/                    # ── BEHAVIOR ──────────────────────────────
│   ├── README.md              # Index: skill → trigger phrases → output
│   ├── _template/             # Copy to create a new skill
│   └── <skill>/SKILL.md       # One contract per workflow
├── loops/                     # Agentic loop specs (iterate + checkpoint contracts)
├── automations/               # Scripts that run without Claude
│   ├── lib/common.sh          # Shared logging + run-tracking
│   └── schedule/              # cron / launchd / Task Scheduler setup
├── state/                     # ── WORKING STATE (gitignored) ────────────
│   ├── current-focus.md       # What's being worked on and why
│   ├── session-log.md         # Newest-first session narrative
│   ├── open-loops.json        # In-flight multi-step work + checkpoints
│   ├── queue/                 # Trigger files from the dashboard (JSON)
│   │   └── done/              # Processed triggers
│   ├── *-checkpoint / btf-*   # Per-loop iteration state
│   └── *.example.*            # Committed shape references
├── vault/                     # ── LONG-TERM MEMORY (Obsidian vault) ─────
│   ├── 00-inbox/              # Unprocessed input: daily/, bugs/, playtests/
│   ├── 10-projects/<id>/      # Per project: bugs/, playtests/, releases/, devlog
│   ├── 20-areas/              # Ongoing responsibilities (no end date)
│   ├── 30-resources/          # Reference material, research/ outputs
│   ├── 40-archive/            # Processed/finished material, by YYYY-MM
│   └── 90-system/             # templates/, dashboards/ (committed)
├── data/                      # ── STRUCTURED MEMORY ─────────────────────
│   ├── schema.sql             # Committed schema (source of truth)
│   └── aios.db                # SQLite (gitignored); CLI: scripts/db.py
├── scripts/                   # CLI helpers used by humans, skills, automations
│   ├── db.py                  # The only sanctioned DB access path
│   └── serve_dashboard.py     # Local web dashboard server (Level 3)
├── dashboard/                 # Static SPA assets for the web dashboard
├── config/                    # ── PERSONALIZATION ───────────────────────
│   ├── aios.example.json      # → copy to aios.json (gitignored)
│   ├── ui.json                # Dashboard panels/theme/refresh (committed)
│   └── projects/*.json        # Per-project build/test commands (gitignored;
│                              #   .example committed)
├── logs/                      # <automation>/YYYY-MM-DD.log (gitignored)
├── backups/                   # Tarballs from backup-state.sh (gitignored)
├── docs/                      # You are here
└── data flow: skills read config → act → write vault/state → record in DB
                → dashboard and Obsidian views render DB + state.
```

## Ownership rules

- **Committed** (framework): skills, loops, automations, scripts, dashboard,
  docs, schema, templates, `.example` files.
- **Gitignored** (yours): `state/`, `logs/`, `backups/`, `data/*.db`,
  `config/aios.json`, `config/projects/*.json`, vault content outside `90-system/`.
- A fresh clone + `install.sh` recreates every gitignored directory; a
  `backup-state.sh` tarball restores your personal layer onto any clone.
