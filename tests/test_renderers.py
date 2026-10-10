import unittest

from terminal_ascii_art.charsets import get_charset
from terminal_ascii_art.renderers import DEMOS
from terminal_ascii_art.terminal import CHAR_ASPECT


class RendererContractTests(unittest.TestCase):
    def test_every_demo_returns_the_requested_frame_size(self) -> None:
        ramp = get_charset("classic")
        for name, demo in DEMOS.items():
            with self.subTest(demo=name):
                frame = demo.render(3, 32, 14, ramp)
                lines = frame.split("\n")
                self.assertEqual(len(lines), 14)
                self.assertTrue(all(len(line) == 32 for line in lines))

    def test_cube_contains_a_visible_surface(self) -> None:
        frame = DEMOS["cube"].render(0, 40, 18, get_charset("classic"))
        self.assertTrue(any(character != " " for character in frame if character != "\n"))

    def test_spherical_demos_remain_round_at_different_grid_sizes(self) -> None:
        for name in ("sphere", "planet"):
            for width, height in ((80, 35), (40, 40), (160, 24), (1, 1)):
                with self.subTest(demo=name, width=width, height=height):
                    lines = DEMOS[name].render(0, width, height, "X").split("\n")
                    points = [
                        (x, y) for y, line in enumerate(lines)
                        for x, character in enumerate(line) if character == "X"
                    ]
                    self.assertTrue(points)
                    span_x = max(x for x, _ in points) - min(x for x, _ in points) + 1
                    span_y = max(y for _, y in points) - min(y for _, y in points) + 1
                    self.assertAlmostEqual(span_x * CHAR_ASPECT, span_y, delta=1.0)

    def test_spherical_demos_have_visible_front_lighting_throughout_animation(self) -> None:
        ramp = get_charset("classic")
        for name in ("sphere", "planet"):
            for frame_index in (0, 40, 80, 120):
                with self.subTest(demo=name, frame=frame_index):
                    lines = DEMOS[name].render(frame_index, 80, 35, ramp).split("\n")
                    self.assertGreaterEqual(ramp.index(lines[17][40]), 4)

    def test_spherical_demos_still_animate(self) -> None:
        for name in ("sphere", "planet"):
            with self.subTest(demo=name):
                render = DEMOS[name].render
                self.assertNotEqual(
                    render(0, 80, 35, get_charset("classic")),
                    render(20, 80, 35, get_charset("classic")),
                )


if __name__ == "__main__":
    unittest.main()
