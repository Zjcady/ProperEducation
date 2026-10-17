# Labs

Each lab is a folder with a `README.md` (the steps, one per 15-minute block), a starter file with functions marked `TODO(you)`, `tests/` (offline, one group per step, run with `python3 coach.py check <id>`), a `RUBRIC.md` Claude grades against at the end, and `NOTES.md` for your own words.

Every function you write has a test that was verified against a working implementation before the lab was committed. If a test looks wrong, it probably isn't, but say so and we'll look together.

| Lab | Builds | Job posting line | Steps |
|---|---|---|---|
| C1 | First LLM call, JSON out, retries, cost | GenAI fundamentals | 3 |
| C2 | Summarize and classify a folder of notes, with a cost report | Prompts in workflows | 3 |
| C3 | The coach as an MCP server, one token-protected tool | Tool calling / MCP, auth | 4 |
| C4 | A hand-written agent loop, then the SDK tool runner | Agentic frameworks | 4 |
| C5 | RAG over `patterns/` with citations and a measured hit rate | Document processing | 4 |
| C6 | Meeting summarizer, SRT subtitles, gecko content pack | Meeting summarizers | 4 |
| C7 | A Claude Code skill and hook for this repo, plus a write-up | AI dev accelerators | 2 |
| C8 | C6 as an S3-triggered Lambda, tested locally, deployed once | AWS | 3 |
| C9 | Evals and traces: gen_ai spans, an LLM-as-judge with seeded failures, pass@k vs pass^k | Review test outcomes; evals | 3 |
| D1 | A survey-drone mission as a state machine with guarded transitions, task planning under a battery budget, abort | "breaking missions into tasks" | 2 |
| D2 | BFS then A* on grid maps, with path validation and expansion counts | "motion/mission planning" | 2 |
| D3 | A PID controller with anti-windup against a simulated plant, with overshoot and settling-time metrics | "controls" | 2 |
| D4 | OpenCV color segmentation and tracking of a synthetic gecko | "perception" | 2 |
| D5 | An operator console: HTTP API plus a polling page to approve or abort mission tasks | "human-machine interfaces" | 2 |
| E1 to E3 | Interview readiness, in `../career/`: STAR stories, resume bullets, design talks | the interview itself | 3, 2, 2 |

Setup once: `pip install -r requirements.txt` from this folder installs everything the labs need. Live calls need `ANTHROPIC_API_KEY` or `ant auth login`; every test runs without one.

`_common/fake_llm.py` is the fake client the tests use. Read it once; it shows exactly what the real response object looks like.
