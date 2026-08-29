"""Small helpers shared by procedural renderers."""

from ascii_art.charsets import brightness_to_index


def shade(unit_brightness: float, ramp: str) -> str:
    value = max(0.0, min(1.0, unit_brightness)) * 255.0
    return ramp[brightness_to_index(value, len(ramp))]


def frame_to_text(buffer: list[list[str]]) -> str:
    return "\n".join("".join(row) for row in buffer)
