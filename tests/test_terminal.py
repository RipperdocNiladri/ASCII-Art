import unittest

from ascii_art.terminal import fit_demo_size, fit_source_size


class TerminalSizingTests(unittest.TestCase):
    def test_source_aspect_ratio_accounts_for_character_cells(self) -> None:
        self.assertEqual(
            fit_source_size(1920, 1080, max_width=100, available=(120, 40)),
            (100, 28),
        )

    def test_source_is_reduced_when_terminal_height_is_tight(self) -> None:
        self.assertEqual(fit_source_size(1920, 1080, available=(80, 10)), (28, 8))

    def test_demo_uses_defaults_within_terminal_bounds(self) -> None:
        self.assertEqual(
            fit_demo_size(default_width=80, height_ratio=0.44, available=(120, 50)),
            (80, 35),
        )

    def test_demo_respects_explicit_dimensions(self) -> None:
        self.assertEqual(
            fit_demo_size(
                default_width=80,
                height_ratio=0.44,
                width=60,
                height=20,
                available=(120, 50),
            ),
            (60, 20),
        )


if __name__ == "__main__":
    unittest.main()
