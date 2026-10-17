# C4 · Agent loop, then a framework

**Maps to:** "Designs and implements simple agent-based systems and integrates agentic frameworks with related technologies."
**You'll have at the end:** an agent that can list files, read them, and run tests inside a sandboxed folder, written twice: once by hand so you own the loop, once with the SDK's tool runner so you can compare.

Setup: `pip install -r requirements.txt`. Tests are offline. `sandbox/` is the only folder the agent may touch.

**What an agent is, in one sentence.** A loop: send the conversation to the model with a list of tools, and if it answers with a tool call, run the tool, append the result, and go again until it answers with text.

## Step 1 · Tools and a dispatcher  (15 min)

Read `agent.py`. `TOOLS` is already defined: three JSON schemas the model reads. You write:

- `safe_path(root, rel)`: resolve `rel` under `root`; raise `PermissionError` if it escapes (`..`, absolute paths, symlinks out).
- `execute_tool(name, inputs, root)`: dispatch to `list_dir`, `read_file`, `run_tests`. Unknown name: `ValueError`. Every path goes through `safe_path`.

`run_tests` runs `python3 -m pytest -q <path>` as a subprocess and returns the last 20 lines.

## Step 2 · The loop  (15 min)

You write `run_agent(client, task, root, max_iters=8, transcript=None)`:

1. `messages = [user: task]`.
2. Call `client.messages.create(model, max_tokens, system=SYSTEM, tools=TOOLS, messages)`.
3. Append the assistant's full `response.content` to `messages` (the whole block list, not just text).
4. If `stop_reason` is not `"tool_use"`: return the text.
5. For every `tool_use` block, run `execute_tool`. Collect one `tool_result` per block, with `tool_use_id` matching the block's `id`. All results go back in **one** user message.
6. Loop. After `max_iters` rounds, raise `RuntimeError`.

## Step 3 · Safety and a transcript  (15 min)

- A tool that raises returns a `tool_result` with `is_error: True` and the error text. The agent keeps going; the model decides what to do with the error.
- Append one dict per tool call to `transcript`: `{"iteration", "tool", "input", "ok", "output"}` (output truncated to 200 chars for the log only, never for the model).
- `save_transcript(transcript, path)`: one JSON object per line.

Try it live: `python3 agent.py "Read notes.txt and tell me the thermostat setting"`.

## Step 4 · The same agent with the tool runner  (15 min)

Read `agent_runner.py`. It's complete. It uses `@beta_tool` and `client.beta.messages.tool_runner`, so the loop you wrote in step 2 is inside the SDK. Run both versions on the same task live. Fill in `COMPARE.md`: what the runner does for you, what you lose, when you'd pick each. Then `python3 coach.py done C4` after the rubric review.
