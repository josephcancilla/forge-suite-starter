# Definition of Failure — forge-designer

## Hard Failures (agent is broken, rebuild required)
- Runs web-build mode without `frontend-design` skill installed at `~/.claude/skills/frontend-design/` (ux-review mode does NOT require the skill).
- Runs web-build mode on a spec with `type: agent` or `type: script` (use `--mode=ux-review --target=<path>` for a universal UX pass on any file).
- (v2 U3) Runs `--mode=ux-review` without `--target=<path>`, or with a target that does not exist.
- (v2 U3) UX-review mode modifies the target file (read-only mandate).
- Attempts to install the `frontend-design` skill itself (the skill-install tool owns that).
- Generates any file containing `ANTHROPIC_API_KEY`.
- Writes to `~/.forge-suite/CLAUDE.md` (root).
- Activates or deploys the scaffolded web build.
- Produces design tokens violating the operator's locked brand direction (e.g. one brand warm/bold/fire-inspired, another editorial/minimal) without `--override-brand` + the operator's approval.

## Soft Failures (correction needed, trust level drop)
- Component file exceeds 200 lines (signal to split).
- Pages array > 10 in one design pass (signal to phase the build).
- Missing `design-tokens.json` at project target.
- Generated JSX missing accessibility basics (alt text, aria labels, keyboard nav).

## Not Failures (noise, ignore)
- Dry-run output to `/tmp/forge-designer-<name>/`.
- Refusing `type: agent|script` spec.
- Surfacing install hint when skill not found.

## Monitoring
- `~/.forge-suite/audit/actions.log` — every design pass logged with spec hash.
- `~/.forge-suite/memory/lessons/designer_lessons.md` — daily self-review feed.

## Last reviewed: 2026-04-22 (v2 U3 ux-review mode added)
