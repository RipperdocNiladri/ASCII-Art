import math
import time


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 80
HEIGHT = 35

FPS = 30

RADIUS = 1.0

CHARS = " .:-=+*#%@"

CAMERA = 3.0


# Light direction
LIGHT = (
    -0.5,
    0.8,
    -1.0
)


# ============================================================
# NORMALIZE
# ============================================================

def normalize(x, y, z):

    length = math.sqrt(
        x*x + y*y + z*z
    )

    return (
        x / length,
        y / length,
        z / length
    )


LIGHT = normalize(*LIGHT)


# ============================================================
# MAIN
# ============================================================

def main():

    angle = 0

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

            depth = [
                [-9999] * WIDTH
                for _ in range(HEIGHT)
            ]


            # ------------------------------------------------
            # Surface
            # ------------------------------------------------

            for py in range(HEIGHT):

                for px in range(WIDTH):

                    x = (
                        (px - WIDTH / 2)
                        / (WIDTH / 2)
                    )

                    y = (
                        (py - HEIGHT / 2)
                        / (HEIGHT / 2)
                        / 0.5
                    )


                    distance = (
                        x*x + y*y
                    )


                    if distance > 1:
                        continue


                    z = math.sqrt(
                        1 - distance
                    )


                    # ------------------------------------------------
                    # Rotate sphere
                    # ------------------------------------------------

                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)

                    xr = (
                        x * cos_a
                        - z * sin_a
                    )

                    zr = (
                        x * sin_a
                        + z * cos_a
                    )


                    # ------------------------------------------------
                    # Surface normal
                    # ------------------------------------------------

                    nx = xr
                    ny = y
                    nz = zr


                    # ------------------------------------------------
                    # Lighting
                    # ------------------------------------------------

                    brightness = (
                        nx * LIGHT[0]
                        + ny * LIGHT[1]
                        + nz * LIGHT[2]
                    )


                    brightness = max(
                        0,
                        brightness
                    )


                    index = int(
                        brightness
                        * (len(CHARS) - 1)
                    )


                    index = max(
                        0,
                        min(
                            len(CHARS) - 1,
                            index
                        )
                    )


                    buffer[py][px] = (
                        CHARS[index]
                    )


            # ------------------------------------------------
            # Render
            # ------------------------------------------------

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


            angle += 0.04


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
            "Sphere stopped."
        )


if __name__ == "__main__":
    main()