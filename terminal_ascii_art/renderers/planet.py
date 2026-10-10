"""Procedural rotating planet renderer."""

import math

from .common import frame_to_text, shade, sphere_point

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
        for px in range(width):
            point = sphere_point(px, py, width, height)
            if point is None:
                continue

            screen_x, screen_y, screen_z = point
            x = screen_x * cos_angle + screen_z * sin_angle
            z = -screen_x * sin_angle + screen_z * cos_angle
            y = screen_y

            # The terrain rotates while sunlight stays fixed in world space.
            light = max(0.0, sum(point[i] * LIGHT[i] for i in range(3)))
            albedo = 1.0 if _surface_pattern(x, y, z) > 0.8 else 0.75
            brightness = 0.06 + light * albedo

            edge = 1 + screen_z
            if edge > 0.82:
                brightness += (edge - 0.82) * 1.5

            buffer[py][px] = shade(brightness, ramp)

    return frame_to_text(buffer)
