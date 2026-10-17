# D5 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | Learner can name the five keys of `/state` from memory and say why the page gets one boolean (`awaiting_approval`) instead of working the rule out from `state` itself. |
| 3 | `approve` after complete or abort changes nothing but the log; learner can say why an ignored press still deserves a log line. |
| 4 | Abort is accepted in every state and the page never disables it; learner can say why the two buttons follow different rules. |
| 5 | Unknown paths get a JSON 404 with the same Content-Type as every other reply; learner can say what the page's `await response.json()` would do with an HTML error page instead. |
| 6 | Learner can say why a `ThreadingHTTPServer` needs the lock (a poll and a click can arrive in the same instant) and point at where it is held. |
| 7 | The page renders the POST reply instead of waiting for the next poll; learner can say what the operator would see otherwise, and what the one-second poll is still for. |
| 8 | Learner can name two things a real operator console needs that this one lacks (who approved and when, a `running` state that lasts, authentication, a confirmation on Abort or a reason not to have one). |
