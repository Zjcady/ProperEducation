"""C3 · The study coach as an MCP server.

    python3 coach_server.py            # stdio: a client such as Claude Code launches this (steps 1-2)
    python3 coach_server.py --http     # streamable HTTP on http://127.0.0.1:8765/mcp, bearer token required (steps 3-4)

Register with Claude Code:
    claude mcp add coach -- python3 "<absolute path to this file>"                                    # stdio
    claude mcp add --transport http coach http://127.0.0.1:8765/mcp --header "Authorization: Bearer <token>"  # HTTP

Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer

from auth import CoachTokenVerifier

HERE = Path(__file__).resolve().parent
COACH = HERE.parents[1] / "coach.py"                       # labs/C3 -> 3. LeetCode/coach.py
TOKENS_FILE = Path(os.environ.get("COACH_TOKENS_FILE", HERE / "tokens.json"))
HOST = "127.0.0.1"
PORT = int(os.environ.get("COACH_PORT", "8765"))
SERVER_URL = f"http://{HOST}:{PORT}"

verifier = CoachTokenVerifier(TOKENS_FILE)

server = MCPServer(
    "coach",
    instructions="Tools for the learner's daily study coach. Call coach_next first. "
                 "coach_done changes the learner's record; if it is denied, tell the learner, don't retry.",
    # Auth applies to HTTP only. Every HTTP request must carry `Authorization: Bearer <token>`;
    # the SDK passes it to verifier.verify_token and answers 401 if that returns None,
    # 403 if the token lacks a required scope. Tools never see the raw header.
    token_verifier=verifier,
    auth=AuthSettings(
        issuer_url=SERVER_URL,                   # who issues tokens: you, by hand, into tokens.json
        resource_server_url=f"{SERVER_URL}/mcp",  # this server; published at /.well-known/oauth-protected-resource/mcp
        required_scopes=["read"],                # every request needs at least read
        validate_token_resource=False,           # tokens.json is this server's own list, so every token in it is for us
    ),
)


def stdio_scopes() -> list[str]:
    # stdio has no HTTP request, so no bearer token. The spec says a stdio server takes
    # its credentials from the environment: whoever launches the process decides.
    # Over HTTP this is never consulted, because an unauthenticated request never reaches a tool.
    return ["read", "write"] if os.environ.get("COACH_WRITE") == "1" else ["read"]


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
def coach_done(item_id: str, rating: int | None = None) -> str:
    """TODO(you): Record an item as done. This changes the learner's record, so the caller needs the write scope; if it's denied, tell the learner rather than retrying. rating (1, 2 or 3) is required for LeetCode problems and ignored for chapters and labs."""
    raise NotImplementedError


if __name__ == "__main__":
    if "--http" in sys.argv[1:]:
        server.run("streamable-http", host=HOST, port=PORT)
    else:
        server.run()
