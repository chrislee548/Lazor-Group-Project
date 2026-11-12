"""Regression tests for every group-created or specification-derived board."""

from pathlib import Path
import unittest

from lazor.parser import parse_bff
from lazor.simulator import trace
from lazor.solver import solve


ROOT = Path(__file__).resolve().parents[1]


class BoardSuiteTests(unittest.TestCase):
    def test_every_board_has_a_verified_solution(self):
        """Parse, solve, and independently retrace each board solution."""

        paths = sorted((ROOT / "boards").glob("*.bff"))
        self.assertGreaterEqual(len(paths), 5)
        for path in paths:
            with self.subTest(board=path.name):
                board = parse_bff(path)
                solution = solve(board, timeout=5)
                self.assertIsNotNone(solution)
                placement = {
                    (x, y): kind for x, y, kind in solution.placement
                }
                visited, _ = trace(board, placement)
                self.assertLessEqual(board.targets, visited)
                self.assertLess(solution.elapsed_seconds, 5)


if __name__ == "__main__":
    unittest.main()
