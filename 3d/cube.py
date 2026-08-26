import math
import time


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 80

# Height is automatic
HEIGHT = 35

FPS = 30

ROTATION_SPEED_X = 0.035
ROTATION_SPEED_Y = 0.045
ROTATION_SPEED_Z = 0.015

CHARS = " .:-=+*#%@"

CAMERA_DISTANCE = 3.0
SCALE = 25


# ============================================================
# ROTATION
# ============================================================

def rotate_x(x, y, z, angle):

    c = math.cos(angle)
    s = math.sin(angle)

    return (
        x,
        y * c - z * s,
        y * s + z * c
    )


def rotate_y(x, y, z, angle):

    c = math.cos(angle)
    s = math.sin(angle)

    return (
        x * c + z * s,
        y,
        -x * s + z * c
    )


def rotate_z(x, y, z, angle):

    c = math.cos(angle)
    s = math.sin(angle)

    return (
        x * c - y * s,
        x * s + y * c,
        z
    )


# ============================================================
# PROJECTION
# ============================================================

def project(x, y, z):

    z += CAMERA_DISTANCE

    if z <= 0:
        return None

    factor = SCALE / z

    sx = int(
        WIDTH / 2 + x * factor
    )

    sy = int(
        HEIGHT / 2 - y * factor * 0.5
    )

    return sx, sy, z


# ============================================================
# POINT INSIDE TRIANGLE
# ============================================================

def edge_function(
    ax, ay,
    bx, by,
    cx, cy
):

    return (
        (cx - ax) * (by - ay)
        -
        (cy - ay) * (bx - ax)
    )


def point_in_triangle(
    px, py,
    a, b, c
):

    d1 = edge_function(
        a[0], a[1],
        b[0], b[1],
        px, py
    )

    d2 = edge_function(
        b[0], b[1],
        c[0], c[1],
        px, py
    )

    d3 = edge_function(
        c[0], c[1],
        a[0], a[1],
        px, py
    )

    has_negative = (
        d1 < 0
        or d2 < 0
        or d3 < 0
    )

    has_positive = (
        d1 > 0
        or d2 > 0
        or d3 > 0
    )

    return not (
        has_negative
        and has_positive
    )


# ============================================================
# MAIN
# ============================================================

def main():

    angle_x = 0.0
    angle_y = 0.0
    angle_z = 0.0

    frame_time = 1 / FPS

    print(
        "\033[2J\033[H",
        end=""
    )

    try:

        while True:

            start = time.perf_counter()

            buffer = [
                [" "] * WIDTH
                for _ in range(HEIGHT)
            ]

            zbuffer = [
                [-999999.0] * WIDTH
                for _ in range(HEIGHT)
            ]


            # ====================================================
            # CUBE VERTICES
            # ====================================================

            vertices = [

                (-1, -1, -1),
                ( 1, -1, -1),
                ( 1,  1, -1),
                (-1,  1, -1),

                (-1, -1,  1),
                ( 1, -1,  1),
                ( 1,  1,  1),
                (-1,  1,  1)
            ]


            transformed = []

            for x, y, z in vertices:

                x, y, z = rotate_x(
                    x, y, z,
                    angle_x
                )

                x, y, z = rotate_y(
                    x, y, z,
                    angle_y
                )

                x, y, z = rotate_z(
                    x, y, z,
                    angle_z
                )

                transformed.append(
                    (x, y, z)
                )


            projected = []

            for vertex in transformed:

                projected.append(
                    project(*vertex)
                )


            # ====================================================
            # CUBE FACES
            # ====================================================

            faces = [

                (0, 1, 2, 3),  # back
                (4, 5, 6, 7),  # front
                (0, 1, 5, 4),  # bottom
                (2, 3, 7, 6),  # top
                (1, 2, 6, 5),  # right
                (0, 3, 7, 4)   # left
            ]


            # Light direction
            lx = -0.5
            ly = 0.8
            lz = -1.0

            length = math.sqrt(
                lx * lx
                + ly * ly
                + lz * lz
            )

            lx /= length
            ly /= length
            lz /= length


            # ====================================================
            # RENDER EACH FACE
            # ====================================================

            for face in faces:

                v0 = transformed[face[0]]
                v1 = transformed[face[1]]
                v2 = transformed[face[2]]


                # ------------------------------------------------
                # Face normal
                # ------------------------------------------------

                ax = v1[0] - v0[0]
                ay = v1[1] - v0[1]
                az = v1[2] - v0[2]

                bx = v2[0] - v0[0]
                by = v2[1] - v0[1]
                bz = v2[2] - v0[2]


                nx = (
                    ay * bz
                    - az * by
                )

                ny = (
                    az * bx
                    - ax * bz
                )

                nz = (
                    ax * by
                    - ay * bx
                )


                normal_length = math.sqrt(
                    nx * nx
                    + ny * ny
                    + nz * nz
                )

                if normal_length == 0:
                    continue

                nx /= normal_length
                ny /= normal_length
                nz /= normal_length


                # ------------------------------------------------
                # Back-face culling
                # ------------------------------------------------

                center_z = sum(
                    transformed[i][2]
                    for i in face
                ) / 4

                if center_z < -0.1:
                    continue


                # ------------------------------------------------
                # Lighting
                # ------------------------------------------------

                brightness = (
                    nx * lx
                    + ny * ly
                    + nz * lz
                )

                brightness = max(
                    0.12,
                    brightness
                )

                brightness = min(
                    1.0,
                    brightness
                )


                char_index = int(
                    brightness
                    * (len(CHARS) - 1)
                )

                char_index = max(
                    0,
                    min(
                        len(CHARS) - 1,
                        char_index
                    )
                )

                char = CHARS[char_index]


                # ------------------------------------------------
                # Project face
                # ------------------------------------------------

                points = []

                for index in face:

                    p = projected[index]

                    if p is None:
                        break

                    points.append(p)

                if len(points) != 4:
                    continue


                # ------------------------------------------------
                # Bounding box
                # ------------------------------------------------

                min_x = max(
                    0,
                    int(
                        min(p[0] for p in points)
                    )
                )

                max_x = min(
                    WIDTH - 1,
                    int(
                        max(p[0] for p in points)
                    )
                )

                min_y = max(
                    0,
                    int(
                        min(p[1] for p in points)
                    )
                )

                max_y = min(
                    HEIGHT - 1,
                    int(
                        max(p[1] for p in points)
                    )
                )


                # ------------------------------------------------
                # Split quad into 2 triangles
                # ------------------------------------------------

                triangles = [

                    (
                        points[0],
                        points[1],
                        points[2]
                    ),

                    (
                        points[0],
                        points[2],
                        points[3]
                    )
                ]


                for p1, p2, p3 in triangles:

                    for py in range(
                        min_y,
                        max_y + 1
                    ):

                        for px in range(
                            min_x,
                            max_x + 1
                        ):

                            if not point_in_triangle(
                                px,
                                py,
                                p1,
                                p2,
                                p3
                            ):
                                continue


                            # ------------------------------------------------
                            # Approximate depth
                            # ------------------------------------------------

                            z = (
                                p1[2]
                                + p2[2]
                                + p3[2]
                            ) / 3


                            if (
                                z
                                >
                                zbuffer[py][px]
                            ):

                                zbuffer[
                                    py
                                ][
                                    px
                                ] = z

                                buffer[
                                    py
                                ][
                                    px
                                ] = char


            # ====================================================
            # DRAW
            # ====================================================

            print(
                "\033[H",
                end=""
            )

            print(
                "\n".join(
                    "".join(row)
                    for row in buffer
                ),
                end="",
                flush=True
            )


            # ====================================================
            # ROTATION
            # ====================================================

            angle_x += ROTATION_SPEED_X
            angle_y += ROTATION_SPEED_Y
            angle_z += ROTATION_SPEED_Z


            # ====================================================
            # FPS
            # ====================================================

            elapsed = (
                time.perf_counter()
                - start
            )

            delay = (
                frame_time
                - elapsed
            )

            if delay > 0:
                time.sleep(delay)


    except KeyboardInterrupt:

        print(
            "\033[2J\033[H"
        )

        print(
            "🧊 Solid cube stopped."
        )


if __name__ == "__main__":
    main()