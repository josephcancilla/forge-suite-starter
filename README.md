# Forge Suite Starter

Updated 2026-11-11.

Forge is a small crew of Claude Code helper agents that build things for you: new agents, scripts, websites, and apps. You describe what you want in plain English. Forge does the rest, and checks its own work before you see it.

## What Forge is

- **SpecMan** interviews you and writes the spec. It also asks the questions you did not think to ask, and checks first whether a tool or skill already exists so you do not build what you can reuse.
- **Architect** plans the build from the spec. Planning only, no code.
- **Designer** produces the look and feel for websites and apps.
- **Builder** creates the real files and makes one clean git commit.
- **Verifier** tries to break the result. It assumes the work is wrong and only passes it when it cannot find the flaw.
- **Pipeline** runs the five in order and stops at your two gates: you approve the spec, and you decide whether to turn the finished build on.

**The trust ladder.** Every agent starts at **L0, draft only**: it shows you its work and you approve before anything lands. **L1** means it stages real actions for your approval. **L2** acts on its own with checks. **L3** is autonomous. Only you move an agent up a level. No agent, and not your commander agent, ever promotes itself.

**Done-bars.** A done-bar is a pass/fail checklist for "finished" (for example, an outbound email or a code build). The Verifier scores work against it line by line. If a line cannot be verified, it fails. Ready-made ones are in `agents/forge/verifier/donebars/`.

**Nightly learning.** Each night `forge-learn` lets every agent review its own day and write one lesson, which is fed into its next run. On a day with no work it does nothing and costs nothing.

## Hand it to your commander agent (copy and paste)

Paste this into your commander agent:

> Install the Forge Suite Starter as your first sub-agent pack: https://github.com/josephcancilla/forge-suite-starter . Read README.md and every agents/forge/ CLAUDE.md first. Adapt it to me and to this computer (I'm on Windows; use Git Bash or PowerShell equivalents). Install it at ~/.forge-suite (or set FORGE_HOME to another folder and use that everywhere), start every agent at L0 draft-only, never raise a trust level yourself. Then do one small test build with me: run SpecMan on a low-risk idea, show me the spec, and wait for my OK before the other agents run. Finish by telling me in plain English what you installed, where it lives, and how I start a new build.

## Windows notes

- Install **Git for Windows** (https://git-scm.com). It includes **Git Bash**, which runs the Forge scripts.
- Install **Python 3** from python.org and tick "Add python.exe to PATH". Forge only uses the standard library, so there is nothing else to install.
- Forge scripts call `python3`. In Git Bash run `python3 --version`. If it says "not found", run this once:
  ```
  mkdir -p ~/bin && printf '#!/usr/bin/env bash\nexec python "$@"\n' > ~/bin/python3 && chmod +x ~/bin/python3
  echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
  ```
  then open a new Git Bash window.
- Install **Claude Code** and sign in once. Forge uses your Claude login. There are no API keys anywhere in this suite, by design.
- Skills go in `%USERPROFILE%\.claude\skills`. In Git Bash that is `~/.claude/skills`.
- Run every Forge command from Git Bash, not from Command Prompt.
- Line endings: this repo ships a `.gitattributes` that keeps Unix line endings. If a script fails with a strange `\r` error, re-clone with `git config --global core.autocrlf input` set first.
- The nightly learning run uses Windows Task Scheduler. See `docs/SCHEDULING.md`.

## Install by hand

Forge lives in one folder, called `FORGE_HOME`. The default is `~/.forge-suite` (in Git Bash on Windows, that is `C:\Users\YOURNAME\.forge-suite`). Everything below runs in Terminal on Mac/Linux, or in Git Bash on Windows. The commands are the same.

1. Get the files and make the folder your own git repo (Builder commits each build into it):
   ```
   git clone https://github.com/josephcancilla/forge-suite-starter ~/.forge-suite
   cd ~/.forge-suite
   git remote remove origin
   ```
2. Put the Forge scripts on your PATH (Windows: the same line, in Git Bash):
   ```
   echo 'export PATH="$HOME/.forge-suite/bin:$PATH"' >> ~/.bashrc
   ```
   On a Mac with the default zsh shell, use `~/.zshrc` instead of `~/.bashrc`. Open a new terminal afterwards.
3. Install the skills Designer uses:
   ```
   mkdir -p ~/.claude/skills
   cp -R ~/.forge-suite/skills/* ~/.claude/skills/
   ```
4. Check it works (each of these only prints help or a status; the first run creates a few empty working folders):
   ```
   forge
   forge-pipeline --help
   forge-learn --dry-run all
   ```
5. If you put Forge somewhere other than `~/.forge-suite`, set `FORGE_HOME` to that folder (in `~/.bashrc` or `~/.zshrc`):
   ```
   export FORGE_HOME="$HOME/path/to/your/forge"
   ```
6. Optional: schedule the nightly learning run. Mac: `launchd/com.forgesuite.forge-learn.plist.example`. Windows: `docs/SCHEDULING.md`.

## Your first build

```
forge-specman "a small tool that renames my downloaded invoices by date"
```

SpecMan writes a Diagnosis into `~/.forge-suite/queue/forge/<name>_spec.md` and stops. Open that file and replace the `<AWAITING CONFIRM OR REDIRECT>` line with your answer (or a correction). Then:

```
forge-pipeline <name>
```

Pipeline finishes the spec, then runs Architect, Builder, and Verifier, and stops at each gate with a plain sentence about what you need to do. When the Verifier passes, read the activation memo it points to, try the build yourself, and then record it:

```
forge-pipeline <name> --mark-active
```

To preview the steps without running anything: `forge-pipeline --dry-run <name>`. To see every build: `forge-pipeline --status`.

## The commands

| Command | What it does |
|---|---|
| `forge-specman "<idea>"` | Phase 1: a Diagnosis for you to redline |
| `forge-specman --confirm-diagnosis <name>` | Phase 2: the full spec, blind-spot questions, prior-art check |
| `forge-architect <name>` | Design doc from the confirmed spec |
| `forge-builder <name>` | Scaffold the build and make one commit (`--dry-run` writes only to /tmp) |
| `forge-designer <name>` | Design pass for website and app specs (also `--mode=ux-review --target=<file>`) |
| `forge-verifier <name>` | Post-build gate. Exit 0 passes, exit 30 fails and blocks activation |
| `forge-pipeline <name>` | Runs the whole line and stops at your gates |
| `forge-learn all` | Nightly self-review (`--dry-run` to preview) |
| `forge-cb status` | Today's token use against the daily cap |
| `verify --task <n> --deliverable <file> --donebar <checklist>` | Check any deliverable against a done-bar |
| `forge audit <agent>` / `forge audit --all` | Score existing agents |
| `forge upgrade <agent>` | Draft an upgrade spec for one agent (you apply it) |

## What is in the box

- `agents/forge/` instructions (`CLAUDE.md`), rules for failure (`dof.md`), and a fresh graduation counter for each agent. `verifier/donebars/` holds the checklists.
- `agents/_shared/` the shared contract, silence rule, and a voice profile template for you to fill in.
- `bin/` the command scripts. `lib/` small Python helpers (standard library only).
- `launchd/` and `docs/` scheduling for Mac and Windows.
- `skills/` the design and website skills Designer uses. See `skills/README.md`.

## Good to know

- **Important:** SpecMan, Architect, Builder and Verifier run Claude Code with permission prompts turned off, so while they run they can execute commands anywhere on this computer without asking. Read each spec and each activation memo before you approve it, start with low-risk builds, and if you can, run Forge on a computer or user account that holds nothing sensitive. Agents start at L0 for that reason.
- Nothing here is specific to any one business. Edit the agent instructions, done-bars, and voice profile to fit yours.
- If a daily token cap is reached, the scripts stop and say so. Change it with `FORGE_CB_INPUT_CAP` and `FORGE_CB_OUTPUT_CAP`.

## License

MIT, see [LICENSE](LICENSE). The third-party skills in `skills/` keep their own licenses, listed in `skills/README.md`.
