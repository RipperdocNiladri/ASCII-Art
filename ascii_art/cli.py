"""Public command-line interface for all renderers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from ascii_art import __version__
from ascii_art.charsets import CHARSETS, DEFAULT_CHARSET, get_charset
from ascii_art.media.image import ImageRenderError, get_image_dimensions, render_image
from ascii_art.media.video import VideoOptions, VideoRenderError, play_video
from ascii_art.renderers import DEMOS, get_demo
from ascii_art.terminal import fit_demo_size, fit_source_size, run_animation


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _unit_float(value: str) -> float:
    parsed = float(value)
    if not 0 <= parsed <= 1:
        raise argparse.ArgumentTypeError("must be between 0 and 1")
    return parsed


def _audio_delay(value: str) -> float:
    parsed = float(value)
    if not -30 <= parsed <= 30:
        raise argparse.ArgumentTypeError("must be between -30 and 30 seconds")
    return parsed


def _add_charset_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--charset",
        choices=sorted(CHARSETS),
        default=DEFAULT_CHARSET,
        help="brightness-to-character ramp (default: %(default)s)",
    )
    parser.add_argument(
        "--invert", action="store_true", help="reverse dark and bright characters"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ascii-art",
        description="Render images, videos, and procedural 3D experiments in a terminal.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list available renderers")
    list_parser.set_defaults(handler=_run_list)

    image_parser = subparsers.add_parser("image", help="convert a still image to ASCII")
    image_parser.add_argument("path", type=Path, help="path to an image")
    image_parser.add_argument(
        "--width", type=_positive_int, default=100, help="maximum character width"
    )
    image_parser.add_argument("--height", type=_positive_int, help="maximum character height")
    image_parser.add_argument("-o", "--output", type=Path, help="write text to a UTF-8 file")
    _add_charset_options(image_parser)
    image_parser.set_defaults(handler=_run_image)

    video_parser = subparsers.add_parser("video", help="play a video as ASCII")
    video_parser.add_argument("path", type=Path, help="path to a video")
    video_parser.add_argument("--color", action="store_true", help="use ANSI true-color")
    video_parser.add_argument(
        "--mono",
        dest="color",
        action="store_false",
        help=argparse.SUPPRESS,
    )
    video_parser.add_argument("--fps", type=_positive_float, default=20.0)
    video_parser.add_argument(
        "--width", type=_positive_int, default=160, help="maximum character width"
    )
    video_parser.add_argument(
        "--smoothing",
        type=_unit_float,
        default=1.0,
        help="temporal smoothing: 1 is crisp, lower values add trails",
    )
    video_parser.add_argument(
        "--quant",
        type=_positive_int,
        default=4,
        help="color quantization step used to reduce ANSI output",
    )
    video_parser.add_argument(
        "--max-frame-skip",
        type=_nonnegative_int,
        default=5,
        help="maximum consecutive frames dropped to catch up",
    )
    video_parser.add_argument("--no-audio", action="store_true", help="disable FFplay audio")
    video_parser.add_argument(
        "--audio-delay",
        type=_audio_delay,
        default=0.0,
        help="audio offset in seconds; positive values delay audio",
    )
    _add_charset_options(video_parser)
    video_parser.set_defaults(handler=_run_video, color=False)

    demo_parser = subparsers.add_parser("demo", help="run a procedural renderer")
    demo_parser.add_argument("name", choices=sorted(DEMOS), help="demo name")
    demo_parser.add_argument("--width", type=_positive_int, help="character width")
    demo_parser.add_argument("--height", type=_positive_int, help="character height")
    demo_parser.add_argument("--fps", type=_positive_float, default=30.0)
    _add_charset_options(demo_parser)
    demo_parser.set_defaults(handler=_run_demo)

    return parser


def _run_list(_args: argparse.Namespace) -> int:
    print("Input renderers:")
    print("  image      Still images through Pillow")
    print("  video      Monochrome or ANSI true-color video through FFmpeg")
    print("\nProcedural demos:")
    for demo in DEMOS.values():
        print(f"  {demo.name:<10} {demo.description}")
    return 0


def _run_image(args: argparse.Namespace) -> int:
    path = args.path.expanduser().resolve()
    if not path.is_file():
        raise ImageRenderError(f"Image not found: {path}")
    source_width, source_height = get_image_dimensions(path)
    width, height = fit_source_size(
        source_width,
        source_height,
        max_width=args.width,
        max_height=args.height,
    )
    output = render_image(
        path,
        width=width,
        height=height,
        ramp=get_charset(args.charset, invert=args.invert),
    )
    if args.output:
        destination = args.output.expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output + "\n", encoding="utf-8")
        print(f"Wrote {width} x {height} ASCII image to {destination}")
    else:
        print(output)
    return 0


def _run_video(args: argparse.Namespace) -> int:
    options = VideoOptions(
        fps=args.fps,
        max_width=args.width,
        color=args.color,
        smoothing=args.smoothing,
        quantization=args.quant,
        max_frame_skip=args.max_frame_skip,
        audio=not args.no_audio,
        audio_delay=args.audio_delay,
    )
    play_video(
        args.path.expanduser().resolve(),
        options=options,
        ramp=get_charset(args.charset, invert=args.invert),
    )
    return 0


def _run_demo(args: argparse.Namespace) -> int:
    demo = get_demo(args.name)
    width, height = fit_demo_size(
        default_width=demo.default_width,
        height_ratio=demo.height_ratio,
        width=args.width,
        height=args.height,
    )
    ramp = get_charset(args.charset, invert=args.invert)
    run_animation(
        lambda frame_index: demo.render(frame_index, width, height, ramp),
        fps=args.fps,
        stopped_message=f"{demo.name.capitalize()} stopped.",
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (ImageRenderError, VideoRenderError, ValueError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
