"""002 · Contains Duplicate  (easy)   pattern: Arrays & Hashing
https://leetcode.com/problems/contains-duplicate/

Run:  python3 coach.py check 002
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run  # noqa: E402


class Solution:
    def containsDuplicate(self, nums: list[int]) -> bool:
        raise NotImplementedError


TESTS = [
    {"args": [[1, 2, 3, 1]], "want": True},
    {"args": [[1, 2, 3, 4]], "want": False},
    {"args": [[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]], "want": True},
    {"args": [[]], "want": False, "name": "empty"},
    {"args": [[7]], "want": False, "name": "single"},
    {"args": [[-1, 0, -1]], "want": True, "name": "negatives"},
]

if __name__ == "__main__":
    run(Solution().containsDuplicate, TESTS)
