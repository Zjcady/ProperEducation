# 002 · Contains Duplicate  (easy)

Pattern: **Arrays & Hashing** → `patterns/01-arrays-hashing.md`
LeetCode: https://leetcode.com/problems/contains-duplicate/

## The problem, in plain words

Given a list of numbers, return `True` if any number shows up more than once, otherwise `False`.

## Example

```
input:  [1, 2, 3, 1]
output: True
why:    1 appears twice
```

## Before you code

- Brute force: compare every pair, O(n²).
- Sorting then checking neighbors works too: O(n log n). Can you do O(n)?

## Hints

<details>
<summary>Hint 1 · a nudge</summary>

You only need to know one thing about each number: have I seen it already?

</details>

<details>
<summary>Hint 2 · the idea</summary>

A `set` answers "have I seen this?" in O(1). Walk the list, check, then add.

</details>

<details>
<summary>Hint 3 · the skeleton</summary>

```
seen = set()
for x in nums:
    if x in seen: return ____
    seen.add(x)
return ____
```

Bonus: there's a one-liner comparing two lengths. Find it *after* you've written the loop version.

</details>

## Explain it back

1. In one sentence, what is the trick?
2. Why is `x in seen` O(1) for a set but O(n) for a list?
3. What's the one-line version and why does it work?
