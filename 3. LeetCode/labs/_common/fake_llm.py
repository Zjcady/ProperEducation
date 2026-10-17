"""A fake stand-in for `anthropic.Anthropic()` so every lab's tests run offline.

It mimics only what the labs use: `client.messages.create(**kwargs)` returning
an object with `.content` (blocks with `.type`, `.text` or `.id/.name/.input`),
`.stop_reason`, `.usage.input_tokens`, `.usage.output_tokens`, `.model`.

Script it with a list of responses, consumed in order:
    "plain text"                                  -> one text block, stop_reason end_turn
    {"text": "..."}                               -> same
    {"tool_use": {"name": "f", "input": {...}}}   -> a tool_use block, stop_reason tool_use
    {"blocks": [SimpleNamespace(...), ...]}       -> raw blocks (several tool_use at once)
    {"raise": SomeException("boom")}              -> raises on that call
    callable(kwargs) -> any of the above          -> decided at call time
When the script runs out, `default` is returned forever.
Every call's kwargs are recorded in `client.calls`.
"""
from __future__ import annotations

import json
from types import SimpleNamespace


class FakeMessages:
    def __init__(self, client: "FakeClient"):
        self._client = client

    def create(self, **kwargs):
        c = self._client
        c.calls.append(kwargs)
        item = c.responses.pop(0) if c.responses else c.default
        if callable(item) and not isinstance(item, (str, dict)):
            item = item(kwargs)
        if isinstance(item, dict) and "raise" in item:
            raise item["raise"]
        return _response(item, kwargs, c)


def _response(item, kwargs, client):
    blocks, stop = [], "end_turn"
    if isinstance(item, str):
        item = {"text": item}
    if item.get("blocks"):                       # raw blocks, e.g. two tool_use blocks at once
        blocks = list(item["blocks"])
        stop = "tool_use" if any(b.type == "tool_use" for b in blocks) else "end_turn"
    if item.get("text"):
        blocks.append(SimpleNamespace(type="text", text=item["text"]))
    if item.get("tool_use"):
        client.tool_counter += 1
        tu = item["tool_use"]
        blocks.append(SimpleNamespace(type="tool_use", id=f"toolu_{client.tool_counter:03d}",
                                      name=tu["name"], input=tu.get("input", {})))
        stop = "tool_use"
    stop = item.get("stop_reason", stop)
    in_tokens = len(json.dumps(kwargs.get("messages", []), default=str)) // 4 + len(str(kwargs.get("system", ""))) // 4
    out_tokens = sum(len(getattr(b, "text", "")) for b in blocks) // 4 + 1
    return SimpleNamespace(content=blocks, stop_reason=stop, model=kwargs.get("model", "fake"),
                           usage=SimpleNamespace(input_tokens=in_tokens, output_tokens=out_tokens))


class FakeClient:
    def __init__(self, responses: list | None = None, default="(fake reply)"):
        self.responses = list(responses or [])
        self.default = default
        self.calls: list[dict] = []
        self.tool_counter = 0
        self.messages = FakeMessages(self)
