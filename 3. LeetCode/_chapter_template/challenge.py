"""{{ID}} challenge · {{TITLE}}
See CHALLENGE.md. Run:  python3 coach.py check {{ID}}
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run_levels  # noqa: E402


def level_1(TODO_ARGS):
    raise NotImplementedError


def level_2(TODO_ARGS):
    raise NotImplementedError


def level_3(TODO_ARGS):
    raise NotImplementedError


LEVELS = [
    ("Level 1 · TODO name", level_1, [
        # {"args": [...], "want": ...},
    ]),
    ("Level 2 · TODO name", level_2, []),
    ("Level 3 · TODO name", level_3, []),
]

if __name__ == "__main__":
    run_levels(LEVELS)
