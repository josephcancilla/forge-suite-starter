# Definition of Failure — forge-architect

## Hard Failures (agent is broken, rebuild required)
- Spec file missing at `~/.forge-suite/queue/forge/<name>_spec.md` (should refuse, exit 22).
- Spec Diagnosis still contains `<AWAITING OPERATOR CONFIRM OR REDIRECT>` placeholder (should refuse, exit 21).
- Design doc missing any required section: Components, Data/State Files, Dependencies, Integration Points, Risks, Verification Plan.
- Design doc invents dependencies, MCPs, or credentials not mentioned in the spec.
- Output written outside declared paths (`queue/forge/designs/` and `outputs/forge/architect/`).
- Calls Claude without a valid spec (preflight skipped or bypassed).
- Writes to `~/.forge-suite/agents/<name>/` (Builder's exclusive zone).
- Includes `ANTHROPIC_API_KEY` or direct API calls in any generated content.
- Dry-run output lands outside `/tmp/forge-architect-<name>/`.

## Soft Failures (correction needed, trust level drop)
- Design doc lists a dependency but omits the credential pattern (MCP/LIB/DSF/STATIC/SUB).
- Risks section contains fewer than 3 entries.
- Verification plan is generic boilerplate rather than steps specific to this build.
- Run summary file missing or empty after a successful Claude run.
- Architect writes a design doc but does not log the run to `~/.forge-suite/audit/actions.log`.

## Not Failures (noise, ignore)
- Dry-run output to `/tmp/forge-architect-<name>/` (correct behavior).
- Exit 21 when Diagnosis placeholder is present (correct behavior — refuse, do not design).
- Exit 22 when spec file is missing (correct behavior).
- Builder later choosing to deviate from the design doc (Builder owns scaffold; Architect owns design only).

## Monitoring
- `~/.forge-suite/audit/actions.log` — every design run logged with spec hash.
- `~/.forge-suite/queue/forge/designs/<name>_design.md` — primary output; absence after a run is a hard failure.
- `~/.forge-suite/outputs/forge/architect/<TS>_<name>_design_summary.md` — run summary for operator review.

## Last reviewed: 2026-06-10 (initial ship)
