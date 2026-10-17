"""003 · Valid Anagram  (easy)   pattern: Arrays & Hashing
https://leetcode.com/problems/valid-anagram/

Run:  python3 coach.py check 003
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run  # noqa: E402


class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        raise NotImplementedError


TESTS = [
    {"args": ["anagram", "nagaram"], "want": True},
    {"args": ["rat", "car"], "want": False},
    {"args": ["a", "ab"], "want": False, "name": "different lengths"},
    {"args": ["", ""], "want": True, "name": "both empty"},
    {"args": ["aacc", "ccac"], "want": False, "name": "same letters, different counts"},
    {"args": ["listen", "silent"], "want": True},
]

if __name__ == "__main__":
    run(Solution().isAnagram, TESTS)
