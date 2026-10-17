# 005 · Top K Frequent Elements  (medium)

Pattern: **Arrays & Hashing** → `patterns/01-arrays-hashing.md` (and a preview of `09-heap.md`)
LeetCode: https://leetcode.com/problems/top-k-frequent-elements/

## The problem, in plain words

Given a list of numbers and a number `k`, return the `k` numbers that appear most often. Any order. The answer is guaranteed to be unique.

## Example

```
input:  nums = [1, 1, 1, 2, 2, 3], k = 2
output: [1, 2]
why:    1 appears 3 times, 2 appears twice, 3 once
```

## Before you code

- Step one is always the same: count. `Counter(nums)`.
- Then you need "the k biggest counts". Sorting the counts is O(n log n) and totally acceptable today.

## Hints

<details>
<summary>Hint 1 · a nudge</summary>

Two steps. Count everything first. Then pick the top k from the counts. Don't try to do both at once.

</details>

<details>
<summary>Hint 2 · the idea</summary>

Version 1: `sorted(counts, key=counts.get, reverse=True)[:k]`. Done, O(n log n).
Version 2 (the O(n) one): **bucket sort**. Make a list of buckets indexed by frequency. `buckets[3] = [1]` means "1 appeared 3 times". Walk the buckets from the highest index down until you've collected k numbers.

</details>

<details>
<summary>Hint 3 · the skeleton (bucket version)</summary>

```
counts = Counter(nums)
buckets = [[] for _ in range(len(nums) + 1)]
for num, freq in counts.items():
    buckets[____].append(num)
result = []
for freq in range(len(buckets) - 1, 0, -1):
    for num in buckets[freq]:
        result.append(num)
        if len(result) == k: return result
```

Why is `len(nums) + 1` the right number of buckets?

</details>

## Explain it back

1. In one sentence, what is the trick?
2. Why can a frequency never exceed `len(nums)`?
3. When would you reach for a heap instead of bucket sort? (Preview of pattern 09.)
