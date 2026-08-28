"""Procedural rotating planet renderer."""

import math

from .common import frame_to_text, shade

_LIGHT = (-0.6, 0.5, -1.0)
_LIGHT_LENGTH = math.sqrt(sum(component * component for component in _LIGHT))
LIGHT = tuple(component / _LIGHT_LENGTH for component in _LIGHT)


def _surface_pattern(x: float, y: float, z: float) -> float:
    value = math.sin(x * 7.0) + math.sin(y * 9.0) + math.sin(z * 8.0)
    return value + math.sin((x + y + z) * 14.0) * 0.5


def render_frame(frame_index: int, width: int, height: int, ramp: str) -> str:
    angle = frame_index * 0.035
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    buffer = [[" "] * width for _ in range(height)]

    for py in range(height):
        screen_y = (py - height / 2) / (height / 2) * 2.0
        for px in range(width):
            screen_x = (px - width / 2) / (width / 2)
            radius_squared = screen_x * screen_x + screen_y * screen_y
            if radius_squared > 1:
                continue

            screen_z = math.sqrt(1 - radius_squared)
            x = screen_x * cos_angle + screen_z * sin_angle
            z = -screen_x * sin_angle + screen_z * cos_angle
            y = screen_y

            brightness = x * LIGHT[0] + y * LIGHT[1] + z * LIGHT[2]
            if _surface_pattern(x, y, z) > 0.8:
                brightness += 0.15
            if brightness < 0:
                brightness *= 0.15

            edge = 1 - screen_z
            if edge > 0.82:
                brightness += (edge - 0.82) * 1.5

            buffer[py][px] = shade(brightness, ramp)

    return frame_to_text(buffer)
