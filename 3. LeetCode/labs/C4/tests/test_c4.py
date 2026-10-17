import json
import os
from pathlib import Path

import pytest

import agent
from fake_llm import FakeClient

SANDBOX = Path(__file__).resolve().parents[1] / "sandbox"


# ---------------------------------------------------------------- step 1

def test_step1_safe_path_allows_inside_and_blocks_escapes(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    assert agent.safe_path(tmp_path, "a.txt") == (tmp_path / "a.txt").resolve()
    assert agent.safe_path(tmp_path, ".") == tmp_path.resolve()
    for bad in ("../secret", "/etc/passwd", "sub/../../x"):
        with pytest.raises(PermissionError):
            agent.safe_path(tmp_path, bad)


def test_step1_safe_path_blocks_symlink_out(tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.txt"
    outside.write_text("secret")
    os.symlink(outside, tmp_path / "link.txt")
    with pytest.raises(PermissionError):
        agent.safe_path(tmp_path, "link.txt")


def test_step1_execute_tool_list_read_and_unknown():
    listing = agent.execute_tool("list_dir", {"path": "."}, SANDBOX)
    assert "notes.txt" in listing and "test_sample.py" in listing
    assert "88 F" in agent.execute_tool("read_file", {"path": "notes.txt"}, SANDBOX)
    with pytest.raises(ValueError):
        agent.execute_tool("delete_everything", {}, SANDBOX)
    with pytest.raises(PermissionError):
        agent.execute_tool("read_file", {"path": "../agent.py"}, SANDBOX)


def test_step1_execute_tool_runs_tests():
    out = agent.execute_tool("run_tests", {"path": "test_sample.py"}, SANDBOX)
    assert "1 passed" in out


# ---------------------------------------------------------------- step 2

def test_step2_loop_runs_tools_and_returns_final_text():
    client = FakeClient([
        {"tool_use": {"name": "list_dir", "input": {"path": "."}}},
        {"tool_use": {"name": "read_file", "input": {"path": "notes.txt"}}},
        "It is set to 88 F.",
    ])
    out = agent.run_agent(client, "What is the thermostat set to?", root=SANDBOX)
    assert out == "It is set to 88 F."
    assert len(client.calls) == 3
    first = client.calls[0]
    assert first["tools"] == agent.TOOLS and first["system"] == agent.SYSTEM
    # second call carries the assistant turn and one user message holding the tool_result
    msgs = client.calls[1]["messages"]
    assert msgs[1]["role"] == "assistant"
    assert msgs[2]["role"] == "user"
    results = msgs[2]["content"]
    assert len(results) == 1 and results[0]["type"] == "tool_result"
    assert results[0]["tool_use_id"] == msgs[1]["content"][0].id
    assert "notes.txt" in results[0]["content"]
    # third call: the read_file result reached the model
    assert "88 F" in client.calls[2]["messages"][4]["content"][0]["content"]


def test_step2_parallel_tool_calls_come_back_in_one_message():
    from types import SimpleNamespace
    two = {"blocks": [
        SimpleNamespace(type="tool_use", id="toolu_a", name="list_dir", input={"path": "."}),
        SimpleNamespace(type="tool_use", id="toolu_b", name="read_file", input={"path": "notes.txt"}),
    ]}
    client = FakeClient([two, "done"])
    agent.run_agent(client, "look around", root=SANDBOX)
    results = client.calls[1]["messages"][2]["content"]
    assert [r["type"] for r in results] == ["tool_result", "tool_result"]
    assert {r["tool_use_id"] for r in results} == {"toolu_a", "toolu_b"}


def test_step2_max_iters_stops_a_runaway_loop():
    client = FakeClient(default={"tool_use": {"name": "list_dir", "input": {"path": "."}}})
    with pytest.raises(RuntimeError):
        agent.run_agent(client, "loop forever", root=SANDBOX, max_iters=3)
    assert len(client.calls) == 3


# ---------------------------------------------------------------- step 3

def test_step3_tool_error_is_reported_not_fatal():
    client = FakeClient([
        {"tool_use": {"name": "read_file", "input": {"path": "../../coach.py"}}},
        "I can't read outside the sandbox.",
    ])
    transcript = []
    out = agent.run_agent(client, "read the coach", root=SANDBOX, transcript=transcript)
    assert "can't" in out
    result = client.calls[1]["messages"][2]["content"][0]
    assert result.get("is_error") is True
    assert "PermissionError" in result["content"]
    assert transcript[0]["ok"] is False and transcript[0]["tool"] == "read_file"


def test_step3_transcript_and_save(tmp_path):
    client = FakeClient([
        {"tool_use": {"name": "read_file", "input": {"path": "notes.txt"}}},
        "88 F",
    ])
    transcript = []
    agent.run_agent(client, "q", root=SANDBOX, transcript=transcript)
    assert transcript == [{"iteration": 1, "tool": "read_file", "input": {"path": "notes.txt"},
                           "ok": True, "output": transcript[0]["output"]}]
    assert len(transcript[0]["output"]) <= 200
    out = tmp_path / "t.jsonl"
    agent.save_transcript(transcript, out)
    assert json.loads(out.read_text().splitlines()[0])["tool"] == "read_file"


# ---------------------------------------------------------------- step 4

def test_step4_compare_md_is_written():
    text = (Path(__file__).resolve().parents[1] / "COMPARE.md").read_text()
    assert "_(you)_" not in text
    assert len(text) > 600
