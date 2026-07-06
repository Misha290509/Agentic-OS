# Vault system folder

The only vault folder committed to git. Contains:

- `templates/` — note templates with the standard frontmatter
  (`title, created, updated, tags, status, related`). Wire them into Obsidian:
  Settings → Templates (or Templater) → folder = `90-system/templates`.
- `dashboards/` — Dataview-powered views (Home, per-project, weekly review).
  Require the **Dataview** community plugin with JavaScript queries enabled.

Vault layout (see also `docs/file-structure.md`):

| Folder | What goes there |
|---|---|
| `00-inbox/` | Anything unprocessed: `daily/` notes, `bugs/` raw reports, `playtests/` raw feedback. Skills drain these. |
| `10-projects/<id>/` | Active projects: `bugs/`, `playtests/`, `releases/`, dev logs. |
| `20-areas/` | Ongoing responsibilities without an end date (marketing, tooling, health-of-codebase). |
| `30-resources/` | Reference: `research/` outputs from the research loop, articles, snippets. |
| `40-archive/` | Processed raw material and finished projects, filed by `YYYY-MM`. |
| `90-system/` | This folder. Templates + dashboards, committed to git. |

To use an existing vault instead: set `vault_path` in `config/aios.json` and
copy `90-system/` into it.
