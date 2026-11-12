from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lazor.model import BlockKind
from lazor.output import write_solution
from lazor.parser import parse_bff
from lazor.solver import placements, solve


ROOT = Path(__file__).resolve().parents[1]


class SolverTests(unittest.TestCase):
    def test_placement_generator_does_not_duplicate_identical_blocks(self):
        board = parse_bff(ROOT / "examples" / "reflect.bff")
        generated = list(placements(board))
        self.assertEqual(len(generated), 4)
        self.assertTrue(all(len(value) == 1 for value in generated))

    def test_solver_finds_reflector_location(self):
        board = parse_bff(ROOT / "examples" / "reflect.bff")
        solution = solve(board, timeout=1)
        self.assertIsNotNone(solution)
        self.assertIn((0, 0, BlockKind.REFLECT), solution.placement)

    def test_solution_writer_refuses_overwrite(self):
        board = parse_bff(ROOT / "examples" / "reflect.bff")
        solution = solve(board, timeout=1)
        with TemporaryDirectory() as directory:
            output = Path(directory) / "solution.txt"
            write_solution(board, solution, output)
            with self.assertRaises(FileExistsError):
                write_solution(board, solution, output)


if __name__ == "__main__":
    unittest.main()

