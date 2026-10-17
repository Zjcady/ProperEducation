# Arrays & Hashing

**Reach for it when you see**
- "find a pair / duplicate / count of something"
- "have I seen this before?"
- a nested loop that only exists to *look something up*

**The move**
Trade memory for time. One pass, and a `dict` or `set` remembers what you've already seen so you never rescan.

**Template**
```python
seen = {}                      # value -> index, or value -> count
for i, x in enumerate(nums):
    if x in seen:              # O(1) lookup replaces an inner loop
        ...
    seen[x] = i
```

**Gotchas**
- Check the dict *before* inserting the current item, or you'll match an item with itself.
- `collections.Counter(s)` is a dict of counts in one line.
- Sorting is O(n log n). Hashing is O(n). If you only need "same letters", a sorted string or a count tuple is a fine dict key.
