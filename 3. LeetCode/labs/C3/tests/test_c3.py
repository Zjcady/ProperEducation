import asyncio
import json

import pytest
from starlette.testclient import TestClient

import auth
import coach_server


def call(name, args=None):
    """Call a tool in-process, the way a stdio client would: no HTTP, so no bearer token."""
    result = asyncio.run(coach_server.server.call_tool(name, args or {}))
    return "".join(getattr(c, "text", "") for c in result.content)


def description(tool):
    # The "TODO(you):" marker is the lab's; delete it when you're done, the model reads this text.
    return (tool.description or "").replace("TODO(you):", "").strip()


# ---------------------------------------------------------------- step 1

def test_step1_run_coach_returns_coach_output():
    out = coach_server.run_coach("list", "foundations")
    assert "A01" in out


def test_step1_coach_next_tool_is_registered_and_runs(monkeypatch):
    names = [t.name for t in asyncio.run(coach_server.server.list_tools())]
    assert "coach_next" in names
    monkeypatch.setattr(coach_server, "run_coach", lambda *a: f"ran {a}")
    assert call("coach_next") == "ran ('next',)"


# ---------------------------------------------------------------- step 2

def test_step2_start_and_check_take_an_item_id(monkeypatch):
    seen = []
    monkeypatch.setattr(coach_server, "run_coach", lambda *a: seen.append(a) or "ok")
    assert call("coach_start", {"item_id": "A01"}) == "ok"
    assert call("coach_check", {"item_id": "two-sum"}) == "ok"
    assert seen == [("start", "A01"), ("check", "two-sum")]


def test_step2_tools_have_descriptions_the_model_can_use(monkeypatch):
    monkeypatch.setattr(coach_server, "run_coach", lambda *a: "ok")
    tools = {t.name: t for t in asyncio.run(coach_server.server.list_tools())}
    for name in ("coach_start", "coach_check"):
        schema = getattr(tools[name], "input_schema", None) or getattr(tools[name], "inputSchema")
        assert "item_id" in schema["properties"]
        assert len(description(tools[name])) > 20, f"{name} needs a description the model can act on"
        assert call(name, {"item_id": "001"}) == "ok"


# ---------------------------------------------------------------- step 3

TOKENS = {"_note": "x", "reader": ["read"], "writer": ["read", "write"]}


@pytest.fixture
def tokens_file(tmp_path, monkeypatch):
    f = tmp_path / "tokens.json"
    f.write_text(json.dumps(TOKENS))
    monkeypatch.setattr(coach_server.verifier, "path", f)
    return f


def verify(verifier, token):
    return asyncio.run(verifier.verify_token(token))


def test_step3_load_tokens_skips_meta_keys_and_missing_file(tmp_path):
    f = tmp_path / "t.json"
    f.write_text(json.dumps({"_note": "x", "abc": ["read"], "xyz": ["read", "write"]}))
    assert auth.load_tokens(f) == {"abc": ["read"], "xyz": ["read", "write"]}
    assert auth.load_tokens(tmp_path / "missing.json") == {}


def test_step3_verifier_maps_tokens_to_scopes(tmp_path):
    f = tmp_path / "tokens.json"
    f.write_text(json.dumps(TOKENS))
    v = auth.CoachTokenVerifier(f)
    writer = verify(v, "writer")
    assert writer is not None and sorted(writer.scopes) == ["read", "write"]
    assert writer.token == "writer"
    assert verify(v, "reader").scopes == ["read"]
    assert verify(v, "bogus") is None
    assert verify(v, "") is None
    assert verify(v, "_note") is None, "meta keys are not tokens"
    assert verify(auth.CoachTokenVerifier(tmp_path / "missing.json"), "writer") is None


def test_step3_verifier_uses_constant_time_compare(tmp_path, monkeypatch):
    import hmac
    f = tmp_path / "tokens.json"
    f.write_text(json.dumps(TOKENS))
    used = []
    real = hmac.compare_digest
    monkeypatch.setattr(hmac, "compare_digest", lambda a, b: used.append(1) or real(a, b))
    assert verify(auth.CoachTokenVerifier(f), "reader") is not None
    assert used, "verify_token must compare through hmac.compare_digest"


def test_step3_on_stdio_coach_done_needs_COACH_WRITE(monkeypatch):
    tools = {t.name: t for t in asyncio.run(coach_server.server.list_tools())}
    schema = getattr(tools["coach_done"], "input_schema", None) or getattr(tools["coach_done"], "inputSchema")
    assert "token" not in schema["properties"], "the token rides on the transport, never in tool arguments"
    ran = []
    monkeypatch.setattr(coach_server, "run_coach", lambda *a: ran.append(a) or "recorded")
    monkeypatch.delenv("COACH_WRITE", raising=False)
    assert call("coach_done", {"item_id": "001", "rating": 2}).startswith("denied")
    assert ran == []
    monkeypatch.setenv("COACH_WRITE", "1")
    assert call("coach_done", {"item_id": "001", "rating": 2}) == "recorded"
    assert call("coach_done", {"item_id": "A01"}) == "recorded"
    assert ran == [("done", "001", "2"), ("done", "A01")]


# The HTTP tests talk to the real Starlette app the SDK builds, in-process (no port, no network).

ACCEPT = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}


def rpc(client, method, params, token=None, session=None, id=1):
    headers = dict(ACCEPT)
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    if session:
        headers["Mcp-Session-Id"] = session
    body = {"jsonrpc": "2.0", "method": method, "params": params}
    if id is not None:
        body["id"] = id
    return client.post("/mcp", headers=headers, json=body)


def result_of(response):
    """The JSON-RPC result from a response that may be plain JSON or one SSE event."""
    assert response.status_code == 200, response.text
    if response.headers["content-type"].startswith("text/event-stream"):
        data = [line[5:] for line in response.text.splitlines() if line.startswith("data:")]
        message = json.loads(data[-1])
    else:
        message = response.json()
    assert "result" in message, message
    return message["result"]


def connect(client, token):
    """MCP handshake: initialize, then the initialized notification. Returns the session id."""
    r = rpc(client, "initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                                   "clientInfo": {"name": "pytest", "version": "0"}}, token=token)
    result_of(r)
    session = r.headers.get("mcp-session-id")
    assert rpc(client, "notifications/initialized", {}, token=token, session=session, id=None).status_code == 202
    return session


def call_http(client, token, name, args):
    session = connect(client, token)
    result = result_of(rpc(client, "tools/call", {"name": name, "arguments": args}, token=token, session=session, id=2))
    return "".join(c.get("text", "") for c in result["content"])


@pytest.fixture
def http(tokens_file):
    with TestClient(coach_server.server.streamable_http_app(), base_url=coach_server.SERVER_URL) as client:
        yield client


def test_step3_http_needs_a_bearer_token(http):
    no_header = rpc(http, "tools/list", {})
    assert no_header.status_code == 401
    assert no_header.headers["www-authenticate"].startswith("Bearer")
    assert rpc(http, "tools/list", {}, token="bogus").status_code == 401
    session = connect(http, "reader")
    tools = result_of(rpc(http, "tools/list", {}, token="reader", session=session, id=2))["tools"]
    assert "coach_done" in [t["name"] for t in tools]


def test_step3_http_coach_done_checks_the_write_scope(http, monkeypatch):
    ran = []
    monkeypatch.setattr(coach_server, "run_coach", lambda *a: ran.append(a) or "recorded")
    monkeypatch.setenv("COACH_WRITE", "1")   # the environment must not grant anything over HTTP
    assert call_http(http, "reader", "coach_next", {}) == "recorded"
    assert call_http(http, "reader", "coach_done", {"item_id": "001", "rating": 2}).startswith("denied")
    assert ran == [("next",)]
    assert call_http(http, "writer", "coach_done", {"item_id": "001", "rating": 2}) == "recorded"
    assert ran == [("next",), ("done", "001", "2")]


# ---------------------------------------------------------------- step 4

def test_step4_auth_md_is_written():
    text = (coach_server.HERE / "AUTH.md").read_text()
    assert "_(you)_" not in text, "fill in every placeholder in AUTH.md"
    for heading in ("Authentication vs authorization", "API keys", "OAuth", "Scopes", "Least privilege",
                    "constant-time", "transport"):
        assert heading.lower() in text.lower()
    assert len(text) > 1200
