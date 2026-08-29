"""Terminal sizing, drawing, and animation lifecycle helpers."""

from __future__ import annotations

import contextlib
import os
import shutil
import sys
import time
from collections.abc import Callable, Iterator

CHAR_ASPECT = 0.5


def terminal_size(fallback: tuple[int, int] = (120, 40)) -> tuple[int, int]:
    size = shutil.get_terminal_size(fallback=fallback)
    return size.columns, size.lines


def fit_source_size(
    source_width: int,
    source_height: int,
    *,
    max_width: int | None = None,
    max_height: int | None = None,
    available: tuple[int, int] | None = None,
    char_aspect: float = CHAR_ASPECT,
) -> tuple[int, int]:
    """Fit source media into the terminal while preserving its visual ratio."""
    if source_width <= 0 or source_height <= 0:
        raise ValueError("Source dimensions must be positive.")
    if char_aspect <= 0:
        raise ValueError("Character aspect correction must be positive.")

    term_cols, term_rows = available or terminal_size()
    cols = max(1, term_cols - 2)
    rows_limit = max(1, term_rows - 2)

    if max_width is not None:
        cols = min(cols, max_width)
    if max_height is not None:
        rows_limit = min(rows_limit, max_height)

    source_ratio = source_height / source_width
    rows = max(1, round(cols * source_ratio * char_aspect))

    if rows > rows_limit:
        rows = rows_limit
        cols = max(1, round(rows / (source_ratio * char_aspect)))

    return cols, rows


def fit_demo_size(
    *,
    default_width: int,
    height_ratio: float,
    width: int | None = None,
    height: int | None = None,
    available: tuple[int, int] | None = None,
) -> tuple[int, int]:
    """Choose a terminal-safe character grid for a procedural demo."""
    if height_ratio <= 0:
        raise ValueError("Height ratio must be positive.")
    term_cols, term_rows = available or terminal_size()
    cols = min(width or default_width, max(1, term_cols - 2))
    rows = height or max(1, round(cols * height_ratio))

    if rows > max(1, term_rows - 1):
        rows = max(1, term_rows - 1)
        if height is None:
            cols = min(cols, max(1, round(rows / height_ratio)))

    return cols, rows


def _enable_windows_ansi() -> None:
    if os.name == "nt":
        os.system("")


@contextlib.contextmanager
def terminal_session() -> Iterator[None]:
    """Prepare the terminal and always restore its cursor and colors."""
    _enable_windows_ansi()
    sys.stdout.write("\033[2J\033[H\033[?25l")
    sys.stdout.flush()
    try:
        yield
    finally:
        sys.stdout.write("\033[0m\033[?25h\n")
        sys.stdout.flush()


def draw_frame(frame: str) -> None:
    sys.stdout.write("\033[H")
    sys.stdout.write(frame)
    sys.stdout.flush()


def run_animation(
    render_frame: Callable[[int], str],
    *,
    fps: float,
    stopped_message: str,
) -> None:
    """Render numbered frames at a stable target rate until interrupted."""
    if fps <= 0:
        raise ValueError("FPS must be positive.")

    frame_duration = 1.0 / fps
    next_frame_at = time.perf_counter()
    frame_index = 0

    try:
        with terminal_session():
            while True:
                draw_frame(render_frame(frame_index))
                frame_index += 1
                next_frame_at += frame_duration
                remaining = next_frame_at - time.perf_counter()
                if remaining > 0:
                    time.sleep(remaining)
                elif remaining < -frame_duration:
                    next_frame_at = time.perf_counter()
    except KeyboardInterrupt:
        print(stopped_message)
