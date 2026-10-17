"""C2 · Prompt in a workflow.

    python3 pipeline.py data            live
    python3 pipeline.py --fake data     offline

Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "C1"))
sys.path.insert(0, str(HERE.parent / "_common"))
from ask import MODEL, ask, estimate_cost, get_client  # noqa: E402

LABELS = ["care-sheet", "health", "build", "shopping", "other"]

# Step 2 scaffolding: what each label means, and two worked examples. These are
# the same on every classify call, which is exactly what prompt caching is for.
LABEL_DEFINITIONS = {
    "care-sheet": "how to keep a species: temperatures, humidity, feeding, substrate, lighting",
    "health": "one animal's condition: vet visits, weight, shedding, illness, medication",
    "build": "making or changing an enclosure: plans, materials, measurements, steps",
    "shopping": "things to buy, prices, where to buy them",
    "other": "anything that fits none of the above",
}

FEW_SHOT = """Examples:

Text: Ordered 2 cork rounds and a 40 W basking bulb, $38 total. Still need a digital thermometer.
Label: shopping

Text: Mochi refused food twice this week and has a retained shed on her tail tip. Booked the vet for Friday.
Label: health"""


def describe_labels(labels: list[str]) -> str:
    """One line per label: "- name: definition" (name alone when we have no definition)."""
    return "\n".join(f"- {l}: {LABEL_DEFINITIONS[l]}" if l in LABEL_DEFINITIONS else f"- {l}"
                     for l in labels)


# ------------------------------------------------------------------ step 1

def collect_files(folder: str | Path, exts: tuple[str, ...] = (".md", ".txt")) -> list[Path]:
    """TODO(you): every file under folder (recursive) with one of these suffixes, sorted."""
    raise NotImplementedError


def chunk_text(text: str, max_chars: int) -> list[str]:
    """TODO(you): split on blank lines, pack paragraphs into chunks <= max_chars.
    A paragraph longer than max_chars is split on spaces. Never cut a word."""
    raise NotImplementedError


def _split_words(para: str, max_chars: int) -> list[str]:
    out, line = [], ""
    for word in para.split():
        if line and len(line) + 1 + len(word) > max_chars:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        out.append(line)
    return out


def summarize(client, text: str, max_chars: int = 6000) -> str:
    """TODO(you): one-sentence summary. Long text: summarize chunks, then the summaries."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 2

def classify(client, text: str, labels: list[str]) -> str:
    """TODO(you): exactly one of labels, else "unknown". One stricter retry.
    The label list (describe_labels) and FEW_SHOT go in `system` as a list of
    text blocks; the last one carries cache_control {"type": "ephemeral"}.
    Only the file's text goes in the user message."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 3

def run(client, folder: str | Path, labels: list[str] = LABELS) -> list[dict]:
    """TODO(you): one row per file with summed token usage across all its calls."""
    raise NotImplementedError


class _UsageTap:
    """Wraps client.messages.create to add up usage for the calls made inside the block.
    input_tokens is only the uncached part; the two cache counts are kept separately."""
    def __init__(self, client):
        self.client, self.input_tokens, self.output_tokens = client, 0, 0
        self.cache_creation_input_tokens = self.cache_read_input_tokens = 0

    def __enter__(self):
        self._orig = self.client.messages.create
        def create(**kwargs):
            resp = self._orig(**kwargs)
            self.input_tokens += resp.usage.input_tokens
            self.output_tokens += resp.usage.output_tokens
            self.cache_creation_input_tokens += getattr(resp.usage, "cache_creation_input_tokens", 0) or 0
            self.cache_read_input_tokens += getattr(resp.usage, "cache_read_input_tokens", 0) or 0
            return resp
        self.client.messages.create = create
        return self

    def __exit__(self, *exc):
        self.client.messages.create = self._orig


def render_report(rows: list[dict], model: str = MODEL) -> str:
    """TODO(you): markdown table + totals + estimated cost, plus a
    "cached input: N%" line (cache reads / all input). Rows may lack the cache keys."""
    raise NotImplementedError


# ------------------------------------------------------------------ CLI

def main(argv: list[str]) -> None:
    fake = "--fake" in argv
    folders = [a for a in argv if not a.startswith("--")]
    if not folders:
        sys.exit(__doc__)
    client = get_client(fake, responses=None)
    if fake:
        client.default = "care-sheet"
    rows = run(client, folders[0])
    print(render_report(rows))


if __name__ == "__main__":
    main(sys.argv[1:])
