import math
import time


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 90

# Height is automatically calculated from WIDTH
HEIGHT = int(WIDTH * 0.42)

FPS = 30

# Planet rotation speed
ROTATION_SPEED = 0.035

# ASCII shading
CHARS = " .:-=+*#%@"

# Light direction
LIGHT_X = -0.6
LIGHT_Y = 0.5
LIGHT_Z = -1.0


# ============================================================
# NORMALIZE LIGHT
# ============================================================

light_length = math.sqrt(
    LIGHT_X ** 2 +
    LIGHT_Y ** 2 +
    LIGHT_Z ** 2
)

LIGHT_X /= light_length
LIGHT_Y /= light_length
LIGHT_Z /= light_length


# ============================================================
# CLEAR TERMINAL
# ============================================================

def clear():

    print(
        "\033[2J\033[H",
        end=""
    )


# ============================================================
# PLANET SURFACE PATTERN
# ============================================================

def surface_pattern(x, y, z):

    # Artificial continents / terrain
    value = (
        math.sin(x * 7.0)
        + math.sin(y * 9.0)
        + math.sin(z * 8.0)
    )

    value += (
        math.sin(
            (x + y + z) * 14
        )
        * 0.5
    )

    return value


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

            buffer = [
                [" "] * WIDTH
                for _ in range(HEIGHT)
            ]


            # ------------------------------------------------
            # Render sphere
            # ------------------------------------------------

            for py in range(HEIGHT):

                for px in range(WIDTH):

                    # Normalized screen coordinates
                    sx = (
                        (px - WIDTH / 2)
                        / (WIDTH / 2)
                    )

                    sy = (
                        (py - HEIGHT / 2)
                        / (HEIGHT / 2)
                    )


                    # Correct terminal character aspect ratio
                    sy *= 2.0


                    r2 = (
                        sx * sx
                        + sy * sy
                    )


                    if r2 > 1:
                        continue


                    # Sphere surface
                    sz = math.sqrt(
                        1 - r2
                    )


                    # ------------------------------------------------
                    # Rotate planet around Y axis
                    # ------------------------------------------------

                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)

                    x = (
                        sx * cos_a
                        + sz * sin_a
                    )

                    z = (
                        -sx * sin_a
                        + sz * cos_a
                    )

                    y = sy


                    # ------------------------------------------------
                    # Lighting
                    # ------------------------------------------------

                    brightness = (
                        x * LIGHT_X
                        + y * LIGHT_Y
                        + z * LIGHT_Z
                    )


                    # ------------------------------------------------
                    # Surface pattern
                    # ------------------------------------------------

                    terrain = surface_pattern(
                        x,
                        y,
                        z
                    )


                    # Slightly modify brightness
                    if terrain > 0.8:

                        brightness += 0.15


                    # Night side
                    if brightness < 0:

                        brightness *= 0.15


                    # Atmospheric rim
                    edge = 1 - sz

                    if edge > 0.82:

                        brightness += (
                            edge - 0.82
                        ) * 1.5


                    brightness = max(
                        0,
                        min(
                            1,
                            brightness
                        )
                    )


                    # ------------------------------------------------
                    # ASCII character
                    # ------------------------------------------------

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


            # ------------------------------------------------
            # Rotate
            # ------------------------------------------------

            angle += ROTATION_SPEED


            # ------------------------------------------------
            # FPS
            # ------------------------------------------------

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
            "🌍 Planet stopped."
        )


if __name__ == "__main__":

    main()