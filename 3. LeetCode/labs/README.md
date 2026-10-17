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
| D1 to D5 | Autonomy flavor (state machines, A*, PID, OpenCV, a tiny HMI) | the responsibilities paragraph | later |

Setup once: `pip install -r requirements.txt` from this folder installs everything the labs need. Live calls need `ANTHROPIC_API_KEY` or `ant auth login`; every test runs without one.

`_common/fake_llm.py` is the fake client the tests use. Read it once; it shows exactly what the real response object looks like.
