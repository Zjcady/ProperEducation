# D2 rubric

| # | Criterion |
|---|---|
| 1 | All tests pass offline. |
| 2 | Learner can explain why BFS returns a shortest path on an unweighted grid (level by level) and point to where in `bfs` a cell becomes "seen" vs "expanded". |
| 3 | `reconstruct_path` walks `came_from` from the goal back to the start; learner can say why the dict is child -> parent and not the other way round. |
| 4 | Learner can say what `g`, `h` and `f` are in one sentence each, and why Manhattan never overestimates on a 4-connected grid. |
| 5 | Learner can explain the `(f, g, cell)` heap entry: what each slot does for ordering and why the run is deterministic. |
| 6 | From the CLI output, learner can say why A* expands as many cells as BFS on `open` but far fewer on `astar_wins`. |
| 7 | Learner can name one thing that would change if moves had different costs (mud, slopes) and which function it lands in. |
