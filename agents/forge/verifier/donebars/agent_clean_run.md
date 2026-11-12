# Done-bar: agent clean run (graduation evidence)

For grading one end-to-end run of an agent against real, checkable output. Judge the run against what the agent's current trust level allows it to do:

- L0 (draft only): it proposes, it does not execute. A run that makes zero external writes is correct.
- L1 (staged): it prepares the real action and queues it for the operator's approval. Judge the staged action as if it had been sent without review.
- L2 and above: it acts on its own, so every external write must be real and verifiable.

Do not fail an L0 or L1 agent for "no live write happened". That is the expected state at that level, not a defect.

- [ ] The run is REAL: triggered through the agent's normal path (schedule, poll, or command), not hand-simulated and not a dry-run
- [ ] The agent picked the work up within its expected cadence (state a number, prove it with timestamps)
- [ ] Routing and classification were correct for every item the run found. Zero items found is a PASS if the log shows a real search happened (query, window, result count)
- [ ] Every action is complete enough to stand on its own: for L0 and L1 the exact target and exact content are written out; for L2 and above every external write is captured with a real link or message id
- [ ] Every check the agent promises (fact-check against sources, brand or style check, duplicate check) was actually run and its result is attached, not skipped
- [ ] Anything a person will read is plain English a teammate would write: no file paths, no code-speak, no raw dumps
- [ ] The analysis or lesson the run wrote says something true and specific about THIS run's data. Filler that would read the same on any day fails, even if the file is well formed
- [ ] The run ended in a terminal state (completed, staged, or a legitimate skip), not stuck, looping, or retrying
- [ ] Zero errors in the run's log window (auth failures, retries, exceptions). Quote the log evidence
- [ ] The agent's own state file reflects the finished run (no drift between the state file and the log)
- [ ] If the run's data exercised a known past defect, the fix is shown working. If it did not touch that code path, say so plainly: that is untested-this-run, not a failure

A run that exited early on its own "already ran today" or time-window guard did no work. That is correct behavior, but it is not evidence of a clean run: say so and grade the most recent run that did the work.

The graduation counter and any bookkeeping file the operator keeps are not the agent's own state. They read "in progress" at the moment a run is judged, because the outcome is recorded after a PASS verdict. Do not fail the state-file item on those.
