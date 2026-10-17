# C9 · Evals and traces

**Maps to:** "Review test outcomes, conducts troubleshooting" in the posting, and the evals expectation that's now in nearly every GenAI job listing: you can say how you know your LLM feature works, and show the numbers.
**You'll have at the end:** a wrapper that writes one trace span per model call using the OpenTelemetry GenAI attribute names, a trace summary (tokens, p50/p95 latency, errors), an LLM-as-judge checked against human labels on 10 meeting summaries with 3 seeded failures, and pass@k vs pass^k over repeated trials.

C9 comes after C8 and reuses C6's shape: the cases are C6-style meeting summaries (`action_items` with owners, `decisions`). C6 built the thing; C9 is how you'd know it's any good.

Setup: `pip install -r requirements.txt`. Stdlib plus pytest, no OpenTelemetry package: you write spans as JSON lines yourself, so you see exactly what a tracing library would send. Tests are offline. All your code goes in `evals.py`.

**Words you'll use** (from Anthropic's [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)):
- **task**: one test with defined inputs and success criteria. Here, one meeting summary.
- **trial**: one attempt at a task. Outputs vary between runs, so you run several.
- **grader**: the logic that scores a trial. Here, an LLM judge, which the article says must be "closely calibrated with human experts".
- **transcript / trace**: the full record of a trial. The article: "You won't know if your graders are working well unless you read the transcripts and grades from many trials."

## Step 1 · Traces  (15 min)

A **span** is one timed operation with a name and attributes. The names come from the [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/anthropic.md) (Anthropic inference spans; status: Development). Use them exactly, so any tracing tool would understand your file:

| key | value |
|---|---|
| span name | `"{gen_ai.operation.name} {gen_ai.request.model}"`, so `"chat claude-opus-5-5"` |
| `gen_ai.operation.name` | `"chat"` |
| `gen_ai.provider.name` | `"anthropic"` |
| `gen_ai.request.model` | the `model` you sent |
| `gen_ai.response.model` | `response.model` |
| `gen_ai.usage.input_tokens` | `input_tokens` **plus** cache reads and cache writes (see below) |
| `gen_ai.usage.output_tokens` | `usage.output_tokens` |
| `gen_ai.response.finish_reasons` | a list: `[response.stop_reason]` |
| `error.type` | only on failure: the exception class name, e.g. `"TimeoutError"` |

The span line itself: `{"name", "kind": "CLIENT", "start", "end", "duration_s", "status": "OK" or "ERROR", "attributes": {...}}`.

You write, in `evals.py`:

- `TracedClient.create(**kwargs)`: `__init__` is written; it sets `self.messages = self` so `TracedClient(client, path).messages.create(...)` is a drop-in for the real client. Time the call with `self.clock`, append one span line, return the response. If the call raises: write the span with `"status": "ERROR"` and `error.type`, then re-raise. (`try` / `except` / `finally` does this neatly.)
- `percentile(values, p)`: nearest-rank. Sort, take the item at 1-based rank `ceil(p/100 * n)`. `None` if empty.
- `summarize_traces(path)`: `{"count", "errors", "input_tokens", "output_tokens", "total_tokens", "p50_s", "p95_s"}`.

Cache tokens: Anthropic's `input_tokens` doesn't count cached tokens, so the convention says to add `cache_read_input_tokens` and the cache-write count. The convention page calls that one `cache_write_input_tokens`; the Anthropic SDK's usage object calls it `cache_creation_input_tokens`. Read it with `getattr(usage, name, 0) or 0`, because older responses (and the fake) don't have the field and the real SDK can send `None`.

Why p95 and not the average: one 30-second timeout hides inside a mean. p95 is "how slow is it for the unlucky 1 in 20".

## Step 2 · An LLM-as-judge with seeded failures  (15 min)

Open `data/eval_cases.json`. Ten C6-style cases: a transcript, a `candidate` summary, a human `label` (`"pass"` or `"fail"`). Three candidates have a **seeded failure**, a bug planted on purpose so you know the right answer: a wrong owner, a missing decision, a hallucinated action item. Read those three first.

You write:

- `judge(client, case)`: one call to `claude-opus-5-5` with `JUDGE_RUBRIC` (written for you), the transcript and the candidate as JSON. Pull the JSON object out of the reply text (models like to add prose or ``` fences; find the first `{` and last `}`). Return `{"pass": bool, "reason": str}`; `ValueError` on anything else. Don't put the `label` or `seeded_failure` in the prompt; that's the answer key.
- `agreement(verdicts, labels)`: `{"accuracy", "disagreements": [indices]}`.

The test that matters: a judge that says "pass" to everything scores **0.7**. That's the floor. 70% sounds fine and it catches nothing. An eval is only worth something if it fails the three seeded cases.

## Step 3 · Consistency  (15 min)

You write:

- `pass_at_k(results)`: fraction of tasks where **at least one** of k trials passed.
- `pass_hat_k(results)`: pass^k, fraction of tasks where **all** k trials passed.
- `run_trials(fn, tasks, k, seed=0)`: `fn(task, rng)` k times per task, one `random.Random(seed)` shared across all calls, a trial that raises counts as a fail. The seed is what makes the test deterministic.

`results` is `{task_id: [True, False, True]}`. That task passes pass@3 and fails pass^3.

**Why pass^k is the one for an agent you'd deploy.** pass@k answers "can it ever do this?", which is right when a human picks the best of several tries (coding suggestions). pass^k answers "does it do this every time?", which is what a user, or a drone operator, experiences. The article says pass^k "matters most for customer-facing agents". It also falls fast: a task that passes 90% of the time has pass^3 of 0.9³ ≈ 73%. Run `python3 evals.py --fake`: the fake judge agrees with every human label on the first run (100%) and still only gets pass^3 = 60%. One run told you nothing about consistency.

(pass@k here is the empirical "did any of my k trials pass". With more than k trials per task you'd use an unbiased estimator; not needed for this lab.)

Then run it live: `python3 evals.py` (40 calls to `claude-opus-5-5`, a few cents). Open `out/traces.jsonl` and read it. For every disagreement, read the judge's `reason` next to the transcript and decide: is the judge wrong, or is the human label wrong? Write it in `NOTES.md`. Then the rubric review and `python3 coach.py done C9`.
