import contextlib
import io
import os
import unittest
from unittest import mock

from terminal_ascii_art.terminal import (
    draw_frame, fit_demo_size, fit_source_size, terminal_session, terminal_size,
)


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

    def test_video_grid_fits_extreme_window_and_source_shapes(self) -> None:
        for available in ((1, 1), (2, 2), (3, 3), (80, 24), (213, 49), (400, 120)):
            for source in ((1920, 1080), (1080, 1920), (100, 100), (4096, 256), (256, 4096)):
                for width in (1, 40, 220, 10000):
                    with self.subTest(available=available, source=source, width=width):
                        cols, rows = fit_source_size(*source, max_width=width, available=available)
                        self.assertGreaterEqual(cols, 1)
                        self.assertGreaterEqual(rows, 1)
                        self.assertLessEqual(cols, min(width, max(1, available[0] - 2)))
                        self.assertLessEqual(rows, max(1, available[1] - 2))

    def test_missing_terminal_dimensions_use_existing_fallback(self) -> None:
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("os.get_terminal_size", side_effect=OSError),
        ):
            self.assertEqual(terminal_size(), (120, 40))

    def test_live_dimensions_override_stale_exported_columns_and_lines(self) -> None:
        with (
            mock.patch.dict(os.environ, {"COLUMNS": "80", "LINES": "24"}),
            mock.patch("os.get_terminal_size", return_value=os.terminal_size((83, 27))),
        ):
            self.assertEqual(terminal_size(live=True), (83, 27))
            self.assertEqual(terminal_size(), (80, 24))

    def test_live_dimensions_fall_back_when_stdout_has_no_file_descriptor(self) -> None:
        with (
            contextlib.redirect_stdout(io.StringIO()),
            mock.patch.dict(os.environ, {"COLUMNS": "80", "LINES": "24"}),
        ):
            self.assertEqual(terminal_size(live=True), (80, 24))


class TerminalDrawingTests(unittest.TestCase):
    def test_positioning_keeps_every_line_at_the_same_column(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            draw_frame("AB\nCD", column=20, row=9)
        self.assertEqual(output.getvalue(), "\033[10;21HAB\033[11;21HCD")

    def test_colored_and_blank_lines_keep_their_position(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            draw_frame("\033[31mAB\033[0m\n  \nCD", column=1)
        self.assertEqual(
            output.getvalue(), "\033[1;2H\033[31mAB\033[0m\033[2;2H  \033[3;2HCD",
        )

    def test_clear_erases_previous_frame_before_positioning(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            draw_frame("A", column=1, row=1, clear=True)
        self.assertEqual(output.getvalue(), "\033[2J\033[2;2HA")

    def test_default_drawing_is_unchanged(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            draw_frame("AB\nCD")
        self.assertEqual(output.getvalue(), "\033[HAB\nCD")

    def test_alternate_screen_is_restored_on_all_normal_exit_paths(self) -> None:
        for error in (None, KeyboardInterrupt(), RuntimeError("decoder failed")):
            with self.subTest(error=error):
                output = io.StringIO()
                try:
                    with contextlib.redirect_stdout(output), terminal_session(alternate_screen=True):
                        if error is not None:
                            raise error
                except (KeyboardInterrupt, RuntimeError):
                    pass
                self.assertEqual(
                    output.getvalue(),
                    "\033[?1049h\033[2J\033[H\033[?25l\033[0m\033[?25h\033[?1049l",
                )

    def test_default_session_does_not_switch_screens(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), terminal_session():
            pass
        self.assertEqual(output.getvalue(), "\033[2J\033[H\033[?25l\033[0m\033[?25h\n")


if __name__ == "__main__":
    unittest.main()
