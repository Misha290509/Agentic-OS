#!/usr/bin/env python3
"""AIOS dashboard server — stdlib only, binds localhost.

    python3 scripts/serve_dashboard.py            # http://127.0.0.1:8321
    python3 scripts/serve_dashboard.py --port 9000

Serves the static SPA from dashboard/ plus two endpoints:

    GET  /api/overview   everything the dashboard shows, one JSON blob
                         (state files + SQLite + queue + config/ui.json)
    POST /api/action     {"action": "<id from ui.json quick_actions>"}
                         -> writes state/queue/<timestamp>-<id>.json for
                         Claude to pick up at session start (CLAUDE.md)

Host/port come from config/aios.json (falling back to aios.example.json).
"""
import json
import os
import re
import sqlite3
import sys
import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "data", "aios.db")
UI_CONFIG = os.path.join(ROOT, "config", "ui.json")
QUEUE_DIR = os.path.join(ROOT, "state", "queue")


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def read_text(path, default=""):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return default


def rows(con, sql, params=()):
    try:
        cur = con.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    except sqlite3.Error:
        return []


def overview():
    ui = load_json(UI_CONFIG, {})
    lim = ui.get("limits", {})
    data = {
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ui": ui,
        "focus": read_text(os.path.join(ROOT, "state", "current-focus.md")),
        "open_loops": (load_json(os.path.join(ROOT, "state", "open-loops.json"), {}) or {}).get("loops", []),
        "session_log": read_text(os.path.join(ROOT, "state", "session-log.md")),
        "queue": [], "tasks": [], "bugs": [], "runs": [], "sessions": [], "metrics": [],
        "counts": {},
    }
    if os.path.isdir(QUEUE_DIR):
        for name in sorted(os.listdir(QUEUE_DIR)):
            if name.endswith(".json"):
                item = load_json(os.path.join(QUEUE_DIR, name), {}) or {}
                item["_file"] = name
                data["queue"].append(item)
    if os.path.exists(DB_PATH):
        con = sqlite3.connect(DB_PATH)
        data["tasks"] = rows(con, "SELECT id,title,status,priority,project,source FROM tasks"
                                  " WHERE status IN ('open','in_progress')"
                                  " ORDER BY priority,id DESC LIMIT ?", (lim.get("tasks", 12),))
        data["bugs"] = rows(con, "SELECT id,title,severity,status,area,report_count FROM bugs"
                                 " WHERE status IN ('open','needs-info')"
                                 " ORDER BY severity,id LIMIT 20")
        data["runs"] = rows(con, "SELECT id,automation,status,started_at,finished_at,detail FROM runs"
                                 " ORDER BY id DESC LIMIT ?", (lim.get("runs", 8),))
        data["sessions"] = rows(con, "SELECT id,started_at,ended_at,focus,summary FROM sessions"
                                     " ORDER BY id DESC LIMIT ?", (lim.get("sessions", 5),))
        for m in ui.get("metrics", []):
            series = rows(con, "SELECT value,recorded_at FROM metrics WHERE name=?"
                               " ORDER BY id DESC LIMIT ?", (m["name"], lim.get("metrics", 6)))
            data["metrics"].append({**m, "latest": series[0] if series else None,
                                    "history": list(reversed(series))})
        c = {}
        c["open_tasks"] = rows(con, "SELECT COUNT(*) n FROM tasks WHERE status IN ('open','in_progress')")[0]["n"]
        c["open_bugs_s1s2"] = rows(con, "SELECT COUNT(*) n FROM bugs WHERE status IN ('open','needs-info')"
                                        " AND severity IN ('S1','S2')")[0]["n"]
        c["open_bugs"] = rows(con, "SELECT COUNT(*) n FROM bugs WHERE status IN ('open','needs-info')")[0]["n"]
        c["failed_runs_7d"] = rows(con, "SELECT COUNT(*) n FROM runs WHERE status='failed'"
                                        " AND started_at >= datetime('now','-7 days')")[0]["n"]
        data["counts"] = c
        con.close()
    data["counts"]["open_loops"] = len(data["open_loops"])
    data["counts"]["queue"] = len(data["queue"])
    return data


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(ROOT, "dashboard"), **kwargs)

    def log_message(self, fmt, *args):  # quieter default logging
        sys.stderr.write("%s %s\n" % (self.log_date_time_string(), fmt % args))

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/overview":
            self._json(overview())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/action":
            self._json({"error": "not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._json({"error": "bad json"}, 400)
            return
        action = payload.get("action", "")
        allowed = {a["id"] for a in load_json(UI_CONFIG, {}).get("quick_actions", [])}
        if action not in allowed or not re.fullmatch(r"[a-z0-9-]+", action):
            self._json({"error": f"unknown action '{action}'"}, 400)
            return
        os.makedirs(QUEUE_DIR, exist_ok=True)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"{stamp}-{action}.json"
        with open(os.path.join(QUEUE_DIR, fname), "w") as f:
            json.dump({"action": action, "requested_at": stamp, "via": "dashboard"}, f, indent=2)
        self._json({"ok": True, "queued": fname})


def main():
    cfg = load_json(os.path.join(ROOT, "config", "aios.json")) or \
          load_json(os.path.join(ROOT, "config", "aios.example.json")) or {}
    dash = cfg.get("dashboard", {})
    host = dash.get("host", "127.0.0.1")
    port = dash.get("port", 8321)
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    server = HTTPServer((host, port), Handler)
    print(f"AIOS dashboard: http://{host}:{port}  (ctrl-c to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
