# C9 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | `out/traces.jsonl` from a live run has one span per call with the exact `gen_ai.*` names, and the learner can say what a span is and why p95 beats the average. |
| 3 | A failed call is still traced (`ERROR`, `error.type`) and the exception still reaches the caller. Learner can say why swallowing it would be worse. |
| 4 | The judge prompt never contains the human label or the seeded-failure note. Learner can say why that would make the eval meaningless. |
| 5 | Learner can explain why an always-pass judge scores 0.7 here, and why that number is the floor, not a good score. |
| 6 | For each live disagreement, learner read the transcript and decided whether the judge or the label was wrong (in NOTES.md). |
| 7 | Learner can explain pass@k vs pass^k with the 2-of-3 example and say which one they'd report for an agent a user depends on. |
