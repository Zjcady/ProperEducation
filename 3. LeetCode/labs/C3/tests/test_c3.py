import asyncio
import json

import pytest

import auth
import coach_server


def call(name, args=None):
    result = asyncio.run(coach_server.server.call_tool(name, args or {}))
    return "".join(getattr(c, "text", "") for c in result.content)


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


def test_step2_tools_have_descriptions_the_model_can_use():
    tools = {t.name: t for t in asyncio.run(coach_server.server.list_tools())}
    for name in ("coach_start", "coach_check"):
        schema = getattr(tools[name], "input_schema", None) or getattr(tools[name], "inputSchema")
        assert "item_id" in schema["properties"]
        assert tools[name].description and "TODO" not in tools[name].description


# ---------------------------------------------------------------- step 3

def test_step3_load_tokens_skips_meta_keys_and_missing_file(tmp_path):
    f = tmp_path / "t.json"
    f.write_text(json.dumps({"_note": "x", "abc": ["read"], "xyz": ["read", "write"]}))
    assert auth.load_tokens(f) == {"abc": ["read"], "xyz": ["read", "write"]}
    assert auth.load_tokens(tmp_path / "missing.json") == {}


def test_step3_authorize_checks_token_and_scope():
    tokens = {"abc": ["read"], "xyz": ["read", "write"]}
    assert auth.authorize("xyz", "write", tokens)
    assert auth.authorize("abc", "read", tokens)
    assert not auth.authorize("abc", "write", tokens)
    assert not auth.authorize("nope", "read", tokens)
    assert not auth.authorize("", "read", tokens)
    assert not auth.authorize(None, "read", tokens)


def test_step3_authorize_uses_constant_time_compare(monkeypatch):
    import hmac
    used = []
    real = hmac.compare_digest
    monkeypatch.setattr(hmac, "compare_digest", lambda a, b: used.append(1) or real(a, b))
    auth.authorize("abc", "read", {"abc": ["read"]})
    assert used, "authorize must go through hmac.compare_digest"


def test_step3_coach_done_denied_without_write_scope(tmp_path, monkeypatch):
    f = tmp_path / "tokens.json"
    f.write_text(json.dumps({"reader": ["read"], "writer": ["read", "write"]}))
    monkeypatch.setattr(coach_server, "TOKENS_FILE", f)
    ran = []
    monkeypatch.setattr(coach_server, "run_coach", lambda *a: ran.append(a) or "recorded")
    assert call("coach_done", {"item_id": "001", "rating": 2, "token": "reader"}).startswith("denied")
    assert call("coach_done", {"item_id": "001", "rating": 2, "token": "bogus"}).startswith("denied")
    assert ran == []
    assert call("coach_done", {"item_id": "001", "rating": 2, "token": "writer"}) == "recorded"
    assert ran == [("done", "001", "2")]


# ---------------------------------------------------------------- step 4

def test_step4_auth_md_is_written():
    text = (coach_server.HERE / "AUTH.md").read_text()
    assert "_(you)_" not in text, "fill in every placeholder in AUTH.md"
    for heading in ("Authentication vs authorization", "API keys", "OAuth", "Scopes", "Least privilege", "constant-time"):
        assert heading.lower() in text.lower()
    assert len(text) > 1200
