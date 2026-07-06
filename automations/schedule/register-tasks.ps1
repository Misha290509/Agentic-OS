# Register (or remove) AIOS automations in Windows Task Scheduler.
# Run from the repo root in an elevated PowerShell:
#   ./automations/schedule/register-tasks.ps1
#   ./automations/schedule/register-tasks.ps1 -Remove
param(
    [switch]$Remove,
    [string]$BashPath = "C:\Program Files\Git\bin\bash.exe"
)

$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$Tasks = @(
    @{ Name = "daily-dev-log"; Script = "automations/daily-dev-log.sh"; Time = "21:00" },
    @{ Name = "backup-state";  Script = "automations/backup-state.sh";  Time = "21:30" }
)

foreach ($t in $Tasks) {
    $full = "AIOS\$($t.Name)"
    if ($Remove) {
        Unregister-ScheduledTask -TaskName $full -Confirm:$false -ErrorAction SilentlyContinue
        Write-Host "Removed $full"
        continue
    }
    if (-not (Test-Path $BashPath)) {
        Write-Error "bash.exe not found at '$BashPath'. Install Git for Windows or pass -BashPath."
        exit 1
    }
    $action  = New-ScheduledTaskAction -Execute $BashPath `
        -Argument "-lc `"cd '$RepoRoot' && ./$($t.Script)`""
    $trigger = New-ScheduledTaskTrigger -Daily -At $t.Time
    Register-ScheduledTask -TaskName $full -Action $action -Trigger $trigger -Force | Out-Null
    Write-Host "Registered $full (daily at $($t.Time))"
}
