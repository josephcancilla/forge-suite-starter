# Definition of Failure — forge-builder

## Hard Failures (agent is broken, rebuild required)
- Scaffolds without a valid spec file at `~/.forge-suite/queue/forge/<name>_spec.md`.
- Scaffolds an agent missing `ANTHROPIC_API_KEY`-free bin script.
- Writes to `~/.forge-suite/CLAUDE.md` (root).
- Activates, launches, or registers the scaffolded build.
- Modifies existing agent files without `--retrofit` flag + separate approval from the operator.
- Creates an agent at any trust level other than L0.
- Scaffolds outside `~/.forge-suite/agents/<name>/` (for type=agent) or the declared project target (script/web).
- Skips graduation_counter.json update.
- Skips token_limits.yaml update.
- Skips git commit.
- Scaffolds from a spec missing `## Blind-Spot Questions` section.
- Scaffolds from a spec missing `## Diagnosis` section (v2 U1).
- Scaffolds from a spec whose Diagnosis still contains `<AWAITING OPERATOR CONFIRM OR REDIRECT>` placeholder (v2 U1).
- Name collision not caught (overwrites existing agent dir or bin).
- Scaffold commit lands but no activation memo was written (neither subprocess nor fallback). Builder MUST always produce `~/.forge-suite/outputs/forge/builder/<TS>_<name>_activation_memo.md` (v2 U2).

## Soft Failures (correction needed, trust level drop)
- Scaffolded CLAUDE.md missing any required section (trust ladder / circuit breaker / DOF ref / voice profile ref / output path / silence contract / behavior contract).
- Scaffolded dof.md missing any required section (Hard / Soft / Not Failures / Monitoring / Last Reviewed).
- Designer invocation failed for web build; Builder commits without design artifacts but flags for follow-up.
- Token tier outside the standard set of default tiers without `--custom-tier` flag + justification.
- Subprocess did not produce activation memo; bin-level fallback synthesized a TODO-stubbed memo (frontmatter: `fallback_memo: true`). The operator must manually fill before activation (v2 U2).

## Not Failures (noise, ignore)
- Dry-run output to `/tmp/forge-builder-<name>/`.
- Refusing `type: web-app|web-site` spec when `frontend-design` skill not installed (surfaces install hint — correct behavior).
- Asking the operator to confirm before scaffold commits.

## Monitoring
- `~/.forge-suite/audit/actions.log` — every scaffold attempt logged with spec hash.
- `~/.forge-suite/state/forge/graduation_counter.json` — tracks all scaffolded agents' graduation status.
- `~/.forge-suite/memory/lessons/builder_lessons.md` — daily self-review feed.

## Last reviewed: 2026-04-22 (v2 U1 + U2 additions)
