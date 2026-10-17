# C4 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | Live run completes a two-tool task and the transcript shows both calls. |
| 3 | `safe_path` blocks `..`, absolute paths and symlinks pointing outside the sandbox. Learner can say why each matters. |
| 4 | Tool results carry the right `tool_use_id`; all results for one turn go back in one user message. Learner can say why that matters. |
| 5 | A tool error becomes `is_error: True`, the loop continues, and `max_iters` stops a runaway loop. |
| 6 | Learner can draw the loop on paper from memory. |
| 7 | COMPARE.md is filled in from actually running both versions. |
| 8 | A flagged tool output never reaches the main model raw, and the screen fails closed on a refusal or unreadable reply. Learner can say why it fails closed. |
| 9 | Learner can explain, without notes, why `safe_path` still matters when the screen misses: the screen is a guess, the path check is a rule. |
| 10 | SAFETY.md maps each control to LLM01 or LLM06, names at least two real gaps, and argues for a human confirmation on `coach_done`. |
