# Backtracking

**Reach for it when you see**
- "all combinations / permutations / subsets"
- "all ways to..."
- a grid where you explore paths and must not reuse cells

**The move**
Build a candidate one choice at a time. Recurse. Then **undo** the choice and try the next one. The undo is what makes it backtracking.

**Template**
```python
def backtrack(start, path):
    if is_complete(path):
        result.append(path[:])          # copy!
        return
    for i in range(start, len(options)):
        path.append(options[i])         # choose
        backtrack(i + 1, path)          # explore  (i, not i+1, if reuse allowed)
        path.pop()                      # un-choose
```

**Gotchas**
- `result.append(path[:])`, not `path`. Otherwise every answer is the same mutated list.
- Subsets: `start` index prevents duplicates. Permutations: a `used` set instead.
- Grid search: mark the cell visited (`board[r][c] = '#'`), recurse, then restore it.
