"""008 · Longest Consecutive Sequence  (medium)   pattern: Arrays & Hashing
https://leetcode.com/problems/longest-consecutive-sequence/

Run:  python3 coach.py check 008
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run  # noqa: E402


class Solution:
    def longestConsecutive(self, nums: list[int]) -> int:
        raise NotImplementedError


TESTS = [
    {"args": [[100, 4, 200, 1, 3, 2]], "want": 4},
    {"args": [[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], "want": 9},
    {"args": [[]], "want": 0, "name": "empty"},
    {"args": [[1, 1, 2]], "want": 2, "name": "duplicates"},
    {"args": [[9]], "want": 1, "name": "single"},
    {"args": [[-3, -1, -2, 5]], "want": 3, "name": "negatives"},
    {"args": [[10, 5, 12, 3, 55, 30, 4, 11, 2]], "want": 4},
]

if __name__ == "__main__":
    run(Solution().longestConsecutive, TESTS)
