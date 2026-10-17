"""C1 · First LLM call.

    python3 ask.py "your prompt"                      live (needs ANTHROPIC_API_KEY or `ant auth login`)
    python3 ask.py --fake "your prompt"               offline, fake client
    python3 ask.py --json "List 3 gecko facts as JSON with keys facts (list) and source"

Functions marked TODO(you) are yours. Everything else is scaffolding; read it, don't change it.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_common"))
from fake_llm import FakeClient  # noqa: E402

MODEL = "claude-opus-5-5"
MAX_TOKENS = 4096

# Dollars per million tokens: (input, output). From the current price list.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}

# Prompt caching, as multipliers of the input price. Writing a prefix into the
# 5-minute cache costs 1.25x; reading it back costs 0.1x on most models, but the
# price list gives some models a cheaper read rate. Check it, don't assume.
CACHE_WRITE_MULTIPLIER = 1.25
CACHE_READ_MULTIPLIER = {"claude-opus-5-5": 0.05}   # Opus 5.5 reads are $0.20 on $4 input; others 0.1


def get_client(fake: bool = False, responses: list | None = None):
    """Real client unless asked for the fake one. The real one reads credentials
    from the environment (ANTHROPIC_API_KEY) or an `ant auth login` profile."""
    if fake or os.environ.get("USE_FAKE_LLM"):
        return FakeClient(responses)
    import anthropic
    return anthropic.Anthropic()


# ------------------------------------------------------------------ step 1

def build_messages(prompt: str) -> list[dict]:
    """TODO(you): the `messages` list for a single user turn."""
    raise NotImplementedError


def text_of(response) -> str:
    """TODO(you): concatenate the text of every block whose type is "text"."""
    raise NotImplementedError


def ask(client, prompt: str, system: str | list[dict] | None = None, model: str = MODEL,
        max_tokens: int = MAX_TOKENS) -> str:
    """TODO(you): one request, return the reply text. Pass `system` only when given."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 2

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def parse_json_reply(text: str) -> dict:
    """TODO(you): accept bare JSON or JSON in a ```json fence. Must be an object.
    Raise ValueError otherwise."""
    raise NotImplementedError


def ask_json(client, prompt: str, required_keys: list[str], retries: int = 1, **kwargs) -> dict:
    """TODO(you): ask, parse, check keys. Retry with a stricter instruction, then give up."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 3

def estimate_cost(usage, model: str = MODEL) -> float:
    """TODO(you): dollars for this response. PRICES are per million tokens.
    Cache writes cost CACHE_WRITE_MULTIPLIER x the input price, cache reads
    CACHE_READ_MULTIPLIER (default 0.1) x. A missing usage field counts as 0."""
    raise NotImplementedError


def default_retryable() -> tuple:
    import anthropic
    return (anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError)


def with_retry(fn, attempts: int = 3, base_delay: float = 1.0, retry_on: tuple | None = None,
               sleep=time.sleep):
    """TODO(you): call fn(). Retry on `retry_on` exceptions with exponential backoff
    (base_delay * 2**attempt). Anything else propagates at once. Re-raise the last
    retryable error after `attempts` tries."""
    raise NotImplementedError


# ------------------------------------------------------------------ CLI

def main(argv: list[str]) -> None:
    fake = "--fake" in argv
    want_json = "--json" in argv
    words = [a for a in argv if not a.startswith("--")]
    if not words:
        sys.exit(__doc__)
    prompt = " ".join(words)
    client = get_client(fake, responses=['{"facts": ["fake"], "source": "fake"}'] if fake else None)
    if want_json:
        print(json.dumps(ask_json(client, prompt, ["facts", "source"]), indent=2))
    else:
        response = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, messages=build_messages(prompt))
        print(text_of(response))
        print(f"\n[{response.usage.input_tokens} in, {response.usage.output_tokens} out, "
              f"~${estimate_cost(response.usage):.4f}]")


if __name__ == "__main__":
    main(sys.argv[1:])
