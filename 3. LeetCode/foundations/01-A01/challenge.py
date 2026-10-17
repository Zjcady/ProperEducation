"""A01 challenge · Values, types, variables, f-strings
See CHALLENGE.md. Run:  python3 coach.py check A01
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import run_levels  # noqa: E402


def kind(value) -> str:
    raise NotImplementedError


def receipt_line(item: str, price: float, qty: int) -> str:
    raise NotImplementedError


def clock(seconds: int) -> str:
    raise NotImplementedError


LEVELS = [
    ("Level 1 · kind", kind, [
        {"args": [3], "want": "int"},
        {"args": [3.0], "want": "float"},
        {"args": ["3"], "want": "str"},
        {"args": [True], "want": "bool", "name": "bool is not int here"},
        {"args": [0], "want": "int"},
    ]),
    ("Level 2 · receipt_line", receipt_line, [
        {"args": ["Apple", 0.5, 3], "want": "3 x Apple @ $0.50 = $1.50"},
        {"args": ["Cricket tub", 12.0, 1], "want": "1 x Cricket tub @ $12.00 = $12.00"},
        {"args": ["Heat mat", 19.99, 2], "want": "2 x Heat mat @ $19.99 = $39.98"},
        {"args": ["Gecko", 150, 1], "want": "1 x Gecko @ $150.00 = $150.00", "name": "int price still shows cents"},
    ]),
    ("Level 3 · clock", clock, [
        {"args": [3669], "want": "1:01:09"},
        {"args": [0], "want": "0:00:00"},
        {"args": [59], "want": "0:00:59"},
        {"args": [3600], "want": "1:00:00"},
        {"args": [86399], "want": "23:59:59"},
        {"args": [90000], "want": "25:00:00", "name": "hours can exceed 24"},
    ]),
]

if __name__ == "__main__":
    run_levels(LEVELS)
