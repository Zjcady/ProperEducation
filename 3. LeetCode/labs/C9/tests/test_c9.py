import json
import random
from types import SimpleNamespace

import pytest

import evals
from fake_llm import FakeClient


def fake_clock(*times):
    it = iter(times)
    return lambda: next(it)


def read_spans(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


# ---------------------------------------------------------------- step 1 · traces

def test_step1_one_call_writes_one_span(tmp_path):
    path = tmp_path / "traces.jsonl"
    tc = evals.TracedClient(FakeClient(["hello there"]), path, clock=fake_clock(100.0, 100.75))
    resp = tc.messages.create(model="claude-opus-5-5", max_tokens=50,
                              messages=[{"role": "user", "content": "hi"}])
    assert resp.content[0].text == "hello there"            # the response comes back unchanged
    [span] = read_spans(path)
    assert span["name"] == "chat claude-opus-5-5"
    assert span["start"] == 100.0 and span["end"] == 100.75
    assert span["duration_s"] == pytest.approx(0.75)
    assert span["status"] == "OK"
    a = span["attributes"]
    assert a["gen_ai.operation.name"] == "chat"
    assert a["gen_ai.provider.name"] == "anthropic"
    assert a["gen_ai.request.model"] == "claude-opus-5-5"
    assert a["gen_ai.usage.input_tokens"] == resp.usage.input_tokens
    assert a["gen_ai.usage.output_tokens"] == resp.usage.output_tokens
    assert a["gen_ai.response.finish_reasons"] == ["end_turn"]
    assert "error.type" not in a


def test_step1_spans_append_one_line_per_call(tmp_path):
    path = tmp_path / "traces.jsonl"
    tc = evals.TracedClient(FakeClient(["a", {"tool_use": {"name": "f"}}]), path,
                            clock=fake_clock(1.0, 2.0, 3.0, 3.5))
    tc.messages.create(model="m1", max_tokens=10, messages=[{"role": "user", "content": "x"}])
    tc.messages.create(model="m2", max_tokens=10, messages=[{"role": "user", "content": "y"}])
    spans = read_spans(path)
    assert [s["name"] for s in spans] == ["chat m1", "chat m2"]
    assert [s["duration_s"] for s in spans] == pytest.approx([1.0, 0.5])
    assert spans[1]["attributes"]["gen_ai.response.finish_reasons"] == ["tool_use"]


def test_step1_error_is_recorded_and_reraised(tmp_path):
    path = tmp_path / "traces.jsonl"
    tc = evals.TracedClient(FakeClient([{"raise": TimeoutError("slow")}]), path, clock=fake_clock(5.0, 35.0))
    with pytest.raises(TimeoutError):
        tc.messages.create(model="claude-opus-5-5", max_tokens=10, messages=[{"role": "user", "content": "x"}])
    [span] = read_spans(path)
    assert span["status"] == "ERROR"
    assert span["attributes"]["error.type"] == "TimeoutError"
    assert span["attributes"]["gen_ai.request.model"] == "claude-opus-5-5"
    assert span["duration_s"] == pytest.approx(30.0)


def test_step1_input_tokens_include_cache_reads_and_writes(tmp_path):
    def stub(usage):
        resp = SimpleNamespace(content=[SimpleNamespace(type="text", text="ok")], stop_reason="end_turn",
                               model="claude-opus-5-5", usage=usage)
        return SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: resp))
    path = tmp_path / "traces.jsonl"
    with_cache = SimpleNamespace(input_tokens=10, output_tokens=4,
                                 cache_read_input_tokens=100, cache_creation_input_tokens=20)
    nulls = SimpleNamespace(input_tokens=10, output_tokens=4,
                            cache_read_input_tokens=None, cache_creation_input_tokens=None)
    for usage in (with_cache, nulls):
        evals.TracedClient(stub(usage), path, clock=fake_clock(0.0, 1.0)).messages.create(
            model="claude-opus-5-5", max_tokens=10, messages=[])
    a, b = (s["attributes"] for s in read_spans(path))
    assert a["gen_ai.usage.input_tokens"] == 130
    assert b["gen_ai.usage.input_tokens"] == 10
    assert a["gen_ai.usage.output_tokens"] == b["gen_ai.usage.output_tokens"] == 4


def test_step1_percentile_nearest_rank():
    assert evals.percentile([], 50) is None
    assert evals.percentile([4.0, 0.2, 2.0, 0.5, 1.0], 50) == 1.0
    assert evals.percentile([4.0, 0.2, 2.0, 0.5, 1.0], 95) == 4.0
    twenty = [float(x) for x in range(20, 0, -1)]
    assert evals.percentile(twenty, 50) == 10.0
    assert evals.percentile(twenty, 95) == 19.0
    assert evals.percentile([7.0], 95) == 7.0


def test_step1_summarize_traces(tmp_path):
    def span(d, status="OK", inp=None, out=None):
        a = {"gen_ai.operation.name": "chat", "gen_ai.request.model": "m"}
        if inp is not None:
            a["gen_ai.usage.input_tokens"], a["gen_ai.usage.output_tokens"] = inp, out
        else:
            a["error.type"] = "TimeoutError"
        return {"name": "chat m", "start": 0, "end": d, "duration_s": d, "status": status, "attributes": a}
    path = tmp_path / "t.jsonl"
    spans = [span(0.5, inp=100, out=20), span(1.0, inp=50, out=5), span(4.0, "ERROR"),
             span(2.0, inp=10, out=10), span(0.2, inp=40, out=15)]
    path.write_text("".join(json.dumps(s) + "\n" for s in spans))
    assert evals.summarize_traces(path) == {"count": 5, "errors": 1, "input_tokens": 200, "output_tokens": 50,
                                            "total_tokens": 250, "p50_s": 1.0, "p95_s": 4.0}
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")
    assert evals.summarize_traces(empty)["count"] == 0
    assert evals.summarize_traces(empty)["p50_s"] is None


# ---------------------------------------------------------------- step 2 · LLM-as-judge

def test_step2_judge_prompt_has_rubric_transcript_and_no_answer_key():
    cases = evals.load_cases()
    seeded = cases[2]
    client = FakeClient([json.dumps({"pass": False, "reason": "wrong owner"})])
    assert evals.judge(client, seeded) == {"pass": False, "reason": "wrong owner"}
    call = client.calls[0]
    assert call["model"] == "claude-opus-5-5"
    prompt = call["messages"][0]["content"]
    assert evals.JUDGE_RUBRIC in prompt
    assert seeded["transcript"] in prompt
    assert seeded["candidate"]["action_items"][0]["task"] in prompt
    assert seeded["candidate"]["decisions"][0] in prompt
    assert seeded["seeded_failure"] not in prompt      # never hand the judge the answer key
    assert '"label"' not in prompt


def test_step2_judge_parses_json_wrapped_in_prose_or_fences():
    case = evals.load_cases()[0]
    wrapped = 'Here is my verdict:\n```json\n{"pass": true, "reason": "ok"}\n```\nDone.'
    assert evals.judge(FakeClient([wrapped]), case) == {"pass": True, "reason": "ok"}


def test_step2_judge_rejects_bad_replies():
    case = evals.load_cases()[0]
    for bad in ["I think it passes.", '{"pass": "yes", "reason": "ok"}', '{"pass": true}', '{"pass": true, oops}']:
        with pytest.raises(ValueError):
            evals.judge(FakeClient([bad]), case)


def test_step2_agreement_math():
    verdicts = [{"pass": True}, {"pass": False}, {"pass": True}, {"pass": True}]
    out = evals.agreement(verdicts, ["pass", "fail", "fail", "pass"])
    assert out["accuracy"] == pytest.approx(0.75)
    assert out["disagreements"] == [2]
    out = evals.agreement([{"pass": False}, {"pass": True}], ["pass", "fail"])
    assert out == {"accuracy": 0.0, "disagreements": [0, 1]}
    with pytest.raises(ValueError):
        evals.agreement([], [])
    with pytest.raises(ValueError):
        evals.agreement([{"pass": True}], ["pass", "fail"])


def test_step2_always_pass_judge_scores_exactly_point_seven():
    cases = evals.load_cases()
    assert len(cases) == 10
    client = FakeClient(default=json.dumps({"pass": True, "reason": "looks fine"}))
    verdicts = [evals.judge(client, c) for c in cases]
    out = evals.agreement(verdicts, [c["label"] for c in cases])
    assert out["accuracy"] == pytest.approx(0.7)
    seeded = [i for i, c in enumerate(cases) if c["seeded_failure"]]
    assert out["disagreements"] == seeded == [2, 5, 8]


# ---------------------------------------------------------------- step 3 · consistency

def test_step3_two_of_three_passes_at_k_but_not_hat_k():
    flaky = {"t": [True, False, True]}
    assert evals.pass_at_k(flaky) == 1.0
    assert evals.pass_hat_k(flaky) == 0.0


def test_step3_pass_at_k_and_hat_k_hand_computed():
    results = {"always": [True, True, True], "flaky": [True, False, True],
               "lucky": [False, False, True], "never": [False, False, False]}
    assert evals.pass_at_k(results) == pytest.approx(3 / 4)
    assert evals.pass_hat_k(results) == pytest.approx(1 / 4)
    for f in (evals.pass_at_k, evals.pass_hat_k):
        with pytest.raises(ValueError):
            f({})
        with pytest.raises(ValueError):
            f({"t": []})


def test_step3_run_trials_shape_order_and_failures():
    calls = []

    def fn(task, rng):
        calls.append(task["id"])
        if task["id"] == "boom":
            raise RuntimeError("tool crashed")
        return task["ok"]
    tasks = [{"id": "a", "ok": True}, {"id": "boom"}, {"id": "c", "ok": False}]
    out = evals.run_trials(fn, tasks, k=3)
    assert out == {"a": [True] * 3, "boom": [False] * 3, "c": [False] * 3}
    assert calls == ["a"] * 3 + ["boom"] * 3 + ["c"] * 3


def test_step3_run_trials_is_deterministic_with_a_seed():
    tasks = [{"id": "easy", "p": 0.9}, {"id": "coin", "p": 0.5}, {"id": "hard", "p": 0.2}]
    fn = lambda task, rng: rng.random() < task["p"]  # noqa: E731
    out = evals.run_trials(fn, tasks, k=4, seed=7)
    rng = random.Random(7)                       # same seed, same order: tasks in turn, k trials each
    expected = {t["id"]: [rng.random() < t["p"] for _ in range(4)] for t in tasks}
    assert out == expected
    assert evals.run_trials(fn, tasks, k=4, seed=7) == out
    assert pass_values_differ_for_some_seed(fn, tasks)


def pass_values_differ_for_some_seed(fn, tasks):
    first = evals.run_trials(fn, tasks, k=4, seed=0)
    return any(evals.run_trials(fn, tasks, k=4, seed=s) != first for s in range(1, 6))
