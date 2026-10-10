import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy

from terminal_ascii_art.media.video import (
    VideoOptions,
    VideoRenderError,
    _render_color,
    _render_mono,
    _smooth,
    _stop_process,
    get_video_dimensions,
    play_video,
    read_frame,
)


class VideoHelperTests(unittest.TestCase):
    def test_read_frame_combines_short_reads(self) -> None:
        self.assertEqual(read_frame(io.BytesIO(b"abcdef"), 6), b"abcdef")

    def test_read_frame_rejects_partial_final_frame(self) -> None:
        self.assertIsNone(read_frame(io.BytesIO(b"abc"), 6))

    def test_video_defaults_are_safe(self) -> None:
        options = VideoOptions()
        self.assertGreater(options.fps, 0)
        self.assertGreater(options.max_width, 0)
        self.assertGreaterEqual(options.max_frame_skip, 0)

    def test_monochrome_render_maps_brightness_endpoints(self) -> None:
        frame = numpy.array([[0, 128, 255]], dtype=numpy.float32)
        self.assertEqual(_render_mono(frame, " .#", numpy), " .#")

    def test_monochrome_uses_nearest_shade_and_preserves_inversion(self) -> None:
        frame = numpy.array([[-10, 64, 191, 255, 300]], dtype=numpy.float32)
        self.assertEqual(_render_mono(frame, " .#", numpy), " ..##")
        self.assertEqual(_render_mono(frame, "#. ", numpy), "#..  ")

    def test_color_quantization_preserves_white(self) -> None:
        frame = numpy.array([[[255, 255, 255]]], dtype=numpy.float32)
        self.assertEqual(
            _render_color(frame, " .#", 4, numpy), "\033[38;2;255;255;255m#\033[0m"
        )

    def test_color_changes_characters_without_repeating_color(self) -> None:
        frame = numpy.array([[[96] * 3, [125] * 3]], dtype=numpy.float32)
        self.assertEqual(
            _render_color(frame, " .:-=+*#%@", 64, numpy),
            "\033[38;2;128;128;128m-=\033[0m",
        )

    def test_blank_color_cells_keep_dimensions_without_color_codes(self) -> None:
        frame = numpy.zeros((2, 3, 3), dtype=numpy.float32)
        self.assertEqual(_render_color(frame, " .#", 4, numpy), "   \033[0m\n   \033[0m")

    def test_smoothing_reduces_small_fluctuations(self) -> None:
        previous = numpy.array([[100]], dtype=numpy.float32)
        current = numpy.array([[104]], dtype=numpy.float32)
        for factor in (0.0, 0.35):
            with self.subTest(factor=factor):
                value = _smooth(current, previous, factor, numpy).item()
                self.assertGreater(value, 100)
                self.assertLess(value, 104)

    def test_smoothing_preserves_motion_and_scene_cuts_in_both_modes(self) -> None:
        for shape in ((2, 3), (2, 3, 3)):
            with self.subTest(shape=shape):
                previous = numpy.zeros(shape, dtype=numpy.float32)
                current = numpy.full(shape, 200, dtype=numpy.float32)
                numpy.testing.assert_array_equal(
                    _smooth(current, previous, 0.35, numpy), current
                )

    def test_color_smoothing_uses_one_blend_for_all_channels(self) -> None:
        previous = numpy.array([[[100, 100, 100]]], dtype=numpy.float32)
        current = numpy.array([[[150, 102, 100]]], dtype=numpy.float32)
        numpy.testing.assert_array_equal(_smooth(current, previous, 0.2, numpy), current)

    def test_smoothing_can_be_disabled_and_handles_the_first_frame(self) -> None:
        current = numpy.array([[100]], dtype=numpy.float32)
        previous = numpy.array([[99]], dtype=numpy.float32)
        self.assertIs(_smooth(current, previous, 1.0, numpy), current)
        self.assertIs(_smooth(current, None, 0.35, numpy), current)

    @mock.patch("terminal_ascii_art.media.video.subprocess.run")
    @mock.patch("terminal_ascii_art.media.video.shutil.which", return_value="ffprobe")
    def test_video_dimensions_are_read_from_ffprobe(
        self, _which: mock.Mock, run: mock.Mock
    ) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=["ffprobe"], returncode=0, stdout="1920x1080\n", stderr=""
        )

        self.assertEqual(get_video_dimensions(Path("movie.mp4")), (1920, 1080))
        self.assertEqual(run.call_args.args[0][0], "ffprobe")

    def test_missing_ffmpeg_has_a_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            video = Path(directory) / "movie.mp4"
            video.write_bytes(b"")
            with mock.patch(
                "terminal_ascii_art.media.video.shutil.which", return_value=None
            ):
                with self.assertRaisesRegex(VideoRenderError, "FFmpeg was not found"):
                    play_video(video, options=VideoOptions(audio=False), ramp=" .#")

    def test_process_cleanup_kills_a_process_that_will_not_stop(self) -> None:
        process = mock.Mock()
        process.poll.return_value = None
        process.wait.side_effect = subprocess.TimeoutExpired("ffmpeg", 2)

        _stop_process(process)

        process.terminate.assert_called_once_with()
        process.kill.assert_called_once_with()


class VideoPlaybackTests(unittest.TestCase):
    def _play(
        self,
        decode_delays: list[float],
        *,
        render_time: float = 0.0,
        audio_delay: float | None = None,
        start_delay: float = 0.0,
        max_frame_skip: int = 5,
    ) -> tuple[list[float], list[float]]:
        now = 0.0
        delays = iter(decode_delays)
        displayed_at = []
        audio_started_at = []

        def sleep(seconds: float) -> None:
            nonlocal now
            self.assertGreaterEqual(seconds, 0)
            now += seconds

        def read(*_args: object) -> bytes | None:
            delay = next(delays, None)
            if delay is None:
                return None
            sleep(delay)
            return b"\xff"

        def render(*_args: object) -> str:
            sleep(render_time)
            return "#"

        def start_audio(_video: Path) -> mock.Mock:
            audio_started_at.append(now)
            return mock.Mock()

        process = mock.Mock(returncode=0)

        def start_decoder(*_args: object, **_kwargs: object) -> mock.Mock:
            self.assertGreaterEqual(now, start_delay)
            return process

        with contextlib.ExitStack() as stack:
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            for name, replacement in (
                ("shutil.which", mock.Mock(return_value="ffmpeg")),
                ("get_video_dimensions", mock.Mock(return_value=(1, 1))),
                ("fit_source_size", mock.Mock(return_value=(1, 1))),
                ("subprocess.Popen", start_decoder),
                ("read_frame", read),
                ("_render_mono", render),
                ("_start_audio", start_audio),
                ("terminal_session", contextlib.nullcontext),
                ("draw_frame", lambda _frame: displayed_at.append(now)),
                ("time.perf_counter", lambda: now),
                ("time.sleep", sleep),
            ):
                stack.enter_context(mock.patch(f"terminal_ascii_art.media.video.{name}", replacement))
            play_video(
                Path(__file__),
                options=VideoOptions(
                    fps=10, audio=audio_delay is not None,
                    audio_delay=audio_delay or 0.0, max_frame_skip=max_frame_skip,
                    start_delay=start_delay,
                ),
                ramp=" .#",
            )
        return displayed_at, audio_started_at

    def test_decoder_startup_does_not_drop_initial_frames(self) -> None:
        displayed, audio = self._play([0.6, 0.0, 0.0], audio_delay=0.0)
        numpy.testing.assert_allclose(displayed, [0.6, 0.7, 0.8])
        self.assertEqual(audio, [0.6])

    def test_render_work_is_done_before_the_frame_deadline(self) -> None:
        displayed, audio = self._play([0.0, 0.0, 0.0], render_time=0.025)
        numpy.testing.assert_allclose(displayed, [0.025, 0.1, 0.2])
        self.assertEqual(audio, [])

    def test_frame_skipping_is_still_bounded(self) -> None:
        displayed, _audio = self._play([0.0, 0.65, 0.0, 0.0], max_frame_skip=2)
        numpy.testing.assert_allclose(displayed, [0.0, 0.65])

    def test_positive_audio_delay_is_checked_after_waiting_for_the_frame(self) -> None:
        displayed, audio = self._play([0.6, 0.0, 0.0], audio_delay=0.15)
        numpy.testing.assert_allclose(displayed, [0.6, 0.7, 0.8])
        numpy.testing.assert_allclose(audio, [0.8])

    def test_negative_audio_delay_gives_audio_a_head_start(self) -> None:
        displayed, audio = self._play([0.6, 0.0], audio_delay=-0.2)
        numpy.testing.assert_allclose(displayed, [0.8, 0.9])
        self.assertEqual(audio, [0.6])

    def test_empty_video_does_not_start_audio(self) -> None:
        self.assertEqual(self._play([], audio_delay=0.0), ([], []))

    def test_start_delay_waits_before_video_and_audio_without_dropping_frames(self) -> None:
        displayed, audio = self._play([0.6, 0.0, 0.0], start_delay=3.0, audio_delay=0.0)
        numpy.testing.assert_allclose(displayed, [3.6, 3.7, 3.8])
        numpy.testing.assert_allclose(audio, [3.6])

    def test_fractional_start_delay_works_without_audio(self) -> None:
        displayed, audio = self._play([0.0, 0.0], start_delay=0.25)
        numpy.testing.assert_allclose(displayed, [0.25, 0.35])
        self.assertEqual(audio, [])

    def test_start_delay_preserves_positive_and_negative_audio_offsets(self) -> None:
        for offset, first_frame, audio_start in ((0.15, 3.6, 3.8), (-0.2, 3.8, 3.6)):
            with self.subTest(offset=offset):
                displayed, audio = self._play(
                    [0.6, 0.0, 0.0], start_delay=3.0, audio_delay=offset
                )
                numpy.testing.assert_allclose(displayed, [first_frame, first_frame + 0.1, first_frame + 0.2])
                numpy.testing.assert_allclose(audio, [audio_start])

    def test_invalid_start_delay_is_rejected_by_playback(self) -> None:
        for value in (-1.0, float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(VideoRenderError, "Start delay must be"):
                    self._play([], start_delay=value)

    @mock.patch("terminal_ascii_art.media.video.shutil.which", return_value="ffmpeg")
    @mock.patch("terminal_ascii_art.media.video.get_video_dimensions", return_value=(1, 1))
    def test_start_delay_can_be_cancelled_before_starting_media(
        self, _dimensions: mock.Mock, _which: mock.Mock
    ) -> None:
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            mock.patch("terminal_ascii_art.media.video.time.sleep", side_effect=KeyboardInterrupt) as sleep,
            mock.patch("terminal_ascii_art.media.video.subprocess.Popen") as decoder,
            mock.patch("terminal_ascii_art.media.video._start_audio") as audio,
            mock.patch("terminal_ascii_art.media.video.terminal_session") as terminal,
        ):
            play_video(Path(__file__), options=VideoOptions(start_delay=3.0), ramp=" .#")
        sleep.assert_called_once_with(3.0)
        decoder.assert_not_called()
        audio.assert_not_called()
        terminal.assert_not_called()
        self.assertIn("Playback stopped.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
