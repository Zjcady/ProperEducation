# C2 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | Live run over `data/` produces a sensible report; learner can point at one summary and say whether it's accurate. |
| 3 | `chunk_text` never splits a word and never silently truncates. Learner can explain why truncation is worse than chunking. |
| 4 | `classify` never returns a label outside the set, and the learner can explain the retry-then-unknown choice. |
| 5 | Learner tried a few-shot prompt and wrote one observation in NOTES.md. |
| 6 | Token totals in the report add up across all calls, not just the last one. |
| 7 | Learner can estimate what running this over 1,000 files would cost, and say one way to cut it. |
