# C3 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass. |
| 2 | Server runs with `--http`; Claude Code, registered with `--transport http` and an `Authorization: Bearer` header, lists the tools and calls `coach_next`. |
| 3 | `coach_done` over HTTP with the read-only token is denied; with the write token it works. Learner demonstrated both. |
| 4 | `coach_done` takes no token argument; the token only ever travels in the `Authorization` header. Learner explains why arguments are the wrong place. |
| 5 | Learner explains 401 vs 403 vs a tool-level "denied", and why stdio takes credentials from the environment instead. |
| 6 | `tokens.json` is gitignored and not committed, and the server was registered at local scope, not into `.mcp.json`. |
| 7 | Learner explains authentication vs authorization without notes. |
| 8 | Learner explains why the default token for the model should be read-only, and why `coach_done` would still want a human confirmation in production. |
| 9 | AUTH.md is complete, about one page, in the learner's words. |
| 10 | Learner can sketch, on paper, the MCP flow over HTTP: request with bearer header, token verified, list tools, model picks, client calls, result returns. |
