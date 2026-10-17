# D1 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | Learner can say why the transitions live in one table instead of if/elif chains, and what `IllegalTransition` buys a mission system. |
| 3 | `fire` changes nothing when it raises, and the history is complete and in order. Learner can name two uses for a history (replay, post-flight review, what the HMI shows). |
| 4 | Learner can say from memory which states allow `abort`, and why `IDLE` and `LANDED` do not. |
| 5 | `plan_tasks` keeps the reserve and the return leg out of the spendable budget. Learner can do the 100 / 20 / 15 arithmetic on paper and say where the third waypoint went. |
| 6 | `run` aborts before a leg that would eat the reserve, never during return or land, and a plan made for battery B never aborts when flown at B. Learner can say why that follows from how the plan was made. |
| 7 | Learner can draw the seven states and their labelled arrows on paper from memory. |
| 8 | Learner can name one thing a real drone's mission machine needs that this one lacks (timeouts, sensor faults, a return-to-launch after abort). |
