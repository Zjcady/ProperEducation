# 003 · Valid Anagram  (easy)

Pattern: **Arrays & Hashing** → `patterns/01-arrays-hashing.md`
LeetCode: https://leetcode.com/problems/valid-anagram/

## The problem, in plain words

Two strings are anagrams if they contain exactly the same letters, the same number of times, in any order. Return `True` if `s` and `t` are anagrams.

## Example

```
input:  s = "anagram", t = "nagaram"
output: True

input:  s = "rat", t = "car"
output: False
```

## Before you code

- Brute force idea: sort both strings and compare. O(n log n). That works. Write it if you want.
- Pattern signal: "same letters, same counts" means **count** them.

## Hints

<details>
<summary>Hint 1 · a nudge</summary>

If the lengths differ, you're done immediately. After that, you don't care about order, only about how many of each letter.

</details>

<details>
<summary>Hint 2 · the idea</summary>

Build a count of letters for `s`. Walk `t` and subtract. If anything goes negative, or the counts don't match, not an anagram. `collections.Counter` does this in one line, but write the dict version once by hand.

</details>

<details>
<summary>Hint 3 · the skeleton</summary>

```
if len(s) != len(t): return False
counts = {}
for ch in s:
    counts[ch] = counts.get(ch, 0) + 1
for ch in t:
    if counts.get(ch, 0) == 0: return ____
    counts[ch] -= 1
return True
```

</details>

## Explain it back

1. In one sentence, what is the trick?
2. Why is the count approach O(n) and the sort approach O(n log n)?
3. Why does the early `len` check make the second loop's logic simpler?
