---
title: "Weekly Review"
created: "2026-07-06"
updated: "2026-07-06"
tags: [system, dashboard, review]
status: active
related: []
---
# 🗓 Weekly Review

> [!tip] Work through top to bottom once a week. The queries pull the week's
> raw material; the prompts at the end are the actual review.

## This week's daily notes

```dataview
LIST
FROM "00-inbox/daily"
WHERE file.day >= date(today) - dur(7 days)
SORT file.name DESC
```

## Bugs opened this week

```dataview
TABLE severity, status
FROM "10-projects"
WHERE contains(tags, "bug") AND file.cday >= date(today) - dur(7 days)
SORT severity ASC
```

## Playtests this week

```dataview
LIST
FROM "10-projects"
WHERE contains(tags, "playtest") AND file.cday >= date(today) - dur(7 days)
```

## Current machine state

![[state-snapshot]]

---

## Review prompts

- [ ] What shipped this week? (check the dev logs above)
- [ ] Which open loop has been stuck the longest — kill it or unblock it?
- [ ] Any S1/S2 bug older than a week? Why?
- [ ] What did playtesters keep repeating?
- [ ] Update `state/current-focus.md` for next week (or tell Claude to)
