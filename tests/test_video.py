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
    _render_mono,
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


if __name__ == "__main__":
    unittest.main()
