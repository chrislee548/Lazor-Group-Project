"""Human-readable, machine-recoverable solution rendering."""

from __future__ import annotations

from pathlib import Path

from .model import Board, Solution


def format_solution(board: Board, solution: Solution) -> str:
    """Render a solved grid, placement list, paths, and search statistics."""

    grid = [list(row) for row in board.grid]
    for x, y, kind in solution.placement:
        grid[y][x] = kind.value
    lines = [
        "# Lazors solution", f"# source: {board.source or '<memory>'}",
        f"# candidates tested: {solution.tested}",
        f"# elapsed seconds: {solution.elapsed_seconds:.6f}", "", "GRID START",
    ]
    lines.extend(" ".join(row) for row in grid)
    lines.extend(["GRID STOP", "", "PLACEMENTS"])
    lines.extend(f"{kind.value} {x} {y}" for x, y, kind in solution.placement)
    lines.append("PATHS")
    for index, path in enumerate(solution.paths, 1):
        lines.append(f"{index}: " + " -> ".join(f"({p.x},{p.y})" for p in path))
    return "\n".join(lines) + "\n"


def write_solution(board: Board, solution: Solution, path: str | Path) -> Path:
    """Write a solution without silently overwriting an existing file."""

    destination = Path(path)
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing file: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(format_solution(board, solution), encoding="utf-8")
    return destination

