import io
import unittest

from ascii_art.media.video import VideoOptions, read_frame


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


if __name__ == "__main__":
    unittest.main()
