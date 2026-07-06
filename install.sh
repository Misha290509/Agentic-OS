#!/usr/bin/env bash
# AIOS installer — scaffolds the personal layer on a fresh clone.
# Safe to re-run: never overwrites existing personal files.
#
#   ./install.sh            interactive
#   ./install.sh --defaults non-interactive (CI / scripted)

set -euo pipefail
cd "$(dirname "$0")"
DEFAULTS=0
[ "${1:-}" = "--defaults" ] && DEFAULTS=1

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
ok()   { printf '    \033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '    \033[1;33m!\033[0m %s\n' "$*"; }

ask() { # var prompt default
  local var="$1" prompt="$2" default="$3" reply
  if [ "$DEFAULTS" = 1 ]; then
    eval "$var=\"\$default\""
    return
  fi
  read -r -p "    $prompt [$default]: " reply || reply=""
  eval "$var=\"\${reply:-\$default}\""
}

say "AIOS installer"

# 1. Dependencies ------------------------------------------------------------
say "Checking dependencies"
missing=0
for dep in git python3 bash; do
  if command -v "$dep" >/dev/null 2>&1; then ok "$dep"; else
    warn "$dep NOT FOUND — install it and re-run"; missing=1
  fi
done
python3 - <<'PY' || { warn "python3 must be 3.8+"; missing=1; }
import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)
PY
[ "$missing" = 0 ] || exit 1
command -v claude >/dev/null 2>&1 && ok "claude (Claude Code)" \
  || warn "claude CLI not found — install from https://claude.com/claude-code (AIOS still installs)"

# 2. Directories -------------------------------------------------------------
say "Scaffolding directories"
mkdir -p state/queue/done logs backups data \
  vault/00-inbox/{daily,bugs,playtests} vault/10-projects vault/20-areas \
  vault/30-resources/research vault/40-archive vault/90-system/dashboards
ok "state/, logs/, backups/, data/, vault/ subtrees"

# 3. State files from examples ------------------------------------------------
say "Initializing state (existing files are left untouched)"
init_from_example() { # target example
  if [ -f "$1" ]; then ok "$1 exists — kept"; else cp "$2" "$1"; ok "$1 created from example"; fi
}
init_from_example state/current-focus.md  state/current-focus.example.md
init_from_example state/session-log.md    state/session-log.example.md
init_from_example state/open-loops.json   state/open-loops.example.json

# 4. Config ------------------------------------------------------------------
say "Configuration"
if [ -f config/aios.json ]; then
  ok "config/aios.json exists — kept"
else
  ask OWNER   "Your name" "$(whoami)"
  ask TZNAME  "Timezone (IANA)" "$( { readlink /etc/localtime 2>/dev/null | sed 's|.*/zoneinfo/||'; } || echo UTC )"
  ask PORT    "Dashboard port" "8321"
  python3 - "$OWNER" "$TZNAME" "$PORT" <<'PY'
import json, sys
cfg = json.load(open("config/aios.example.json"))
cfg.pop("_comment", None)
cfg.update(owner=sys.argv[1], timezone=sys.argv[2])
cfg["dashboard"]["port"] = int(sys.argv[3])
json.dump(cfg, open("config/aios.json", "w"), indent=2)
PY
  ok "config/aios.json written"
fi
[ -e config/projects/.gitkeep ] || touch config/projects/.gitkeep
ok "add your projects as config/projects/<id>.json (see example-game.json.example)"

# 5. Database ----------------------------------------------------------------
say "Database"
python3 scripts/db.py init >/dev/null && ok "data/aios.db ready (schema: data/schema.sql)"

# 6. Permissions & smoke test --------------------------------------------------
chmod +x automations/*.sh scripts/*.py 2>/dev/null || true
say "Smoke test"
python3 scripts/db.py query "SELECT COUNT(*) AS tables FROM sqlite_master WHERE type='table'" >/dev/null && ok "db.py query works"
python3 scripts/sync_vault_views.py >/dev/null && ok "vault snapshot renders"

# 7. Next steps ----------------------------------------------------------------
say "Done. Next steps:"
cat <<'EOF'
    1. claude                                  # start Claude Code here
       > onboard me                            # personalize your AIOS
    2. python3 scripts/serve_dashboard.py      # http://127.0.0.1:<port>
    3. Open vault/ in Obsidian (install the Dataview plugin)
    4. Schedule automations: automations/schedule/README.md
EOF
