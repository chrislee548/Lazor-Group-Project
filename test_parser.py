from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lazor.model import BlockKind
from lazor.parser import BFFError, parse_bff


ROOT = Path(__file__).resolve().parents[1]


class ParserTests(unittest.TestCase):
    def test_reads_comments_fixed_blocks_and_inventory(self):
        board = parse_bff(ROOT / "examples" / "fixed_and_refract.bff")
        self.assertEqual(board.width, 2)
        self.assertEqual(board.fixed_blocks[(0, 0)].kind, BlockKind.REFRACT)
        self.assertTrue(board.fixed_blocks[(0, 0)].fixed)
        self.assertEqual(board.fixed_blocks[(1, 1)].kind, BlockKind.OPAQUE)
        self.assertEqual(len(board.lasers), 1)
        self.assertEqual(len(board.targets), 2)

    def test_rejects_ragged_grid_with_line_number(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "bad.bff"
            path.write_text("GRID START\no o\no\nGRID STOP\nL 0 1 1 1\nP 1 2\n")
            with self.assertRaisesRegex(BFFError, r"line 3: ragged"):
                parse_bff(path)

    def test_rejects_inventory_larger_than_open_space(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "bad.bff"
            path.write_text("GRID START\no\nGRID STOP\nA 2\nL 0 1 1 1\nP 1 2\n")
            with self.assertRaisesRegex(BFFError, "movable blocks"):
                parse_bff(path)


if __name__ == "__main__":
    unittest.main()

