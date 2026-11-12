"""Deterministic half-cell ray tracing for Lazors optics."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping

from .model import Block, BlockKind, Board, Point


State = tuple[int, int, int, int]


def _entering_cell(x: int, y: int, vx: int, vy: int) -> tuple[tuple[int, int], str] | None:
    """Return the cell being entered and the boundary orientation."""

    if x % 2 == 0 and y % 2 == 1:  # vertical block edge
        return ((x // 2 if vx > 0 else x // 2 - 1, y // 2), "vertical")
    if x % 2 == 1 and y % 2 == 0:  # horizontal block edge
        return ((x // 2, y // 2 if vy > 0 else y // 2 - 1), "horizontal")
    return None


def trace(
    board: Board, placement: Mapping[tuple[int, int], Block | BlockKind]
) -> tuple[frozenset[Point], tuple[tuple[Point, ...], ...]]:
    """Trace every laser and refracted branch; return visited points and paths."""

    blocks = board.fixed_blocks
    blocks.update(
        {
            cell: value if isinstance(value, Block) else Block(value)
            for cell, value in placement.items()
        }
    )
    queue: deque[tuple[State, tuple[Point, ...]]] = deque(
        ((laser.start.x, laser.start.y, laser.vx, laser.vy), (laser.start,))
        for laser in board.lasers
    )
    visited_points: set[Point] = set()
    completed: list[tuple[Point, ...]] = []
    seen_states: set[State] = set()

    while queue:
        (x, y, vx, vy), path = queue.popleft()
        branch: list[Point] = list(path)
        while True:
            state = (x, y, vx, vy)
            if state in seen_states:
                completed.append(tuple(branch))
                break
            seen_states.add(state)
            visited_points.add(Point(x, y))
            contact = _entering_cell(x, y, vx, vy)
            if contact is not None:
                cell, orientation = contact
                block = blocks.get(cell)
                if block is None:
                    directions = ((vx, vy),)
                else:
                    directions = block.outgoing_directions(vx, vy, orientation)
                if not directions:
                    completed.append(tuple(branch))
                    break
                vx, vy = directions[0]
                for branch_vx, branch_vy in directions[1:]:
                    queue.append(((x, y, branch_vx, branch_vy), tuple(branch)))
            nx, ny = x + vx, y + vy
            if not (0 <= nx <= board.lattice_width and 0 <= ny <= board.lattice_height):
                completed.append(tuple(branch))
                break
            x, y = nx, ny
            point = Point(x, y)
            branch.append(point)
            visited_points.add(point)

    return frozenset(visited_points), tuple(completed)

