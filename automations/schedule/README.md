# Scheduling AIOS automations

Pick the section for your OS. All examples assume the repo lives at
`~/Agentic-OS` — adjust paths if yours differs.

## macOS (launchd — recommended over cron on Mac)

1. Edit the two `.plist` files here, replacing `/Users/YOURNAME/Agentic-OS`
   with your absolute repo path.
2. Install and load:

   ```bash
   cp automations/schedule/com.aios.*.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.aios.daily-dev-log.plist
   launchctl load ~/Library/LaunchAgents/com.aios.backup-state.plist
   ```

3. Verify: `launchctl list | grep com.aios` and check `logs/` after the first
   scheduled time (or force one: `launchctl start com.aios.daily-dev-log`).
4. Uninstall: `launchctl unload ~/Library/LaunchAgents/com.aios.<name>.plist`
   then delete the plist.

## Linux (cron)

```bash
crontab -e
```

Paste (adjusting the path) the contents of `crontab.example`:

```cron
0 21 * * *   $HOME/Agentic-OS/automations/daily-dev-log.sh
30 21 * * *  $HOME/Agentic-OS/automations/backup-state.sh
*/5 * * * *  $HOME/Agentic-OS/automations/watch-queue.sh --once
```

Verify with `crontab -l`; output/errors land in `logs/`.

## Windows (Task Scheduler)

The bash scripts run under Git Bash or WSL. From an elevated PowerShell in the
repo root:

```powershell
./automations/schedule/register-tasks.ps1          # registers both daily tasks
./automations/schedule/register-tasks.ps1 -Remove  # unregisters them
```

The script uses `bash.exe` from Git for Windows (`C:\Program Files\Git\bin`);
pass `-BashPath` if yours is elsewhere. Verify in Task Scheduler under the
`AIOS` folder, or run one manually: `Start-ScheduledTask -TaskName "AIOS\daily-dev-log"`.

## Which schedule to choose

- `daily-dev-log` before you typically write your dev log (default 21:00).
- `backup-state` after it (21:30), so the backup includes the day's collection.
- `watch-queue --once` every 5 minutes only if you use the dashboard's quick
  actions and want notifications; otherwise skip it — Claude checks the queue
  at session start anyway.
