import pytest
from types import SimpleNamespace

import ask
from fake_llm import FakeClient


# ---------------------------------------------------------------- step 1

def test_step1_build_messages_is_one_user_turn():
    assert ask.build_messages("hi") == [{"role": "user", "content": "hi"}]


def test_step1_text_of_joins_only_text_blocks():
    r = SimpleNamespace(content=[SimpleNamespace(type="thinking", thinking="..."),
                                 SimpleNamespace(type="text", text="a"),
                                 SimpleNamespace(type="text", text="b")])
    assert ask.text_of(r) == "ab"


def test_step1_ask_sends_model_max_tokens_messages():
    client = FakeClient(["pong"])
    assert ask.ask(client, "ping") == "pong"
    call = client.calls[0]
    assert call["model"] == ask.MODEL
    assert call["max_tokens"] > 0
    assert call["messages"] == [{"role": "user", "content": "ping"}]
    assert "system" not in call


def test_step1_ask_passes_system_when_given():
    client = FakeClient(["ok"])
    ask.ask(client, "ping", system="Be terse.")
    assert client.calls[0]["system"] == "Be terse."
    blocks = [{"type": "text", "text": "Be terse.", "cache_control": {"type": "ephemeral"}}]
    ask.ask(client, "ping", system=blocks)                 # C2 sends a list of blocks
    assert client.calls[1]["system"] == blocks


# ---------------------------------------------------------------- step 2

def test_step2_parse_bare_and_fenced_json():
    assert ask.parse_json_reply('{"a": 1}') == {"a": 1}
    assert ask.parse_json_reply('Sure!\n```json\n{"a": 1}\n```\nDone.') == {"a": 1}
    assert ask.parse_json_reply('```\n{"a": [1, 2]}\n```') == {"a": [1, 2]}


def test_step2_parse_rejects_prose_and_lists():
    with pytest.raises(ValueError):
        ask.parse_json_reply("I'd be happy to help!")
    with pytest.raises(ValueError):
        ask.parse_json_reply("[1, 2, 3]")


def test_step2_ask_json_retries_with_stricter_prompt_then_succeeds():
    client = FakeClient(["Here you go: not json", '{"facts": ["x"], "source": "y"}'])
    data = ask.ask_json(client, "facts please", ["facts", "source"], retries=1)
    assert data["facts"] == ["x"]
    assert len(client.calls) == 2
    second_prompt = client.calls[1]["messages"][0]["content"]
    assert "facts" in second_prompt and "source" in second_prompt
    assert second_prompt != "facts please"


def test_step2_ask_json_checks_required_keys_and_gives_up():
    client = FakeClient(['{"facts": []}', '{"facts": []}'])
    with pytest.raises(ValueError):
        ask.ask_json(client, "p", ["facts", "source"], retries=1)
    assert len(client.calls) == 2


# ---------------------------------------------------------------- step 3

def test_step3_estimate_cost_uses_price_table():
    usage = SimpleNamespace(input_tokens=1_000_000, output_tokens=0)
    assert ask.estimate_cost(usage, "claude-opus-5-5") == pytest.approx(4.00)
    usage = SimpleNamespace(input_tokens=2000, output_tokens=500)
    price_in, price_out = ask.PRICES["claude-haiku-5-5"]
    assert ask.estimate_cost(usage, "claude-haiku-5-5") == pytest.approx((2000 * price_in + 500 * price_out) / 1e6)


def test_step3_estimate_cost_prices_cache_writes_and_reads():
    write = SimpleNamespace(input_tokens=0, output_tokens=0,
                            cache_creation_input_tokens=1_000_000, cache_read_input_tokens=0)
    read = SimpleNamespace(input_tokens=0, output_tokens=0,
                           cache_creation_input_tokens=0, cache_read_input_tokens=1_000_000)
    # the published price list: Opus 5.5 is $4 input, $5 cache write, $0.20 cache read
    assert ask.estimate_cost(write, "claude-opus-5-5") == pytest.approx(5.00)
    assert ask.estimate_cost(read, "claude-opus-5-5") == pytest.approx(0.20)
    # a model with no special read rate gets the standard 0.1x
    assert ask.estimate_cost(read, "claude-haiku-5-5") == pytest.approx(0.10 * 0.1)


def test_step3_estimate_cost_adds_all_four_kinds_and_tolerates_missing_fields():
    usage = SimpleNamespace(input_tokens=100, output_tokens=50,
                            cache_creation_input_tokens=2000, cache_read_input_tokens=8000)
    p_in, p_out = ask.PRICES["claude-haiku-5-5"]
    expected = (100 * p_in + 2000 * p_in * 1.25 + 8000 * p_in * 0.1 + 50 * p_out) / 1e6
    assert ask.estimate_cost(usage, "claude-haiku-5-5") == pytest.approx(expected)
    partial = SimpleNamespace(input_tokens=100, output_tokens=50, cache_read_input_tokens=None)
    assert ask.estimate_cost(partial, "claude-haiku-5-5") == pytest.approx((100 * p_in + 50 * p_out) / 1e6)


class Transient(Exception):
    pass


class Fatal(Exception):
    pass


def test_step3_with_retry_backs_off_then_succeeds():
    calls, naps = [], []
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise Transient("try again")
        return "ok"
    out = ask.with_retry(flaky, attempts=3, base_delay=1.0, retry_on=(Transient,), sleep=naps.append)
    assert out == "ok"
    assert naps == [1.0, 2.0]


def test_step3_with_retry_gives_up_and_does_not_retry_fatal():
    def always():
        raise Transient("nope")
    with pytest.raises(Transient):
        ask.with_retry(always, attempts=2, base_delay=0, retry_on=(Transient,), sleep=lambda s: None)
    count = []
    def fatal():
        count.append(1)
        raise Fatal("your bug")
    with pytest.raises(Fatal):
        ask.with_retry(fatal, attempts=3, retry_on=(Transient,), sleep=lambda s: None)
    assert len(count) == 1
