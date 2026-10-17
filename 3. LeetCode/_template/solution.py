"""{{ID}} · {{TITLE}}  ({{DIFFICULTY}})   pattern: {{PATTERN}}
{{URL}}

Run:  python3 coach.py check {{ID}}     (or just: python3 solution.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run  # noqa: E402


class Solution:
    def TODO_METHOD_NAME(self, TODO_ARGS):
        raise NotImplementedError


TESTS = [
    # {"args": [...], "want": ...},
]

if __name__ == "__main__":
    run(Solution().TODO_METHOD_NAME, TESTS)
