"""Stylized black-hole and accretion-disk renderer."""

import math
import random

from .common import frame_to_text, shade

BLACK_HOLE_RADIUS = 0.42
DISK_INNER = 0.52
DISK_OUTER = 1.55


def _stars(count: int = 180) -> tuple[tuple[float, float, float], ...]:
    randomizer = random.Random(42)
    return tuple(
        (
            randomizer.uniform(-2.0, 2.0),
            randomizer.uniform(-1.0, 1.0),
            randomizer.random(),
        )
        for _ in range(count)
    )


STARS = _stars()


def render_frame(frame_index: int, width: int, height: int, ramp: str) -> str:
    angle = frame_index * 0.045
    brightness_buffer = [[0.0] * width for _ in range(height)]

    for star_x, star_y, brightness in STARS:
        px = int(width / 2 + star_x * width / 2)
        py = int(height / 2 + star_y * height / 2)
        if 0 <= px < width and 0 <= py < height:
            brightness_buffer[py][px] = brightness

    for py in range(height):
        y = (py - height / 2) / (height / 2) * 2.0
        for px in range(width):
            x = (px - width / 2) / (width / 2)
            radius = math.sqrt(x * x + y * y)
            intensity = brightness_buffer[py][px]

            if DISK_INNER < radius < DISK_OUTER:
                theta = math.atan2(y, x)
                spiral = (math.sin((theta + angle) * 8 + radius * 12) + 1) / 2
                distance_factor = max(0.0, 1 - abs(radius - 0.95) / 0.63)
                disk = spiral * distance_factor
                disk += math.exp(-(radius - DISK_INNER) * 10) * 1.5
                doppler = 0.5 + 0.5 * math.cos(theta)
                disk *= 0.55 + doppler * 0.8
                intensity = max(intensity, disk)

            if radius < BLACK_HOLE_RADIUS:
                intensity = 0.0
            elif radius < DISK_OUTER:
                intensity += BLACK_HOLE_RADIUS / radius * 0.15

            ring_distance = abs(radius - BLACK_HOLE_RADIUS)
            intensity += math.exp(-ring_distance * 80) * 1.5
            brightness_buffer[py][px] = intensity

    output = [
        [shade(brightness_buffer[py][px], ramp) for px in range(width)]
        for py in range(height)
    ]
    return frame_to_text(output)
