"""Procedural shaded sphere renderer."""

import math

from .common import frame_to_text, shade, sphere_point

_LIGHT = (-0.5, 0.8, -1.0)
_LIGHT_LENGTH = math.sqrt(sum(component * component for component in _LIGHT))
LIGHT = tuple(component / _LIGHT_LENGTH for component in _LIGHT)


def render_frame(frame_index: int, width: int, height: int, ramp: str) -> str:
    angle = frame_index * 0.04
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    # Orbit the light around the viewing axis, keeping it in front of the sphere.
    light_x = LIGHT[0] * cos_angle - LIGHT[1] * sin_angle
    light_y = LIGHT[0] * sin_angle + LIGHT[1] * cos_angle
    buffer = [[" "] * width for _ in range(height)]

    for py in range(height):
        for px in range(width):
            point = sphere_point(px, py, width, height)
            if point is None:
                continue
            x, y, z = point
            brightness = max(0.0, x * light_x + y * light_y + z * LIGHT[2])
            buffer[py][px] = shade(0.1 + 0.9 * brightness, ramp)

    return frame_to_text(buffer)
