import sys
import subprocess
import shutil
import os
import time

# ASCII characters: dark → bright
CHARS = " .:-=+*#%@"

# Resolution
WIDTH = min(shutil.get_terminal_size().columns - 2, 80)
HEIGHT = 32

# Video frame rate
FPS = 15

# Temporal smoothing
SMOOTHING = 0.45


def read_frame(stream, size):
    """Read exactly one complete video frame."""

    data = bytearray()

    while len(data) < size:
        chunk = stream.read(size - len(data))

        if not chunk:
            return None

        data.extend(chunk)

    return bytes(data)


def frame_to_brightness(frame):
    """Convert raw grayscale frame into brightness values."""

    return [
        list(frame[y * WIDTH:(y + 1) * WIDTH])
        for y in range(HEIGHT)
    ]


def smooth_frame(previous, current):
    """Smooth brightness between video frames."""

    result = []

    for y in range(HEIGHT):

        row = []

        for x in range(WIDTH):

            old = previous[y][x]
            new = current[y][x]

            value = old + (new - old) * SMOOTHING

            row.append(value)

        result.append(row)

    return result


def brightness_to_ascii(matrix):
    """Convert brightness matrix into ASCII."""

    output = []

    for y in range(HEIGHT):

        line = ""

        for x in range(WIDTH):

            brightness = matrix[y][x]

            index = int(
                brightness *
                (len(CHARS) - 1) /
                255
            )

            index = max(
                0,
                min(len(CHARS) - 1, index)
            )

            line += CHARS[index]

        output.append(line)

    return "\n".join(output)


def main():

    if len(sys.argv) != 2:

        print(
            "Usage:\n"
            "python ascii_video.py video.mp4"
        )

        return

    video = os.path.expanduser(
        sys.argv[1]
    )

    if not os.path.isfile(video):

        print("❌ File not found:")
        print(video)

        return

    print("🎬 Smooth ASCII Video")
    print("----------------------")
    print("Resolution:", WIDTH, "x", HEIGHT)
    print("FPS:", FPS)
    print("Mode: Smooth / No Cascade")
    print()
    print("Starting...")

    time.sleep(1)

    # FFmpeg converts video → grayscale frames
    command = [

        "ffmpeg",

        "-loglevel",
        "error",

        "-i",
        video,

        "-vf",
        f"fps={FPS},scale={WIDTH}:{HEIGHT}",

        "-f",
        "rawvideo",

        "-pix_fmt",
        "gray",

        "-"
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    frame_size = WIDTH * HEIGHT

    previous = [
        [0.0] * WIDTH
        for _ in range(HEIGHT)
    ]

    # Clear terminal
    print("\033[2J\033[H", end="")

    frame_time = 1 / FPS

    try:

        while True:

            start = time.perf_counter()

            frame = read_frame(
                process.stdout,
                frame_size
            )

            if frame is None:
                break

            current = frame_to_brightness(
                frame
            )

            # Smooth transition
            previous = smooth_frame(
                previous,
                current
            )

            # Convert to ASCII
            ascii_frame = brightness_to_ascii(
                previous
            )

            # Move cursor to top-left
            print(
                "\033[H",
                end=""
            )

            print(
                ascii_frame,
                end="",
                flush=True
            )

            # Maintain FPS
            elapsed = (
                time.perf_counter() - start
            )

            delay = frame_time - elapsed

            if delay > 0:
                time.sleep(delay)

    except KeyboardInterrupt:

        print(
            "\n\n⏹ Stopped."
        )

    finally:

        try:
            process.stdout.close()
        except:
            pass

        process.wait()

    print(
        "\n\n✅ Finished."
    )


if __name__ == "__main__":
    main()
