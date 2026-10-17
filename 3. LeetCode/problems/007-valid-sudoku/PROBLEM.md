# 007 · Valid Sudoku  (medium)

Pattern: **Arrays & Hashing** → `patterns/01-arrays-hashing.md`
LeetCode: https://leetcode.com/problems/valid-sudoku/

## The problem, in plain words

You get a 9×9 sudoku board as a list of lists of single-character strings. Empty cells are `"."`. Return `True` if no row, no column, and no 3×3 box has a repeated digit. You are **not** checking whether it's solvable, only that nothing already placed breaks a rule.

## Example

```
A board with a 5 at the top left and another 5 later in the same column -> False
The standard LeetCode example board -> True
```

## Before you code

- Brute force: for each cell, scan its row, column and box for a duplicate. O(81 × 27). Honestly fine, but messy.
- Pattern signal: 27 separate "have I seen this digit here before?" questions. That's 27 sets. Or one set with clever keys.

## Hints

<details>
<summary>Hint 1 · a nudge</summary>

One pass over all 81 cells. For each digit you need to ask three questions: seen in this row? this column? this box? Each question is a set lookup.

</details>

<details>
<summary>Hint 2 · the idea</summary>

Keep `rows[9]`, `cols[9]`, `boxes[9]` as lists of sets. The box index for cell `(r, c)` is `(r // 3) * 3 + c // 3`. Say why that formula works before using it.

</details>

<details>
<summary>Hint 3 · the skeleton</summary>

```
rows  = [set() for _ in range(9)]
cols  = [set() for _ in range(9)]
boxes = [set() for _ in range(9)]
for r in range(9):
    for c in range(9):
        v = board[r][c]
        if v == ".": continue
        b = ____________
        if v in rows[r] or v in cols[c] or v in boxes[b]: return False
        rows[r].add(v); cols[c].add(v); boxes[b].add(v)
return True
```

</details>

## Explain it back

1. In one sentence, what is the trick?
2. Draw the 9 boxes and label each with `(r // 3) * 3 + c // 3`. Why does it hit 0 through 8 exactly once each?
3. Why is `[set()] * 9` a bug? (It's the same bug as `[[0] * m] * n` in pattern 13.)
