# Two Pointers

**Reach for it when you see**
- a **sorted** array, or something you're allowed to sort
- pairs or triples that need to hit a target
- "palindrome", "from both ends", "in place"

**The move**
Put one pointer at each end. Compare. Move the pointer that is on the wrong side of the target. Each step throws away part of the search space for a reason you can say out loud.

**Template**
```python
lo, hi = 0, len(nums) - 1
while lo < hi:
    total = nums[lo] + nums[hi]
    if total == target: return ...
    if total < target: lo += 1    # need bigger
    else:              hi -= 1    # need smaller
```

**Gotchas**
- Only works on sorted input. If it isn't sorted, sort it first, or this is a hashing problem.
- Skip duplicates with `while lo < hi and nums[lo] == nums[lo-1]` when the answer must be unique.
- 3Sum = fix one element, two-pointer the rest.
