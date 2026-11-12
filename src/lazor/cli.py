"""Command-line interface for solving and validating Lazors boards."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .output import write_solution
from .parser import BFFError, parse_bff
from .solver import solve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lazor", description="Solve a Lazors .bff board")
    parser.add_argument("board", type=Path, help="input .bff board")
    parser.add_argument("-o", "--output", type=Path, help="solution path (default: <board>_solution.txt)")
    parser.add_argument("--timeout", type=float, default=60.0, help="seconds before stopping (default: 60)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        board = parse_bff(args.board)
        solution = solve(board, args.timeout)
        if solution is None:
            print("No solution exists for this board.", file=sys.stderr)
            return 1
        output = args.output or args.board.with_name(f"{args.board.stem}_solution.txt")
        write_solution(board, solution, output)
    except (BFFError, FileExistsError, TimeoutError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Solved after {solution.tested} candidate(s) in {solution.elapsed_seconds:.6f}s")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
