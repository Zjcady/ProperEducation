# 001 · Two Sum  (easy)

Pattern: **Arrays & Hashing** → read `patterns/01-arrays-hashing.md` first if it's new to you.
LeetCode: https://leetcode.com/problems/two-sum/

## The problem, in plain words

You get a list of numbers and a target. Exactly one pair of numbers in the list adds up to the target. Return the two **positions** (indices) of that pair, in any order. You can't use the same position twice.

## Example

```
input:  nums = [2, 7, 11, 15], target = 9
output: [0, 1]
why:    nums[0] + nums[1] = 2 + 7 = 9
```

## Before you code (30 seconds, out loud or in NOTES.md)

- Brute force: try every pair. That's two nested loops, O(n²). Say that out loud, it's fine.
- Which pattern signal do you see? "Have I seen the number I need before?"

## Hints (open one at a time, only after 5 real minutes of being stuck)

<details>
<summary>Hint 1 · a nudge</summary>

When you're standing on the number 7 and the target is 9, you already know exactly which number you're looking for. You don't need to search for it. You need to *remember* whether you've passed it.

</details>

<details>
<summary>Hint 2 · the idea</summary>

Walk the list once. Keep a dict of `number -> index` for everything you've already walked past. At each number, compute `need = target - x` and ask the dict if `need` is in it.

</details>

<details>
<summary>Hint 3 · the skeleton</summary>

```
seen = {}
for i, x in enumerate(nums):
    need = target - x
    if need in seen:
        return [________, i]
    seen[x] = i
```

Fill in the blank. And notice the order: check first, insert after. Why does that matter?

</details>

## Explain it back (required before rating 3)

1. In one sentence, what is the trick?
2. Why is this O(n) instead of O(n²)?
3. What goes wrong if you insert into the dict *before* checking it? Try `nums=[3, 3], target=6` and `nums=[3, 2, 4], target=6`.
