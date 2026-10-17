"""C3 · The study coach as an MCP server.

    python3 coach_server.py          # serves on stdio; a client such as Claude Code launches this

Register with Claude Code:
    claude mcp add coach -- python3 "<absolute path to this file>"

Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from auth import authorize, load_tokens

HERE = Path(__file__).resolve().parent
COACH = HERE.parents[1] / "coach.py"                       # labs/C3 -> 3. LeetCode/coach.py
TOKENS_FILE = Path(os.environ.get("COACH_TOKENS_FILE", HERE / "tokens.json"))

server = MCPServer(
    "coach",
    instructions="Tools for the learner's daily study coach. Call coach_next first. "
                 "coach_done changes the learner's record and needs a write token.",
)


def run_coach(*args: str) -> str:
    """TODO(you): run coach.py with these args, from its own folder; return stdout + stderr."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 1

@server.tool()
def coach_next() -> str:
    """TODO(you): Today's study blocks, in order. Call this first to find out what the learner should do now."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 2

@server.tool()
def coach_start(item_id: str) -> str:
    """TODO(you): Start an item and its timer. item_id is a problem number like "001", a slug like "two-sum", or a chapter/lab id like "A01" or "C1"."""
    raise NotImplementedError


@server.tool()
def coach_check(item_id: str) -> str:
    """TODO(you): Run the tests for an item (same id format as coach_start) and return the results."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 3

@server.tool()
def coach_done(item_id: str, token: str, rating: int | None = None) -> str:
    """TODO(you): Record an item as done. Needs a token with the write scope. rating (1, 2 or 3) is required for LeetCode problems and ignored for chapters and labs."""
    raise NotImplementedError


if __name__ == "__main__":
    server.run()
