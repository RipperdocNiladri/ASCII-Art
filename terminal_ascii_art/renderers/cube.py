"""Filled, lit cube with perspective projection and depth buffering."""

import math

from .common import frame_to_text, shade

CAMERA_DISTANCE = 3.0

VERTICES = (
    (-1.0, -1.0, -1.0),
    (1.0, -1.0, -1.0),
    (1.0, 1.0, -1.0),
    (-1.0, 1.0, -1.0),
    (-1.0, -1.0, 1.0),
    (1.0, -1.0, 1.0),
    (1.0, 1.0, 1.0),
    (-1.0, 1.0, 1.0),
)

# Counter-clockwise when viewed from outside the cube.
FACES = (
    (0, 3, 2, 1),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (2, 3, 7, 6),
    (1, 2, 6, 5),
    (0, 4, 7, 3),
)

_LIGHT = (-0.5, 0.8, -1.0)
_LIGHT_LENGTH = math.sqrt(sum(component * component for component in _LIGHT))
LIGHT = tuple(component / _LIGHT_LENGTH for component in _LIGHT)


def _rotate(
    point: tuple[float, float, float], angle_x: float, angle_y: float, angle_z: float
) -> tuple[float, float, float]:
    x, y, z = point
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
    cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
    return x * cos_z - y * sin_z, x * sin_z + y * cos_z, z


def _normal(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
    third: tuple[float, float, float],
) -> tuple[float, float, float]:
    ax, ay, az = (second[i] - first[i] for i in range(3))
    bx, by, bz = (third[i] - first[i] for i in range(3))
    nx, ny, nz = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    return nx / length, ny / length, nz / length


def _project(
    point: tuple[float, float, float], width: int, height: int
) -> tuple[float, float, float] | None:
    x, y, z = point
    depth = z + CAMERA_DISTANCE
    if depth <= 0:
        return None
    scale = min(width * 0.32, height * 0.75)
    return width / 2 + x * scale / depth, height / 2 - y * scale * 0.5 / depth, depth


def _barycentric(
    px: float,
    py: float,
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    c: tuple[float, float, float],
) -> tuple[float, float, float] | None:
    denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if abs(denominator) < 1e-9:
        return None
    first = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) / denominator
    second = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / denominator
    third = 1.0 - first - second
    if first < -1e-6 or second < -1e-6 or third < -1e-6:
        return None
    return first, second, third


def render_frame(frame_index: int, width: int, height: int, ramp: str) -> str:
    transformed = [
        _rotate(vertex, frame_index * 0.035, frame_index * 0.045, frame_index * 0.015)
        for vertex in VERTICES
    ]
    projected = [_project(vertex, width, height) for vertex in transformed]
    buffer = [[" "] * width for _ in range(height)]
    zbuffer = [[math.inf] * width for _ in range(height)]
    camera = (0.0, 0.0, -CAMERA_DISTANCE)

    for face in FACES:
        vertices = [transformed[index] for index in face]
        normal = _normal(vertices[0], vertices[1], vertices[2])
        center = tuple(sum(vertex[axis] for vertex in vertices) / 4 for axis in range(3))
        view = tuple(camera[axis] - center[axis] for axis in range(3))
        if sum(normal[axis] * view[axis] for axis in range(3)) <= 0:
            continue

        brightness = max(0.12, min(1.0, sum(normal[i] * LIGHT[i] for i in range(3))))
        character = shade(brightness, ramp)
        points = [projected[index] for index in face]
        if any(point is None for point in points):
            continue
        quad = [point for point in points if point is not None]

        for first, second, third in ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])):
            min_x = max(0, math.floor(min(first[0], second[0], third[0])))
            max_x = min(width - 1, math.ceil(max(first[0], second[0], third[0])))
            min_y = max(0, math.floor(min(first[1], second[1], third[1])))
            max_y = min(height - 1, math.ceil(max(first[1], second[1], third[1])))

            for py in range(min_y, max_y + 1):
                for px in range(min_x, max_x + 1):
                    weights = _barycentric(px + 0.5, py + 0.5, first, second, third)
                    if weights is None:
                        continue
                    depth = sum(weights[index] * point[2] for index, point in enumerate((first, second, third)))
                    if depth < zbuffer[py][px]:
                        zbuffer[py][px] = depth
                        buffer[py][px] = character

    return frame_to_text(buffer)
