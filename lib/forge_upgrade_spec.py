"""
forge_upgrade_spec.py — Generate operator-reviewable upgrade specs from audit results.

Reads an AuditResult dict (from forge_audit.py) and produces a markdown spec
listing every FAILed criterion with a concrete patch instruction. The spec
lands in ~/.forge-suite/queue/forge/<agent>_upgrade_spec.md (or /tmp if --dry-run).

Forge L0 contract: spec is drafted, the operator approves. Apply step deferred to v2.1.

CLI:
    python3 forge_upgrade_spec.py <agent> [--dry-run]
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


HOME = Path.home()
FORGE_SUITE = HOME / ".forge-suite"
QUEUE_DIR = FORGE_SUITE / "queue" / "forge"
AUDIT_DIR = FORGE_SUITE / "outputs" / "forge" / "audit"


# ── Patch recipes — keyed by criterion number ────────────────────────────────
# Each recipe takes the criterion result dict + agent name; returns markdown.

def _patch_for_criterion(c: dict, agent: str) -> str:
    n = c["n"]
    name = c["name"]
    notes = c.get("notes", "")
    claude_md = f"~/.forge-suite/agents/{agent}/CLAUDE.md"
    dof_md = f"~/.forge-suite/agents/{agent}/dof.md"
    bin_path = f"~/.forge-suite/bin/forge-{agent}"

    if n == 1:
        return (
            f"- **File:** `{claude_md}`\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** CLAUDE.md with at least 10 lines documenting role, trust level, output paths, "
            f"and the 8-field Behavior Contract.\n"
            f"- **Patch:** Restore from latest backup or scaffold from `~/.forge-suite/agents/_templates/`. "
            f"If agent is being retired, run `forge-retire {agent}` (agent lifecycle tooling)."
        )
    if n == 2:
        return (
            f"- **File:** `{dof_md}`\n"
            f"- **Section:** Hard Failures / Soft Failures / Not Failures / Monitoring / Last reviewed\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** All 5 sections per `~/.forge-suite/agents/_shared/AGENT_BEHAVIOR_CONTRACT.md` §6.\n"
            f"- **Patch:** Add missing section headers and fill from CLAUDE.md §Failure modes."
        )
    if n == 3:
        return (
            f"- **File:** `{bin_path}`\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** Executable bin script at `~/.forge-suite/bin/forge-{agent}` with chmod +x.\n"
            f"- **Patch:** `chmod +x {bin_path}` if exists; otherwise scaffold from template."
        )
    if n == 4:
        return (
            f"- **File:** `{bin_path}`\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** No `ANTHROPIC_API_KEY` references on non-comment lines (subscription-only auth, see ~/.forge-suite/CLAUDE.md OPERATING CONSTRAINTS).\n"
            f"- **Patch:** Replace any `$ANTHROPIC_API_KEY` invocations with subscription-auth Claude calls. "
            f"If pattern is in a comment, move the comment to clarify it is illustrative."
        )
    if n == 5:
        return (
            f"- **File:** `{claude_md}`\n"
            f"- **Section:** `## Behavior Contract`\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** All 8 fields per `~/.forge-suite/agents/_shared/AGENT_BEHAVIOR_CONTRACT.md` "
            f"(Identity, Triggers, Ambient listening, Blast radius, Silence contract, Failure modes, Dedup strategy, Deployment).\n"
            f"- **Patch:** Append a `## Behavior Contract` section copying the template; fill each `### N. Field` block with the agent's actual triggers, ambient surfaces, and blast radius. Blocks promotion to L2+."
        )
    if n == 6:
        return (
            f"- **File:** `{claude_md}`\n"
            f"- **Section:** `## Silence Contract`\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** A `## Silence Contract` section that references `~/.forge-suite/agents/_shared/silence_rule.md`.\n"
            f"- **Patch:** Add a short section: \"Default behavior when not explicitly addressed: silence. Silent-skip log: `~/.forge-suite/audit/silent-skips.log`. Reference: `~/.forge-suite/agents/_shared/silence_rule.md`.\""
        )
    if n == 7:
        return (
            f"- **Files:** `{bin_path}`, `~/.forge-suite/lib/{agent}_factlock.py` (new if outbound writes), `{claude_md}`\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** Outbound-writing agent must import a `factlock` module and call `verify_facts()` before every CRM comment, email, file write, or status flip. Read-only agents declare `fact_lock_exempt: read-only` in CLAUDE.md.\n"
            f"- **Patch:** If agent writes outbound: model on an existing outbound agent's fact-lock module in `~/.forge-suite/lib/` — build manifest from FactClaim list and call `verify_facts()` before action. If read-only: add a one-line `fact_lock_exempt: read-only` to CLAUDE.md frontmatter. Blocks promotion to L2+ per Engineering Rule 15."
        )
    if n == 8:
        return (
            f"- **File:** `{claude_md}`\n"
            f"- **Section:** New section or update existing schedule docs\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** Declare ONE power-down pattern per Engineering Rule 14: (a) day-keyed output guard, (b) time-window guard (5-22 PHX), (c) inherent idempotency (cooldown-ledger), or (d) no-schedule (manual/CLI only).\n"
            f"- **Patch:** Add a `## Power-down survivability` section stating which pattern this agent uses and where the guard lives (bin line / ledger path / cron-only). Blocks promotion to L2+."
        )
    if n == 9:
        return (
            f"- **File:** `~/.forge-suite/agents/{agent}/graduation_counter.json`\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** A graduation_counter.json with keys `current_tier`, `clean_runs`, `required_clean_runs` per `~/.forge-suite/policy/grader_criteria_l0_l1.md`.\n"
            f"- **Patch:** Run your graduation tracker's init command for {agent} (if available) or copy from a peer agent's counter and reset clean_runs=0."
        )
    if n == 10:
        return (
            f"- **Files:** `~/.forge-suite/config/token_limits.yaml`, `{claude_md}`\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** Token tier declared either in token_limits.yaml under `agents.{agent}:` or referenced in CLAUDE.md.\n"
            f"- **Patch:** Add an entry to `token_limits.yaml` with daily_input/daily_output caps matching the agent's tier (light/standard/heavy)."
        )
    if n == 11:
        return (
            f"- **File:** `{claude_md}`\n"
            f"- **Current:** {notes}\n"
            f"- **Required:** Reference to `~/.forge-suite/agents/_shared/VOICE_PROFILE.md`, or an explicit \"no outbound writes\" / \"read-only\" declaration.\n"
            f"- **Patch:** Add to CLAUDE.md: \"Voice canon: `~/.forge-suite/agents/_shared/VOICE_PROFILE.md` — em-dash ban, & vs + connector style, banned vocab. All written output must comply.\""
        )
    return f"- **Note:** unknown criterion {n} — {name} — {notes}"


def _last_reviewed_from_dof(agent: str) -> str:
    dof = HOME / ".forge-suite" / "agents" / agent / "dof.md"
    if not dof.exists():
        return "unknown (no dof.md)"
    text = dof.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Last reviewed[:\s]*([0-9]{4}-[0-9]{2}-[0-9]{2})", text, re.IGNORECASE)
    return m.group(1) if m else "unknown"


def _latest_audit_path(agent: str) -> str:
    if not AUDIT_DIR.exists():
        return "(none — fresh audit just run)"
    matches = sorted(AUDIT_DIR.glob(f"*_{agent}.md"), reverse=True)
    if matches:
        return str(matches[0])
    return "(none on disk — fresh audit just run)"


def generate_spec(agent: str, audit: dict, dry_run: bool = False) -> str:
    """Generate the upgrade spec markdown and write it. Returns the path."""
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    failed = [c for c in audit["criteria"] if c["result"] == "FAIL"]

    lines: list[str] = []
    lines.append(f"# Forge Upgrade Spec — {agent}")
    lines.append(f"*Generated: {datetime.now().isoformat(timespec='seconds')}*")
    lines.append(f"*Source audit: {_latest_audit_path(agent)}*")
    lines.append("")
    lines.append("## Current state")
    lines.append(f"- Score: {audit['score']}/100")
    lines.append(f"- Status: {audit['status']}")
    lines.append(f"- Last reviewed: {_last_reviewed_from_dof(agent)}")
    lines.append(f"- Failed criteria: {len(failed)}")
    if audit["blockers"]:
        lines.append(f"- Graduation blockers: {len(audit['blockers'])} (criteria 5/7/8)")
    lines.append("")

    if not failed:
        lines.append("## No failed criteria")
        lines.append("")
        lines.append(f"Agent **{agent}** scored {audit['score']}/100 ({audit['status']}). No upgrade needed.")
    else:
        lines.append("## Failed criteria — patches needed")
        lines.append("")
        for c in failed:
            lines.append(f"### {c['n']}. {c['name']} (weight {c['weight']})")
            lines.append("")
            lines.append(_patch_for_criterion(c, agent))
            lines.append("")

    if audit["blockers"]:
        lines.append("## Graduation blockers (criteria 5/7/8)")
        for b in audit["blockers"]:
            lines.append(f"- {b}")
        lines.append("")
        lines.append("These FAILs block promotion to L2+ per Engineering Rules 14/15/16.")
        lines.append("")

    lines.append("## Backfill plan")
    lines.append("")
    lines.append(f"Before any in-place edit, write backups to `/tmp/forge-upgrade-{agent}-{ts}/<filename>.bak` per Engineering Rule 10.")
    lines.append("")

    lines.append("## Operator approval")
    lines.append("")
    lines.append(f"This is a Forge L0 upgrade — the operator must approve before any patch lands.")
    lines.append(f"Run: `forge upgrade {agent} --apply` after review.")
    lines.append(f"(Apply mode is NOT IN SCOPE for v2.0 — spec-generation only. Apply step lands in v2.1.)")
    lines.append("")

    lines.append("## Reporting line")
    lines.append("")
    lines.append(f"- Output dir: `~/.forge-suite/outputs/forge/upgrades/{ts}_{agent}.md`")
    lines.append(f"- Audit log line: `forge upgrade_spec_drafted {agent} score={audit['score']}`")
    lines.append("")

    content = "\n".join(lines)

    if dry_run:
        target = Path(f"/tmp/forge-upgrade-{agent}-spec.md")
    else:
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        target = QUEUE_DIR / f"{agent}_upgrade_spec.md"

    target.write_text(content, encoding="utf-8")
    return str(target)


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: forge_upgrade_spec.py <agent> [--dry-run]", file=sys.stderr)
        return 2
    agent = argv[0]
    dry_run = "--dry-run" in argv[1:]

    # Run audit fresh by calling forge_audit module
    sys.path.insert(0, str(HOME / ".forge-suite" / "lib"))
    from forge_audit import audit_agent
    audit_result = audit_agent(agent)
    spec_path = generate_spec(agent, audit_result.to_dict(), dry_run=dry_run)
    print(json.dumps({"spec": spec_path, "score": audit_result.score, "status": audit_result.status}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
