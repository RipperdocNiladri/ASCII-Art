import math
import random
import time


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 100
HEIGHT = int(WIDTH * 0.42)

FPS = 30

ROTATION_SPEED = 0.045

CHARS = " .:-=+*#%@"

# Black hole size
BLACK_HOLE_RADIUS = 0.42

# Accretion disk
DISK_INNER = 0.52
DISK_OUTER = 1.55


# ============================================================
# STAR FIELD
# ============================================================

random.seed(42)

STARS = []

for _ in range(180):

    x = random.uniform(
        -2.0,
        2.0
    )

    y = random.uniform(
        -1.0,
        1.0
    )

    brightness = random.random()

    STARS.append(
        (
            x,
            y,
            brightness
        )
    )


# ============================================================
# CLEAR TERMINAL
# ============================================================

def clear():

    print(
        "\033[2J\033[H",
        end=""
    )


# ============================================================
# MAIN
# ============================================================

def main():

    angle = 0.0

    frame_time = 1 / FPS

    clear()

    try:

        while True:

            start = time.perf_counter()


            # ------------------------------------------------
            # Buffers
            # ------------------------------------------------

            buffer = [
                [" "] * WIDTH
                for _ in range(HEIGHT)
            ]


            brightness_buffer = [
                [0.0] * WIDTH
                for _ in range(HEIGHT)
            ]


            # =================================================
            # BACKGROUND STARS
            # =================================================

            for sx, sy, brightness in STARS:

                px = int(
                    WIDTH / 2
                    + sx * WIDTH / 2
                )

                py = int(
                    HEIGHT / 2
                    + sy * HEIGHT / 2
                )

                if (
                    0 <= px < WIDTH
                    and
                    0 <= py < HEIGHT
                ):

                    brightness_buffer[
                        py
                    ][
                        px
                    ] = brightness


            # =================================================
            # ACCRETION DISK
            # =================================================

            for py in range(HEIGHT):

                for px in range(WIDTH):

                    x = (
                        (px - WIDTH / 2)
                        / (WIDTH / 2)
                    )

                    y = (
                        (py - HEIGHT / 2)
                        / (HEIGHT / 2)
                    )

                    # Correct terminal aspect
                    y *= 2.0


                    radius = math.sqrt(
                        x * x
                        + y * y
                    )


                    # ------------------------------------------------
                    # Disk
                    # ------------------------------------------------

                    if (
                        DISK_INNER
                        < radius
                        < DISK_OUTER
                    ):

                        # Angle around black hole
                        theta = math.atan2(
                            y,
                            x
                        )


                        # Rotate disk
                        rotated_theta = (
                            theta
                            + angle
                        )


                        # Spiral structure
                        spiral = (
                            math.sin(
                                rotated_theta * 8
                                + radius * 12
                            )
                            + 1
                        ) / 2


                        # Disk intensity
                        distance_factor = (
                            1
                            - abs(
                                radius - 0.95
                            )
                            / 0.63
                        )


                        distance_factor = max(
                            0,
                            distance_factor
                        )


                        intensity = (
                            spiral
                            * distance_factor
                        )


                        # Bright inner edge
                        inner_glow = math.exp(
                            -(
                                radius
                                - DISK_INNER
                            ) * 10
                        )


                        intensity += (
                            inner_glow * 1.5
                        )


                        # Relativistic-style Doppler effect
                        # One side is brighter.
                        doppler = (
                            0.5
                            + 0.5
                            * math.cos(
                                theta
                            )
                        )


                        intensity *= (
                            0.55
                            + doppler
                            * 0.8
                        )


                        # Add to buffer
                        if intensity > brightness_buffer[
                            py
                        ][
                            px
                        ]:

                            brightness_buffer[
                                py
                            ][
                                px
                            ] = intensity


                    # =================================================
                    # BLACK HOLE
                    # =================================================

                    if radius < BLACK_HOLE_RADIUS:

                        brightness_buffer[
                            py
                        ][
                            px
                        ] = 0


                    # =================================================
                    # GRAVITATIONAL LENSING
                    # =================================================

                    if (
                        BLACK_HOLE_RADIUS
                        < radius
                        < DISK_OUTER
                    ):

                        lens = (
                            BLACK_HOLE_RADIUS
                            / radius
                        )


                        if lens > 0.35:

                            brightness_buffer[
                                py
                            ][
                                px
                            ] += (
                                lens * 0.15
                            )


            # =================================================
            # EVENT HORIZON RING
            # =================================================

            for py in range(HEIGHT):

                for px in range(WIDTH):

                    x = (
                        (px - WIDTH / 2)
                        / (WIDTH / 2)
                    )

                    y = (
                        (py - HEIGHT / 2)
                        / (HEIGHT / 2)
                    )

                    y *= 2.0


                    radius = math.sqrt(
                        x * x
                        + y * y
                    )


                    # Bright photon-ring style edge
                    ring_distance = abs(
                        radius
                        - BLACK_HOLE_RADIUS
                    )


                    ring = math.exp(
                        -ring_distance * 80
                    )


                    brightness_buffer[
                        py
                    ][
                        px
                    ] += ring * 1.5


            # =================================================
            # CONVERT TO ASCII
            # =================================================

            for py in range(HEIGHT):

                for px in range(WIDTH):

                    brightness = (
                        brightness_buffer[
                            py
                        ][
                            px
                        ]
                    )


                    brightness = max(
                        0,
                        min(
                            1,
                            brightness
                        )
                    )


                    index = int(
                        brightness
                        * (
                            len(CHARS)
                            - 1
                        )
                    )


                    index = max(
                        0,
                        min(
                            len(CHARS) - 1,
                            index
                        )
                    )


                    buffer[
                        py
                    ][
                        px
                    ] = CHARS[index]


            # =================================================
            # DRAW
            # =================================================

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


            # =================================================
            # ROTATE
            # =================================================

            angle += ROTATION_SPEED


            # =================================================
            # FPS
            # =================================================

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

        clear()

        print(
            "🕳️ Black hole stopped."
        )


if __name__ == "__main__":

    main()