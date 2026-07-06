---
title: "Home"
created: "2026-07-06"
updated: "2026-07-06"
tags: [system, dashboard]
status: active
related: []
---
# 🏠 AIOS Home

> [!tip] Same state as the web dashboard (`python3 scripts/serve_dashboard.py`).
> The snapshot below refreshes when `scripts/sync_vault_views.py` runs
> (end-session does this; you can also schedule it).

![[state-snapshot]]

---

## 📥 Inbox (unprocessed)

Needs a skill run if anything shows up here:

```dataview
LIST
FROM "00-inbox"
WHERE file.name != ".gitkeep"
SORT file.mtime DESC
LIMIT 15
```

## 🎮 Active projects

```dataview
TABLE status, updated
FROM "10-projects"
WHERE contains(tags, "project") AND status = "active"
SORT updated DESC
```

## 📅 Recent daily notes

```dataview
LIST
FROM "00-inbox/daily"
SORT file.name DESC
LIMIT 7
```
