"""Duplicate-free placement generation and correct-by-simulation solving."""

from __future__ import annotations

from collections.abc import Iterator
from itertools import combinations
from time import monotonic

from .model import Block, BlockKind, Board, Solution
from .simulator import trace


def placements(board: Board) -> Iterator[dict[tuple[int, int], Block]]:
    """Yield unique placements without permuting indistinguishable blocks."""

    cells = board.open_cells
    counts = tuple((kind, count) for kind, count in board.inventory if count)

    def visit(index: int, available: tuple[tuple[int, int], ...], current: dict):
        if index == len(counts):
            yield dict(current)
            return
        kind, count = counts[index]
        for chosen in combinations(available, count):
            chosen_set = set(chosen)
            for cell in chosen:
                current[cell] = Block(kind)
            remaining = tuple(cell for cell in available if cell not in chosen_set)
            yield from visit(index + 1, remaining, current)
            for cell in chosen:
                del current[cell]

    yield from visit(0, cells, {})


def solve(board: Board, timeout: float = 60.0) -> Solution | None:
    """Find the first valid board, or return ``None``; enforce a time limit."""

    if timeout <= 0:
        raise ValueError("timeout must be positive")
    started = monotonic()
    for tested, placement in enumerate(placements(board), 1):
        if monotonic() - started > timeout:
            raise TimeoutError(f"no solution found within {timeout:g} seconds")
        visited, paths = trace(board, placement)
        if board.targets <= visited:
            items = tuple(
                sorted((x, y, block.kind) for (x, y), block in placement.items())
            )
            return Solution(items, paths, tested, monotonic() - started)
    return None

