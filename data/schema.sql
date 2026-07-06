-- AIOS database schema. Applied idempotently by `scripts/db.py init`.
-- Documented in docs/data-model.md — keep the two in sync.

CREATE TABLE IF NOT EXISTS tasks (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT NOT NULL,
  description  TEXT NOT NULL DEFAULT '',
  status       TEXT NOT NULL DEFAULT 'open',  -- open | in_progress | done | dropped
  priority     INTEGER NOT NULL DEFAULT 3,    -- 1 (highest) .. 5 (lowest)
  project      TEXT NOT NULL DEFAULT '',
  source       TEXT NOT NULL DEFAULT '',      -- e.g. playtest:alpha-3, queue:morning-report
  created_at   TEXT NOT NULL,
  updated_at   TEXT NOT NULL,
  completed_at TEXT
);

CREATE TABLE IF NOT EXISTS bugs (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT NOT NULL,
  severity     TEXT NOT NULL DEFAULT 'S3',    -- S1..S4 (see skills/bug-triage)
  status       TEXT NOT NULL DEFAULT 'open',  -- open | needs-info | fixed | wontfix
  project      TEXT NOT NULL DEFAULT '',
  area         TEXT NOT NULL DEFAULT '',      -- gameplay | ui | audio | perf | save | build | other
  repro        TEXT NOT NULL DEFAULT '',
  notes        TEXT NOT NULL DEFAULT '',
  report_count INTEGER NOT NULL DEFAULT 1,
  first_seen   TEXT NOT NULL,
  last_seen    TEXT NOT NULL,
  fixed_at     TEXT
);

CREATE TABLE IF NOT EXISTS feedback (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  text       TEXT NOT NULL,
  playtest   TEXT NOT NULL DEFAULT '',        -- label, e.g. alpha-3
  category   TEXT NOT NULL DEFAULT 'design',  -- bug | design | praise | confusion | request
  sentiment  INTEGER NOT NULL DEFAULT 0,      -- -1 | 0 | 1
  theme      TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  automation  TEXT NOT NULL,
  started_at  TEXT NOT NULL,
  finished_at TEXT,
  status      TEXT NOT NULL DEFAULT 'running', -- running | ok | failed
  detail      TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS metrics (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL,
  value       REAL NOT NULL,
  unit        TEXT NOT NULL DEFAULT '',
  context     TEXT NOT NULL DEFAULT '',
  recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  ended_at   TEXT,
  focus      TEXT NOT NULL DEFAULT '',
  summary    TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_bugs_status    ON bugs(status, project);
CREATE INDEX IF NOT EXISTS idx_feedback_pt    ON feedback(playtest);
CREATE INDEX IF NOT EXISTS idx_runs_started   ON runs(started_at);
CREATE INDEX IF NOT EXISTS idx_metrics_name   ON metrics(name, recorded_at);
