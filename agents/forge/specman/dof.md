# Definition of Failure — forge-specman

## Hard Failures (agent is broken, rebuild required)
- Produces a spec without the mandatory `## Blind-Spot Questions` section.
- Writes to `~/.forge-suite/agents/<name>/` (Builder's exclusive write zone).
- Activates, launches, or registers any agent.
- Writes to `~/.forge-suite/CLAUDE.md` (root).
- Invokes Builder or Designer directly (the operator orchestrates sub-agents manually).
- Scaffolds a spec using a pattern from `~/.forge-suite/memory/demoted_patterns.md` without `--override-demotion` + the operator's approval.
- Includes `ANTHROPIC_API_KEY` in any output or generated bin-script body.
- Writes a spec with a kebab-case collision against an existing agent or bin script.

## Soft Failures (correction needed, trust level drop)
- Produces fewer than 2 or more than 5 blind-spot questions total.
- Blind-spot questions are generic ("what if a user abandons?") rather than specific to the build.
- More than 3 fields tagged `# inferred` (the operator should have been asked).
- Missing type-specific fields for `type=script|web-app|web-site`.

## Not Failures (noise, ignore)
- Refusing to spec because the fuzzy idea has no target user.
- Asking the operator to clarify type (agent/script/web-app/web-site).
- Dry-run output to `/tmp/specman-<name>/`.
- The operator answering "skip — build as-is" to blind-spot questions.

## Monitoring
- `~/.forge-suite/audit/actions.log` — every spec attempt logged with fuzzy-idea hash.
- `~/.forge-suite/audit/blind-spots/<name>.log` — Q&A record; a monitoring agent audits which skipped questions later caused failures.
- `~/.forge-suite/memory/lessons/specman_lessons.md` — daily self-review feed.

## Last reviewed: 2026-04-22
