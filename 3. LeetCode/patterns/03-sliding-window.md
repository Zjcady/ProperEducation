# Sliding Window

**Reach for it when you see**
- "longest / shortest **substring or subarray** with property X"
- "contiguous"
- a brute force that re-examines the same elements over and over

**The move**
Two pointers that both move *forward*. Grow the right edge. When the window breaks the rule, shrink the left edge until it's valid again. Track the best size you've seen.

**Template**
```python
left = 0
state = {}                              # what's inside the window
best = 0
for right, x in enumerate(s):
    add(state, x)
    while window_is_invalid(state):     # shrink from the left
        remove(state, s[left])
        left += 1
    best = max(best, right - left + 1)
```

**Gotchas**
- Fixed-size window: no `while`, just drop `s[right - k]` each step.
- "Minimum window" flips it: shrink while *valid*, record best inside the loop.
- The window state is usually a count dict. Keep it honest on both add and remove.
