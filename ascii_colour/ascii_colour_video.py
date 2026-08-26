import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("This script requires numpy.\nInstall it with:  pip install numpy")
    sys.exit(1)


# ============================================================
# CHARACTER RAMPS (dark -> bright). No quote characters, to keep
# the string literals simple.
# ============================================================

CHARSETS = {
    # Classic, chunky, easy to read at small sizes.
    "classic": " .:-=+*#%@",

    # Longer ramp -> finer brightness gradations, more "painted" look.
    "detailed": " .`^\\,:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",

    # Letters/symbols only (no space) for a denser, more "text-like" look.
    "letters": ".,:;irsXA253hMHGS#9B&@",
}

DEFAULT_CHARSET = "detailed"
DEFAULT_FPS = 20
DEFAULT_MAX_WIDTH = 160
DEFAULT_SMOOTHING = 1.0      # 1.0 = no motion smoothing/ghosting (crisp, recommended)
DEFAULT_QUANT = 4            # color quantization step, used only to build longer
                              # same-color runs for cheaper ANSI output
DEFAULT_MAX_FRAME_SKIP = 5   # safety cap on consecutive dropped frames

CHAR_ASPECT = 0.5  # terminal character cells are roughly twice as tall as
                    # wide; corrects the render so video isn't stretched


# ============================================================
# TERMINAL / VIDEO INFO
# ============================================================

def get_terminal_size():
    size = shutil.get_terminal_size(fallback=(120, 40))
    return size.columns, size.lines


def get_video_dimensions(video):
    """Return (width, height) of the video's first video stream, or
    None if ffprobe isn't available or the probe fails."""
    if shutil.which("ffprobe") is None:
        return None
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=p=0:s=x",
                str(video),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        w_str, h_str = result.stdout.strip().split("x")
        return int(w_str), int(h_str)
    except Exception:
        return None


def compute_render_size(term_cols, term_rows, video_dims, max_width):
    """Work out how many character columns/rows to render, trying to
    preserve the source video's aspect ratio."""
    cols = max(term_cols - 2, 10)
    if max_width:
        cols = min(cols, max_width)

    rows_available = max(term_rows - 3, 5)

    if video_dims:
        vid_w, vid_h = video_dims
        video_aspect = vid_h / vid_w
    else:
        video_aspect = 9 / 16  # reasonable default guess

    rows = int(cols * video_aspect * CHAR_ASPECT)
    rows = max(5, min(rows, rows_available))
    return cols, rows


# ============================================================
# FRAME READING
# ============================================================

def read_frame(stream, size):
    """Read exactly `size` bytes from a stream, or None on EOF."""
    data = bytearray()
    while len(data) < size:
        chunk = stream.read(size - len(data))
        if not chunk:
            return None
        data.extend(chunk)
    return bytes(data)


# ============================================================
# VECTORIZED FRAME PROCESSING (numpy)
# ============================================================

def bytes_to_array(raw, rows, cols):
    return np.frombuffer(raw, dtype=np.uint8).reshape(
        (rows, cols, 3)
    ).astype(np.float32)


def apply_smoothing(arr, prev_arr, smoothing):
    if prev_arr is None or smoothing >= 0.999:
        return arr
    return prev_arr + (arr - prev_arr) * smoothing


def quantize(arr, step):
    if step <= 1:
        return arr.astype(np.int32)
    return (arr // step * step).astype(np.int32)


def render_ascii(arr, quant_step, ramp):
    """arr: float32 array of shape (rows, cols, 3). Returns the full
    ANSI text for one frame, built entirely from `ramp` characters."""
    disp = np.clip(arr, 0, 255).astype(np.int32)

    brightness = (
        0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
    )
    char_idx = np.clip(
        (brightness * (len(ramp) - 1) / 255).astype(np.int32),
        0,
        len(ramp) - 1,
    )

    # Quantized color folded together with the character index so a
    # "run" only continues while both the glyph AND its color stay
    # the same - this is what lets us emit one ANSI code per run
    # instead of one per character.
    color_q = quantize(arr, quant_step)
    key = (
        (color_q[..., 0].astype(np.int64) << 40)
        | (color_q[..., 1].astype(np.int64) << 32)
        | (color_q[..., 2].astype(np.int64) << 24)
        | char_idx.astype(np.int64)
    )

    lines = []
    n_rows, n_cols = key.shape
    for y in range(n_rows):
        row_key = key[y]
        changes = np.flatnonzero(row_key[1:] != row_key[:-1]) + 1
        starts = np.concatenate(([0], changes))
        ends = np.concatenate((changes, [n_cols]))

        parts = []
        for s, e in zip(starts.tolist(), ends.tolist()):
            r, g, b = disp[y, s]
            ch = ramp[char_idx[y, s]]
            parts.append(f"\033[38;2;{r};{g};{b}m" + ch * (e - s))
        lines.append("".join(parts) + "\033[0m")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def parse_args():
    p = argparse.ArgumentParser(description="Terminal ASCII letter-art video player with synced audio.")
    p.add_argument("video", help="Path to the video file")
    p.add_argument("--charset", choices=list(CHARSETS.keys()), default=DEFAULT_CHARSET,
                    help="Which brightness->character ramp to use")
    p.add_argument("--fps", type=float, default=DEFAULT_FPS, help="Target playback FPS")
    p.add_argument("--width", type=int, default=DEFAULT_MAX_WIDTH, help="Max render width in columns")
    p.add_argument("--mono", action="store_true", help="Render in plain white/gray instead of source color")
    p.add_argument("--smoothing", type=float, default=DEFAULT_SMOOTHING,
                    help="Color smoothing factor, 1.0=none (crisp) .. 0.0=frozen (heavy trail)")
    p.add_argument("--quant", type=int, default=DEFAULT_QUANT,
                    help="Color quantization step used to build cheaper ANSI runs")
    p.add_argument("--max-frame-skip", type=int, default=DEFAULT_MAX_FRAME_SKIP,
                    help="Max consecutive frames to drop to catch back up to audio")
    p.add_argument("--audio-delay", type=float, default=0.0,
                    help="Shift audio relative to video, in seconds (+ delays audio)")
    return p.parse_args()


def main():
    args = parse_args()

    if os.name == "nt":
        os.system("")  # enable ANSI escape processing on modern Windows consoles

    video = Path(os.path.expanduser(args.video)).resolve()
    if not video.is_file():
        print(f"\u274c Video not found: {video}")
        return

    if shutil.which("ffmpeg") is None:
        print("\u274c FFmpeg not found.")
        return
    if shutil.which("ffplay") is None:
        print("\u274c FFplay not found.")
        return

    ramp = CHARSETS[args.charset]

    term_cols, term_rows = get_terminal_size()
    video_dims = get_video_dimensions(video)
    cols, rows = compute_render_size(term_cols, term_rows, video_dims, args.width)

    print()
    print("+------------------------------------------+")
    print("|          ASCII LETTER ART VIDEO PLAYER    |")
    print("+------------------------------------------+")
    print()
    print(f"Video:      {video.name}")
    print(f"Charset:    {args.charset} ({len(ramp)} levels)")
    print(f"Render:     {cols} x {rows} chars")
    print(f"Target FPS: {args.fps}")
    print()
    print("Starting... (Ctrl+C to stop)")
    time.sleep(0.6)

    frame_size = cols * rows * 3
    frame_duration = 1.0 / args.fps

    # --------------------------------------------------------
    # Launch audio first; the moment it starts is our sync clock.
    # --------------------------------------------------------
    audio_cmd = ["ffplay", "-nodisp", "-vn", "-autoexit", "-loglevel", "quiet", str(video)]
    audio_process = subprocess.Popen(audio_cmd)

    if args.audio_delay > 0:
        time.sleep(args.audio_delay)

    start_time = time.perf_counter()

    video_cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", str(video),
        "-vf", f"fps={args.fps},scale={cols}:{rows}",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ]
    video_process = subprocess.Popen(
        video_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=10 ** 8,
    )

    print("\033[2J\033[H", end="")   # clear screen, home cursor
    print("\033[?25l", end="", flush=True)  # hide cursor

    prev_arr = None
    frame_index = 0
    consecutive_drops = 0

    try:
        while True:
            raw = read_frame(video_process.stdout, frame_size)
            if raw is None:
                break

            target_time = start_time + frame_index * frame_duration
            frame_index += 1
            now = time.perf_counter()
            lag = now - target_time

            if lag > frame_duration and consecutive_drops < args.max_frame_skip:
                # Behind schedule: skip rendering this frame so we can
                # catch back up to the audio clock, instead of drifting
                # further and further out of sync.
                consecutive_drops += 1
                continue

            consecutive_drops = 0
            if lag < 0:
                time.sleep(-lag)

            arr = bytes_to_array(raw, rows, cols)
            arr = apply_smoothing(arr, prev_arr, args.smoothing)
            prev_arr = arr

            if args.mono:
                gray = (
                    0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
                )
                arr = np.stack([gray, gray, gray], axis=-1)

            frame_text = render_ascii(arr, args.quant, ramp)

            sys.stdout.write("\033[H")
            sys.stdout.write(frame_text)
            sys.stdout.flush()

    except KeyboardInterrupt:
        sys.stdout.write("\033[0m\n\n\u23f9 Stopped.\n")

    finally:
        sys.stdout.write("\033[0m")
        sys.stdout.write("\033[?25h")  # show cursor
        sys.stdout.flush()

        for proc in (video_process, audio_process):
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    print("\n\n\u2705 Finished.")


if __name__ == "__main__":
    main()