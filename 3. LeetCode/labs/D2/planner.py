"""D2 · Path planning on a grid: BFS, then A*.

    python3 planner.py               every sample map, both planners
    python3 planner.py astar_wins    one map by name (open, wall, astar_wins, no_path)

A map is a list of strings: "." free, "#" wall, "S" start, "G" goal. A cell is (row, col).
Both planners return (path, nodes_expanded): path is a list of cells from start to goal
inclusive, or None when the goal can't be reached. Functions marked TODO(you) are yours.
"""
from __future__ import annotations

import heapq
import sys
from collections import deque
from typing import Callable

Cell = tuple[int, int]

# ------------------------------------------------------------------ sample maps

MAP_OPEN = """
S......
.......
.......
.......
......G
"""

# The only way past the wall is along the bottom row, so the route is 15 moves, not 7.
MAP_WALL = """
S..#...G
...#....
...#....
...#....
........
"""

# S and G share a row with open field above and below. The shortest path is the same for
# both planners; BFS fans out in every direction, A* walks the row.
MAP_ASTAR_WINS = """
...............
...............
...##..........
...............
..S........G...
...............
.........##....
...............
...............
"""

MAP_NO_PATH = """
S....
.....
#####
.....
....G
"""

SAMPLE_MAPS = {"open": MAP_OPEN, "wall": MAP_WALL, "astar_wins": MAP_ASTAR_WINS, "no_path": MAP_NO_PATH}


# ------------------------------------------------------------------ scaffolding

def parse_grid(text: str) -> tuple[list[str], Cell, Cell]:
    """(grid, start, goal) from a map string. Blank lines and indentation around the map are ignored."""
    grid = [line.strip() for line in text.strip().splitlines()]
    if any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("every row must have the same width")
    start = goal = None
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == "S":
                start = (r, c)
            elif ch == "G":
                goal = (r, c)
    if start is None or goal is None:
        raise ValueError("a map needs one S and one G")
    return grid, start, goal


def in_bounds(grid: list[str], cell: Cell) -> bool:
    r, c = cell
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])


def render_path(grid: list[str], path: list[Cell] | None) -> str:
    """The map with the route drawn as '*' (S and G stay). No path: the map unchanged."""
    rows = [list(row) for row in grid]
    for r, c in path or []:
        if rows[r][c] == ".":
            rows[r][c] = "*"
    return "\n".join("".join(row) for row in rows)


# ------------------------------------------------------------------ step 1

def neighbors(grid: list[str], cell: Cell) -> list[Cell]:
    """TODO(you): the up/down/left/right cells around cell that are in bounds and not '#'."""
    raise NotImplementedError


def reconstruct_path(came_from: dict[Cell, Cell], start: Cell, goal: Cell) -> list[Cell]:
    """TODO(you): follow came_from (child -> parent) from goal back to start, then reverse. Start to goal inclusive."""
    raise NotImplementedError


def bfs(grid: list[str], start: Cell, goal: Cell) -> tuple[list[Cell] | None, int]:
    """TODO(you): breadth-first search. (path, nodes_expanded), or (None, nodes_expanded) when unreachable.

    A cell is expanded when it is popped off the frontier. Stop when the popped cell is the goal.
    """
    raise NotImplementedError


# ------------------------------------------------------------------ step 2

def manhattan(a: Cell, b: Cell) -> int:
    """TODO(you): |dr| + |dc|, the number of moves between a and b if no walls were in the way."""
    raise NotImplementedError


def astar(grid: list[str], start: Cell, goal: Cell,
          heuristic: Callable[[Cell, Cell], int] = manhattan) -> tuple[list[Cell] | None, int]:
    """TODO(you): A* over a heapq of (f, g, cell) entries. Same return shape as bfs.

    g is moves from the start, f = g + heuristic(cell, goal). Ties on f break on g, then on the
    cell, so the pop order is deterministic. A popped cell that is already closed is a stale
    entry: skip it without counting it.
    """
    raise NotImplementedError


def path_cost(path: list[Cell] | None) -> int | float:
    """TODO(you): the number of moves in path, len(path) - 1. None costs float('inf')."""
    raise NotImplementedError


# ------------------------------------------------------------------ CLI

def main(argv: list[str]) -> None:
    names = argv or list(SAMPLE_MAPS)
    for name in names:
        if name not in SAMPLE_MAPS:
            sys.exit(f"unknown map {name!r}; pick from: {', '.join(SAMPLE_MAPS)}")
        grid, start, goal = parse_grid(SAMPLE_MAPS[name])
        for label, planner in (("BFS", bfs), ("A*", astar)):
            path, expanded = planner(grid, start, goal)
            cost = "no path" if path is None else f"{path_cost(path)} moves"
            print(f"== {name} · {label}: {cost}, {expanded} cell(s) expanded")
            print(render_path(grid, path))
            print()


if __name__ == "__main__":
    main(sys.argv[1:])
