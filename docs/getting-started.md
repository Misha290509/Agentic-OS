# Getting Started

You have [Claude Code](https://claude.com/claude-code) installed. This gets
you from zero to a personalized AIOS in about 20 minutes.

## 1. Install (2 min)

```bash
git clone https://github.com/misha290509/agentic-os.git
cd agentic-os
./install.sh        # Windows: ./install.ps1 in PowerShell
```

The installer checks dependencies (`git`, `python3` 3.8+ — nothing else),
creates the personal directories (`state/`, `logs/`, `data/`, vault subtrees),
copies the example state files, asks three questions (name, timezone,
dashboard port) to write `config/aios.json`, and initializes the SQLite
database. Re-running is safe: it never overwrites files you already have.

## 2. Onboard (10 min)

```bash
claude
> onboard me
```

Claude runs the onboarding skill: it interviews you about your work, writes
*your* `docs/workflow-audit.md`, fills in `config/aios.json` and your first
`config/projects/<id>.json`, sets your `state/current-focus.md`, and tells you
which existing skills match your workflows (and drafts new ones for workflows
that don't match).

## 3. Learn the three sentences that run everything

| You say | What happens |
|---|---|
| `resume where we left off` | Claude reconstructs full context from `state/` + DB and proposes the next action |
| `run my <skill> skill` (e.g. `triage bugs`) | Claude executes that `SKILL.md` contract |
| `wrap up` | Claude checkpoints everything to disk so tomorrow's session resumes cold |

The complete skill list with trigger phrases: [`skills/README.md`](../skills/README.md).

## 4. Open the interfaces (5 min)

**Web dashboard:**

```bash
python3 scripts/serve_dashboard.py
# → http://127.0.0.1:8321
```

Live view of focus, tasks, bugs, loops, automation runs; the buttons queue
trigger files that Claude processes at its next session start.

**Obsidian:** open the `vault/` folder as a vault, install the community
**Dataview** plugin, then open `90-system/dashboards/Home.md` and pin it.

## 5. Schedule the automations (3 min, optional)

Follow [`automations/schedule/README.md`](../automations/schedule/README.md)
for your OS. Start with `daily-dev-log` (nightly git-activity collection) and
`backup-state` (daily snapshot of your personal layer into `backups/`).

## Daily rhythm

1. `claude` → "resume where we left off"
2. Work — Claude follows skills and loops, checkpointing as it goes
3. "wrap up" before you leave
4. "write my dev log" (or let the nightly automation pre-collect and do it
   next morning)

## When something breaks

- Dashboard empty → is `data/aios.db` there? `python3 scripts/db.py init`
- Claude seems lost → point it at `CLAUDE.md` ("read CLAUDE.md first")
- A loop died mid-flight → its checkpoint file under `state/` says exactly
  where it stopped; "resume" picks it up
- Restore from backup → `tar -xzf backups/aios-backup-<stamp>.tar.gz -C .`
