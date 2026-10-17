import math

import planner

# shortest length in moves for each sample map; None means the goal can't be reached
LENGTHS = {"open": 10, "wall": 15, "astar_wins": 9, "no_path": None}


def parsed(name):
    return planner.parse_grid(planner.SAMPLE_MAPS[name])


def assert_valid_path(grid, path, start, goal):
    assert path[0] == start and path[-1] == goal
    assert len(set(path)) == len(path), "a shortest path never visits a cell twice"
    for r, c in path:
        assert planner.in_bounds(grid, (r, c))
        assert grid[r][c] != "#", f"path goes through a wall at {(r, c)}"
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        assert abs(r1 - r2) + abs(c1 - c2) == 1, f"{(r1, c1)} -> {(r2, c2)} is not one move"


# ---------------------------------------------------------------- step 1

def test_step1_neighbors_skip_walls_and_edges():
    grid, start, goal = planner.parse_grid("""
    S.#
    .#.
    ..G
    """)
    assert sorted(planner.neighbors(grid, start)) == [(0, 1), (1, 0)]
    assert planner.neighbors(grid, (0, 1)) == [(0, 0)]              # wall below and to the right
    assert sorted(planner.neighbors(grid, (2, 1))) == [(2, 0), (2, 2)]   # S and G are free cells
    assert sorted(planner.neighbors(grid, goal)) == [(1, 2), (2, 1)]


def test_step1_reconstruct_path_walks_back_from_goal():
    came_from = {(0, 1): (0, 0), (0, 2): (0, 1), (1, 2): (0, 2)}
    assert planner.reconstruct_path(came_from, (0, 0), (1, 2)) == [(0, 0), (0, 1), (0, 2), (1, 2)]
    assert planner.reconstruct_path({}, (3, 3), (3, 3)) == [(3, 3)]


def test_step1_bfs_finds_the_known_shortest_length_on_every_sample():
    for name in ("open", "wall", "astar_wins"):
        grid, start, goal = parsed(name)
        path, expanded = planner.bfs(grid, start, goal)
        assert path is not None, name
        assert len(path) - 1 == LENGTHS[name], name


def test_step1_bfs_paths_are_valid():
    for name in ("open", "wall", "astar_wins"):
        grid, start, goal = parsed(name)
        path, _ = planner.bfs(grid, start, goal)
        assert_valid_path(grid, path, start, goal)


def test_step1_bfs_unreachable_returns_none_after_looking_everywhere():
    grid, start, goal = parsed("no_path")
    path, expanded = planner.bfs(grid, start, goal)
    assert path is None
    assert expanded == 10          # every cell above the wall, each counted once


def test_step1_bfs_start_is_goal_and_expanded_is_counted():
    grid, start, goal = parsed("open")
    assert planner.bfs(grid, start, start) == ([start], 1)
    path, expanded = planner.bfs(grid, start, goal)
    free_cells = sum(row.count(".") for row in grid) + 2
    assert isinstance(expanded, int)
    assert len(path) <= expanded <= free_cells


# ---------------------------------------------------------------- step 2

def test_step2_manhattan_distance():
    assert planner.manhattan((0, 0), (0, 0)) == 0
    assert planner.manhattan((0, 0), (3, 4)) == 7
    assert planner.manhattan((5, 2), (1, 7)) == 9
    assert planner.manhattan((2, 9), (4, 1)) == planner.manhattan((4, 1), (2, 9))


def test_step2_astar_matches_bfs_length_on_every_sample():
    for name in planner.SAMPLE_MAPS:
        grid, start, goal = parsed(name)
        bfs_path, _ = planner.bfs(grid, start, goal)
        astar_path, _ = planner.astar(grid, start, goal)
        if LENGTHS[name] is None:
            assert bfs_path is None and astar_path is None, name
        else:
            assert len(astar_path) == len(bfs_path) == LENGTHS[name] + 1, name


def test_step2_astar_paths_are_valid():
    for name in ("open", "wall", "astar_wins"):
        grid, start, goal = parsed(name)
        path, _ = planner.astar(grid, start, goal)
        assert_valid_path(grid, path, start, goal)


def test_step2_astar_unreachable_returns_none():
    grid, start, goal = parsed("no_path")
    path, expanded = planner.astar(grid, start, goal)
    assert path is None
    assert expanded == 10


def test_step2_astar_expands_fewer_cells_than_bfs_on_the_designed_map():
    grid, start, goal = parsed("astar_wins")
    bfs_path, bfs_n = planner.bfs(grid, start, goal)
    astar_path, astar_n = planner.astar(grid, start, goal)
    assert len(astar_path) == len(bfs_path)
    assert astar_n < bfs_n, f"A* expanded {astar_n} cells, BFS {bfs_n}"


def test_step2_astar_is_deterministic():
    grid, start, goal = parsed("wall")
    runs = [planner.astar(grid, start, goal) for _ in range(3)]
    assert runs[0] == runs[1] == runs[2]
    assert_valid_path(grid, runs[0][0], start, goal)


def test_step2_heuristic_is_pluggable_and_zero_falls_back_to_dijkstra():
    grid, start, goal = parsed("astar_wins")
    path_h, n_h = planner.astar(grid, start, goal)
    path_0, n_0 = planner.astar(grid, start, goal, heuristic=lambda a, b: 0)
    assert len(path_0) == len(path_h)       # still a shortest path
    assert n_0 > n_h                        # but it had to look at far more cells


def test_step2_path_cost():
    assert planner.path_cost([(0, 0)]) == 0
    assert planner.path_cost([(0, 0), (0, 1), (1, 1)]) == 2
    assert planner.path_cost(None) == math.inf
    grid, start, goal = parsed("wall")
    path, _ = planner.astar(grid, start, goal)
    assert planner.path_cost(path) == LENGTHS["wall"]
