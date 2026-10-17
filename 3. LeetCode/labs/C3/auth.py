"""Token-and-scope authorization for the coach MCP server. Functions marked TODO(you) are yours."""
from __future__ import annotations

import hmac
import json
from pathlib import Path


def load_tokens(path: str | Path) -> dict[str, list[str]]:
    """TODO(you): {token: [scopes]} from a JSON file. Skip keys starting with "_".
    A missing file means no tokens (empty dict), not a crash."""
    raise NotImplementedError


def authorize(token: str | None, scope: str, tokens: dict[str, list[str]]) -> bool:
    """TODO(you): True only if a token matches in constant time AND has the scope."""
    raise NotImplementedError
