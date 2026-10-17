# 008 · Longest Consecutive Sequence  (medium)

Pattern: **Arrays & Hashing** → `patterns/01-arrays-hashing.md`
LeetCode: https://leetcode.com/problems/longest-consecutive-sequence/

## The problem, in plain words

Given an unsorted list of integers, find the length of the longest run of consecutive integers that all appear in the list (like 1, 2, 3, 4). They don't have to be next to each other in the list. Must run in O(n).

## Example

```
input:  [100, 4, 200, 1, 3, 2]
output: 4
why:    1, 2, 3, 4 are all present
```

## Before you code

- Sorting then scanning is O(n log n) and would pass LeetCode. Write it first if you want a win.
- Pattern signal: "is `x + 1` in the list?" is a set question.

## Hints

<details>
<summary>Hint 1 · a nudge</summary>

Put everything in a set. Now for any number you can ask "is the next one here?" in O(1). The danger is counting the same run many times.

</details>

<details>
<summary>Hint 2 · the idea</summary>

Only start counting from a number that is the **start** of a run: a number `x` where `x - 1` is **not** in the set. Then walk forward `x+1, x+2, ...` while they exist. Every number gets visited at most twice overall, so it's O(n).

</details>

<details>
<summary>Hint 3 · the skeleton</summary>

```
s = set(nums)
best = 0
for x in s:
    if ________ not in s:          # x is the start of a run
        length = 1
        while x + length in s:
            length += 1
        best = max(best, length)
return best
```

</details>

## Explain it back

1. In one sentence, what is the trick?
2. Why is this O(n) even though there's a `while` inside a `for`?
3. What happens on duplicates like `[1, 1, 2]`? Why does iterating the *set* instead of the list matter?
