import sys
import subprocess
import shutil
import os
import time
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

CHARS = " .:-=+*#%@"

FPS = 15

SMOOTHING = 0.45

# Maximum ASCII width
MAX_WIDTH = 120

# Terminal character aspect correction
CHAR_ASPECT = 0.5


# ============================================================
# TERMINAL
# ============================================================

def get_terminal_size():

    size = shutil.get_terminal_size(
        fallback=(120, 40)
    )

    terminal_width = size.columns
    terminal_height = size.lines

    return terminal_width, terminal_height


# ============================================================
# FRAME READING
# ============================================================

def read_frame(stream, size):

    data = bytearray()

    while len(data) < size:

        chunk = stream.read(
            size - len(data)
        )

        if not chunk:
            return None

        data.extend(chunk)

    return bytes(data)


# ============================================================
# BRIGHTNESS MATRIX
# ============================================================

def frame_to_brightness(
    frame,
    width,
    height
):

    return [

        list(
            frame[
                y * width:
                (y + 1) * width
            ]
        )

        for y in range(height)
    ]


# ============================================================
# TEMPORAL SMOOTHING
# ============================================================

def smooth_frame(
    previous,
    current,
    width,
    height
):

    result = []

    for y in range(height):

        row = []

        for x in range(width):

            old = previous[y][x]

            new = current[y][x]

            value = (
                old
                + (new - old)
                * SMOOTHING
            )

            row.append(value)

        result.append(row)

    return result


# ============================================================
# ASCII CONVERSION
# ============================================================

def brightness_to_ascii(
    matrix,
    width,
    height
):

    output = []

    for y in range(height):

        line = []

        for x in range(width):

            brightness = matrix[y][x]

            index = int(
                brightness
                * (len(CHARS) - 1)
                / 255
            )

            index = max(
                0,
                min(
                    len(CHARS) - 1,
                    index
                )
            )

            line.append(
                CHARS[index]
            )

        output.append(
            "".join(line)
        )

    return "\n".join(output)


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Check video argument
    # --------------------------------------------------------

    if len(sys.argv) != 2:

        print()
        print("Usage:")
        print(
            "py ascii\\ascii_video.py "
            "assets\\videos\\test.mp4"
        )

        return


    # --------------------------------------------------------
    # Video path
    # --------------------------------------------------------

    video = Path(
        os.path.expanduser(
            sys.argv[1]
        )
    ).resolve()


    if not video.is_file():

        print()
        print("❌ Video not found:")
        print(video)

        return


    # --------------------------------------------------------
    # Check FFmpeg
    # --------------------------------------------------------

    if shutil.which("ffmpeg") is None:

        print()
        print("❌ FFmpeg was not found.")

        return


    # --------------------------------------------------------
    # Check FFplay
    # --------------------------------------------------------

    if shutil.which("ffplay") is None:

        print()
        print("❌ FFplay was not found.")

        return


    # --------------------------------------------------------
    # Terminal dimensions
    # --------------------------------------------------------

    terminal_width, terminal_height = (
        get_terminal_size()
    )


    width = terminal_width - 2


    if MAX_WIDTH is not None:

        width = min(
            width,
            MAX_WIDTH
        )


    height = terminal_height - 4


    if height < 5:

        height = 5


    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    print()
    print(
        "╔══════════════════════════════════════╗"
    )

    print(
        "║     ASCII VIDEO PLAYER V1 + AUDIO    ║"
    )

    print(
        "╚══════════════════════════════════════╝"
    )

    print()

    print(
        "Video:",
        video.name
    )

    print(
        "Resolution:",
        width,
        "x",
        height
    )

    print(
        "FPS:",
        FPS
    )

    print(
        "Smoothing:",
        SMOOTHING
    )

    print(
        "Audio: ENABLED 🔊"
    )

    print()

    print(
        "Starting..."
    )

    print(
        "Press Ctrl+C to stop."
    )

    time.sleep(1)


    # ========================================================
    # START AUDIO
    # ========================================================

    audio_command = [

        "ffplay",

        "-nodisp",

        "-autoexit",

        "-loglevel",
        "quiet",

        str(video)
    ]


    audio_process = subprocess.Popen(
        audio_command
    )


    # ========================================================
    # START VIDEO / FFMPEG
    # ========================================================

    command = [

        "ffmpeg",

        "-hide_banner",

        "-loglevel",
        "error",

        "-i",
        str(video),

        "-vf",
        (
            f"fps={FPS},"
            f"scale={width}:{height}"
        ),

        "-f",
        "rawvideo",

        "-pix_fmt",
        "gray",

        "-"
    ]


    process = subprocess.Popen(

        command,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        bufsize=0
    )


    # ========================================================
    # FRAME SETUP
    # ========================================================

    frame_size = (
        width * height
    )


    previous = [

        [0.0] * width

        for _ in range(height)
    ]


    frame_time = 1 / FPS


    # Clear terminal
    print(
        "\033[2J\033[H",
        end=""
    )


    # Hide cursor
    print(
        "\033[?25l",
        end="",
        flush=True
    )


    # ========================================================
    # PLAY
    # ========================================================

    try:

        while True:

            start = (
                time.perf_counter()
            )


            # ------------------------------------------------
            # Read frame
            # ------------------------------------------------

            frame = read_frame(

                process.stdout,

                frame_size
            )


            if frame is None:

                break


            # ------------------------------------------------
            # Convert
            # ------------------------------------------------

            current = (
                frame_to_brightness(

                    frame,

                    width,

                    height
                )
            )


            # ------------------------------------------------
            # Smooth
            # ------------------------------------------------

            previous = (
                smooth_frame(

                    previous,

                    current,

                    width,

                    height
                )
            )


            # ------------------------------------------------
            # ASCII
            # ------------------------------------------------

            ascii_frame = (
                brightness_to_ascii(

                    previous,

                    width,

                    height
                )
            )


            # ------------------------------------------------
            # Draw
            # ------------------------------------------------

            print(
                "\033[H",
                end=""
            )

            print(
                ascii_frame,

                end="",

                flush=True
            )


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

                time.sleep(
                    delay
                )


    except KeyboardInterrupt:

        print(
            "\n\n⏹ Stopped."
        )


    finally:

        # Show cursor
        print(
            "\033[?25h",
            end="",
            flush=True
        )


        # Stop video process
        try:

            process.terminate()

            process.wait(
                timeout=2
            )

        except:

            process.kill()


        # Stop audio
        try:

            audio_process.terminate()

            audio_process.wait(
                timeout=2
            )

        except:

            try:
                audio_process.kill()

            except:
                pass


    print(
        "\n\n✅ Finished."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()