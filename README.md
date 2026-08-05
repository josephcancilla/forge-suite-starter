# Forge Suite — Starter Template

A ready-to-adapt agent suite for building **agents, websites, software, and apps**
with an AI coding assistant. Forge takes a request, turns it into a precise spec,
plans it, designs it, builds it, and verifies the result before it counts as done.

This is a **starter template**. It carries the architecture and skills, not any
one owner's business data. Replace the placeholders (see Setup) and make it yours.

## The suite

**Forge** is the orchestrator. It runs a request through five specialists:

| Agent | Role |
|-------|------|
| **Specman** | Turns a request into a precise, approved spec |
| **Architect** | Plans the build from the spec (planning only — no code, no writes) |
| **Designer** | Produces UI and design tokens for web builds |
| **Builder** | Scaffolds the real files and makes one clean commit |
| **Verifier** | Checks the result against done-bar checklists before it counts |
| **Pipeline** | Coordinates the hand-offs between the above |

The **trust ladder** (draft → staged → auto → autonomous) lets each agent earn more
independence as it proves clean runs. The **done-bars** (in `agents/forge/verifier/donebars/`)
are the checklists work must pass to be called finished.

## Layout

- `agents/forge/` — each agent's instructions (`CLAUDE.md`), guardrails (`dof.md`),
  and a fresh graduation counter. Verifier's `donebars/` holds the done-bar checklists.
- `bin/` — the command scripts (`forge`, `verify`, and the `forge-*` sub-agent runners).
- `lib/` — supporting Python libraries.
- `launchd/` — an example scheduler entry (macOS) for the nightly learning run.

## Setup

1. Install the suite wherever you like; the files assume a base of `~/.forge-suite/`.
   If you use a different location, update the paths in `bin/` and `launchd/`.
2. In the `launchd/` files, replace `/Users/YOURNAME` with your real home path and
   load the job with `launchctl` if you want the scheduled learning run.
3. The scripts run through an AI coding assistant's normal auth. **No API keys are
   included, by design** — the suite forbids them in any generated output. Wire your
   assistant per its own docs.
4. Point the Designer's brand direction at your own brand tokens. It ships neutral.

## Notes

- Nothing here is secret or business-specific. Adapt the agent instructions, done-bars,
  and token budgets to your own workflow.
- Share it with your own team or clients as a head start.

## License

MIT — see [LICENSE](LICENSE). Use it, adapt it, build on it.
