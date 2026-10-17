# C3 · MCP server with a protected tool

**Maps to:** "Designs simple integrations between AI assistants and applications or APIs; understands authentication and authorization for tool calling."
**You'll have at the end:** an MCP server that exposes your own study coach as tools. Over HTTP it checks a bearer token on every request, the way the MCP spec says a server should, and one tool needs the `write` scope. Claude Code can connect to it. This is the lab to talk about in an interview.

Setup: `pip install -r requirements.txt`. The container's `mcp` package is 2.x: the server class is `MCPServer` (it was `FastMCP` in 1.x; old tutorials will show that name). Tests are offline: they call the server in-process, and the HTTP tests talk to the SDK's web app without opening a port.

**What MCP is, in three sentences.** Model Context Protocol is a standard way for an AI assistant (the client) to discover and call tools that some program (the server) exposes. The server declares each tool's name, description and input schema; the client lists them, the model picks one, the client calls it, the result goes back to the model. Transport is usually stdio (the client launches your script) or HTTP (your server is already running and the client connects to a URL).

## Step 1 · One tool  (15 min)

Read `coach_server.py` down to the step 1 line. Skip the `auth=` part for now; that's step 3. You write:

- `run_coach(*args)`: run `coach.py` with those arguments as a subprocess, from the coach's own folder, and return its stdout plus stderr as one string.
- the `coach_next` tool: no arguments, returns `run_coach("next")`.

The decorator `@server.tool()` turns a typed Python function into an MCP tool. The docstring becomes the tool description the model reads, so write it for the model, and delete the `TODO(you): ` prefix when you're done.

Try it: `python3 coach_server.py` starts the server on stdio and waits. Ctrl-C. That's what a client would launch.

## Step 2 · Tools with arguments  (15 min)

You write `coach_start(item_id)` and `coach_check(item_id)`. Type hints become the input schema. Each docstring is one line that tells the model when to use it and what `item_id` looks like ("001", "two-sum", "A01").

## Step 3 · The protected tool  (15 min)

`coach_done` changes the learner's record, so it needs the `write` scope. Notice what it does **not** take: a token. Over HTTP the token travels in a header, `Authorization: Bearer <token>`, on every request, and the SDK checks it before any tool runs. The model never sees it and can't pass a different one. That's what the MCP spec requires of an HTTP server: it is an OAuth 2.1 *resource server*.

Read the `server = MCPServer(...)` block. `token_verifier=` is the object the SDK asks "is this token real, and what may it do?". `required_scopes=["read"]` means every request needs at least `read`: no token, or an unknown one, gets **401**; a token without `read` gets **403**. You write:

- in `auth.py`, `load_tokens(path)`: read a JSON file mapping token -> list of scopes. Ignore keys starting with `_`. A missing file means no tokens.
- in `auth.py`, `CoachTokenVerifier.verify_token(token)`: look the token up in `load_tokens(self.path)` comparing **in constant time** (`hmac.compare_digest`), and return `AccessToken(token=token, client_id="learner", scopes=...)`, or `None` if nothing matches. An empty token is never valid. It's `async def` because real verifiers make a network call; yours doesn't need `await`.
- in `coach_server.py`, the body of `coach_done(item_id, rating)`: get the caller's scopes, and if `write` isn't one of them return `"denied: ..."` without touching the coach. Otherwise `run_coach("done", item_id, <rating as a string, if given>)`.
  - Over HTTP: `get_access_token()` (already imported) returns the verified `AccessToken` for the request in flight. Its `.scopes` is your list.
  - On stdio there's no request header, so `get_access_token()` returns `None`. The spec says a stdio server takes its credentials from the environment instead: use `stdio_scopes()`, which grants `write` only when the process was started with `COACH_WRITE=1`. So on stdio, auth as such doesn't apply; whoever launches the process decides, and by default `coach_done` is refused.

Run `python3 -m pytest tests -q -k step3`. The last two tests start the real HTTP app in-process and send requests with and without the header; read them, they're the protocol on the wire.

In production, `coach_done` is also the kind of tool that belongs behind a **human confirmation** ("Record A01 as done, rating 2? y/n") even when the token allows it: it writes the learner's record, and a scope says what the client *may* do, not what the learner *meant*. Claude Code's permission prompt plays that role here.

Concepts, for AUTH.md in step 4: **authentication** is proving who you are (the token). **Authorization** is what you're allowed to do (the scope). **Least privilege**: the read-only token exists so the model can plan without being able to write. Why constant-time compare: a normal `==` leaks how many leading bytes matched through timing. Why the header and not an argument: arguments are written by the model, they land in the transcript and logs, and a prompt injection could make the model send any token it has seen.

## Step 4 · Connect it, write it up  (15 min)

1. Copy `tokens.example.json` to `tokens.json` and put two real random tokens in it (one `["read"]`, one `["read", "write"]`). It's gitignored; keep it that way.
2. In a second terminal: `python3 coach_server.py --http`. It serves `http://127.0.0.1:8765/mcp` (change the port with `COACH_PORT`).
3. Register it with the **read-only** token:
   `claude mcp add --transport http coach http://127.0.0.1:8765/mcp --header "Authorization: Bearer <read token>"`
   Leave the default (local) scope. `--scope project` would write the header, token and all, into `.mcp.json`, which gets committed.
   In a session, `/mcp` shows `coach` connected; ask "what's my study plan today" and watch it call `coach_next`. Then ask it to mark something done: `coach_done` answers `denied`.
4. Swap in the write token: `claude mcp remove coach`, then the same `add` with the write token. Ask again: it's recorded. The coach has no undo, so use something you really finished (today's problem with your real rating), not a test item. You've now shown refusal and success with the same tool.
5. Fill in `AUTH.md`: every `_(you)_` placeholder, in your own words. Keep it to one page. This page is what you'd hand a teammate.

Then ask Claude to review you against `RUBRIC.md`, write `REVIEW.md`, and `python3 coach.py done C3`.

Prefer stdio? `claude mcp add coach -- python3 "<absolute path>/coach_server.py"` still works, read-only. Adding `--transport stdio --env COACH_WRITE=1` before `coach` gives it write, for everything that session's model does; that's the trade-off HTTP scopes exist to avoid.
