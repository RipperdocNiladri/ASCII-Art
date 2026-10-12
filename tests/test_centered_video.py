import contextlib
import io
import re
import unittest
from pathlib import Path
from unittest import mock

from terminal_ascii_art.media.video import VideoOptions, VideoRenderError, _smooth, play_video


class CenteredVideoTests(unittest.TestCase):
    def _play(
        self, sizes: list[tuple[int, int]], *, color: bool = False,
        source: tuple[int, int] | None = (160, 90), width: int = 40,
        audio_delay: float = 0.0, render_error: BaseException | None = None,
        returncode: int = 0,
    ) -> tuple[list[dict], mock.Mock, mock.Mock, mock.Mock, str]:
        now = 0.0
        drawings = []
        output = io.StringIO()
        self.last_output = output
        decoder = mock.Mock(returncode=returncode)
        decoder.poll.return_value = None
        decoder.stderr = io.BytesIO(b"invalid input" if returncode else b"")
        audio = mock.Mock()
        audio.poll.return_value = None
        self.decoder, self.audio = decoder, audio

        def start_decoder(command: list[str], **_kwargs: object) -> mock.Mock:
            scale = re.search(r"scale=(\d+):(\d+)", command[command.index("-vf") + 1])
            cols, rows = map(int, scale.groups())
            frame = bytes([137]) * cols * rows * (3 if color else 1)
            decoder.stdout = io.BytesIO(frame * len(sizes))
            return decoder

        def sleep(seconds: float) -> None:
            nonlocal now
            self.assertGreaterEqual(seconds, 0)
            now += seconds

        def draw(frame: str, **kwargs: object) -> None:
            if render_error:
                raise render_error
            plain = re.sub(r"\033\[[0-9;]*m", "", frame)
            drawings.append({"lines": plain.split("\n"), "time": now, **kwargs})

        with contextlib.ExitStack() as stack:
            stack.enter_context(contextlib.redirect_stdout(output))
            patches = {
                "shutil.which": mock.Mock(return_value="ffmpeg"),
                "get_video_dimensions": mock.Mock(return_value=source),
                "terminal_size": mock.Mock(side_effect=[sizes[0], *sizes]),
                "subprocess.Popen": mock.Mock(side_effect=start_decoder),
                "_start_audio": mock.Mock(return_value=audio),
                "draw_frame": draw,
                "time.perf_counter": lambda: now,
                "time.sleep": sleep,
                "_smooth": mock.Mock(wraps=_smooth),
            }
            for name, replacement in patches.items():
                stack.enter_context(mock.patch("terminal_ascii_art.media.video." + name, replacement))
            stack.enter_context(mock.patch("terminal_ascii_art.terminal.terminal_size", return_value=sizes[0]))
            play_video(
                Path(__file__), options=VideoOptions(
                    center=True, max_width=width, color=color, fps=10,
                    smoothing=0.5, audio_delay=audio_delay,
                ), ramp=" .#",
            )
        decoder.terminate.assert_called_once_with()
        audio.terminate.assert_called_once_with()
        return drawings, patches["subprocess.Popen"], patches["_start_audio"], patches["_smooth"], output.getvalue()

    def test_live_resize_preserves_playback_and_audio_clock_in_both_modes(self) -> None:
        for color in (False, True):
            with self.subTest(color=color):
                drawings, decoder, audio, smooth, output = self._play(
                    [(80, 24), (12, 8), (100, 60)], color=color,
                )
                self.assertEqual([d["time"] for d in drawings], [0.0, 0.1, 0.2])
                self.assertEqual([(d["column"], d["row"]) for d in drawings], [(20, 6), (1, 2), (30, 24)])
                self.assertEqual([(len(d["lines"][0]), len(d["lines"])) for d in drawings], [(40, 11), (10, 3), (40, 11)])
                self.assertTrue(all(d["clear"] for d in drawings))
                self.assertTrue(all(call.args[1] is None for call in smooth.call_args_list))
                decoder.assert_called_once()
                audio.assert_called_once()
                self.assertIn("\033[?1049l", output)

    def test_moving_unchanged_grid_clears_once_and_retains_smoothing(self) -> None:
        drawings, _, _, smooth, _ = self._play([(80, 24), (83, 27), (83, 27)])
        self.assertEqual([d["clear"] for d in drawings], [True, True, False])
        self.assertEqual([(d["column"], d["row"]) for d in drawings], [(20, 6), (21, 8), (21, 8)])
        self.assertIsNone(smooth.call_args_list[0].args[1])
        self.assertIsNotNone(smooth.call_args_list[1].args[1])

    def test_odd_margins_differ_by_at_most_one_cell(self) -> None:
        drawings, _, _, _, _ = self._play([(81, 25)])
        d = drawings[0]
        self.assertLessEqual(abs(d["column"] - (81 - len(d["lines"][0]) - d["column"])), 1)
        self.assertLessEqual(abs(d["row"] - (25 - len(d["lines"]) - d["row"])), 1)

    def test_tiny_windows_keep_a_single_cell_without_negative_offsets(self) -> None:
        drawings, _, _, _, _ = self._play([(1, 1), (2, 2)])
        for d in drawings:
            self.assertEqual(d["lines"], ["."])
            self.assertEqual((d["column"], d["row"]), (0, 0))

    def test_wide_portrait_and_square_sources_fit_resized_windows(self) -> None:
        sizes = [(80, 24), (25, 50), (120, 15)]
        for source in ((320, 40), (40, 320), (100, 100)):
            with self.subTest(source=source):
                drawings, _, _, _, _ = self._play(sizes, source=source)
                for (cols, rows), d in zip(sizes, drawings):
                    width, height = len(d["lines"][0]), len(d["lines"])
                    self.assertLessEqual(width, min(40, cols - 2))
                    self.assertLessEqual(height, rows - 2)
                    self.assertGreaterEqual(d["column"], 0)
                    self.assertGreaterEqual(d["row"], 0)
                    self.assertLessEqual(d["column"] + width, cols)
                    self.assertLessEqual(d["row"] + height, rows)

    def test_large_width_does_not_upscale_the_decoder_beyond_native_size(self) -> None:
        drawings, decoder, _, _, _ = self._play([(80, 24)], source=(2, 2), width=10000)
        command = decoder.call_args.args[0]
        self.assertIn("scale=2:1:", command[command.index("-vf") + 1])
        self.assertLessEqual(len(drawings[0]["lines"][0]), 78)

    def test_unavailable_probe_retains_16_by_9_fallback(self) -> None:
        drawings, decoder, _, _, _ = self._play([(80, 24)], source=None)
        self.assertIn("scale=40:11:", decoder.call_args.args[0][decoder.call_args.args[0].index("-vf") + 1])
        self.assertEqual((len(drawings[0]["lines"][0]), len(drawings[0]["lines"])), (40, 11))

    def test_audio_offsets_survive_resizing(self) -> None:
        for delay, expected in ((-0.2, [0.2, 0.3, 0.4]), (0.15, [0.0, 0.1, 0.2])):
            with self.subTest(delay=delay):
                drawings, decoder, audio, _, _ = self._play([(80, 24), (12, 8), (100, 60)], audio_delay=delay)
                for d, timestamp in zip(drawings, expected):
                    self.assertAlmostEqual(d["time"], timestamp)
                decoder.assert_called_once()
                audio.assert_called_once()

    def test_interrupt_restores_screen_and_stops_media(self) -> None:
        _, _, _, _, output = self._play([(80, 24)], render_error=KeyboardInterrupt())
        self.assertIn("Playback stopped.", output)
        self.assertIn("\033[?25h\033[?1049l", output)

    def test_decoder_failure_is_reported_after_restoring_screen(self) -> None:
        with self.assertRaisesRegex(VideoRenderError, "invalid input"):
            self._play([(80, 24)], returncode=1)
        self.assertIn("\033[?25h\033[?1049l", self.last_output.getvalue())
        self.decoder.terminate.assert_called_once_with()
        self.audio.terminate.assert_called_once_with()

    def test_unexpected_render_error_restores_screen_and_stops_media(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "render failed"):
            self._play([(80, 24)], render_error=RuntimeError("render failed"))
        self.assertIn("\033[?25h\033[?1049l", self.last_output.getvalue())
        self.decoder.terminate.assert_called_once_with()
        self.audio.terminate.assert_called_once_with()

    def test_missing_file_and_media_tools_fail_before_switching_screens(self) -> None:
        cases = [
            (Path(__file__).with_name("missing-test-video.mp4"), "ffmpeg", "Video not found"),
            (Path(__file__), None, "FFmpeg was not found"),
            (Path(__file__), ["ffmpeg", None], "FFplay was not found"),
        ]
        for path, tools, message in cases:
            with self.subTest(message=message):
                output = io.StringIO()
                tool_mock = mock.Mock(side_effect=tools) if isinstance(tools, list) else mock.Mock(return_value=tools)
                with (
                    contextlib.redirect_stdout(output),
                    mock.patch("terminal_ascii_art.media.video.shutil.which", tool_mock),
                    mock.patch("terminal_ascii_art.media.video.subprocess.Popen") as decoder,
                    self.assertRaisesRegex(VideoRenderError, message),
                ):
                    play_video(path, options=VideoOptions(center=True), ramp=" .#")
                decoder.assert_not_called()
                self.assertNotIn("\033[?1049h", output.getvalue())


if __name__ == "__main__":
    unittest.main()
