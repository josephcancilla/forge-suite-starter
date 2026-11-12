# Scheduling the nightly learning run

`forge-learn all` is the only Forge job meant to run on a schedule. Each night it reviews what the Forge agents produced that day and writes lessons that shape their next run. It is built to be cheap: if nothing was built in the last 24 hours, it records a "skipped" receipt and makes no Claude call at all. It also skips itself if it already ran successfully in the last 18 hours, so a missed run that catches up later never double-fires.

Everything else in Forge (SpecMan, Builder, and the rest) runs only when you or your commander agent start it. You can skip scheduling entirely and run `forge-learn all` by hand now and then.

Before you schedule anything, test it once by hand. This prints the plan and writes nothing:

```
forge-learn --dry-run all
```

## Windows: Task Scheduler

You need Git for Windows (it provides Git Bash) and Python 3 installed, and the suite installed under `%USERPROFILE%\.forge-suite` (or wherever `FORGE_HOME` points). The task runs the script through Git Bash.

Open PowerShell and run these lines. They create a task named `ForgeLearn` that runs at 2:00 AM every day, and that also runs once as soon as possible if the computer was off at 2:00 AM.

```powershell
$bash     = "C:\Program Files\Git\bin\bash.exe"
$cmd      = '-lc "mkdir -p $HOME/.forge-suite/logs && $HOME/.forge-suite/bin/forge-learn all >> $HOME/.forge-suite/logs/forge-learn.log 2>&1"'
$action   = New-ScheduledTaskAction -Execute $bash -Argument $cmd
$trigger  = New-ScheduledTaskTrigger -Daily -At 2:00AM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
Register-ScheduledTask -TaskName "ForgeLearn" -Action $action -Trigger $trigger -Settings $settings
```

Notes:

- The single quotes keep `$HOME` literal, so Git Bash expands it, not PowerShell.
- If Git for Windows is installed somewhere else, change the `$bash` path.
- If `python3` is not found in Git Bash, see the Windows notes in the README.
- By default the task runs only while you are logged in, which is what you want. Your Claude Code login lives in your user profile.
- The task finds the Claude CLI on your PATH. If it does not, add `export CLAUDE_BIN=$HOME/.local/bin/claude;` at the start of the `-lc` string (use the real location of `claude.exe` if it differs).

Check it, run it now, or remove it:

```powershell
Get-ScheduledTask -TaskName "ForgeLearn"
Start-ScheduledTask -TaskName "ForgeLearn"
Unregister-ScheduledTask -TaskName "ForgeLearn" -Confirm:$false
```

Where to look afterwards: the log is `%USERPROFILE%\.forge-suite\logs\forge-learn.log`, and each real run adds one line to `%USERPROFILE%\.forge-suite\state\receipts\forge-learn.jsonl` with the status `ok`, `skipped`, or `error`.

Prefer clicking? Open Task Scheduler, choose Create Task, add a Daily trigger at 2:00 AM, and add an action with Program `C:\Program Files\Git\bin\bash.exe` and the arguments from the `$cmd` line above (without the outer single quotes). On the Settings tab, tick "Run task as soon as possible after a scheduled start is missed".

## macOS: launchd

Copy `launchd/com.forgesuite.forge-learn.plist.example` to `~/Library/LaunchAgents/com.forgesuite.forge-learn.plist`, replace every YOURNAME in the file with your Mac user name, and load it:

```
mkdir -p ~/.forge-suite/logs/forge
launchctl load ~/Library/LaunchAgents/com.forgesuite.forge-learn.plist
```

## Linux: cron

```
0 2 * * * $HOME/.forge-suite/bin/forge-learn all >> $HOME/.forge-suite/logs/forge-learn.log 2>&1
```
