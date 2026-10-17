# Intervals

**Reach for it when you see**
- `[[start, end], ...]`
- "merge", "overlap", "insert", "minimum removals", "meeting rooms"

**The move**
Sort by start. Walk left to right, comparing each interval to the last one you kept. Two intervals overlap when `a.start <= b.end and b.start <= a.end`.

**Template**
```python
intervals.sort()
merged = [intervals[0]]
for start, end in intervals[1:]:
    if start <= merged[-1][1]:                 # overlap
        merged[-1][1] = max(merged[-1][1], end)
    else:
        merged.append([start, end])
```

**Gotchas**
- Draw two intervals on a number line before coding. Every overlap case is visible there.
- Non-overlapping Intervals: sort by **end**, keep the one that ends earliest. Greedy.
- `<=` vs `<` on the boundary depends on whether touching counts as overlapping. Read the problem.
