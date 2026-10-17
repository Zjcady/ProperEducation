# Auth for tool calling, in one page

## Authentication vs authorization
_(you)_

## API keys
Where they live, how they're sent, how they're rotated, what happens when one leaks.
_(you)_

## OAuth, in five sentences
Who the three parties are, what a token represents, why it expires.
_(you)_

## Scopes
What `read` and `write` mean in this server, and why the model's default token is read-only.
_(you)_

## Least privilege
One concrete example from this lab.
_(you)_

## Why constant-time comparison
_(you)_

## The token belongs on the transport
The old version of this lab had `coach_done(item_id, token, rating)`. Why is a token in the tool's arguments a problem? (Who writes the arguments, and where do they end up?)
_(you)_

On HTTP the token is a header the SDK checks before any tool runs. What does the server answer with no token, with an unknown token, and with a read token calling `coach_done`, and why are those three different?
_(you)_

On stdio there is no header. Where do credentials come from instead, and who is trusted when you set `COACH_WRITE=1`?
_(you)_
