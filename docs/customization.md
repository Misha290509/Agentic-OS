# Customizing the Dashboard & Views

All UI configuration lives in [`config/ui.json`](../config/ui.json). No code
changes are needed for: hiding panels, changing the refresh interval, theming,
adding quick actions, or tracking new metrics.

## config/ui.json reference

| Key | What it does |
|---|---|
| `refresh_seconds` | Poll interval for the web dashboard |
| `panels.<name>` | `true`/`false` — show/hide each panel |
| `quick_actions[]` | Buttons. `id` becomes the trigger file's `action`; must be `[a-z0-9-]+`. `label` is the button text, `hint` the tooltip |
| `metrics[]` | Which metric names (from the `metrics` table) to display, with label + unit |
| `limits` | Row caps per panel |
| `theme` | Hex tokens; applied at runtime as CSS variables (`dashboard/style.css` holds the same defaults) |

Changes take effect on the next poll — no server restart needed.

## Adding a quick action

1. Add `{ "id": "latest-deploy", "label": "Latest Deploy", "hint": "…" }` to
   `quick_actions`.
2. Clicking it queues `state/queue/<timestamp>-latest-deploy.json`.
3. Teach Claude what the action means: add a handling note to the relevant
   skill (or create one) — the session protocol in `CLAUDE.md` makes Claude
   check the queue at session start. Nothing else to wire up.

## Adding a new dashboard panel

Web dashboard (three small edits):

1. **Server** — in `scripts/serve_dashboard.py::overview()`, add a key to
   `data` (a `rows(con, "SELECT …")` call or a file read).
2. **Markup** — in `dashboard/index.html`, copy an existing
   `<article id="panel-XXX">` block.
3. **Renderer** — in `dashboard/app.js::render()`, add a
   `show("XXX", () => $("XXX").innerHTML = tbl(d.XXX, [...columns]))` line,
   and add `"XXX": true` to `panels` in `config/ui.json`.

Obsidian views:

- Add a Dataview block to `vault/90-system/dashboards/Home.md` (queries can
  only see vault files), **or**
- extend `scripts/sync_vault_views.py` to render new state/DB data into the
  embedded `state-snapshot.md`.

## Theming

Edit `theme` in `config/ui.json` — the dashboard applies tokens at runtime.
Keep status colors (`good/warning/serious/critical`) reserved for statuses;
they're paired with text labels everywhere so meaning never rides on color
alone. If you swap in your own palette, keep text/background contrast in mind
(the defaults are validated for the dark surface).

## Changing dashboard host/port

`config/aios.json` → `"dashboard": { "host": "127.0.0.1", "port": 8321 }`.
Keep the host on `127.0.0.1` — the server has no auth by design.
