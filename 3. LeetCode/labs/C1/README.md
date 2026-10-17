# C1 · First LLM call

**Maps to:** "Generative AI fundamentals" in the job posting.
**You'll have at the end:** a small CLI that sends a prompt to Claude, gets structured JSON back, survives errors, and reports what it cost.

Setup once (any step): `pip install -r requirements.txt`. For live calls, set `ANTHROPIC_API_KEY` (console.anthropic.com) or run `ant auth login`. Every step's tests run **offline** against a fake client, so you can do the whole lab without a key. Try the live version at the end of each step if you have one.

Run a step's tests: `python3 coach.py check C1` (runs the tests for your current step), or directly `python3 -m pytest tests -q -k step1`.

## Step 1 · Send a prompt, read the reply  (15 min)

Read `ask.py` top to bottom first. It already has the CLI and the client factory. You write:

- `build_messages(prompt)`: the `messages` list the API wants. One user turn.
- `text_of(response)`: join the `text` blocks of a response. Responses are lists of blocks; some are not text.
- `ask(client, prompt, system=None, ...)`: call `client.messages.create(...)` with `model`, `max_tokens`, `messages`, and `system` only when given. Return the text.

Concepts: a **token** is roughly 4 characters. `max_tokens` caps the *output*. The **system prompt** sets behavior; the user message carries the task. The model id is a string; this lab uses `claude-opus-5-5`.

Try live: `python3 ask.py "Explain a gecko's tail autotomy in one sentence"`.

## Step 2 · Structured output  (15 min)

Models return prose unless you ask otherwise. You write:

- `parse_json_reply(text)`: accept bare JSON or JSON inside a ```json fence. Return a dict. Raise `ValueError` for anything else, including a JSON list.
- `ask_json(client, prompt, required_keys, retries=1)`: ask, parse, check keys. On failure, ask again with a stricter instruction appended. After `retries` extra attempts, raise `ValueError`.

Concept: the real API has a `output_config.format` option that guarantees JSON. You build the manual version first so you understand what it's protecting you from. Then read about structured outputs and note in `NOTES.md` when you'd use each.

## Step 3 · Errors and cost  (15 min)

You write:

- `estimate_cost(usage, model)`: dollars from `usage.input_tokens`, `usage.output_tokens` and the `PRICES` table. Prices are per million tokens.
- `with_retry(fn, attempts=3, base_delay=1.0, retry_on=None, sleep=time.sleep)`: call `fn()`. On a retryable exception, wait `base_delay * 2**attempt` and try again. Non-retryable exceptions propagate immediately. After `attempts` failures, re-raise the last one.

Concepts: 429 (rate limit), 500 and 529 (server) are retryable. 400 and 401 are your bug, never retry those. The SDK already retries for you (`max_retries`); you build it once to know what it does, then you use the SDK's.

Finish: run all tests, then ask Claude to review you against `RUBRIC.md` and write the result into `REVIEW.md`. Then `python3 coach.py done C1`.
