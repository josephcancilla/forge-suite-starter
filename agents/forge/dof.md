# Definition of Failure — Forge

## Hard Failures (agent is broken, rebuild required)
- Creates, modifies, or activates any agent without your explicit approval in the current session.
- Writes to `~/.forge-suite/CLAUDE.md` (root). Only you write to the root CLAUDE.md.
- Modifies an existing agent's `CLAUDE.md` or `dof.md` without an explicit `--retrofit` flag AND separate approval from you.
- Scaffolds an agent whose bin script contains `ANTHROPIC_API_KEY`, direct `anthropic.Anthropic()` calls, or any path that bypasses Claude Code subscription auth.
- Produces a `CLAUDE.md` missing any of: trust-ladder gates, circuit-breaker caps, DOF reference, voice profile reference, output path convention.
- Creates an agent at any trust level other than L0.
- Writes the scaffolded agent to any directory outside `~/.forge-suite/agents/<name>/`.

## Soft Failures (correction needed, trust level drop)
- Produces a DOF missing any required section (Hard / Soft / Not Failures / Monitoring / Last Reviewed).
- Uses a token-limit tier outside the four established tiers (see `token_limits.yaml`) without a `--custom-tier` flag.
- Scaffolds with a name that collides with an existing agent or bin script.
- Bin script fails a dry-run execution test before your approval.
- Missing entry in `token_limits.yaml`, dashboard tile spec, or `actions.log` init line.

## Not Failures (noise, ignore)
- Rejecting a spec that lacks sufficient detail (this is correct behavior — surface the gap).
- Asking you to clarify scope, cadence, or reporting line before scaffolding.
- Refusing to scaffold when a required field is missing from the spec.

## Monitoring
- `audit/actions.log` — every scaffold attempt logged with spec hash.
- `~/.forge-suite/agents/` — a monitoring agent watches for unauthorized directory creation.
- Every scaffolded agent is reviewed by you against this DOF before activation.

## Last reviewed: 2026-04-19
