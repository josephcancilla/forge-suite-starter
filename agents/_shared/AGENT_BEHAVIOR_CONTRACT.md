# Agent Behavior Contract (8 fields)

Every agent Forge builds carries these eight fields, in its spec and in its `CLAUDE.md` under `## Behavior Contract`. Number the headings `### 1. Identity` through `### 8. Deployment`.

1. **Identity.** Name (kebab-case) and a one-sentence mandate: what it does, for whom.
2. **Triggers.** Every way it can start: a command, a schedule, a webhook, a message. Table format. If it has no schedule, say "CLI only".
3. **Ambient listening.** What it reads without being asked (files, queues, feeds). Read only. "None" is a valid answer.
4. **Actions and blast radius.** Every side effect it can cause, the gate that allows it, and the worst case if it is wrong. End with a "Never" list.
5. **Silence contract.** Default when not addressed (see `silence_rule.md`) and where silent skips are logged.
6. **Failure modes.** Hard failures (broken, must be fixed), soft failures (correct and flag), and not-failures (noise). Points to `dof.md`.
7. **Dedup strategy.** How it avoids doing the same thing twice (name collisions, ledgers, day-keyed guards, idempotency).
8. **Deployment.** Where the script, state, logs, and outputs live, how it is scheduled, and its token budget.

A spec missing any of the eight is refused by Builder.
