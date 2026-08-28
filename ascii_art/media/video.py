"""FFmpeg-backed monochrome and ANSI true-color video playback."""

from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

from ascii_art.terminal import draw_frame, fit_source_size, terminal_session


class VideoRenderError(RuntimeError):
    pass


@dataclass(frozen=True)
class VideoOptions:
    fps: float = 20.0
    max_width: int = 160
    color: bool = False
    smoothing: float = 1.0
    quantization: int = 4
    max_frame_skip: int = 5
    audio: bool = True
    audio_delay: float = 0.0


def _load_numpy() -> Any:
    try:
        import numpy
    except ImportError as exc:
        raise VideoRenderError(
            "Video rendering requires NumPy. Install the project dependencies first."
        ) from exc
    return numpy


def read_frame(stream: BinaryIO, size: int) -> bytes | None:
    """Read one complete raw frame, returning None for EOF or a partial frame."""
    data = bytearray()
    while len(data) < size:
        chunk = stream.read(size - len(data))
        if not chunk:
            return None
        data.extend(chunk)
    return bytes(data)


def get_video_dimensions(video: Path) -> tuple[int, int] | None:
    if shutil.which("ffprobe") is None:
        return None
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=p=0:s=x",
                str(video),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        width_text, height_text = result.stdout.strip().split("x")
        width, height = int(width_text), int(height_text)
        return (width, height) if width > 0 and height > 0 else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _frame_array(raw: bytes, rows: int, cols: int, color: bool, np: Any) -> Any:
    shape = (rows, cols, 3) if color else (rows, cols)
    return np.frombuffer(raw, dtype=np.uint8).reshape(shape).astype(np.float32)


def _smooth(current: Any, previous: Any | None, factor: float) -> Any:
    if previous is None or factor >= 0.999:
        return current
    return previous + (current - previous) * factor


def _render_mono(array: Any, ramp: str, np: Any) -> str:
    indices = np.clip(
        (array * (len(ramp) - 1) / 255).astype(np.int32), 0, len(ramp) - 1
    )
    return "\n".join("".join(ramp[index] for index in row) for row in indices.tolist())


def _render_color(array: Any, ramp: str, quantization: int, np: Any) -> str:
    brightness = 0.299 * array[..., 0] + 0.587 * array[..., 1] + 0.114 * array[..., 2]
    char_indices = np.clip(
        (brightness * (len(ramp) - 1) / 255).astype(np.int32), 0, len(ramp) - 1
    )
    clipped = np.clip(array, 0, 255)
    if quantization > 1:
        colors = (clipped // quantization * quantization).astype(np.int64)
    else:
        colors = clipped.astype(np.int64)

    key = (
        (colors[..., 0] << 40)
        | (colors[..., 1] << 32)
        | (colors[..., 2] << 24)
        | char_indices.astype(np.int64)
    )

    lines = []
    rows, cols = key.shape
    for y in range(rows):
        changes = np.flatnonzero(key[y, 1:] != key[y, :-1]) + 1
        starts = np.concatenate(([0], changes))
        ends = np.concatenate((changes, [cols]))
        parts = []
        for start, end in zip(starts.tolist(), ends.tolist()):
            red, green, blue = colors[y, start]
            character = ramp[char_indices[y, start]]
            parts.append(
                f"\033[38;2;{red};{green};{blue}m" + character * (end - start)
            )
        lines.append("".join(parts) + "\033[0m")
    return "\n".join(lines)


def _start_audio(video: Path) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        [
            "ffplay",
            "-nodisp",
            "-vn",
            "-autoexit",
            "-loglevel",
            "quiet",
            str(video),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _stop_process(process: subprocess.Popen[Any] | None) -> None:
    if process is None or process.poll() is not None:
        return
    try:
        process.terminate()
        process.wait(timeout=2)
    except (OSError, subprocess.SubprocessError):
        try:
            process.kill()
        except OSError:
            pass


def play_video(video: Path, *, options: VideoOptions, ramp: str) -> None:
    if not video.is_file():
        raise VideoRenderError(f"Video not found: {video}")
    if shutil.which("ffmpeg") is None:
        raise VideoRenderError("FFmpeg was not found on PATH.")
    if options.audio and shutil.which("ffplay") is None:
        raise VideoRenderError("FFplay was not found on PATH. Use --no-audio to continue.")

    np = _load_numpy()
    source_width, source_height = get_video_dimensions(video) or (16, 9)
    cols, rows = fit_source_size(source_width, source_height, max_width=options.max_width)
    pixel_format = "rgb24" if options.color else "gray"
    channels = 3 if options.color else 1
    frame_size = cols * rows * channels

    print(f"Video: {video.name}")
    print(f"Render: {cols} x {rows} characters at {options.fps:g} FPS")
    print(f"Mode: {'ANSI true-color' if options.color else 'monochrome'}")
    print(f"Audio: {'enabled' if options.audio else 'disabled'}")
    print("Starting... Press Ctrl+C to stop.")

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video),
        "-vf",
        f"fps={options.fps},scale={cols}:{rows}",
        "-f",
        "rawvideo",
        "-pix_fmt",
        pixel_format,
        "-",
    ]

    video_process: subprocess.Popen[bytes] | None = None
    audio_process: subprocess.Popen[bytes] | None = None
    interrupted = False

    try:
        video_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=10**8,
        )
        if video_process.stdout is None:
            raise VideoRenderError("FFmpeg did not provide a video stream.")

        if options.audio and options.audio_delay <= 0:
            audio_process = _start_audio(video)
            if options.audio_delay < 0:
                time.sleep(-options.audio_delay)

        start_time = time.perf_counter()
        audio_start_time = (
            start_time + options.audio_delay
            if options.audio and options.audio_delay > 0
            else None
        )
        frame_duration = 1.0 / options.fps
        frame_index = 0
        consecutive_drops = 0
        previous = None

        with terminal_session():
            while True:
                raw = read_frame(video_process.stdout, frame_size)
                if raw is None:
                    break

                now = time.perf_counter()
                if audio_start_time is not None and now >= audio_start_time:
                    audio_process = _start_audio(video)
                    audio_start_time = None

                target_time = start_time + frame_index * frame_duration
                frame_index += 1
                lag = now - target_time
                if lag > frame_duration and consecutive_drops < options.max_frame_skip:
                    consecutive_drops += 1
                    continue

                consecutive_drops = 0
                if lag < 0:
                    time.sleep(-lag)

                current = _frame_array(raw, rows, cols, options.color, np)
                current = _smooth(current, previous, options.smoothing)
                previous = current
                if options.color:
                    frame = _render_color(current, ramp, options.quantization, np)
                else:
                    frame = _render_mono(current, ramp, np)
                draw_frame(frame)

        video_process.wait(timeout=5)
        if video_process.returncode:
            decoder_error = ""
            if video_process.stderr is not None:
                decoder_error = video_process.stderr.read().decode(errors="replace").strip()
            raise VideoRenderError(decoder_error or "FFmpeg could not decode the video.")
    except KeyboardInterrupt:
        interrupted = True
    except OSError as exc:
        raise VideoRenderError(f"Could not start media playback: {exc}") from exc
    except subprocess.SubprocessError as exc:
        raise VideoRenderError(f"Media process failed: {exc}") from exc
    finally:
        _stop_process(video_process)
        _stop_process(audio_process)

    print("Playback stopped." if interrupted else "Playback finished.")
