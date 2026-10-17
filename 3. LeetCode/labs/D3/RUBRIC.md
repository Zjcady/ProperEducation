# D3 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | Learner can say what P, I and D each respond to in one sentence each, and which term removes the steady-state error and why P alone cannot (zero error means zero push, but the heater needs 0.5 forever). |
| 3 | `update` clamps the output and, when `integral_limit` is set, the integral. Learner can say what windup is and point at the moment in the heater run where it happens (power pinned at 1 while the error is large). |
| 4 | Learner can say why `dt` appears in the I and D terms and not in P, and why the first call returns a derivative of 0. |
| 5 | `settling_time` walks back from the end to the last excursion; learner can give a trace where "first time inside the band" gives the wrong answer. |
| 6 | From the CLI output, learner can do the P-only arithmetic on paper (0.1 * e * 4 = 0.05 * (40 - e)) and say where the 4.4 C comes from. |
| 7 | Learner can say what `--no-integral-limit` changed and why, and what `--kd 0.5` did to the power column. |
| 8 | Learner can name one thing a real controller needs that this one lacks (filtering noise before the D term, derivative on measurement, feed-forward, setpoint ramping). |
