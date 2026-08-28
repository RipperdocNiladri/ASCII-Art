import contextlib
import io
import unittest

from ascii_art.cli import build_parser, main


class CliTests(unittest.TestCase):
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

    def test_invalid_fps_is_rejected(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            build_parser().parse_args(["demo", "cube", "--fps", "0"])


if __name__ == "__main__":
    unittest.main()
