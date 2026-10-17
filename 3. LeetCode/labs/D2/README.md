# D2 · Path planning: BFS then A*

**Maps to:** the responsibilities paragraph: "perception, motion/mission planning, controls". Motion planning at its smallest: a robot on a grid with walls, a start and a goal, and two ways to find the shortest route.
**You'll have at the end:** a planner that finds the shortest path on a grid map with BFS and again with A*, draws the route, and reports how many cells each search had to look at. The LeetCode grid patterns you already know, pointed at a robot.

Setup: `pip install -r requirements.txt` (pure Python; pytest is the only dependency). Tests are offline. `python3 planner.py` prints every sample map with both routes once your functions work.

Read `planner.py` first. A map is a list of strings: `.` free, `#` wall, `S` start, `G` goal. A cell is `(row, col)`. `parse_grid`, `in_bounds`, the four sample maps and `render_path` are done. Both planners return the same shape, `(path, nodes_expanded)`: `path` is a list of cells from start to goal inclusive, or `None` when the goal can't be reached. A cell counts as **expanded** the moment you pop it off the frontier; stop when the cell you popped is the goal.

## Step 1 · BFS  (15 min)

You write `neighbors`, `reconstruct_path` and `bfs`:

- `neighbors(grid, cell)`: the up/down/left/right cells that are in bounds and not `#`. `S` and `G` are free cells.
- `reconstruct_path(came_from, start, goal)`: `came_from[child] = parent`. Start at the goal, follow parents back to the start, reverse. Start to goal inclusive.
- `bfs(grid, start, goal)`: a `deque` frontier, a `seen` set, a `came_from` dict. Pop, count it, check for the goal, then push each unseen neighbor (mark it seen and record its parent at push time so no cell is queued twice). Return `(reconstruct_path(...), nodes_expanded)`, or `(None, nodes_expanded)` when the frontier runs dry.

Same loop as the LeetCode grid problems. The only new thing is counting.

## Step 2 · A*  (15 min)

You write `manhattan`, `astar` and `path_cost`:

- `manhattan(a, b)`: `|dr| + |dc|`, the number of moves if no walls were in the way. It never overestimates the real distance, and that is what keeps A* optimal.
- `astar(grid, start, goal, heuristic=manhattan)`: a `heapq` of `(f, g, cell)` tuples, where `g` is moves from the start and `f = g + heuristic(cell, goal)`. Keep `g_score` (best g per cell), `came_from` and a `closed` set. Pop the smallest; if the cell is already closed it is a stale entry, skip it without counting; otherwise count it, check for the goal, and push every neighbor whose `g + 1` beats its `g_score`. Ties on `f` break on `g`, then on the cell itself, so two runs always pop in the same order. (On this unit-cost grid a cell is always first reached with its best `g`, so the stale-entry skip never fires here; it matters once moves have different costs. Keep it anyway: it's part of the algorithm.)
- `path_cost(path)`: moves in the path, `len(path) - 1`. `None` costs `float("inf")`.

Run `python3 planner.py` and compare the expanded counts. On `open` A* saves nothing; on `astar_wins` it skips most of the map. Be ready to say why for each. Then rubric review and `python3 coach.py done D2`.
