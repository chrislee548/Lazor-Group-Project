"""Strict but whitespace- and comment-tolerant parser for Lazors .bff files."""

from __future__ import annotations

from pathlib import Path

from .model import BlockKind, Board, Laser, Point


class BFFError(ValueError):
    """Raised when a board file is malformed or internally inconsistent."""


def _integer(token: str, line: int) -> int:
    try:
        return int(token)
    except ValueError as exc:
        raise BFFError(f"line {line}: expected integer, got {token!r}") from exc


def parse_bff(path: str | Path) -> Board:
    """Parse and validate one assignment-format ``.bff`` board."""

    source = Path(path)
    if source.suffix.lower() != ".bff":
        raise BFFError(f"expected a .bff file: {source}")
    try:
        raw_lines = source.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise BFFError(f"cannot read {source}: {exc}") from exc

    grid: list[tuple[str, ...]] = []
    inventory = {kind: 0 for kind in BlockKind}
    lasers: list[Laser] = []
    targets: set[Point] = set()
    in_grid = False
    saw_start = saw_stop = False

    for number, raw in enumerate(raw_lines, 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        upper = line.upper()
        if upper == "GRID START":
            if saw_start or in_grid:
                raise BFFError(f"line {number}: duplicate GRID START")
            saw_start = in_grid = True
            continue
        if upper == "GRID STOP":
            if not in_grid:
                raise BFFError(f"line {number}: GRID STOP without GRID START")
            in_grid = False
            saw_stop = True
            continue
        if in_grid:
            row = tuple(line.split())
            invalid = set(row) - {"o", "x", "A", "B", "C"}
            if invalid:
                raise BFFError(f"line {number}: invalid grid token(s): {sorted(invalid)}")
            if grid and len(row) != len(grid[0]):
                raise BFFError(f"line {number}: ragged grid row")
            if not row:
                raise BFFError(f"line {number}: empty grid row")
            grid.append(row)
            continue
        parts = line.split()
        key = parts[0].upper()
        if key in {"A", "B", "C"}:
            if len(parts) != 2:
                raise BFFError(f"line {number}: block count must be '<A|B|C> n'")
            count = _integer(parts[1], number)
            if count < 0:
                raise BFFError(f"line {number}: block count cannot be negative")
            inventory[BlockKind(key)] += count
        elif key == "L":
            if len(parts) != 5:
                raise BFFError(f"line {number}: laser must be 'L x y vx vy'")
            x, y, vx, vy = (_integer(value, number) for value in parts[1:])
            if (vx, vy) not in {(-1, -1), (-1, 1), (1, -1), (1, 1)}:
                raise BFFError(f"line {number}: laser direction must be diagonal +/-1")
            lasers.append(Laser(Point(x, y), vx, vy))
        elif key == "P":
            if len(parts) != 3:
                raise BFFError(f"line {number}: target must be 'P x y'")
            targets.add(Point(_integer(parts[1], number), _integer(parts[2], number)))
        else:
            raise BFFError(f"line {number}: unrecognized directive {parts[0]!r}")

    if in_grid or saw_start != saw_stop:
        raise BFFError("missing GRID STOP")
    if not grid:
        raise BFFError("board has no grid")
    if not lasers:
        raise BFFError("board has no lasers")
    if not targets:
        raise BFFError("board has no target points")
    movable = sum(inventory.values())
    open_count = sum(value == "o" for row in grid for value in row)
    if movable > open_count:
        raise BFFError(f"{movable} movable blocks but only {open_count} open cells")
    max_x, max_y = 2 * len(grid[0]), 2 * len(grid)
    for label, points in (
        ("laser", (laser.start for laser in lasers)), ("target", targets)
    ):
        for point in points:
            if not (0 <= point.x <= max_x and 0 <= point.y <= max_y):
                raise BFFError(f"{label} point {point} lies outside 0..{max_x}, 0..{max_y}")

    return Board(
        tuple(grid), tuple((kind, inventory[kind]) for kind in BlockKind),
        tuple(lasers), frozenset(targets), source,
    )

