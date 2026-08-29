"""Parametric torus renderer."""

import math

from .common import frame_to_text, shade


def render_frame(frame_index: int, width: int, height: int, ramp: str) -> str:
    angle_x = frame_index * 0.04
    angle_z = frame_index * 0.02
    cos_a = math.cos(angle_x)
    sin_a = math.sin(angle_x)
    cos_b = math.cos(angle_z)
    sin_b = math.sin(angle_z)

    output = [[" "] * width for _ in range(height)]
    zbuffer = [[0.0] * width for _ in range(height)]
    scale_x = width * 0.375
    scale_y = height * (15 / 35)

    theta = 0.0
    while theta < 2 * math.pi:
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        circle_x = 2.0 + cos_theta
        circle_y = sin_theta

        phi = 0.0
        while phi < 2 * math.pi:
            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)
            x = circle_x * cos_phi
            y = circle_x * sin_phi
            z = circle_y

            y2 = y * cos_a - z * sin_a
            z2 = y * sin_a + z * cos_a
            x2 = x * cos_b - y2 * sin_b
            y3 = x * sin_b + y2 * cos_b
            distance = z2 + 5.0
            if distance <= 0:
                phi += 0.04
                continue

            inverse_depth = 1.0 / distance
            screen_x = int(width / 2 + scale_x * inverse_depth * x2)
            screen_y = int(height / 2 + scale_y * inverse_depth * y3)

            if 0 <= screen_x < width and 0 <= screen_y < height:
                normal_x = cos_theta * cos_phi
                normal_y = cos_theta * sin_phi
                normal_z = sin_theta
                normal_y2 = normal_y * cos_a - normal_z * sin_a
                normal_z2 = normal_y * sin_a + normal_z * cos_a
                normal_y3 = normal_x * sin_b + normal_y2 * cos_b
                brightness = normal_y3 * 0.7 - normal_z2

                if brightness > 0 and inverse_depth > zbuffer[screen_y][screen_x]:
                    zbuffer[screen_y][screen_x] = inverse_depth
                    output[screen_y][screen_x] = shade(brightness, ramp)

            phi += 0.04
        theta += 0.07

    return frame_to_text(output)
