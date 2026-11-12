from pathlib import Path
import unittest

from lazor.model import BlockKind, Board, Laser, Point
from lazor.parser import parse_bff
from lazor.simulator import trace


ROOT = Path(__file__).resolve().parents[1]


class SimulatorTests(unittest.TestCase):
    def test_direct_ray_hits_multiple_targets(self):
        board = parse_bff(ROOT / "examples" / "direct.bff")
        visited, _ = trace(board, {})
        self.assertLessEqual(board.targets, visited)

    def test_reflector_flips_component_normal_to_surface(self):
        board = parse_bff(ROOT / "examples" / "reflect.bff")
        visited, _ = trace(board, {(0, 0): BlockKind.REFLECT})
        self.assertIn(Point(3, 2), visited)

    def test_refractor_splits_into_transmitted_and_reflected_rays(self):
        board = parse_bff(ROOT / "examples" / "fixed_and_refract.bff")
        visited, paths = trace(board, {})
        self.assertLessEqual(board.targets, visited)
        self.assertGreaterEqual(len(paths), 2)

    def test_opaque_block_stops_at_contact_point(self):
        board = parse_bff(ROOT / "examples" / "reflect.bff")
        visited, _ = trace(board, {(0, 0): BlockKind.OPAQUE})
        self.assertEqual(visited, {Point(2, 1)})

    def test_multiple_lasers_collectively_cover_all_targets(self):
        board = Board(
            grid=(("o", "o"), ("o", "o")),
            inventory=tuple((kind, 0) for kind in BlockKind),
            lasers=(Laser(Point(0, 1), 1, 1), Laser(Point(4, 1), -1, 1)),
            targets=frozenset({Point(1, 2), Point(3, 2)}),
        )
        visited, paths = trace(board, {})
        self.assertLessEqual(board.targets, visited)
        self.assertEqual(len(paths), 2)


if __name__ == "__main__":
    unittest.main()

