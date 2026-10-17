"""C4 · A hand-written agent loop over three sandboxed tools.

    python3 agent.py "Read notes.txt and tell me the thermostat setting"
    python3 agent.py --fake "..."        offline (scripted fake replies)

Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "C1"))
sys.path.insert(0, str(HERE.parent / "_common"))
from ask import MODEL, get_client, text_of  # noqa: E402

SANDBOX = HERE / "sandbox"
MAX_TOKENS = 4096
SYSTEM = ("You are a careful assistant working inside a sandboxed folder. Use the tools to look "
          "before you answer. Paths are relative to the sandbox root. When you have the answer, "
          "reply in plain text.")

TOOLS = [
    {"name": "list_dir", "description": "List files and folders at a path relative to the sandbox root. Use '.' for the root.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}},
                      "required": ["path"], "additionalProperties": False}, "strict": True},
    {"name": "read_file", "description": "Read a UTF-8 text file at a path relative to the sandbox root.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}},
                      "required": ["path"], "additionalProperties": False}, "strict": True},
    {"name": "run_tests", "description": "Run pytest on a file or folder relative to the sandbox root and return the tail of its output.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}},
                      "required": ["path"], "additionalProperties": False}, "strict": True},
]


# ------------------------------------------------------------------ step 1

def safe_path(root: Path, rel: str) -> Path:
    """TODO(you): the resolved path for rel under root. PermissionError if it escapes root."""
    raise NotImplementedError


def execute_tool(name: str, inputs: dict, root: Path) -> str:
    """TODO(you): dispatch by name. Unknown name -> ValueError. Every path via safe_path."""
    raise NotImplementedError


# ------------------------------------------------------------------ steps 2 and 3

def run_agent(client, task: str, root: Path = SANDBOX, max_iters: int = 8,
              transcript: list | None = None, model: str = MODEL) -> str:
    """TODO(you): the loop. See README steps 2 and 3."""
    raise NotImplementedError


def save_transcript(transcript: list[dict], path: str | Path) -> None:
    """TODO(you): one JSON object per line."""
    raise NotImplementedError


# ------------------------------------------------------------------ CLI

def main(argv: list[str]) -> None:
    fake = "--fake" in argv
    words = [a for a in argv if not a.startswith("--")]
    if not words:
        sys.exit(__doc__)
    scripted = [{"tool_use": {"name": "read_file", "input": {"path": "notes.txt"}}},
                "The thermostat is set to 88 F on the warm side."] if fake else None
    client = get_client(fake, responses=scripted)
    transcript: list[dict] = []
    answer = run_agent(client, " ".join(words), transcript=transcript)
    save_transcript(transcript, HERE / "transcript.jsonl")
    print(answer)
    print(f"\n[{len(transcript)} tool call(s), transcript.jsonl written]")


if __name__ == "__main__":
    main(sys.argv[1:])
