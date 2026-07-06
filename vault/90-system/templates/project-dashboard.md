---
title: "{{project}} — Dashboard"
created: "{{date}}"
updated: "{{date}}"
tags: [system, dashboard, "{{project}}"]
status: active
related: []
---
# 🎮 {{project}} — Dashboard

Copy this into `10-projects/{{project}}/Dashboard.md` and replace `{{project}}`
in the queries' folder paths.

## Open bugs

```dataview
TABLE severity, status, file.mtime AS updated
FROM "10-projects/{{project}}/bugs"
WHERE status != "fixed" AND status != "wontfix"
SORT severity ASC
```

## Playtest history

```dataview
LIST
FROM "10-projects/{{project}}/playtests"
SORT file.name DESC
```

## Releases

```dataview
LIST
FROM "10-projects/{{project}}/releases"
SORT file.name DESC
```

## Machine state (all projects)

![[state-snapshot]]
