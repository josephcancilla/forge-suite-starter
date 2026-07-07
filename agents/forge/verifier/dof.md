# Definition of Failure — forge-verifier

## Hard Failures (agent is broken, verdict must be FAIL)

1. Spec file missing at `~/.forge-suite/queue/forge/<name>_spec.md` — exit 21, no verdict written.
2. `agents/<name>/CLAUDE.md` missing or has no `## Behavior Contract` section — check b FAIL.
3. `agents/<name>/dof.md` missing — check c FAIL.
4. `bin/<name>` missing or not executable — check d FAIL.
5. `bin/<name> --dry-run` (or `--help` fallback) exits non-zero or times out after 120s — check e FAIL.
6. `graduation_counter.json` not valid JSON — check f FAIL.
7. Spec declares MCPs required AND `CLAUDE.md` has no credential pattern declaration — check g FAIL.
8. **Wallpaper pass:** Claude verdict PASS but declared outputs from spec do not exist on disk — override to FAIL; do not let structurally-complete-but-content-false artifacts graduate.
9. **Unnamed failure:** Claude returns FAIL verdict without naming the exact failed check — flag "verdict incomplete" in notes, still exit 30.
10. Verifier exits 0 (PASS) without having run all seven deterministic checks — broken run, not a pass.

## Soft Failures (flag in verdict, do not block)

1. `bin/<name>` has no `--dry-run` flag; fell back to `--help` — note `dry_run_fallback: true` in verdict JSON.
2. `graduation_counter.json` parses as valid JSON but does not match any recognized shape in `graduation_counters.py` — note in verdict, do not fail.
3. Claude call times out or fails — verdict JSON records `claude_verdict: "error: <message>"` and Verifier exits 30 (conservative: unknown ≠ pass).
4. Summary `.md` write fails (disk full, permissions) — log to audit, exit with appropriate code; verdict JSON still written if possible.

## Not Failures (noise, ignore)

- Agent's `--dry-run` exits 0 without producing output (correct for dry-run).
- Verdict overwrites a prior `<name>_verdict.json` (last run wins, by design).
- Running against test-echo — expected to show some check failures (graduation_counter.json missing at agent dir); this is diagnostic, not a Verifier bug.
- `--dry-run` flag on Verifier itself — skipping Claude call is the correct behavior, not a soft failure.

## Monitoring

- `~/.forge-suite/audit/actions.log` — every run logged with name, exit code, pass/fail.
- `~/.forge-suite/queue/forge/verdicts/<name>_verdict.json` — machine-readable per-agent verdict history.
- `~/.forge-suite/outputs/forge/verifier/` — human-readable summaries.

## Last reviewed: 2026-06-10 (initial ship)
