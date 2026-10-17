# 006 · Product of Array Except Self  (medium)

Pattern: **Arrays & Hashing** (really: prefix / suffix arrays) → `patterns/01-arrays-hashing.md`
LeetCode: https://leetcode.com/problems/product-of-array-except-self/

## The problem, in plain words

For each position, return the product of every *other* number in the list. You are **not allowed to use division**, and it has to run in O(n).

## Example

```
input:  [1, 2, 3, 4]
output: [24, 12, 8, 6]
why:    position 0 is 2*3*4 = 24, position 1 is 1*3*4 = 12, ...
```

## Before you code

- Brute force: for each position, multiply everything else. O(n²).
- Division trick (total / nums[i]) is banned, and breaks on zeros anyway.
- Pattern signal: "everything to my left" and "everything to my right" are two separate running products.

## Hints

<details>
<summary>Hint 1 · a nudge</summary>

The product of everything except position `i` is (product of everything left of `i`) × (product of everything right of `i`).

</details>

<details>
<summary>Hint 2 · the idea</summary>

Make a `prefix` array where `prefix[i]` = product of `nums[0..i-1]`. Make a `suffix` array the same way from the right. Answer is `prefix[i] * suffix[i]`. Three passes, O(n). Get this version passing first.

</details>

<details>
<summary>Hint 3 · the skeleton (O(1) extra space version)</summary>

```
res = [1] * len(nums)
left = 1
for i in range(len(nums)):
    res[i] = left
    left *= nums[i]
right = 1
for i in range(len(nums) - 1, -1, -1):
    res[i] *= ____
    right *= nums[i]
return res
```

</details>

## Explain it back

1. In one sentence, what is the trick?
2. Why does the first loop store `left` *before* multiplying by `nums[i]`?
3. What happens with one zero in the input? Two zeros? Walk through `[0, 4, 0]` by hand.
