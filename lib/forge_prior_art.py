"""Prior-art check for Forge specs (stdlib only).

Before anything new is built, the spec must show that someone looked for an
existing tool, skill, or open-source project first, and made an explicit
Adopt / Fork / Build decision.

A passing spec has a "## Prior art" section that contains:
  * at least one piece of evidence: a link (https://...) or a line like
      Searched: <what you searched> -> no fit: <why nothing fit>
  * a decision line:  Decision: Adopt|Fork|Build <at least three words of why>

Usage:
  python3 forge_prior_art.py <spec.md> [--json]   exit 0 = pass, 1 = fail, 2 = unreadable
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SECTION_TEMPLATE = """## Prior art
- Existing tools or skills: <links with evidence, or the search you ran and why nothing fit>
- Open-source projects: <links with evidence, or the search you ran and why nothing fit>
- Decision: <!-- author: Adopt|Fork|Build + why -->
"""

_HEADING = re.compile(r"^(#{2,3})[ \t]+Prior[ \t]+art\b.*$", re.I | re.M)
_ANY_HEADING = re.compile(r"^(#{1,6})[ \t]+", re.M)
_PLACEHOLDER = re.compile(r"<[^>]*>|\.\.\.|\btbd\b|\btodo\b|\bpending\b|fill in", re.I)
_URL = re.compile(r"https?://[^\s<>)]+/\S+|https?://[^\s<>)]+\.[a-z]{2,}", re.I)
_SEARCHED = re.compile(r"Searched[^\n:]*:\s*\S.*->\s*no fit:\s*\S.+", re.I)
_DECISION = re.compile(r"^\W*Decision:\s*(Adopt|Fork|Build)\b(.+)$", re.I)

REASONS = {
    "missing_section": "The '## Prior art' section is missing.",
    "no_evidence": "The prior art section needs a link, or a line like 'Searched: <query> -> no fit: <why>'.",
    "no_decision": "Write 'Decision: Adopt, Fork, or Build' followed by at least three words explaining why.",
}


def check_text(text: str) -> list[str]:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # comments never count as evidence
    m = _HEADING.search(text)
    if not m:
        return ["missing_section"]
    end = len(text)
    for nxt in _ANY_HEADING.finditer(text, m.end()):
        if len(nxt.group(1)) <= len(m.group(1)):
            end = nxt.start()
            break
    lines = [ln for ln in text[m.end():end].splitlines() if ln.strip()]
    reasons = []
    evidence = [ln for ln in lines if (_URL.search(ln) or _SEARCHED.search(ln))
                and not ln.strip("-* \t").lower().startswith("decision")]
    if not evidence:
        reasons.append("no_evidence")
    ok = False
    for ln in lines:
        d = _DECISION.match(ln.strip("-* \t"))
        if d and len(re.findall(r"\w+", _PLACEHOLDER.sub("", d.group(2)))) >= 3:
            ok = True
    if not ok:
        reasons.append("no_decision")
    return reasons


def check_file(path) -> list[str]:
    try:
        return check_text(Path(path).read_text(encoding="utf-8"))
    except OSError:
        return ["unreadable"]


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args or "--help" in argv or "-h" in argv:
        print(__doc__.strip())
        return 0 if ("--help" in argv or "-h" in argv) else 2
    reasons = check_file(args[0])
    if "unreadable" in reasons:
        print(f"forge_prior_art: cannot read {args[0]}", file=sys.stderr)
        return 2
    if "--json" in argv:
        print(json.dumps({"ok": not reasons, "reasons": reasons}))
    elif reasons:
        print("prior-art check FAILED: " + " ".join(REASONS[r] for r in reasons))
    else:
        print("prior-art check passed")
    return 0 if not reasons else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
