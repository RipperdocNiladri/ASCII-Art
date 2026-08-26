import math
import time


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 80
HEIGHT = 35

FPS = 30

CHARS = " .,-~:;=!*#$@"


# ============================================================
# MAIN
# ============================================================

def main():

    A = 0
    B = 0

    frame_time = 1 / FPS

    print(
        "\033[2J\033[H",
        end=""
    )

    try:

        while True:

            start = time.perf_counter()


            output = [
                [" "] * WIDTH
                for _ in range(HEIGHT)
            ]


            zbuffer = [
                [0] * WIDTH
                for _ in range(HEIGHT)
            ]


            # ------------------------------------------------
            # Torus
            # ------------------------------------------------

            theta = 0

            while theta < 2 * math.pi:

                phi = 0

                while phi < 2 * math.pi:

                    # Torus radius
                    R1 = 1
                    R2 = 2


                    cos_theta = math.cos(theta)
                    sin_theta = math.sin(theta)

                    cos_phi = math.cos(phi)
                    sin_phi = math.sin(phi)


                    circle_x = (
                        R2
                        + R1 * cos_theta
                    )

                    circle_y = (
                        R1 * sin_theta
                    )


                    # ------------------------------------------------
                    # 3D point
                    # ------------------------------------------------

                    x = (
                        circle_x * cos_phi
                    )

                    y = (
                        circle_x * sin_phi
                    )

                    z = circle_y


                    # ------------------------------------------------
                    # Rotate around X
                    # ------------------------------------------------

                    cos_a = math.cos(A)
                    sin_a = math.sin(A)

                    y2 = (
                        y * cos_a
                        - z * sin_a
                    )

                    z2 = (
                        y * sin_a
                        + z * cos_a
                    )


                    # ------------------------------------------------
                    # Rotate around Z
                    # ------------------------------------------------

                    cos_b = math.cos(B)
                    sin_b = math.sin(B)

                    x2 = (
                        x * cos_b
                        - y2 * sin_b
                    )

                    y3 = (
                        x * sin_b
                        + y2 * cos_b
                    )


                    # ------------------------------------------------
                    # Perspective
                    # ------------------------------------------------

                    distance = z2 + 5

                    if distance <= 0:
                        phi += 0.04
                        continue


                    ooz = 1 / distance


                    screen_x = int(
                        WIDTH / 2
                        + 30 * ooz * x2
                    )

                    screen_y = int(
                        HEIGHT / 2
                        + 15 * ooz * y3
                    )


                    if (
                        screen_x < 0
                        or screen_x >= WIDTH
                        or screen_y < 0
                        or screen_y >= HEIGHT
                    ):

                        phi += 0.04
                        continue


                    # ------------------------------------------------
                    # Lighting
                    # ------------------------------------------------

                    nx = (
                        cos_theta * cos_phi
                    )

                    ny = (
                        cos_theta * sin_phi
                    )

                    nz = sin_theta


                    # Rotate normal
                    ny2 = (
                        ny * cos_a
                        - nz * sin_a
                    )

                    nz2 = (
                        ny * sin_a
                        + nz * cos_a
                    )


                    nx2 = (
                        nx * cos_b
                        - ny2 * sin_b
                    )

                    ny3 = (
                        nx * sin_b
                        + ny2 * cos_b
                    )


                    brightness = (
                        nx2 * 0
                        + ny3 * 0.7
                        + nz2 * -1
                    )


                    if brightness > 0:

                        index = int(
                            brightness
                            * (
                                len(CHARS) - 1
                            )
                        )

                        index = max(
                            0,
                            min(
                                len(CHARS) - 1,
                                index
                            )
                        )


                        # Depth buffering
                        if (
                            ooz
                            > zbuffer[
                                screen_y
                            ][
                                screen_x
                            ]
                        ):

                            zbuffer[
                                screen_y
                            ][
                                screen_x
                            ] = ooz


                            output[
                                screen_y
                            ][
                                screen_x
                            ] = CHARS[index]


                    phi += 0.04

                theta += 0.07


            # ------------------------------------------------
            # Draw
            # ------------------------------------------------

            print(
                "\033[H",
                end=""
            )

            print(
                "\n".join(
                    "".join(row)
                    for row in output
                ),
                end="",
                flush=True
            )


            # ------------------------------------------------
            # Rotation
            # ------------------------------------------------

            A += 0.04
            B += 0.02


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
            "Donut stopped."
        )


if __name__ == "__main__":
    main()