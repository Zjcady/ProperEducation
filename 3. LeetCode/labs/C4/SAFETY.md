# C4 safety: what my agent does about OWASP LLM01 and LLM06

Short answers are fine. One or two sentences per box. Write it from what you saw running
`python3 agent.py "Read VENDOR_README.txt and summarize it"`, not from memory of the docs.

## LLM01 Prompt Injection: which C4 controls address it

For each control: does it stop the injection, limit the damage, or just let you see it afterwards?

| Control in C4 | What it does about prompt injection |
|---|---|
| `<untrusted_content_policy>` in `SYSTEM` | _(you)_ |
| Tool results as JSON with `source` and `path` (`wrap_tool_result`) | _(you)_ |
| `screen_tool_output` (Haiku, strict boolean schema, fails closed) | _(you)_ |
| `safe_path` on every tool | _(you)_ |

## LLM06 Excessive Agency: which C4 controls address it

OWASP names three root causes: excessive functionality, excessive permissions, excessive autonomy.
Say which one each control shrinks.

| Control in C4 | Which root cause it shrinks, and how |
|---|---|
| Only three tools, none of them writes or deletes | _(you)_ |
| `strict: True` schemas with `additionalProperties: false` | _(you)_ |
| `sandbox/` as the only folder (`safe_path`) | _(you)_ |
| `max_iters` | _(you)_ |
| `transcript.jsonl` | _(you)_ |

## What C4 still does not cover

Name at least two honest gaps. Starters, if you're stuck: what if the injection is aimed at the
screen itself? What can `run_tests` do if someone plants a test file in the sandbox?

_(you)_

## Why coach_done needs a human confirmation

One paragraph. In lab C3, `coach_done` writes to your progress record and needs the `write` scope.
Why isn't the scope enough once an agent that reads files can call it?
Use the words "autonomy" and "injection".

_(you)_
