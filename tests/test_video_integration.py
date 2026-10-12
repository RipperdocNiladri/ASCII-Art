"""Real FFmpeg and terminal checks; skipped when the required tools are absent."""

import os
import selectors
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

if os.name == "posix":
    import fcntl
    import termios


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires FFmpeg and FFprobe")
class VideoIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.video = Path(cls.directory.name) / "sample.mp4"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=10",
             "-t", "2", "-c:v", "mpeg4", str(cls.video)],
            check=True, capture_output=True, timeout=20,
        )

    def command(self, path: Path | None = None) -> list[str]:
        return [sys.executable, "-m", "terminal_ascii_art", "video", str(path or self.video),
                "--center", "--width", "40", "--fps", "10", "--no-audio"]

    def test_eof_restores_screen_in_color_and_monochrome(self) -> None:
        for color in (False, True):
            with self.subTest(color=color):
                result = subprocess.run(
                    self.command() + (["--color"] if color else []),
                    capture_output=True, timeout=10,
                    env={**os.environ, "COLUMNS": "80", "LINES": "24"},
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                self.assertEqual(result.stderr, b"")
                self.assertIn(b"\033[7;21H", result.stdout)
                self.assertIn(b"\033[?25h\033[?1049l", result.stdout)
                self.assertIn(b"Playback finished.", result.stdout)

    def test_corrupt_file_restores_screen_before_reporting_error(self) -> None:
        path = Path(self.directory.name) / "broken.mp4"
        path.write_bytes(b"not a video")
        result = subprocess.run(self.command(path), capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"\033[?25h\033[?1049l", result.stdout)
        self.assertIn(b"error:", result.stderr)

    @unittest.skipUnless(os.name == "posix", "requires a POSIX pseudoterminal")
    def test_real_window_resize_and_interrupt_restore_the_terminal(self) -> None:
        for color in (False, True):
            with self.subTest(color=color):
                master, slave = os.openpty()
                process = None
                captured = bytearray()
                try:
                    self.resize(master, 80, 24)
                    env = {**os.environ, "COLUMNS": "80", "LINES": "24"}
                    process = subprocess.Popen(
                        self.command() + (["--color"] if color else []),
                        stdin=subprocess.DEVNULL, stdout=slave, stderr=subprocess.PIPE,
                        start_new_session=True, env=env,
                    )
                    os.close(slave)
                    slave = -1
                    self.read_until(master, captured, b"\033[7;21H")
                    self.resize(master, 12, 8)
                    before = len(captured)
                    self.read_until(master, captured, b"\033[3;2H", start=before)
                    self.assertIn(b"\033[2J", captured[before:])
                    self.resize(master, 100, 60)
                    before = len(captured)
                    self.read_until(master, captured, b"\033[25;31H", start=before)
                    self.assertIn(b"\033[2J", captured[before:])
                    children_path = Path(f"/proc/{process.pid}/task/{process.pid}/children")
                    children = children_path.read_text().split() if children_path.exists() else []
                    process.send_signal(signal.SIGINT)
                    self.read_until(master, captured, b"\033[?25h\033[?1049l")
                    process.wait(timeout=5)
                    self.assertEqual(process.returncode, 0, process.stderr.read().decode())
                    for pid in children:
                        self.assertFalse(Path(f"/proc/{pid}").exists(), f"decoder {pid} was not reaped")
                finally:
                    if process is not None:
                        if process.poll() is None:
                            os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=5)
                        process.stderr.close()
                    os.close(master)
                    if slave >= 0:
                        os.close(slave)

    @unittest.skipUnless(os.name == "posix", "requires a POSIX pseudoterminal")
    def test_start_delay_can_be_cancelled_without_switching_screens(self) -> None:
        master, slave = os.openpty()
        process = subprocess.Popen(
            self.command() + ["--start-delay", "10"], stdin=subprocess.DEVNULL,
            stdout=slave, stderr=subprocess.PIPE, start_new_session=True,
        )
        os.close(slave)
        captured = bytearray()
        try:
            self.read_until(master, captured, b"Press Ctrl+C to cancel.")
            process.send_signal(signal.SIGINT)
            self.read_until(master, captured, b"Playback stopped.")
            process.wait(timeout=5)
            self.assertEqual(process.returncode, 0, process.stderr.read().decode())
            self.assertNotIn(b"\033[?1049h", captured)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
            process.stderr.close()
            os.close(master)

    @staticmethod
    def resize(fd: int, cols: int, rows: int) -> None:
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))

    def read_until(self, fd: int, captured: bytearray, pattern: bytes, *, start: int = 0) -> None:
        deadline = time.monotonic() + 5
        with selectors.DefaultSelector() as selector:
            selector.register(fd, selectors.EVENT_READ)
            while pattern not in captured[start:]:
                remaining = deadline - time.monotonic()
                self.assertGreater(remaining, 0, f"terminal did not produce {pattern!r}")
                if selector.select(remaining):
                    captured.extend(os.read(fd, 65536))


if __name__ == "__main__":
    unittest.main()
