# C1 rubric

Claude grades each line 0 (missing), 1 (works), 2 (works and the learner can explain why). Write the result to REVIEW.md with one sentence per line.

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | A live call works with the learner's own key, and the key is not in the code or the repo. |
| 3 | Learner can explain, in one sentence each: token, max_tokens, system prompt, model id. |
| 4 | `parse_json_reply` rejects a JSON list and prose, and accepts fenced JSON. |
| 5 | `ask_json` retries with a stricter prompt and gives up after `retries`. |
| 6 | Learner can say which HTTP errors are retryable and why 400 is not. |
| 7 | `estimate_cost` matches the price table and the learner can estimate the cost of a 2,000-token prompt by hand. |
| 8 | NOTES.md has the learner's own one-paragraph summary of when to use `output_config.format` instead of manual parsing. |
