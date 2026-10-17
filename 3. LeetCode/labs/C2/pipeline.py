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
    """TODO(you): exactly one of labels, else "unknown". One stricter retry."""
    raise NotImplementedError


# ------------------------------------------------------------------ step 3

def run(client, folder: str | Path, labels: list[str] = LABELS) -> list[dict]:
    """TODO(you): one row per file with summed token usage across all its calls."""
    raise NotImplementedError


class _UsageTap:
    """Wraps client.messages.create to add up usage for the calls made inside the block."""
    def __init__(self, client):
        self.client, self.input_tokens, self.output_tokens = client, 0, 0

    def __enter__(self):
        self._orig = self.client.messages.create
        def create(**kwargs):
            resp = self._orig(**kwargs)
            self.input_tokens += resp.usage.input_tokens
            self.output_tokens += resp.usage.output_tokens
            return resp
        self.client.messages.create = create
        return self

    def __exit__(self, *exc):
        self.client.messages.create = self._orig


def render_report(rows: list[dict], model: str = MODEL) -> str:
    """TODO(you): markdown table + totals + estimated cost."""
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
