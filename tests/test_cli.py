import contextlib
import io
import unittest
from unittest import mock

from terminal_ascii_art import __version__
from terminal_ascii_art.cli import build_parser, main
from terminal_ascii_art.media.video import VideoOptions


class CliTests(unittest.TestCase):
    def test_version_option_reports_package_version(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            build_parser().parse_args(["--version"])
        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), f"ascii-art {__version__}")

    def test_list_command_describes_all_demos(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["list"]), 0)
        for name in ("cube", "sphere", "donut", "planet", "blackhole"):
            self.assertIn(name, output.getvalue())

    def test_video_arguments_are_parsed(self) -> None:
        args = build_parser().parse_args(
            ["video", "movie.mp4", "--color", "--fps", "15", "--no-audio"]
        )
        self.assertTrue(args.color)
        self.assertEqual(args.fps, 15)
        self.assertTrue(args.no_audio)

    def test_legacy_mono_option_overrides_color(self) -> None:
        args = build_parser().parse_args(["video", "movie.mp4", "--color", "--mono"])
        self.assertFalse(args.color)

    def test_video_defaults_to_monochrome(self) -> None:
        args = build_parser().parse_args(["video", "movie.mp4"])
        self.assertFalse(args.color)
        self.assertEqual(args.fps, 30.0)
        self.assertEqual(args.fps, VideoOptions().fps)
        self.assertEqual(args.start_delay, 0.0)
        self.assertEqual(args.start_delay, VideoOptions().start_delay)

    def test_start_delay_accepts_zero_positive_and_fractional_seconds(self) -> None:
        for value in ("0", "3", "0.25"):
            with self.subTest(value=value):
                args = build_parser().parse_args(["video", "movie.mp4", "--start-delay", value])
                self.assertEqual(args.start_delay, float(value))

    def test_start_delay_rejects_negative_non_finite_and_invalid_values(self) -> None:
        for value in ("-1", "nan", "inf", "-inf", "invalid"):
            with self.subTest(value=value):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                    build_parser().parse_args(["video", "movie.mp4", f"--start-delay={value}"])
                self.assertEqual(raised.exception.code, 2)

    @mock.patch("terminal_ascii_art.cli.play_video")
    def test_start_delay_is_passed_to_playback(self, play: mock.Mock) -> None:
        self.assertEqual(main(["video", "movie.mp4", "--start-delay", "3"]), 0)
        self.assertEqual(play.call_args.kwargs["options"].start_delay, 3.0)

    def test_invalid_fps_is_rejected(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            build_parser().parse_args(["demo", "cube", "--fps", "0"])

    def test_non_finite_fps_is_rejected(self) -> None:
        for value in ("nan", "inf", "-inf"):
            with self.subTest(value=value):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(
                    SystemExit
                ):
                    build_parser().parse_args(
                        ["demo", "cube", f"--fps={value}"]
                    )


if __name__ == "__main__":
    unittest.main()
