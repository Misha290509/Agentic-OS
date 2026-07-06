# AIOS installer for Windows (PowerShell). Safe to re-run.
# The automations are bash scripts — Git for Windows (or WSL) provides bash.
#   ./install.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Say($m)  { Write-Host "==> $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "    + $m" -ForegroundColor Green }
function Warn($m) { Write-Host "    ! $m" -ForegroundColor Yellow }

Say "AIOS installer (Windows)"

Say "Checking dependencies"
$missing = $false
foreach ($dep in @("git", "python")) {
    if (Get-Command $dep -ErrorAction SilentlyContinue) { Ok $dep }
    else { Warn "$dep NOT FOUND"; $missing = $true }
}
if (-not (Get-Command bash -ErrorAction SilentlyContinue)) {
    Warn "bash not found - install Git for Windows for the automations (core AIOS still works)"
}
if ($missing) { exit 1 }

Say "Scaffolding directories"
$dirs = @("state\queue\done", "logs", "backups", "data",
    "vault\00-inbox\daily", "vault\00-inbox\bugs", "vault\00-inbox\playtests",
    "vault\10-projects", "vault\20-areas", "vault\30-resources\research",
    "vault\40-archive", "vault\90-system\dashboards")
foreach ($d in $dirs) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
Ok "directories ready"

Say "Initializing state (existing files kept)"
$pairs = @(
    @("state\current-focus.md", "state\current-focus.example.md"),
    @("state\session-log.md",   "state\session-log.example.md"),
    @("state\open-loops.json",  "state\open-loops.example.json"))
foreach ($p in $pairs) {
    if (Test-Path $p[0]) { Ok "$($p[0]) exists - kept" }
    else { Copy-Item $p[1] $p[0]; Ok "$($p[0]) created" }
}

Say "Configuration"
if (Test-Path "config\aios.json") { Ok "config\aios.json exists - kept" }
else {
    $owner = Read-Host "    Your name [$env:USERNAME]"
    if (-not $owner) { $owner = $env:USERNAME }
    $port = Read-Host "    Dashboard port [8321]"
    if (-not $port) { $port = 8321 }
    $cfg = Get-Content "config\aios.example.json" | ConvertFrom-Json
    $cfg.PSObject.Properties.Remove("_comment")
    $cfg.owner = $owner
    $cfg.dashboard.port = [int]$port
    $cfg | ConvertTo-Json -Depth 5 | Set-Content "config\aios.json"
    Ok "config\aios.json written"
}

Say "Database"
python scripts\db.py init | Out-Null
Ok "data\aios.db ready"

Say "Smoke test"
python scripts\sync_vault_views.py | Out-Null
Ok "vault snapshot renders"

Say "Done. Next steps:"
Write-Host @"
    1. claude                               # start Claude Code here
       > onboard me                         # personalize your AIOS
    2. python scripts\serve_dashboard.py    # http://127.0.0.1:$port
    3. Open vault\ in Obsidian (install the Dataview plugin)
    4. Schedule automations: automations\schedule\README.md (register-tasks.ps1)
"@
