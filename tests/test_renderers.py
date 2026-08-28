import unittest

from ascii_art.charsets import get_charset
from ascii_art.renderers import DEMOS


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


if __name__ == "__main__":
    unittest.main()
