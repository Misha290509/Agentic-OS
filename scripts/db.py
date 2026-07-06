#!/usr/bin/env python3
"""AIOS database CLI — the only sanctioned way to touch data/aios.db.

Python 3.8+, stdlib only. Every subcommand prints human-readable output;
`--quiet` prints just the new row id (used by automations).

Examples:
    db.py init
    db.py task add "Fix save crash" --project mygame --priority 1
    db.py task list --status open
    db.py task done 3
    db.py bug add "Falls through floor" --severity S1 --area gameplay
    db.py bug update 2 --seen                 # duplicate report: bump count
    db.py feedback add "Tutorial too long" --playtest alpha-3 --sentiment -1
    db.py run start daily-dev-log             # prints run id
    db.py run finish 7 --status ok
    db.py metric add build_time 143 --unit s
    db.py session start --focus "alpha-3 stabilization"
    db.py session end 4 --summary "Fixed BUG-2, drafted release notes"
    db.py query "SELECT severity, COUNT(*) FROM bugs GROUP BY 1"

Schema: data/schema.sql, documented in docs/data-model.md.
"""
import argparse
import datetime
import os
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("AIOS_DB", os.path.join(ROOT, "data", "aios.db"))
SCHEMA = os.path.join(ROOT, "data", "schema.sql")


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db(con: sqlite3.Connection) -> None:
    with open(SCHEMA) as f:
        con.executescript(f.read())
    con.commit()


def ensure_db(con: sqlite3.Connection) -> None:
    row = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
    ).fetchone()
    if row is None:
        init_db(con)


def table(rows, columns) -> str:
    if not rows:
        return "(no rows)"
    data = [[("" if r[c] is None else str(r[c])) for c in columns] for r in rows]
    widths = [max(len(c), *(len(d[i]) for d in data)) for i, c in enumerate(columns)]
    fmt = "  ".join("{:<%d}" % w for w in widths)
    out = [fmt.format(*columns), fmt.format(*("-" * w for w in widths))]
    out += [fmt.format(*d) for d in data]
    return "\n".join(out)


def emit(args, row_id, message) -> None:
    print(row_id if args.quiet else message)


def main(argv=None) -> int:
    # --quiet is accepted anywhere in the command line
    argv = list(sys.argv[1:] if argv is None else argv)
    quiet = "--quiet" in argv
    argv = [a for a in argv if a != "--quiet"]

    p = argparse.ArgumentParser(
        prog="db.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="create tables from data/schema.sql (idempotent)")

    q = sub.add_parser("query", help="run a read-only SELECT")
    q.add_argument("sql")

    # task
    t = sub.add_parser("task", help="task queue").add_subparsers(dest="op", required=True)
    ta = t.add_parser("add")
    ta.add_argument("title")
    ta.add_argument("--description", default="")
    ta.add_argument("--project", default="")
    ta.add_argument("--priority", type=int, default=3)
    ta.add_argument("--source", default="")
    tl = t.add_parser("list")
    tl.add_argument("--status", default="open", help="open|in_progress|done|dropped|all")
    tl.add_argument("--project", default=None)
    tl.add_argument("--completed-on", dest="completed_on", default=None, metavar="YYYY-MM-DD")
    tl.add_argument("--completed", action="store_true", help="only done tasks")
    tl.add_argument("--since", default=None, metavar="YYYY-MM-DD")
    tl.add_argument("--limit", type=int, default=50)
    for op in ("start", "done", "drop"):
        t.add_parser(op).add_argument("id", type=int)

    # bug
    b = sub.add_parser("bug", help="bug tracker").add_subparsers(dest="op", required=True)
    ba = b.add_parser("add")
    ba.add_argument("title")
    ba.add_argument("--severity", default="S3", choices=["S1", "S2", "S3", "S4"])
    ba.add_argument("--project", default="")
    ba.add_argument("--area", default="")
    ba.add_argument("--repro", default="")
    ba.add_argument("--notes", default="")
    ba.add_argument("--status", default="open")
    bl = b.add_parser("list")
    bl.add_argument("--status", default="open", help="open|needs-info|fixed|wontfix|all")
    bl.add_argument("--project", default=None)
    bl.add_argument("--since", default=None, metavar="YYYY-MM-DD",
                    help="with --status fixed: fixed on/after this date")
    bl.add_argument("--limit", type=int, default=50)
    bu = b.add_parser("update")
    bu.add_argument("id", type=int)
    bu.add_argument("--status", default=None)
    bu.add_argument("--severity", default=None)
    bu.add_argument("--notes", default=None)
    bu.add_argument("--seen", action="store_true",
                    help="duplicate report: report_count+1, last_seen=now")

    # feedback
    f = sub.add_parser("feedback", help="playtest feedback").add_subparsers(dest="op", required=True)
    fa = f.add_parser("add")
    fa.add_argument("text")
    fa.add_argument("--playtest", default="")
    fa.add_argument("--category", default="design",
                    choices=["bug", "design", "praise", "confusion", "request"])
    fa.add_argument("--sentiment", type=int, default=0, choices=[-1, 0, 1])
    fa.add_argument("--theme", default="")
    fl = f.add_parser("list")
    fl.add_argument("--playtest", default=None)
    fl.add_argument("--limit", type=int, default=100)

    # run
    r = sub.add_parser("run", help="automation run history").add_subparsers(dest="op", required=True)
    rs = r.add_parser("start")
    rs.add_argument("automation")
    rs.add_argument("--detail", default="")
    rf = r.add_parser("finish")
    rf.add_argument("id", type=int)
    rf.add_argument("--status", default="ok", choices=["ok", "failed"])
    rf.add_argument("--detail", default=None)
    rl = r.add_parser("list")
    rl.add_argument("--limit", type=int, default=20)

    # metric
    m = sub.add_parser("metric", help="metrics").add_subparsers(dest="op", required=True)
    ma = m.add_parser("add")
    ma.add_argument("name")
    ma.add_argument("value", type=float)
    ma.add_argument("--unit", default="")
    ma.add_argument("--context", default="")
    ml = m.add_parser("list")
    ml.add_argument("--name", default=None)
    ml.add_argument("--limit", type=int, default=50)

    # session
    s = sub.add_parser("session", help="Claude session records").add_subparsers(dest="op", required=True)
    ss = s.add_parser("start")
    ss.add_argument("--focus", default="")
    se = s.add_parser("end")
    se.add_argument("id", type=int)
    se.add_argument("--summary", default="")
    sl = s.add_parser("list")
    sl.add_argument("--limit", type=int, default=10)

    args = p.parse_args(argv)
    args.quiet = quiet
    con = connect()

    if args.cmd == "init":
        init_db(con)
        emit(args, 0, f"initialized {DB_PATH}")
        return 0

    ensure_db(con)

    if args.cmd == "query":
        if not args.sql.lstrip().lower().startswith("select"):
            print("query accepts SELECT only; use the typed subcommands to write", file=sys.stderr)
            return 2
        rows = con.execute(args.sql).fetchall()
        print(table(rows, rows[0].keys() if rows else []))

    elif args.cmd == "task":
        if args.op == "add":
            cur = con.execute(
                "INSERT INTO tasks (title, description, status, priority, project, source,"
                " created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                (args.title, args.description, "open", args.priority, args.project,
                 args.source, now(), now()))
            emit(args, cur.lastrowid, f"task {cur.lastrowid} added: {args.title}")
        elif args.op == "list":
            sql, params = "SELECT * FROM tasks WHERE 1=1", []
            if args.completed_on:
                sql += " AND status='done' AND date(completed_at)=?"
                params.append(args.completed_on)
            elif args.completed:
                sql += " AND status='done'"
                if args.since:
                    sql += " AND date(completed_at)>=?"
                    params.append(args.since)
            elif args.status != "all":
                sql += " AND status=?"
                params.append(args.status)
            if args.project:
                sql += " AND project=?"
                params.append(args.project)
            sql += " ORDER BY priority, id DESC LIMIT ?"
            params.append(args.limit)
            rows = con.execute(sql, params).fetchall()
            print(table(rows, ["id", "priority", "status", "project", "title", "source"]))
        else:  # start / done / drop
            status = {"start": "in_progress", "done": "done", "drop": "dropped"}[args.op]
            completed = now() if args.op == "done" else None
            n = con.execute(
                "UPDATE tasks SET status=?, updated_at=?, completed_at=COALESCE(?, completed_at)"
                " WHERE id=?", (status, now(), completed, args.id)).rowcount
            if n == 0:
                print(f"no task with id {args.id}", file=sys.stderr)
                return 1
            emit(args, args.id, f"task {args.id} -> {status}")

    elif args.cmd == "bug":
        if args.op == "add":
            cur = con.execute(
                "INSERT INTO bugs (title, severity, status, project, area, repro, notes,"
                " first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?,?)",
                (args.title, args.severity, args.status, args.project, args.area,
                 args.repro, args.notes, now(), now()))
            emit(args, cur.lastrowid, f"bug {cur.lastrowid} added [{args.severity}]: {args.title}")
        elif args.op == "list":
            sql, params = "SELECT * FROM bugs WHERE 1=1", []
            if args.status != "all":
                sql += " AND status=?"
                params.append(args.status)
            if args.project:
                sql += " AND project=?"
                params.append(args.project)
            if args.since:
                sql += " AND date(COALESCE(fixed_at, last_seen))>=?"
                params.append(args.since)
            sql += " ORDER BY severity, id LIMIT ?"
            params.append(args.limit)
            rows = con.execute(sql, params).fetchall()
            print(table(rows, ["id", "severity", "status", "area", "report_count", "title"]))
        else:  # update
            sets, params = ["last_seen=?"], [now()]
            if args.seen:
                sets.append("report_count=report_count+1")
            if args.status:
                sets.append("status=?")
                params.append(args.status)
                if args.status == "fixed":
                    sets.append("fixed_at=?")
                    params.append(now())
            if args.severity:
                sets.append("severity=?")
                params.append(args.severity)
            if args.notes is not None:
                sets.append("notes=?")
                params.append(args.notes)
            params.append(args.id)
            n = con.execute(f"UPDATE bugs SET {', '.join(sets)} WHERE id=?", params).rowcount
            if n == 0:
                print(f"no bug with id {args.id}", file=sys.stderr)
                return 1
            emit(args, args.id, f"bug {args.id} updated")

    elif args.cmd == "feedback":
        if args.op == "add":
            cur = con.execute(
                "INSERT INTO feedback (text, playtest, category, sentiment, theme, created_at)"
                " VALUES (?,?,?,?,?,?)",
                (args.text, args.playtest, args.category, args.sentiment, args.theme, now()))
            emit(args, cur.lastrowid, f"feedback {cur.lastrowid} added")
        else:
            sql, params = "SELECT * FROM feedback WHERE 1=1", []
            if args.playtest:
                sql += " AND playtest=?"
                params.append(args.playtest)
            sql += " ORDER BY id LIMIT ?"
            params.append(args.limit)
            rows = con.execute(sql, params).fetchall()
            print(table(rows, ["id", "playtest", "category", "sentiment", "theme", "text"]))

    elif args.cmd == "run":
        if args.op == "start":
            cur = con.execute(
                "INSERT INTO runs (automation, started_at, status, detail) VALUES (?,?,?,?)",
                (args.automation, now(), "running", args.detail))
            emit(args, cur.lastrowid, f"run {cur.lastrowid} started: {args.automation}")
        elif args.op == "finish":
            sets, params = ["finished_at=?", "status=?"], [now(), args.status]
            if args.detail is not None:
                sets.append("detail=?")
                params.append(args.detail)
            params.append(args.id)
            n = con.execute(f"UPDATE runs SET {', '.join(sets)} WHERE id=?", params).rowcount
            if n == 0:
                print(f"no run with id {args.id}", file=sys.stderr)
                return 1
            emit(args, args.id, f"run {args.id} -> {args.status}")
        else:
            rows = con.execute(
                "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (args.limit,)).fetchall()
            print(table(rows, ["id", "automation", "status", "started_at", "finished_at", "detail"]))

    elif args.cmd == "metric":
        if args.op == "add":
            cur = con.execute(
                "INSERT INTO metrics (name, value, unit, context, recorded_at) VALUES (?,?,?,?,?)",
                (args.name, args.value, args.unit, args.context, now()))
            emit(args, cur.lastrowid, f"metric {args.name}={args.value}{args.unit} recorded")
        else:
            sql, params = "SELECT * FROM metrics WHERE 1=1", []
            if args.name:
                sql += " AND name=?"
                params.append(args.name)
            sql += " ORDER BY id DESC LIMIT ?"
            params.append(args.limit)
            rows = con.execute(sql, params).fetchall()
            print(table(rows, ["id", "name", "value", "unit", "recorded_at", "context"]))

    elif args.cmd == "session":
        if args.op == "start":
            cur = con.execute(
                "INSERT INTO sessions (started_at, focus) VALUES (?,?)", (now(), args.focus))
            emit(args, cur.lastrowid, f"session {cur.lastrowid} started")
        elif args.op == "end":
            n = con.execute(
                "UPDATE sessions SET ended_at=?, summary=? WHERE id=?",
                (now(), args.summary, args.id)).rowcount
            if n == 0:
                print(f"no session with id {args.id}", file=sys.stderr)
                return 1
            emit(args, args.id, f"session {args.id} ended")
        else:
            rows = con.execute(
                "SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (args.limit,)).fetchall()
            print(table(rows, ["id", "started_at", "ended_at", "focus", "summary"]))

    con.commit()
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
