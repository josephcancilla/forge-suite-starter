# Done-bar templates: the Verifier's checklist library
Copy one, fill the blanks, hand it to `verify` with your deliverable.
Every line is pass/fail. If a verifier cannot score a line from the material
given, that line FAILS (unverifiable = not done). No confidence percentages.
Usage: verify --task <name> --deliverable <path> --donebar <filled-checklist.md>

Included: code_build_deliverable, document_deliverable, external_system_write,
outbound_email, roadmap_item_completion, forge_spec (adds the prior-art gate),
and agent_clean_run (graduation evidence, judged against the agent's trust level).
