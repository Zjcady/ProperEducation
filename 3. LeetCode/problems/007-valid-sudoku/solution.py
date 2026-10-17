"""007 · Valid Sudoku  (medium)   pattern: Arrays & Hashing
https://leetcode.com/problems/valid-sudoku/

Run:  python3 coach.py check 007
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run  # noqa: E402


class Solution:
    def isValidSudoku(self, board: list[list[str]]) -> bool:
        raise NotImplementedError


def board(rows):
    """Build a board from 9 strings like '53..7....'."""
    return [list(row) for row in rows]


VALID = board([
    "53..7....",
    "6..195...",
    ".98....6.",
    "8...6...3",
    "4..8.3..1",
    "7...2...6",
    ".6....28.",
    "...419..5",
    "....8..79",
])
BAD_COLUMN = board([
    "83..7....",   # 8 here...
    "6..195...",
    ".98....6.",
    "8...6...3",   # ...and 8 here, same column
    "4..8.3..1",
    "7...2...6",
    ".6....28.",
    "...419..5",
    "....8..79",
])
BAD_ROW = board([
    "55..7....",
    "6..195...",
    ".98....6.",
    "8...6...3",
    "4..8.3..1",
    "7...2...6",
    ".6....28.",
    "...419..5",
    "....8..79",
])
BAD_BOX = board([
    "53..7....",
    "6..195...",
    ".98....6.",
    "8...6...3",
    "4..8.3..1",
    "7...2...6",
    ".6....28.",
    "...419..5",
    "....8.979",   # 9 twice in the bottom-right box
])
EMPTY = board(["........."] * 9)

TESTS = [
    {"args": [VALID], "want": True, "name": "leetcode example"},
    {"args": [BAD_COLUMN], "want": False, "name": "duplicate in a column"},
    {"args": [BAD_ROW], "want": False, "name": "duplicate in a row"},
    {"args": [BAD_BOX], "want": False, "name": "duplicate in a box"},
    {"args": [EMPTY], "want": True, "name": "empty board is valid"},
]

if __name__ == "__main__":
    run(Solution().isValidSudoku, TESTS)
