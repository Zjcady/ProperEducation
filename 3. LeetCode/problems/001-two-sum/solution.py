"""001 · Two Sum  (easy)   pattern: Arrays & Hashing
https://leetcode.com/problems/two-sum/

Run:  python3 coach.py check 001     (or just: python3 solution.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run  # noqa: E402


class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        raise NotImplementedError


TESTS = [
    {"args": [[2, 7, 11, 15], 9], "want": [0, 1], "norm": sorted},
    {"args": [[3, 2, 4], 6], "want": [1, 2], "norm": sorted},
    {"args": [[3, 3], 6], "want": [0, 1], "norm": sorted, "name": "same value twice"},
    {"args": [[-1, -2, -3, -4, -5], -8], "want": [2, 4], "norm": sorted, "name": "negatives"},
    {"args": [[0, 4, 3, 0], 0], "want": [0, 3], "norm": sorted, "name": "zeros"},
    {"args": [[1, 5, 1, 5], 10], "want": [1, 3], "norm": sorted, "name": "duplicates present"},
]

if __name__ == "__main__":
    run(Solution().twoSum, TESTS)
