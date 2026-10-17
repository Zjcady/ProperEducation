# Graphs

**Reach for it when you see**
- a grid where you count regions, flood, or spread
- "connected", "reachable", "cycle", "prerequisites", "order"
- `edges = [[a, b], ...]` or an adjacency list

**The move**
Pick DFS or BFS. DFS for "explore everything connected to here". BFS for "shortest number of steps" or "spread one layer at a time". Always keep a `visited` set.

**Templates**
```python
# grid DFS (islands)
def dfs(r, c):
    if r < 0 or c < 0 or r >= R or c >= C or grid[r][c] != '1': return
    grid[r][c] = '0'                        # mark visited in place
    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
        dfs(r + dr, c + dc)

# BFS layers (rotting oranges, shortest path)
from collections import deque
q = deque(starts); steps = 0
while q:
    for _ in range(len(q)):
        r, c = q.popleft()
        ...push unvisited neighbors
    steps += 1
```

**Gotchas**
- Course Schedule is "does this directed graph have a cycle?" Use three colors: unvisited, in-progress, done. In-progress twice = cycle.
- Build the adjacency list first, with `defaultdict(list)`, before any traversal.
- Network Delay Time is Dijkstra: BFS with a heap keyed by distance.
