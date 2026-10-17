"""004 · Group Anagrams  (medium)   pattern: Arrays & Hashing
https://leetcode.com/problems/group-anagrams/

Run:  python3 coach.py check 004
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run  # noqa: E402


class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        raise NotImplementedError


def as_groups(result):
    """Order of groups and order inside groups don't matter."""
    return sorted(sorted(group) for group in result)


TESTS = [
    {"args": [["eat", "tea", "tan", "ate", "nat", "bat"]],
     "want": [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]], "norm": as_groups},
    {"args": [[""]], "want": [[""]], "norm": as_groups, "name": "one empty string"},
    {"args": [["a"]], "want": [["a"]], "norm": as_groups, "name": "single letter"},
    {"args": [["ab", "ba", "abc", "cab", "bca", "x"]],
     "want": [["ab", "ba"], ["abc", "cab", "bca"], ["x"]], "norm": as_groups},
    {"args": [["aab", "abb"]], "want": [["aab"], ["abb"]], "norm": as_groups,
     "name": "same letters, different counts stay apart"},
]

if __name__ == "__main__":
    run(Solution().groupAnagrams, TESTS)
