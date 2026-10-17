# C8 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | Learner can explain why the storage interface exists and how the fake S3 client makes the Lambda testable. |
| 3 | `parse_s3_event` handles URL-encoded keys; learner can say why keys arrive encoded. |
| 4 | Deployed once: the summary appeared in the bucket. Learner has the log line to prove it. |
| 5 | Torn down afterwards; DEPLOY.md records the cost. |
| 6 | Learner can name the three AWS services used and what each did. |
| 7 | Learner can say where the API key should live in a real system, and why not in the template. |
