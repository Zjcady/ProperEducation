"""C9 · Evals and traces.

    python3 evals.py --fake     offline: a fake judge that is right most of the time
    python3 evals.py            live: claude-opus-5-5 judges data/eval_cases.json (40 calls)

Writes out/traces.jsonl (one span per model call) and prints judge agreement,
pass@3 / pass^3, and a trace summary.

Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "_common"))

OUT = HERE / "out"
CASES = HERE / "data" / "eval_cases.json"
MODEL = "claude-opus-5-5"


# ------------------------------------------------------------------ step 1 · traces

class TracedClient:
    """Drop-in wrapper: `TracedClient(client, path).messages.create(...)` works like the real client
    and appends one span (a JSON object on one line) to `path` per call.

    `clock` returns seconds as a float. Tests pass a fake one so timestamps are exact.
    """

    def __init__(self, client, path, clock=time.time):
        self.client = client
        self.path = Path(path)
        self.clock = clock
        self.messages = self          # so callers can write traced.messages.create(...)

    def create(self, **kwargs):
        """TODO(you): call the wrapped client's messages.create(**kwargs), append one span line, return the response.

        Span: {"name": "chat <model>", "kind": "CLIENT", "start", "end", "duration_s",
               "status": "OK" | "ERROR", "attributes": {gen_ai.* names from the README}}.
        Input tokens include cache reads and writes when the usage object has them.
        On an exception: status "ERROR", attributes["error.type"] = the exception class name, write the line, re-raise.
        """
        raise NotImplementedError


def percentile(values: list[float], p: float) -> float | None:
    """TODO(you): nearest-rank percentile: sort, take the value at rank ceil(p/100 * n) (1-based). None if empty."""
    raise NotImplementedError


def summarize_traces(path) -> dict:
    """TODO(you): read the span lines and return
    {"count", "errors", "input_tokens", "output_tokens", "total_tokens", "p50_s", "p95_s"}.

    Latency percentiles use every span's duration_s, errors included. A missing token attribute counts as 0.
    """
    raise NotImplementedError


# ------------------------------------------------------------------ step 2 · LLM-as-judge

JUDGE_RUBRIC = """You are grading a meeting summary against the meeting transcript.
The summary FAILS if any one of these is true:
1. An action item has the wrong owner (the person who said they'd do it is not the owner listed).
2. A decision stated in the transcript is missing from the decisions list.
3. An action item or decision appears that nobody said in the transcript (hallucinated).
Otherwise it PASSES. Wording may differ from the transcript; meaning may not.
Answer with only a JSON object: {"pass": true or false, "reason": "<one sentence naming the problem, or 'ok'>"}"""


def load_cases(path=CASES) -> list[dict]:
    return json.loads(Path(path).read_text())


def judge(client, case: dict) -> dict:
    """TODO(you): ask MODEL for a verdict on one case; return {"pass": bool, "reason": str}.

    The prompt holds JUDGE_RUBRIC, the transcript and the candidate summary (as JSON), and nothing else
    from the case: the human label and the seeded_failure note are the answer key.
    Parse the JSON object out of the text block (the model may wrap it in prose or ``` fences).
    ValueError if there is no JSON object, or "pass" is not a bool, or "reason" is not a str.
    """
    raise NotImplementedError


def agreement(verdicts: list[dict], labels: list[str]) -> dict:
    """TODO(you): compare judge verdicts with human labels ("pass" / "fail").

    Return {"accuracy": fraction that agree, "disagreements": [indices where they don't]}.
    ValueError if the lists are empty or different lengths.
    """
    raise NotImplementedError


# ------------------------------------------------------------------ step 3 · consistency

def pass_at_k(results: dict[str, list[bool]]) -> float:
    """TODO(you): fraction of tasks where AT LEAST ONE of the k trials passed. ValueError if empty or a task has no trials."""
    raise NotImplementedError


def pass_hat_k(results: dict[str, list[bool]]) -> float:
    """TODO(you): pass^k: fraction of tasks where ALL k trials passed. ValueError if empty or a task has no trials."""
    raise NotImplementedError


def run_trials(fn, tasks: list[dict], k: int, seed: int = 0) -> dict[str, list[bool]]:
    """TODO(you): run fn(task, rng) k times per task; return {task["id"]: [bool, ...k]}.

    One random.Random(seed) shared by every call, tasks in order, all k trials of a task before the next task.
    A trial that raises counts as a failed trial (False); the run keeps going.
    """
    raise NotImplementedError


# ------------------------------------------------------------------ the CLI (written for you)

K = 3


def fake_judge_client(cases: list[dict], seed: int = 0):
    """An offline client that answers like a judge that's right about 90% of the time."""
    from fake_llm import FakeClient
    rng = random.Random(seed)

    def reply(kwargs):
        prompt = kwargs["messages"][0]["content"]
        case = next(c for c in cases if c["transcript"] in prompt)
        truth = case["label"] == "pass"
        verdict = truth if rng.random() < 0.9 else not truth
        return json.dumps({"pass": verdict, "reason": "fake verdict"})
    return FakeClient(default=reply)


def main(argv: list[str]) -> None:
    cases = load_cases()
    if "--fake" in argv:
        client = fake_judge_client(cases)
    else:
        import anthropic
        client = anthropic.Anthropic()
    traces = OUT / "traces.jsonl"
    if traces.exists():
        traces.unlink()
    tc = TracedClient(client, traces)

    verdicts = [judge(tc, c) for c in cases]
    agree = agreement(verdicts, [c["label"] for c in cases])
    print(f"judge agreement with human labels: {agree['accuracy']:.0%}")
    for i in agree["disagreements"]:
        c = cases[i]
        print(f"  {c['id']}: human={c['label']} judge={'pass' if verdicts[i]['pass'] else 'fail'}"
              f"  reason: {verdicts[i]['reason']}")

    results = run_trials(lambda c, rng: judge(tc, c)["pass"] == (c["label"] == "pass"), cases, K)
    print(f"judge correct, pass@{K}: {pass_at_k(results):.0%}   pass^{K}: {pass_hat_k(results):.0%}")
    for cid, trials in results.items():
        if not all(trials):
            print(f"  {cid}: {''.join('P' if t else '.' for t in trials)}")

    print("traces:", json.dumps(summarize_traces(traces)))
    print(f"wrote out/{traces.name}")


if __name__ == "__main__":
    main(sys.argv[1:])
