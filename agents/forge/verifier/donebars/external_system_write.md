# Done-bar — external system write (create or update)
- [ ] App schema was read first; every value landed in the most specific existing field
- [ ] No new fields created (unless the operator explicitly approved that field)
- [ ] Dedup check ran before any create; no duplicate item exists for the same real-world thing
- [ ] Every field that could legitimately be filled is filled (derive dates, mine notes, obvious statuses)
- [ ] Images went to the image field; PDFs and other files to Files
- [ ] Any comment posted is plain English a teammate would write — no paths, no code-speak, no dumps
- [ ] Any @-mention uses the format the system requires so the notification actually fires
- [ ] The item link (real URL from the system) is captured in the run output
- [ ] For money-adjacent fields: the write went through Fact-Lock + Approvals, not straight to the API
