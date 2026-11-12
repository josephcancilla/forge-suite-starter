# Forge Suite — Umbrella CLAUDE.md

**Lane:** Self-learning general-purpose builder. Scaffolds agents, scripts, web apps, and websites from fuzzy English descriptions, and surfaces the questions the operator didn't think to ask.
**Sub-agents:** SpecMan (`forge/specman/`), Architect (`forge/architect/`), Builder (`forge/builder/`), Designer (`forge/designer/`), Verifier (`forge/verifier/`). Pipeline (`forge/pipeline/`) chains them.
**Base folder:** `$FORGE_HOME` (default `~/.forge-suite`). Every path below is relative to it.

---

## Role

Forge removes the manual-build bottleneck. The operator describes what they want in plain English. SpecMan turns that into a validated, type-tagged spec AND asks the blind-spot questions the operator didn't consider. Before anything new is designed, SpecMan checks for prior art: an existing tool, skill, or open-source project that already does the job. Architect turns the confirmed spec into a build design doc. Builder reads the approved spec and produces every required artifact in one git commit. Designer (web builds only) produces HTML/CSS/React using the `frontend-design` skill. Verifier tries to break the result against a done-bar checklist: a FAIL blocks activation.

Forge is self-learning: each sub-agent reviews its own recent outputs every night, writes a lesson, and that lesson is fed into the agent's next run. Forge reports to your commander agent, which is the only thing that talks to the operator.

**Mandate:** products shipped via Forge should be 10X better than what the operator would describe alone. SpecMan's blind-spot protocol is the mechanism, and the prior-art check keeps it cheap.

---

## Sub-Agents

1. **SpecMan** (`forge/specman/`) — fuzzy idea -> `queue/forge/<name>_spec.md`. Two phases: a Diagnosis the operator redlines, then the full spec. Runs the 5-pass blind-spot protocol (2 to 5 specific questions) and the prior-art check.
2. **Architect** (`forge/architect/`) — confirmed spec -> build design document (components, state files, dependencies, integration points, risks, verification plan). Planning only: no code, no writes outside its own outputs.
3. **Builder** (`forge/builder/`) — approved spec -> `CLAUDE.md` + `dof.md` + bin script + token entry + graduation counter entry + lessons seed. One git commit. Every new agent starts at L0.
4. **Designer** (`forge/designer/`) — for `type: web-app` or `type: web-site` specs, uses the `frontend-design` skill to produce design artifacts and tokens. Also has a `--mode=ux-review` pass for any file.
5. **Verifier** (`forge/verifier/`) — post-build gate. Eight deterministic checks (a to h) plus one Claude judgment that assumes the build is wrong and tries to prove it. Exit 0 = PASS, exit 30 = FAIL. It always leaves a parseable verdict, even if it crashes. `verify` (in `bin/`) is the same Verifier as a general front door for any deliverable plus a done-bar.
6. **Pipeline** (`forge/pipeline/`) — the stage machine that runs the others in order and stops at your gates.

Sub-agents never invoke each other directly, with one sanctioned exception: `forge-pipeline`. You run individual sub-agents with approval gates, or run `forge-pipeline <name>` to advance the whole chain. `forge-pipeline --dry-run <name>` prints the plan and runs nothing.

**Handoff chain:**
`fuzzy idea -> forge-specman -> queue/forge/<name>_spec.md -> you approve -> forge-architect -> forge-builder (-> forge-designer if web) -> git commit -> forge-verifier -> you activate`

---

## Prior art first

Before building something new, look for something that already exists. SpecMan searches the web and GitHub and checks the skills already installed, then records the result in the spec's `## Prior art` section and writes an Adopt, Fork, or Build decision with a reason. `lib/forge_prior_art.py` checks it: SpecMan's Phase 2 exits 23 without a passing section, Verifier check h fails a build whose spec lacks one, and a done-bar with `<!-- gate:prior-art -->` (see `donebars/forge_spec.md`) applies the same gate through `verify`. Reuse beats rebuild.

---

## Token Budget

Combined daily cap: 500,000 input / 95,000 output tokens, enforced by `forge-cb check forge` (override with `FORGE_CB_INPUT_CAP` / `FORGE_CB_OUTPUT_CAP`). All sub-agents and `forge-learn` draw from the same `forge` bucket.

Per-sub-agent run caps:
- SpecMan: 40K in / 8K out
- Architect: 60K in / 12K out
- Builder: 80K in / 15K out
- Designer: 120K in / 25K out
- Verifier: 40K in / 8K out
- forge-learn: 20K in / 5K out per sub-agent per day

---

## Trust Level

The ladder: **L0 draft only**, **L1 staged** (you approve before anything lands or sends), **L2 automatic with checks**, **L3 autonomous**.

**Every sub-agent starts at L0.** Each surfaces its output for your approval before it counts. Dry-run mode writes to `/tmp/`, never to the suite.

Graduation counter per sub-agent: consecutive zero-edit approvals earn a recommendation for the next level. **Only the operator raises a level. No agent, including Forge and your commander agent, promotes itself or another agent.**

`agents/forge/<sub-agent>/graduation_counter.json` holds each sub-agent's counter. Agents Builder scaffolds are tracked in `state/forge/graduation_counter.json`.

---

## Continuous Learning (forge-learn)

`forge-learn all` runs once a night (see `docs/SCHEDULING.md`; macOS launchd or Windows Task Scheduler). It is built to cost almost nothing on a quiet day:

1. **Throttle.** If a successful run happened in the last 18 hours, exit.
2. **No-work pre-check.** If none of the five sub-agents wrote any output in the last 24 hours, record a "skipped" receipt and exit. No circuit-breaker call, no Claude call.
3. **Per-agent idle check.** An agent with no recent output is skipped on its own.
4. **Self-review.** For each active agent, one small Claude call reads the agent's `CLAUDE.md`, the day's outputs, and its existing lessons, scores outputs CLEAN / SOFT_FAIL / HARD_FAIL against the agent's DOF, and appends one lesson line to `memory/lessons/<sub-agent>_lessons.md`.
5. **Lessons reach the next run.** The newest five lessons are copied to `agents/forge/<sub-agent>/LESSONS.md`. Each sub-agent's script appends that file to its prompt, so what was learned last night changes tomorrow's behavior. A lesson is advice, never permission to widen scope or raise a trust level.
6. **Digest and receipt.** A one-line digest goes to `journal/pending/forge_daily_<YYYY-MM-DD>.md`, and every real run appends a receipt (status `ok`, `skipped`, or `error`, with counts) to `state/receipts/forge-learn.jsonl`.

`forge-learn --dry-run all` prints what would happen and writes nothing. All loop calls flow through the Claude Code CLI (subscription auth). **No `ANTHROPIC_API_KEY`.**

---

## Output Locations

- SpecMan: `outputs/forge/specman/<TS>_<name>_spec.md`
- Architect: `outputs/forge/architect/<TS>_<name>_design_summary.md`, design doc in `queue/forge/designs/<name>_design.md`
- Builder: `outputs/forge/builder/<TS>_<name>_scaffold.md` and `<TS>_<name>_activation_memo.md`
- Designer: `outputs/forge/designer/<TS>_<name>_design.md`
- Verifier: `queue/forge/verdicts/<name>_verdict.json`, summary in `outputs/forge/verifier/`
- Spec queue: `queue/forge/<name>_spec.md`
- Pipeline state: `queue/forge/pipeline/<name>.json`
- Blind-spot log: `audit/blind-spots/<agent>.log`
- Audit log: `audit/actions.log`

---

## Definition of Failure

Each sub-agent has its own DOF file: `agents/forge/<sub-agent>/dof.md`. The umbrella DOF is `agents/forge/dof.md`.

---

## The `forge` command

`bin/forge` is the older dispatcher and repair tool. With no arguments it prints the five-agent usage. It also scaffolds directly from a spec (`forge new`, bypassing SpecMan; advanced use only) and audits existing agents:

- **`forge audit <agent>`** scores one agent 0 to 100 against 11 criteria (Behavior Contract, fact-check retrofit, power-down pattern, DOF, and so on). HEALTHY 85 and up, DEGRADED 60 to 84, NEEDS-UPGRADE under 60.
- **`forge audit --all`** sweeps every agent and ranks the gaps.
- **`forge upgrade <agent>`** writes an upgrade spec to `queue/forge/<agent>_upgrade_spec.md`, one concrete patch per failed criterion. You review it; nothing is applied automatically.
- **`forge sweep`** audits everything and drafts upgrade specs for the three weakest agents.
- **`forge skill-request --description "<gap>" [--url <github>]`** logs a skill gap to `queue/forge/skill-requests.jsonl`. You install the skill yourself by copying its folder into your skills folder.

**Audit criteria (weights add to 100):**
1. CLAUDE.md present (10 or more lines): 10
2. dof.md has all 5 sections: 10
3. Bin script exists and is executable: 10
4. Bin has no `ANTHROPIC_API_KEY` on non-comment lines: 10
5. Behavior Contract, 8 fields present: 15 (graduation blocker)
6. Silence Contract section and `silence_rule.md` reference: 5
7. Fact-check retrofit or declared exempt: 15 (graduation blocker)
8. Power-down pattern declared (day-keyed, time-window, inherent idempotency, or no-schedule): 10 (graduation blocker)
9. graduation_counter.json present: 5
10. Token tier declared: 5
11. Voice profile referenced or read-only declared: 5

Forge audits and drafts at L0. It never raises a trust level.

---

## Pipeline

`forge-pipeline <name>` owns the stage machine for a named build:

```
forge-specman (Phase 1: you run this first)
  -> [YOUR GATE: redline the Diagnosis in the spec]
  -> forge-specman --confirm-diagnosis   (Phase 2: spec + blind-spot questions + prior art)
  -> forge-architect                     (design doc)
  -> forge-builder                       (scaffold; calls Designer for web builds)
  -> forge-verifier                      (gate: exit 30 = failed, fix and retry; 3 failures in a row escalate to you)
  -> [YOUR GATE: read the activation memo, run the bin yourself]
  -> active  (forge-pipeline <name> --mark-active records it)
```

State file per build: `queue/forge/pipeline/<name>.json`. `forge-pipeline --status` lists every build. `forge-pipeline --dry-run <name>` shows the plan without running anything. Agent instructions: `agents/forge/pipeline/CLAUDE.md`.

---

## Behavior Contract (umbrella)

The Forge Suite is an umbrella, not a runnable agent. Operational contracts live on each sub-agent's CLAUDE.md. This section is the umbrella-level summary and must not conflict with them.

### 1. Identity
- **Name:** `forge` (umbrella)
- **Mandate:** Coordinate SpecMan, Architect, Builder, Designer, and Verifier so a fuzzy English idea becomes a validated spec, a prior-art decision, a scaffolded build in one git commit, and an independent verdict, with blind-spot questions and continuous learning built in.

### 2. Triggers
The umbrella has no triggers. Sub-agents carry their own:
- `forge-specman`, `forge-architect`, `forge-builder`, `forge-designer`, `forge-verifier`, `forge-pipeline`: CLI only.
- `forge-learn`: your scheduler, once a night (see `docs/SCHEDULING.md`), or by hand.

### 3. Ambient listening
None at the umbrella level.

### 4. Actions and blast radius
None at the umbrella level. Every side effect belongs to a sub-agent and is gated in that sub-agent's section 4.

### 5. Silence contract
- **Default when not explicitly addressed:** SILENCE. The umbrella never acts directly.
- **Silence rule:** `agents/_shared/silence_rule.md`.
- **Silent-skip log:** `audit/silent-skips.log`.

### 6. Failure modes
- **Hard failure (umbrella level):** running a `forge-*` script with missing prerequisites (no spec for Builder, a non-web spec for Designer). Each sub-agent logs its own failures to `audit/actions.log`.
- **Soft failures:** handled per sub-agent DOF.
- **DOF files:** `agents/forge/<sub-agent>/dof.md`.

### 7. Dedup strategy
- Kebab-case collision check: Builder refuses to scaffold if `agents/<name>/` exists.
- One git commit per Builder run, so a bad build reverts cleanly.
- The daily token cap gates all sub-agent activity together with `forge-learn`.

### 8. Deployment
- **Scripts:** `bin/forge-specman`, `forge-architect`, `forge-builder`, `forge-designer`, `forge-verifier`, `forge-pipeline`, `forge-learn`, `forge-cb`, `forge` (dispatcher), `verify`.
- **Scheduler examples:** `launchd/com.forgesuite.forge-learn.plist.example` (macOS) and `docs/SCHEDULING.md` (Windows Task Scheduler).
- **Libraries:** `lib/forge_audit.py`, `lib/forge_upgrade_spec.py`, `lib/forge_prior_art.py` (stdlib only).
- **Runtime folders (created on first use):** `queue/`, `outputs/`, `state/`, `journal/`, `memory/`, `audit/`.
- **Token limits:** daily cap in `bin/forge-cb`; per-agent entries Builder appends to `config/token_limits.yaml`.
