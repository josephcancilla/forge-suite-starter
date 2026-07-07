# Forge Suite — Umbrella CLAUDE.md

**Lane:** Self-learning general-purpose builder. Scaffolds agents, scripts, web-apps, and websites from fuzzy English descriptions — and surfaces the questions you didn't think to ask.
**Phase:** 3.1 — Forge Suite ship.
**Sub-agents:** SpecMan (`forge/specman/`), Builder (`forge/builder/`), Designer (`forge/designer/`).

---

## Role

Forge removes the manual-build bottleneck. You describe what you want in plain English. SpecMan converts that into a validated, type-tagged spec AND asks the blind-spot questions you didn't consider. Builder reads the approved spec and produces every required artifact in one git commit. Designer (web builds only) produces HTML/CSS/React via Anthropic's `frontend-design` skill.

Forge is self-learning: every sub-agent runs a daily self-review at 2am, ingests insights from Research (trending patterns), absorbs warnings from a monitoring agent (drift/failures), and reports to the Commander. The Commander then synthesizes cross-agent themes at 3am via `teach` and propagates them back into the ecosystem.

**Mandate-level directive:** products shipped via Forge should be 10X better than what you would describe alone. SpecMan's blind-spot protocol is the mechanism.

---

## Sub-Agents

1. **SpecMan** (`forge/specman/`) — Turns fuzzy idea → `~/.forge-suite/queue/forge/<name>_spec.md`. Runs 5-pass blind-spot protocol (edge cases, 10X adjacencies, failure-mode gaps, UX/second-order, ecosystem fit). 2–5 questions per spec. You answer inline or skip.
2. **Builder** (`forge/builder/`) — Reads approved spec → scaffolds CLAUDE.md + dof.md + bin + token_limits entry + graduation_counter entry + journal dir. One git commit. Closes all legacy Forge manual gaps.
3. **Designer** (`forge/designer/`) — For `type: web-app` or `type: web-site` specs, invokes Anthropic's `frontend-design` skill to produce design artifacts. Hands back to Builder for inclusion in final commit.
4. **Architect** (`forge/architect/`) — Sits between SpecMan and Builder. Confirmed spec → build design document (components, state files, dependencies, integration points, risks, verification plan).
5. **Verifier** (`forge/verifier/`) — Post-build gate. Runs deterministic checks (a–g) + Claude DOF/spec-fidelity verdict. Exit 0 = PASS, exit 30 = FAIL; blocks activation on FAIL.

Sub-agents never invoke each other directly — with one sanctioned exception: `forge-pipeline` (see Pipeline section below). You run individual sub-agents with approval gates, or run `forge-pipeline <name>` to advance the whole chain.

**Handoff chain:**
`Your fuzzy idea → forge-specman → queue/forge/<name>_spec.md → you approve → forge-builder (→ forge-designer if web) → git commit → graduation_counter updated → you activate`

---

## Token Budget

Combined daily cap: 500,000 input / 95,000 output tokens (enforced by `cb check forge`).
All three sub-agents + forge-learn draw from the same `forge` bucket.

Per-sub-agent run sub-caps:
- SpecMan: 40K in / 8K out
- Builder: 80K in / 15K out
- Designer: 120K in / 25K out
- forge-learn: 20K in / 5K out per sub-agent per day

---

## Trust Level

**L0 — Draft only.** Every sub-agent surfaces output for your approval before any filesystem write lands (dry-run mode writes to `/tmp/`).

Graduation counter per sub-agent: 5 consecutive zero-edit approvals → L1 (auto-commit on pass-through).

`~/.forge-suite/state/forge/graduation_counter.json` — per-agent counters, keyed by kebab-case name.

---

## Continuous Learning

Every sub-agent runs a daily 2am launchd job (`com.forge-suite.forge-learn`) that:

1. Reads the day's outputs from `~/.forge-suite/outputs/forge/<sub-agent>/`.
2. Scores each output against its DOF.
3. Queries Research for trending patterns in the sub-agent's lane.
4. Reads the last 24h of monitoring-agent audit findings.
5. Appends a lesson entry to `~/.forge-suite/memory/lessons/<sub-agent>_lessons.md`.
6. Writes one-line digest to `~/.forge-suite/journal/pending/forge_daily_<YYYY-MM-DD>.md`.

All loop calls flow through Claude Code (subscription auth). **No ANTHROPIC_API_KEY.** A monitoring agent watches for drift.

---

## Commander Leadership Layer

`teach` runs at 3am daily (after forge-learn finishes) and:

1. Synthesizes cross-agent themes from that day's lesson files.
2. Propagates teaching memos to `~/.forge-suite/memory/teachings/<YYYY-MM-DD>_<theme>.md`.
3. Promotes patterns with 5 clean runs to `~/.forge-suite/memory/promoted_patterns.md` (SpecMan reads this before generating new specs).
4. Demotes patterns with 3+ drift events to `~/.forge-suite/memory/demoted_patterns.md` (SpecMan refuses to spec using them).
5. Weekly rollup every Sunday 11pm → `~/.forge-suite/audit/<YYYY-MM-DD>_teaching_weekly.md` (surfaced in the Monday operations brief).

`teach` applies to the whole agent ecosystem, not just Forge. Existing 10 agents get retrofitted with lessons files in Phase 3.2.

---

## Auto-Install Skills

`~/.forge-suite/bin/skill-install <github-url>` — you never clone manually. The Commander parses URL → prompts for "y" → tries `git clone` → falls back to Chrome MCP → validates SKILL.md frontmatter → copies to `~/.claude/skills/<name>/` → updates MANIFEST.md → prints claude.ai Project parity reminder.

Hard gate: any skill requesting broad OAuth scopes at install = HARD STOP (Vercel April 2026 learned principle).

---

## Output Locations

- SpecMan: `~/.forge-suite/outputs/forge/specman/<TS>_<name>_spec.md`
- Builder: `~/.forge-suite/outputs/forge/builder/<TS>_<name>_scaffold.md`
- Designer: `~/.forge-suite/outputs/forge/designer/<TS>_<name>_design.md`
- Spec queue: `~/.forge-suite/queue/forge/<name>_spec.md`
- Blind-spot log: `~/.forge-suite/audit/blind-spots/<agent>.log`
- Graduation counter: `~/.forge-suite/state/forge/graduation_counter.json`

---

## Definition of Failure

Each sub-agent has its own DOF file:
- `~/.forge-suite/agents/forge/specman/dof.md`
- `~/.forge-suite/agents/forge/builder/dof.md`
- `~/.forge-suite/agents/forge/designer/dof.md`

---

## Legacy `forge` Bin

The original `~/.forge-suite/bin/forge` bin stays as a thin dispatcher. Running it prints:

```
Forge suite is a 3-sub-agent pipeline. Use:
  forge-specman "<fuzzy idea>"   → draft spec + blind-spot questions
  forge-builder <name>            → scaffold approved spec
  forge-designer <name>           → web-app/web-site design pass
```

No other behavior. You invoke sub-agent bins directly.

---

## Forge v2 — Repair, Upgrade, Audit (shipped 2026-05-15)

Forge is no longer new-agent-only. v2 lets the Commander activate Forge against the existing roster:

- **`forge audit <agent>`** — scores one agent 0-100 against 11 canon criteria (Behavior Contract, fact-lock, power-down, DOF, etc.). HEALTHY ≥85, DEGRADED 60-84, NEEDS-UPGRADE <60.
- **`forge audit --all`** — sweeps every real agent, ranked deficit report with per-agent links.
- **`forge upgrade <agent>`** — generates an upgrade spec in `~/.forge-suite/queue/forge/<agent>_upgrade_spec.md`. Each FAILed criterion gets a concrete patch instruction (file, section, current state, required state, patch). You review; apply step deferred to v2.1.
- **`forge sweep`** — Commander-callable orchestrator. Audit-all + auto-generate upgrade specs for the top-3 lowest-scoring NEEDS-UPGRADE agents. Drops specs in `~/.forge-suite/queue/forge/` for your approval.
- **`forge skill-request --description "<gap>" [--url <github>] [--install]`** — the Commander logs a skill gap; optional `--install` invokes `~/.forge-suite/bin/skill-install`.

**Audit criteria (11, weighted to 100):**
1. CLAUDE.md present (≥10 lines) — 10
2. dof.md has all 5 sections — 10
3. Bin script exists + executable — 10
4. Bin has no ANTHROPIC_API_KEY on non-comment lines — 10
5. Behavior Contract: 8 fields present — 15 *(graduation blocker)*
6. Silence Contract section + silence_rule.md ref — 5
7. Fact-lock retrofit or declared exempt — 15 *(graduation blocker)*
8. Power-down pattern declared (day-keyed / time-window / inherent idempotency / no-schedule) — 10 *(graduation blocker)*
9. graduation_counter.json present — 5
10. Token tier declared (token_limits.yaml or CLAUDE.md) — 5
11. Voice canon referenced (VOICE_PROFILE.md / read-only declaration) — 5

**Trust model:** Forge audits + drafts upgrade specs at L0. You approve all patches. Forge does NOT graduate trust levels — a separate grading agent remains grader of record. Audit reports flag "graduation-blocking gaps" (FAILs on criteria 5/7/8) so that agent's surface is informed by Forge's findings.

**Outputs:**
- Single agent audit: `~/.forge-suite/outputs/forge/audit/<TS>_<agent>.md`
- All-agents audit: `~/.forge-suite/outputs/forge/audit/<TS>_all.md`
- Upgrade specs: `~/.forge-suite/queue/forge/<agent>_upgrade_spec.md`
- Sweep summaries: `~/.forge-suite/outputs/forge/sweep/<TS>_sweep.md`
- Skill requests: `~/.forge-suite/queue/forge/skill-requests.jsonl`

**Power-down pattern:** Forge v2 is CLI-only — no scheduled plist, no ambient triggers. Pattern: no-schedule.

**Renamed commands:** `forge retrofit` and `forge retrofit-ack` (v1 stubs) now print a rename notice and exit 0. Use `forge upgrade <agent>` instead.

**Implementation:** Audit logic lives in `~/.forge-suite/lib/forge_audit.py`; spec generation in `~/.forge-suite/lib/forge_upgrade_spec.py`. Stdlib only.

---

## Pipeline

`forge-pipeline <name>` is the sanctioned exception to "sub-agents never invoke each other directly." It owns the stage-machine for a named build and chains sub-agents in order:

```
forge-specman (Phase 1 — you run first)
  → [YOUR GATE: redline Diagnosis in spec]
  → forge-specman --confirm-diagnosis   (Phase 2)
  → forge-architect                     (design doc)
  → forge-builder                       (scaffold)
  → forge-verifier                      (gate: exit 30 = failed, fix + retry)
  → [YOUR GATE: review activation memo, run the bin manually]
  → active
```

State file per build: `~/.forge-suite/queue/forge/pipeline/<name>.json`
Sub-agent list: SpecMan, Architect, Builder, Verifier (Designer is invoked by Builder for web builds — pipeline does not call it directly).
Status command: `forge-pipeline --status`
Bin: `~/.forge-suite/bin/forge-pipeline`
Agent instructions: `~/.forge-suite/agents/forge/pipeline/CLAUDE.md`

---

## Behavior Contract (umbrella)

The Forge Suite is an umbrella, not a runnable agent. Operational contracts live on each sub-agent's CLAUDE.md. This section is the umbrella-level summary; it must not conflict with sub-agent contracts.

### 1. Identity
- **Name:** `forge` (umbrella)
- **Mandate:** Coordinate SpecMan + Builder + Designer so fuzzy English → validated spec → scaffolded artifacts → git commit, with blind-spot interrogation baked in and continuous learning across all three.

### 2. Triggers
Umbrella has no direct triggers. Sub-agents carry their own:
- `forge-specman` — CLI-only (see `specman/CLAUDE.md` §Behavior Contract §2)
- `forge-builder` — CLI-only (see `builder/CLAUDE.md` §Behavior Contract §2)
- `forge-designer` — CLI-only (see `designer/CLAUDE.md` §Behavior Contract §2)
- `forge-learn` — scheduled launchd 2am daily (`com.forge-suite.forge-learn.plist`)

### 3. Ambient listening
None at the umbrella level. Ambient surfaces are sub-agent-scoped.

### 4. Actions — blast radius
None at the umbrella level. Every side effect belongs to a sub-agent and is gated in that sub-agent's §4.

### 5. Silence contract
- **Default when not explicitly addressed:** SILENCE — the umbrella never acts directly.
- **Silence rule ref:** `~/.forge-suite/agents/_shared/silence_rule.md`.
- **Silent-skip log:** each sub-agent writes its own skip line to `~/.forge-suite/audit/silent-skips.log`.

### 6. Failure modes
- **Hard failure (umbrella-level):** you running a `forge-*` bin script with missing prerequisites (no spec for Builder; non-web spec for Designer). Each sub-agent surfaces its own failures to `~/.forge-suite/audit/actions.log`.
- **Soft failures:** handled per sub-agent DOF.
- **DOF files:** `specman/dof.md`, `builder/dof.md`, `designer/dof.md`.

### 7. Dedup strategy
- Kebab-case collision check: Builder refuses to scaffold if `~/.forge-suite/agents/<name>/` exists.
- Git commit per Builder run: `rollback` reverts cleanly.
- 500K/95K daily cap gates total sub-agent activity across all three + forge-learn.

### 8. Deployment
- **Binaries:** `~/.forge-suite/bin/forge-specman`, `~/.forge-suite/bin/forge-builder`, `~/.forge-suite/bin/forge-designer`, `~/.forge-suite/bin/forge-architect`, `~/.forge-suite/bin/forge-verifier`, `~/.forge-suite/bin/forge-pipeline` (orchestrator), `~/.forge-suite/bin/forge-learn`, `~/.forge-suite/bin/forge` (dispatcher), `~/.forge-suite/bin/teach`, `~/.forge-suite/bin/skill-install`.
- **Plists:** `~/.forge-suite/launchd/com.forge-suite.forge-learn.plist.example` (2am daily), `~/.forge-suite/launchd/com.forge-suite.teach.plist.example` (3am daily).
- **Output tree:** `~/.forge-suite/outputs/forge/{specman,builder,designer}/`
- **Queue:** `~/.forge-suite/queue/forge/<name>_spec.md`
- **State:** `~/.forge-suite/state/forge/graduation_counter.json`
- **Learning:** `~/.forge-suite/memory/lessons/{specman,builder,designer}_lessons.md`
- **Teaching:** `~/.forge-suite/memory/teachings/<YYYY-MM-DD>_<theme>.md`, `~/.forge-suite/memory/{promoted,demoted}_patterns.md`
- **Blind-spot audit:** `~/.forge-suite/audit/blind-spots/<agent>.log`
- **Token limits:** `~/.forge-suite/config/token_limits.yaml` → `agents.forge` (500K in / 95K out daily, shared across sub-agents + forge-learn)
- **Shared audit log:** `~/.forge-suite/audit/actions.log`
