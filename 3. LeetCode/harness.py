"""Tiny test harness for the LeetCode folder. No dependencies.

Each solution.py ends with:

    TESTS = [
        {"args": [[2, 7, 11, 15], 9], "want": [0, 1]},
        ...
    ]
    if __name__ == "__main__":
        run(Solution().twoSum, TESTS)

Optional keys per test:
    "norm":  a function applied to BOTH the result and `want` before comparing
             (use for "any order is fine" answers, e.g. norm=sorted)
    "check": a function (result) -> bool, used instead of comparing to `want`
    "name":  a label shown in the output
"""
from __future__ import annotations

import copy
import sys
import time
import traceback


def _fmt(value, limit: int = 70) -> str:
    text = repr(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def run(func, tests, *, stop_on_first_fail: bool = False) -> None:
    passed, total = _run_one(func, tests, stop_on_first_fail=stop_on_first_fail)
    print(f"\n{passed}/{total} passed")
    if passed == total:
        print("All green. Now run:  python3 coach.py done <id> <1|2|3>")
    sys.exit(0 if passed == total else 1)


def run_levels(levels) -> None:
    """levels: [(label, func, tests), ...]. Runs each level in order; a level with
    an unimplemented function or failures stops the run so you work one level at a time."""
    for label, func, tests in levels:
        print("=" * len(label)); print(label); print("=" * len(label))
        passed, total = _run_one(func, tests)
        print(f"{passed}/{total} passed\n")
        if passed < total:
            print("Pass this level before moving on. Next:  python3 coach.py hint <id> 1")
            sys.exit(1)
    print("All levels green. Now run:  python3 coach.py done <id>")
    sys.exit(0)


def _run_one(func, tests, *, stop_on_first_fail: bool = False):
    passed = 0
    started = time.perf_counter()
    for index, test in enumerate(tests, 1):
        label = test.get("name") or f"test {index}"
        args = copy.deepcopy(test.get("args", []))
        try:
            got = func(*args)
        except NotImplementedError:
            print(f"  --  {label}: not implemented yet")
            continue
        except Exception:
            print(f"FAIL {label}: raised an exception")
            print("     args:", _fmt(test.get("args", [])))
            traceback.print_exc(limit=3)
            if stop_on_first_fail:
                break
            continue

        if "check" in test:
            ok = bool(test["check"](got))
            want_text = "custom check"
        else:
            norm = test.get("norm", lambda v: v)
            ok = norm(got) == norm(test["want"])
            want_text = _fmt(test["want"])

        if ok:
            passed += 1
            print(f"PASS {label}")
        else:
            print(f"FAIL {label}")
            print("     args:", _fmt(test.get("args", [])))
            print("     want:", want_text)
            print("     got: ", _fmt(got))
            if stop_on_first_fail:
                break

    return passed, len(tests)


# ---- helpers for linked lists and trees (import these in solution.py) ----

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"List{to_list(self)}"


def to_linked(values):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head


def to_list(node):
    out = []
    seen = set()
    while node is not None and id(node) not in seen:
        seen.add(id(node))
        out.append(node.val)
        node = node.next
    return out


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Tree{to_level_order(self)}"


def to_tree(values):
    """Build a tree from LeetCode's level-order list, where None marks a hole."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


def to_level_order(root):
    out, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out
