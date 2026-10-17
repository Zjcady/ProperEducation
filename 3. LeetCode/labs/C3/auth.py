"""Bearer-token verification for the coach MCP server over HTTP. Functions marked TODO(you) are yours.

Over HTTP the server is an OAuth 2.1 resource server: every request carries
`Authorization: Bearer <token>`, and the SDK hands that token to `verify_token`
before any tool runs. The token never appears in a tool's arguments, so the
model never sees it. Here the "authorization server" is you: you mint tokens by
hand into tokens.json. A real deployment would verify tokens issued by an OAuth
server (by checking a JWT signature, or by asking the server to introspect).
"""
from __future__ import annotations

import hmac
import json
from pathlib import Path

from mcp.server.auth.provider import AccessToken, TokenVerifier


def load_tokens(path: str | Path) -> dict[str, list[str]]:
    """TODO(you): {token: [scopes]} from a JSON file. Skip keys starting with "_".
    A missing file means no tokens (empty dict), not a crash."""
    raise NotImplementedError


class CoachTokenVerifier(TokenVerifier):
    """Checks a bearer token against tokens.json. The file is re-read on every request,
    so deleting a line from it revokes that token without restarting the server."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    async def verify_token(self, token: str) -> AccessToken | None:
        """TODO(you): The AccessToken for this bearer token, or None if it isn't in tokens.json.
        Compare with hmac.compare_digest (constant time), never ==. An empty token is never valid.
        Return AccessToken(token=token, client_id="learner", scopes=<that token's scopes>)."""
        raise NotImplementedError
