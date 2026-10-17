#!/usr/bin/env python3
"""PreToolUse hook: block Claude from editing the learner's own answer files.

Claude Code runs this before Edit/Write and pipes a JSON object to stdin:
    {"tool_name": "Edit", "tool_input": {"file_path": "/abs/path/to/file", ...}, ...}
Exit 0 to allow. Exit 2 to block; whatever you print to stderr is shown to Claude.
"""
import json
import re
import sys

PROTECTED = [
    r"problems/[^/]+/solution\.py$",
    r"foundations/[^/]+/challenge\.py$",
]
# A file that is still the untouched template may be filled in (that's how the
# morning scheduled task writes the stub and tests). Once the learner has
# started, it's theirs.
TEMPLATE_MARKERS = ("TODO_METHOD_NAME", "TODO_ARGS")


def is_protected(path: str) -> bool:
    """TODO(you): True when path matches one of PROTECTED (use re.search)."""
    raise NotImplementedError


def is_untouched_template(path: str) -> bool:
    """TODO(you): True when the file exists and still contains a TEMPLATE_MARKERS string."""
    raise NotImplementedError


def main() -> int:
    """TODO(you): read stdin JSON, get tool_input.file_path, block (exit 2 + stderr reason)
    when protected and not an untouched template; otherwise allow (exit 0)."""
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
