# Binary Search

**Reach for it when you see**
- sorted input, or a *monotonic* yes/no question ("can we finish in h hours?")
- an O(log n) requirement
- "minimum X such that..." / "maximum X such that..."

**The move**
Keep a range that must contain the answer. Check the middle. Throw away the half that can't have it. Repeat until the range is one item.

**Template (first position where condition becomes true)**
```python
lo, hi = 0, len(nums) - 1
while lo < hi:
    mid = (lo + hi) // 2
    if condition(mid): hi = mid        # mid could be the answer
    else:              lo = mid + 1    # mid is definitely not
return lo
```

**Gotchas**
- Decide what `lo` and `hi` *mean* before writing the loop, then don't change your mind.
- Off-by-one bugs come from `hi = mid` vs `hi = mid - 1`. Use the template above and only move `lo = mid + 1`.
- Rotated arrays: one half is always sorted. Figure out which, decide if the target is in it.
- Binary search on the *answer*, not the array (Koko eating bananas): the array is the candidate speeds.
