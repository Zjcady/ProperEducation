"""A fake stand-in for `anthropic.Anthropic()` so every lab's tests run offline.

It mimics only what the labs use: `client.messages.create(**kwargs)` returning
an object with `.content` (blocks with `.type`, `.text` or `.id/.name/.input`),
`.stop_reason`, `.usage.input_tokens`, `.usage.output_tokens`,
`.usage.cache_creation_input_tokens`, `.usage.cache_read_input_tokens`, `.model`.

Script it with a list of responses, consumed in order:
    "plain text"                                  -> one text block, stop_reason end_turn
    {"text": "..."}                               -> same
    {"tool_use": {"name": "f", "input": {...}}}   -> a tool_use block, stop_reason tool_use
    {"blocks": [SimpleNamespace(...), ...]}       -> raw blocks (several tool_use at once)
    {"raise": SomeException("boom")}              -> raises on that call
    callable(kwargs) -> any of the above          -> decided at call time
When the script runs out, `default` is returned forever.
Every call's kwargs are recorded in `client.calls`.

Prompt caching, simulated: when `system` is a list of blocks and one of them has
`cache_control`, everything up to and including the last such block (plus
`model` and `tools`) is the cached prefix. The first call with that exact
prefix reports its tokens as `cache_creation_input_tokens`; later calls with
the identical prefix report them as `cache_read_input_tokens`. `input_tokens`
is then only the uncached remainder, so
    input_tokens + cache_creation_input_tokens + cache_read_input_tokens
always equals what an uncached call would report. Without a breakpoint both
cache fields are 0. Not simulated: the minimum cacheable length (the real API
silently skips caching short prefixes), the 5-minute TTL, and breakpoints on
`tools`, `messages` or top-level `cache_control`.
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
    created = read = 0
    prefix = _cached_prefix(kwargs)
    if prefix is not None:
        key, prefix_tokens = prefix
        prefix_tokens = min(prefix_tokens, in_tokens)
        if key in client.cache:
            read = prefix_tokens
        else:
            client.cache.add(key)
            created = prefix_tokens
        in_tokens -= prefix_tokens
    return SimpleNamespace(content=blocks, stop_reason=stop, model=kwargs.get("model", "fake"),
                           usage=SimpleNamespace(input_tokens=in_tokens, output_tokens=out_tokens,
                                                 cache_creation_input_tokens=created,
                                                 cache_read_input_tokens=read))


def _cached_prefix(kwargs):
    """(cache key, prefix tokens) when system carries a cache_control breakpoint, else None."""
    system = kwargs.get("system")
    if not isinstance(system, list):
        return None
    marks = [i for i, b in enumerate(system) if isinstance(b, dict) and b.get("cache_control")]
    if not marks:
        return None
    head = system[: marks[-1] + 1]
    key = json.dumps([kwargs.get("model"), kwargs.get("tools"), head], sort_keys=True, default=str)
    return key, len(str(head)) // 4


class FakeClient:
    def __init__(self, responses: list | None = None, default="(fake reply)"):
        self.responses = list(responses or [])
        self.default = default
        self.calls: list[dict] = []
        self.tool_counter = 0
        self.cache: set[str] = set()     # prefixes "written" so far; see the docstring
        self.messages = FakeMessages(self)
