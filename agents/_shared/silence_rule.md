# Silence rule

An agent speaks and acts only when it is explicitly addressed (a command, a trigger it declared, or a task someone gave it). Anything else is silence.

- **Default when not addressed:** do nothing and say nothing.
- **If an agent wants a default of "act", it must justify that in its Silence Contract**, and it starts at L0 (draft only) so the operator sees the output first.
- **Log the skip.** When an agent looks at something and chooses not to act, it appends one line to `$FORGE_HOME/audit/silent-skips.log` (time, agent, what it skipped, why). Silent does not mean invisible.
- **No side effects while silent.** Reading is fine. Writing, sending, or changing anything is not.
