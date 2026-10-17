# Greedy

**Reach for it when you see**
- "maximum subarray", "can you reach the end", "minimum number of..."
- a local choice that never needs to be undone

**The move**
Make the best choice right now, carry one or two numbers forward, never look back. The hard part is *proving* the local choice is safe. If you can't say why, it's probably DP instead.

**Templates**
```python
# Kadane (max subarray): a running sum that resets when it goes negative
best = cur = nums[0]
for x in nums[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)

# Jump Game: the farthest index reachable so far
reach = 0
for i, jump in enumerate(nums):
    if i > reach: return False
    reach = max(reach, i + jump)
return True
```

**Gotchas**
- Kadane: `cur = max(x, cur + x)` means "start fresh here, or extend". That's the whole idea.
- Greedy usually needs sorting first (intervals, meetings).
