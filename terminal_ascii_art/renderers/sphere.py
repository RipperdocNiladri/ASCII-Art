"""Procedural shaded sphere renderer."""

import math

from .common import frame_to_text, shade

_LIGHT = (-0.5, 0.8, -1.0)
_LIGHT_LENGTH = math.sqrt(sum(component * component for component in _LIGHT))
LIGHT = tuple(component / _LIGHT_LENGTH for component in _LIGHT)


def render_frame(frame_index: int, width: int, height: int, ramp: str) -> str:
    angle = frame_index * 0.04
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    buffer = [[" "] * width for _ in range(height)]

    for py in range(height):
        y = (py - height / 2) / (height / 2) / 0.5
        for px in range(width):
            x = (px - width / 2) / (width / 2)
            distance = x * x + y * y
            if distance > 1:
                continue

            z = math.sqrt(1 - distance)
            rotated_x = x * cos_angle - z * sin_angle
            rotated_z = x * sin_angle + z * cos_angle
            brightness = (
                rotated_x * LIGHT[0] + y * LIGHT[1] + rotated_z * LIGHT[2]
            )
            buffer[py][px] = shade(max(0.0, brightness), ramp)

    return frame_to_text(buffer)
