"""Immutable domain objects used by the parser, simulator, and solver."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class BlockKind(str, Enum):
    """The three optical block behaviours from the assignment."""

    REFLECT = "A"
    OPAQUE = "B"
    REFRACT = "C"


@dataclass(frozen=True, slots=True)
class Block:
    """A block, optionally fixed, that owns its optical behaviour."""

    kind: BlockKind
    fixed: bool = False

    def outgoing_directions(
        self, vx: int, vy: int, orientation: str
    ) -> tuple[tuple[int, int], ...]:
        """Return ray direction(s) produced at this block's surface.

        An empty tuple means absorption. A refractive block returns both the
        transmitted and reflected directions.
        """

        if self.kind is BlockKind.OPAQUE:
            return ()
        if orientation == "vertical":
            reflected = (-vx, vy)
        elif orientation == "horizontal":
            reflected = (vx, -vy)
        else:
            raise ValueError(f"unknown block-face orientation: {orientation}")
        if self.kind is BlockKind.REFRACT:
            return ((vx, vy), reflected)
        return (reflected,)


@dataclass(frozen=True, slots=True)
class Point:
    """A coordinate on the half-cell laser lattice."""

    x: int
    y: int


@dataclass(frozen=True, slots=True)
class Laser:
    """A laser start point and diagonal unit direction."""

    start: Point
    vx: int
    vy: int


@dataclass(frozen=True, slots=True)
class Board:
    """A parsed puzzle before movable blocks are placed."""

    grid: tuple[tuple[str, ...], ...]
    inventory: tuple[tuple[BlockKind, int], ...]
    lasers: tuple[Laser, ...]
    targets: frozenset[Point]
    source: Path | None = None

    @property
    def width(self) -> int:
        return len(self.grid[0])

    @property
    def height(self) -> int:
        return len(self.grid)

    @property
    def lattice_width(self) -> int:
        return 2 * self.width

    @property
    def lattice_height(self) -> int:
        return 2 * self.height

    @property
    def open_cells(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (x, y) for y, row in enumerate(self.grid)
            for x, value in enumerate(row) if value == "o"
        )

    @property
    def fixed_blocks(self) -> dict[tuple[int, int], Block]:
        return {
            (x, y): Block(BlockKind(value), fixed=True)
            for y, row in enumerate(self.grid)
            for x, value in enumerate(row) if value in {"A", "B", "C"}
        }


@dataclass(frozen=True, slots=True)
class Solution:
    """A valid placement plus useful search and simulation evidence."""

    placement: tuple[tuple[int, int, BlockKind], ...]
    paths: tuple[tuple[Point, ...], ...]
    tested: int
    elapsed_seconds: float

