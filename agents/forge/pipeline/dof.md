# Forge Pipeline — Definition of Failure

**Agent:** forge-pipeline
**Last Reviewed:** 2026-06-10

---

## Hard Failures

These conditions must never occur. A hard failure halts the pipeline and exits non-zero.

1. **Invalid name** — non-kebab-case name passed as argument; pipeline refuses immediately.
2. **Spec missing on init** — forge-pipeline called for a name that has no spec file at `~/.forge-suite/queue/forge/<name>_spec.md`; pipeline reports missing and exits 2.
3. **Circuit breaker tripped** — `cb check forge` returns non-zero; pipeline exits 3 without calling any sub-agent.
4. **Sub-agent internal error** — forge-specman, forge-architect, forge-builder, or forge-verifier exits with an unexpected code (not a gate-refusal code like 20, 21, 22, or 30); pipeline records the failure, stays at the current stage, and exits with that code.
5. **Stage file corruption** — state file exists but is not valid JSON; pipeline should surface the error rather than silently advancing to a wrong stage.

---

## Soft Failures

These conditions are logged and handled, but the pipeline continues.

1. **Project-tracker update fails** — soft-update of the Build Queue item fails for any reason (auth, network, missing item); log to audit.log and continue. The build is not blocked.
2. **State file write race** — mitigated by Python atomic tmp-file replace; if it fails, log and warn, do not corrupt the existing state.
3. **forge-verifier returns exit 30 (FAIL)** — this is a controlled result, not an error. Pipeline advances stage to `failed`, prints instructions, and exits 0. The operator must fix the issues and re-run.

---

## Not Failures

- Stopping cleanly at an operator gate (awaiting_redline, awaiting_activation) with exit 0.
- forge-specman exiting 21 on a still-placeholder Diagnosis — pipeline surfaces this as a gate message.
- forge-architect exiting 21 or 22 — surfaces as a gate or pre-condition failure with plain-English message.
- forge-verifier --dry-run path.
- --status with an empty pipeline dir — prints "no builds" and exits 0.
- Re-running at any stage — idempotent; only advances when the gate condition is met.

---

## Monitoring

- Every stage transition is appended to `~/.forge-suite/audit/actions.log` with tag `forge-pipeline`.
- Per-build state file at `~/.forge-suite/queue/forge/pipeline/<name>.json` is the durable record; history array shows every transition.
- A monitoring agent watches `audit/actions.log` for forge-pipeline hard failure codes.

---

## Last Reviewed

2026-06-10 — initial ship at L0.
