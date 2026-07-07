"""
forge_audit.py — Score agents against current canon.

Forge v2. Replaces new-agent-only Forge with audit + upgrade
capability across the existing roster.

Audits one agent or every real agent dir under ~/.forge-suite/agents/ against 11
weighted criteria covering CLAUDE.md hygiene, dof.md completeness, bin script
safety, the 8-field Behavior Contract, Silence Contract, fact-lock retrofit,
power-down survivability, graduation_counter presence, token tier declaration,
and voice canon references.

Score ranges:
    >= 85 = HEALTHY
    60-84 = DEGRADED
    <  60 = NEEDS-UPGRADE

Failures on criteria 5 (Behavior Contract), 7 (Fact-lock), or 8 (Power-down)
are flagged as "graduation blockers" per Engineering Rules 14/15/16.

CLI:
    python3 forge_audit.py <agent>          → JSON for one agent
    python3 forge_audit.py --all            → JSON list of all real agents
    python3 forge_audit.py --list-agents    → newline list of real agent names

No third-party deps — stdlib only.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


HOME = Path.home()
FORGE_SUITE = HOME / ".forge-suite"
AGENTS_DIR = FORGE_SUITE / "agents"
BIN_DIR = FORGE_SUITE / "bin"
LIB_DIR = FORGE_SUITE / "lib"
TOKEN_LIMITS = FORGE_SUITE / "config" / "token_limits.yaml"

# Internal dirs not to be audited as standalone agents
FORGE_INTERNALS = {"forge/builder", "forge/designer", "forge/specman"}

# Agents that have no graduation_counter by design (umbrella / non-promotable)
GRADUATION_EXEMPT = {"forge", "_commander", "_shared", "_templates"}

BEHAVIOR_FIELDS = [
    "Identity",
    "Triggers",
    "Ambient listening",
    "Blast radius",
    "Silence contract",
    "Failure modes",
    "Dedup strategy",
    "Deployment",
]

POWER_DOWN_PATTERNS = [
    r"day[- ]keyed",
    r"time[- ]window",
    r"inherent idempotency",
    r"no[- ]schedule",
    r"cooldown[- ]ledger",  # cooldown-ledger pattern — equivalent to inherent idempotency
]


@dataclass
class CriterionResult:
    n: int
    name: str
    weight: int
    result: str  # PASS | FAIL | N/A
    notes: str = ""


@dataclass
class AuditResult:
    agent: str
    score: int
    max_score: int
    status: str  # HEALTHY | DEGRADED | NEEDS-UPGRADE
    criteria: list = field(default_factory=list)
    blockers: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "score": self.score,
            "max_score": self.max_score,
            "status": self.status,
            "criteria": [asdict(c) for c in self.criteria],
            "blockers": self.blockers,
        }


# ── Helpers ──────────────────────────────────────────────────────────────────


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _grep_noncomment(text: str, needle: str) -> bool:
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        if needle in line:
            return True
    return False


def _has_behavior_field(text: str, field_name: str) -> bool:
    # Matches "### 1. Identity", "### 2. Triggers (...)", etc — number tolerant
    pattern = rf"^\s*###\s+\d+\.\s+{re.escape(field_name)}\b"
    return re.search(pattern, text, re.MULTILINE | re.IGNORECASE) is not None


def _power_down_pattern_found(text: str) -> Optional[str]:
    for pat in POWER_DOWN_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return pat
    return None


def _token_tier_declared(agent: str, claude_text: str) -> tuple[bool, str]:
    # First check token_limits.yaml for an entry under "agents:"
    if TOKEN_LIMITS.exists():
        yaml_text = _read_text(TOKEN_LIMITS)
        # Match "  <agent>:" or "  <agent>_<x>:" near the top of an agents: block
        if re.search(rf"^\s{{2,4}}{re.escape(agent)}\s*:", yaml_text, re.MULTILINE):
            return True, "in token_limits.yaml"
    # Fallback: CLAUDE.md mentions a tier
    if re.search(r"(token tier|daily_input|light|standard|heavy)", claude_text, re.IGNORECASE):
        return True, "tier referenced in CLAUDE.md"
    return False, "no tier in token_limits.yaml or CLAUDE.md"


def _factlock_evidence(agent: str, agent_dir: Path, bin_path: Path, claude_text: str) -> tuple[bool, str]:
    # 1. Explicit exemption declared
    if re.search(r"fact[_ ]lock[_ ]exempt\s*[:=]\s*read[- ]only", claude_text, re.IGNORECASE):
        return True, "declared fact_lock_exempt: read-only"
    if re.search(r"fact[- ]?lock\s+exempt", claude_text, re.IGNORECASE):
        return True, "marked fact-lock exempt in CLAUDE.md"
    # 2. Bin imports/calls factlock
    if bin_path.exists():
        bin_text = _read_text(bin_path)
        if "factlock" in bin_text.lower():
            return True, f"bin references factlock"
    # 3. Any .py in the agent dir imports factlock
    if agent_dir.exists():
        for py in agent_dir.rglob("*.py"):
            if "factlock" in _read_text(py).lower():
                return True, f"{py.name} imports factlock"
    # 4. Any ~/.forge-suite/lib/<agent>*.py imports factlock
    for py in LIB_DIR.glob(f"{agent}*.py"):
        if "factlock" in _read_text(py).lower():
            return True, f"lib/{py.name} imports factlock"
    # Also check pattern like <agent>_factlock.py
    for py in LIB_DIR.glob(f"*{agent}*.py"):
        if "factlock" in _read_text(py).lower():
            return True, f"lib/{py.name} imports factlock"
    return False, "no factlock retrofit found; not declared exempt"


def _voice_canon_referenced(claude_text: str) -> tuple[bool, str]:
    for marker in ("VOICE_PROFILE.md", "no outbound writes", "read-only", "Voice Profile"):
        if marker.lower() in claude_text.lower():
            return True, f"references {marker}"
    return False, "no voice canon reference; no read-only declaration"


# ── Audit ────────────────────────────────────────────────────────────────────


def audit_agent(name: str) -> AuditResult:
    agent_dir = AGENTS_DIR / name
    claude_md = agent_dir / "CLAUDE.md"
    dof_md = agent_dir / "dof.md"
    grad_counter = agent_dir / "graduation_counter.json"

    # Bin naming has two conventions in this repo: prefixed <name> (e.g. forge-mailer) and bare <name> (e.g. mailer, scheduler).
    bin_candidates = [BIN_DIR / f"forge-{name}", BIN_DIR / name]
    bin_path = next((p for p in bin_candidates if p.exists()), bin_candidates[0])

    claude_text = _read_text(claude_md)
    dof_text = _read_text(dof_md)
    bin_text = _read_text(bin_path)

    criteria: list[CriterionResult] = []

    # 1 — CLAUDE.md exists, >= 10 lines
    if claude_md.exists() and len(claude_text.splitlines()) >= 10:
        criteria.append(CriterionResult(1, "CLAUDE.md present (>=10 lines)", 10, "PASS",
                                        f"{len(claude_text.splitlines())} lines"))
    else:
        why = "missing" if not claude_md.exists() else f"only {len(claude_text.splitlines())} lines"
        criteria.append(CriterionResult(1, "CLAUDE.md present (>=10 lines)", 10, "FAIL", why))

    # 2 — dof.md has 5 sections
    dof_sections = ["Hard Failures", "Soft Failures", "Not Failures", "Monitoring", "Last reviewed"]
    if dof_md.exists():
        missing_dof = [s for s in dof_sections if s.lower() not in dof_text.lower()]
        if not missing_dof:
            criteria.append(CriterionResult(2, "dof.md has all 5 sections", 10, "PASS",
                                            "all sections present"))
        else:
            criteria.append(CriterionResult(2, "dof.md has all 5 sections", 10, "FAIL",
                                            f"missing: {', '.join(missing_dof)}"))
    else:
        criteria.append(CriterionResult(2, "dof.md has all 5 sections", 10, "FAIL", "dof.md missing"))

    # 3 — bin exists and executable (try both forge-<name> and bare <name>)
    import os
    found_bin = next((p for p in bin_candidates if p.exists()), None)
    if found_bin and os.access(str(found_bin), os.X_OK):
        criteria.append(CriterionResult(3, "bin script exists + executable", 10, "PASS", str(found_bin)))
    elif found_bin:
        criteria.append(CriterionResult(3, "bin script exists + executable", 10, "FAIL",
                                        f"{found_bin} exists but not executable"))
    else:
        criteria.append(CriterionResult(3, "bin script exists + executable", 10, "FAIL",
                                        f"no bin at forge-{name} or {name}"))

    # 4 — bin has no ANTHROPIC_API_KEY on non-comment line
    if bin_path.exists():
        if _grep_noncomment(bin_text, "ANTHROPIC_API_KEY"):
            criteria.append(CriterionResult(4, "bin has no ANTHROPIC_API_KEY (non-comment)", 10, "FAIL",
                                            "found in non-comment line — violates subscription-only auth"))
        else:
            criteria.append(CriterionResult(4, "bin has no ANTHROPIC_API_KEY (non-comment)", 10, "PASS", ""))
    else:
        criteria.append(CriterionResult(4, "bin has no ANTHROPIC_API_KEY (non-comment)", 10, "N/A",
                                        "bin missing — see criterion 3"))

    # 5 — Behavior Contract 8 fields
    missing_bc = [f for f in BEHAVIOR_FIELDS if not _has_behavior_field(claude_text, f)]
    if not missing_bc:
        criteria.append(CriterionResult(5, "Behavior Contract: 8 fields present", 15, "PASS",
                                        "all 8 fields"))
    else:
        criteria.append(CriterionResult(5, "Behavior Contract: 8 fields present", 15, "FAIL",
                                        f"missing: {', '.join(missing_bc)}"))

    # 6 — Silence Contract section + silence_rule.md reference
    has_silence_section = bool(re.search(r"##\s+Silence Contract", claude_text, re.IGNORECASE))
    has_silence_ref = "silence_rule.md" in claude_text
    if has_silence_section and has_silence_ref:
        criteria.append(CriterionResult(6, "Silence Contract + silence_rule.md ref", 5, "PASS", ""))
    else:
        missing = []
        if not has_silence_section:
            missing.append("section")
        if not has_silence_ref:
            missing.append("silence_rule.md reference")
        criteria.append(CriterionResult(6, "Silence Contract + silence_rule.md ref", 5, "FAIL",
                                        f"missing: {', '.join(missing)}"))

    # 7 — Fact-lock
    fl_ok, fl_note = _factlock_evidence(name, agent_dir, bin_path, claude_text)
    criteria.append(CriterionResult(7, "Fact-lock retrofit or declared exempt", 15,
                                    "PASS" if fl_ok else "FAIL", fl_note))

    # 8 — Power-down pattern
    pd = _power_down_pattern_found(claude_text)
    if pd:
        criteria.append(CriterionResult(8, "Power-down pattern declared", 10, "PASS",
                                        f"matched: {pd}"))
    else:
        criteria.append(CriterionResult(8, "Power-down pattern declared", 10, "FAIL",
                                        "no day-keyed/time-window/inherent idempotency/no-schedule pattern in CLAUDE.md"))

    # 9 — graduation_counter.json
    if name in GRADUATION_EXEMPT:
        criteria.append(CriterionResult(9, "graduation_counter.json present", 5, "N/A",
                                        "umbrella/exempt agent"))
    elif grad_counter.exists():
        criteria.append(CriterionResult(9, "graduation_counter.json present", 5, "PASS", ""))
    else:
        criteria.append(CriterionResult(9, "graduation_counter.json present", 5, "FAIL",
                                        f"missing at {grad_counter}"))

    # 10 — token tier declared
    tier_ok, tier_note = _token_tier_declared(name, claude_text)
    criteria.append(CriterionResult(10, "Token tier declared", 5,
                                    "PASS" if tier_ok else "FAIL", tier_note))

    # 11 — voice canon referenced
    vc_ok, vc_note = _voice_canon_referenced(claude_text)
    criteria.append(CriterionResult(11, "Voice canon referenced", 5,
                                    "PASS" if vc_ok else "FAIL", vc_note))

    # Score
    earned = sum(c.weight for c in criteria if c.result == "PASS")
    applicable_max = sum(c.weight for c in criteria if c.result != "N/A")
    # Normalize to 100 across applicable criteria
    score = round((earned / applicable_max) * 100) if applicable_max else 0

    if score >= 85:
        status = "HEALTHY"
    elif score >= 60:
        status = "DEGRADED"
    else:
        status = "NEEDS-UPGRADE"

    # Graduation blockers — FAILs on criteria 5, 7, 8
    blockers = []
    for c in criteria:
        if c.n in (5, 7, 8) and c.result == "FAIL":
            blockers.append(f"Criterion {c.n}: {c.name} — {c.notes}")

    return AuditResult(
        agent=name,
        score=score,
        max_score=100,
        status=status,
        criteria=criteria,
        blockers=blockers,
    )


# ── Discovery ────────────────────────────────────────────────────────────────


def list_real_agents() -> list[str]:
    """Real agents: dirs under ~/.forge-suite/agents/ with a CLAUDE.md, no leading _,
    not Forge internals (forge/builder|designer|specman)."""
    if not AGENTS_DIR.exists():
        return []
    out = []
    for child in sorted(AGENTS_DIR.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("_"):
            continue
        # Forge sub-agents are internals — exclude
        if child.name in {"builder", "designer", "specman"}:
            # only if they're at top level (not under forge/). At top level
            # there IS a "builder" dir which IS a real agent — keep it.
            # Forge internals live at agents/forge/builder, not top-level builder.
            pass
        if not (child / "CLAUDE.md").exists():
            continue
        out.append(child.name)
    return out


def audit_all() -> list[AuditResult]:
    return [audit_agent(name) for name in list_real_agents()]


# ── CLI ──────────────────────────────────────────────────────────────────────


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: forge_audit.py <agent> | --all | --list-agents", file=sys.stderr)
        return 2

    if argv[0] == "--all":
        results = audit_all()
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return 0
    if argv[0] == "--list-agents":
        for a in list_real_agents():
            print(a)
        return 0

    name = argv[0]
    if not (AGENTS_DIR / name).exists():
        print(json.dumps({"error": f"agent '{name}' not found at {AGENTS_DIR / name}"}))
        return 1
    result = audit_agent(name)
    print(json.dumps(result.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
