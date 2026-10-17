# C3 · MCP server with a protected tool

**Maps to:** "Designs simple integrations between AI assistants and applications or APIs; understands authentication and authorization for tool calling."
**You'll have at the end:** an MCP server that exposes your own study coach as tools, one of which needs a token with the right scope. Claude Code can connect to it. This is the lab to talk about in an interview.

Setup: `pip install -r requirements.txt`. The container's `mcp` package is 2.x: the server class is `MCPServer` (it was `FastMCP` in 1.x; old tutorials will show that name). Tests are offline and call the server in-process.

**What MCP is, in three sentences.** Model Context Protocol is a standard way for an AI assistant (the client) to discover and call tools that some program (the server) exposes. The server declares each tool's name, description and input schema; the client lists them, the model picks one, the client calls it, the result goes back to the model. Transport is usually stdio (the client launches your script) or HTTP.

## Step 1 · One tool  (15 min)

Read `coach_server.py`. You write:

- `run_coach(*args)`: run `coach.py` with those arguments as a subprocess, from the coach's own folder, and return its stdout plus stderr as one string.
- the `coach_next` tool: no arguments, returns `run_coach("next")`.

The decorator `@server.tool()` turns a typed Python function into an MCP tool. The docstring becomes the tool description the model reads, so write it for the model.

Try it: `python3 coach_server.py` starts the server on stdio and waits. Ctrl-C. That's what a client would launch.

## Step 2 · Tools with arguments  (15 min)

You write `coach_start(item_id)` and `coach_check(item_id)`. Type hints become the input schema. Add a one-line docstring each that tells the model when to use it and what `item_id` looks like ("001", "two-sum", "A01").

## Step 3 · The protected tool  (15 min)

`coach_done` changes the learner's record, so it needs a token with the `write` scope. You write, in `auth.py`:

- `load_tokens(path)`: read a JSON file mapping token -> list of scopes. Ignore keys starting with `_`.
- `authorize(token, scope, tokens)`: `True` only if some token in the map matches **in constant time** (`hmac.compare_digest`) and has the scope. A missing or empty token is never authorized.

and in `coach_server.py` the `coach_done(item_id, rating, token)` tool, which returns `"denied: ..."` without touching the coach when `authorize` says no.

Concepts, for AUTH.md in step 4: **authentication** is proving who you are (the token). **Authorization** is what you're allowed to do (the scope). **Least privilege**: the read-only token exists so the model can plan without being able to write. Why constant-time compare: a normal `==` leaks how many leading bytes matched through timing.

## Step 4 · Connect it, write it up  (15 min)

1. Copy `tokens.example.json` to `tokens.json`, put real random tokens in it.
2. Register with Claude Code: `claude mcp add coach -- python3 "<absolute path>/coach_server.py"`. In a session, ask "what's my study plan today" and watch it call `coach_next`.
3. Fill in `AUTH.md`: every `_(you)_` placeholder, in your own words. Keep it to one page. This page is what you'd hand a teammate.

Then ask Claude to review you against `RUBRIC.md`, write `REVIEW.md`, and `python3 coach.py done C3`.
