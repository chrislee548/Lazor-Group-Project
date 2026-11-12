"""Repeatable local timing harness; these examples are not instructor boards."""

from pathlib import Path
from time import perf_counter

from lazor.parser import parse_bff
from lazor.solver import solve


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    paths = sorted((ROOT / "examples").glob("*.bff"))
    paths.extend(sorted((ROOT / "boards").glob("*.bff")))
    for path in paths:
        board = parse_bff(path)
        started = perf_counter()
        solution = solve(board, timeout=60)
        elapsed = perf_counter() - started
        status = "solved" if solution else "unsolved"
        tested = solution.tested if solution else "all"
        print(f"{path.name:24} {status:8} {elapsed:.6f}s candidates={tested}")


if __name__ == "__main__":
    main()
