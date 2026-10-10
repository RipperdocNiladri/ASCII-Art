"""Small helpers shared by procedural renderers."""

import math

from terminal_ascii_art.charsets import brightness_to_index
from terminal_ascii_art.terminal import CHAR_ASPECT


def shade(unit_brightness: float, ramp: str) -> str:
    value = max(0.0, min(1.0, unit_brightness)) * 255.0
    return ramp[brightness_to_index(value, len(ramp))]


def frame_to_text(buffer: list[list[str]]) -> str:
    return "\n".join("".join(row) for row in buffer)


def sphere_point(
    px: int, py: int, width: int, height: int
) -> tuple[float, float, float] | None:
    """Reconstruct a front-facing sphere with the terminal cell aspect ratio."""
    radius = 0.9 * min(width / 2, height / (2 * CHAR_ASPECT))
    x = (px + 0.5 - width / 2) / radius
    y = (height / 2 - py - 0.5) / (radius * CHAR_ASPECT)
    distance = x * x + y * y
    if distance > 1:
        return None
    return x, y, -math.sqrt(1 - distance)
