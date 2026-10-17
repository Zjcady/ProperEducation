"""C4 step 4 · The same agent using the SDK's tool runner (beta). Complete; read and run it.

    python3 agent_runner.py "Read notes.txt and tell me the thermostat setting"

The runner owns the loop: it calls the API, runs the tool your function implements,
feeds the result back, and stops when the model answers with text.
"""
from __future__ import annotations

import sys
from pathlib import Path

import anthropic
from anthropic import beta_tool

from agent import MODEL, SANDBOX, SYSTEM, execute_tool


@beta_tool
def list_dir(path: str) -> str:
    """List files and folders at a path relative to the sandbox root. Use '.' for the root.

    Args:
        path: Folder path relative to the sandbox root.
    """
    return execute_tool("list_dir", {"path": path}, SANDBOX)


@beta_tool
def read_file(path: str) -> str:
    """Read a UTF-8 text file at a path relative to the sandbox root.

    Args:
        path: File path relative to the sandbox root.
    """
    return execute_tool("read_file", {"path": path}, SANDBOX)


@beta_tool
def run_tests(path: str) -> str:
    """Run pytest on a file or folder relative to the sandbox root and return the tail of its output.

    Args:
        path: File or folder path relative to the sandbox root.
    """
    return execute_tool("run_tests", {"path": path}, SANDBOX)


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    client = anthropic.Anthropic()
    runner = client.beta.messages.tool_runner(
        model=MODEL, max_tokens=4096, system=SYSTEM,
        tools=[list_dir, read_file, run_tests],
        messages=[{"role": "user", "content": " ".join(argv)}],
    )
    last = None
    for message in runner:          # one BetaMessage per model turn
        last = message
        for block in message.content:
            if block.type == "tool_use":
                print(f"[tool] {block.name}({block.input})")
    print("".join(b.text for b in last.content if b.type == "text"))


if __name__ == "__main__":
    main(sys.argv[1:])
