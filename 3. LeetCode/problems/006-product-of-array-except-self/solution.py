"""006 · Product of Array Except Self  (medium)   pattern: Arrays & Hashing
https://leetcode.com/problems/product-of-array-except-self/

Run:  python3 coach.py check 006
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run  # noqa: E402


class Solution:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        raise NotImplementedError


TESTS = [
    {"args": [[1, 2, 3, 4]], "want": [24, 12, 8, 6]},
    {"args": [[-1, 1, 0, -3, 3]], "want": [0, 0, 9, 0, 0], "name": "one zero"},
    {"args": [[0, 4, 0]], "want": [0, 0, 0], "name": "two zeros"},
    {"args": [[2, 3]], "want": [3, 2], "name": "two elements"},
    {"args": [[5, 1, 1, 1]], "want": [1, 5, 5, 5]},
    {"args": [[-2, -3, 4]], "want": [-12, -8, 6], "name": "negatives"},
]

if __name__ == "__main__":
    run(Solution().productExceptSelf, TESTS)
