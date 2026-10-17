"""005 · Top K Frequent Elements  (medium)   pattern: Arrays & Hashing
https://leetcode.com/problems/top-k-frequent-elements/

Run:  python3 coach.py check 005
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run  # noqa: E402


class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        raise NotImplementedError


TESTS = [
    {"args": [[1, 1, 1, 2, 2, 3], 2], "want": [1, 2], "norm": sorted},
    {"args": [[1], 1], "want": [1], "norm": sorted},
    {"args": [[4, 4, 4, 5, 5, 6, 6, 6, 6], 1], "want": [6], "norm": sorted},
    {"args": [[3, 0, 1, 0], 1], "want": [0], "norm": sorted, "name": "zero is a value too"},
    {"args": [[-1, -1, 2, 2, 2, 3], 2], "want": [-1, 2], "norm": sorted, "name": "negatives"},
    {"args": [[5, 5, 5, 5], 1], "want": [5], "norm": sorted, "name": "all the same"},
]

if __name__ == "__main__":
    run(Solution().topKFrequent, TESTS)
