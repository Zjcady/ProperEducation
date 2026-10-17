# 004 · Group Anagrams  (medium)

Pattern: **Arrays & Hashing** → `patterns/01-arrays-hashing.md`
LeetCode: https://leetcode.com/problems/group-anagrams/

## The problem, in plain words

Given a list of words, group the ones that are anagrams of each other. Return the groups as a list of lists. Order of groups and order within a group don't matter.

## Example

```
input:  ["eat", "tea", "tan", "ate", "nat", "bat"]
output: [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
```

## Before you code

- Brute force: compare every word to every other word with yesterday's `isAnagram`. O(n² · k).
- Pattern signal: you want to throw words into buckets. Buckets = a dict. What's the **key**?

## Hints

<details>
<summary>Hint 1 · a nudge</summary>

Two anagrams need to land in the same bucket. So the bucket's key must be something that is *identical* for any two anagrams and *different* otherwise.

</details>

<details>
<summary>Hint 2 · the idea</summary>

Key option A: the sorted word. `"eat"`, `"tea"`, `"ate"` all become `"aet"`.
Key option B: a tuple of 26 letter counts. Faster, and it's the "real" interview answer.
Either way: `dict[key].append(word)`, then return the dict's values.

</details>

<details>
<summary>Hint 3 · the skeleton</summary>

```
from collections import defaultdict
groups = defaultdict(list)
for word in strs:
    key = ______________
    groups[key].append(word)
return list(groups.values())
```

</details>

## Explain it back

1. In one sentence, what is the trick?
2. Why can't a `list` be a dict key, and what do you use instead?
3. Compare the cost of key A vs key B when words are long.
