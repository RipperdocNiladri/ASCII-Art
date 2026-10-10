# ASCII Art & Terminal Renderer

A small Python command-line tool for converting images and videos into ASCII art and running five animated 3D demos in your terminal. Videos support monochrome or ANSI true color, with optional audio.

- [Download and install](#download-and-install)
- [Usage examples](#usage-examples)
- [All commands and options](#all-commands-and-options)
- [Quality and performance](#quality-and-performance)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Download and install

### 1. Install the prerequisites

Install [Python 3.10 or newer](https://www.python.org/downloads/), then check that Python and pip are available:

```powershell
python --version
python -m pip --version
```

Pillow and NumPy are installed automatically with the tool. Video playback also needs external FFmpeg programs; images and demos do not need them.

For video, choose a build for your operating system from the [FFmpeg download page](https://ffmpeg.org/download.html). On Windows, extract a build containing `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe`, add its `bin` directory to `PATH`, and reopen PowerShell.

```powershell
ffmpeg -version
ffplay -version
ffprobe -version
```

FFmpeg decodes video. FFplay supplies audio and is optional with `--no-audio`. FFprobe detects video dimensions; the tool assumes a 16:9 source when probing is unavailable or fails.

### 2. Choose an installation method

**Option A: Install the published package**

Download and install the latest published version from [PyPI](https://pypi.org/project/terminal-ascii-art/):

```powershell
pip install terminal-ascii-art
```

**Option B: Download and install the source**

## Usage examples

It is recommended to use **PowerShell** in windows . Run one example at a time, and adjust the paths, sizes, or options to suit your files. Example images and videos are **not bundled** with the tool.

### Play a video

Start with monochrome playback and audio:

```powershell
ascii-art video $videoPath
```

Use color, a detailed character ramp, 30 FPS, and a three-second startup delay:

```powershell
ascii-art video video.mp4 --color --charset detailed --fps 30 --width 250 --start-delay 3
```
or

```powershell
ascii-art video video.mp4 --color --charset letters --fps 30 --width 250 --start-delay 3
```

Change `250` to the maximum number of columns you want. The output still shrinks to fit the terminal. Remove `--color` for monochrome or `--start-delay 3` to start immediately.

Reduce shimmer in still areas while preserving moving edges:

```powershell
ascii-art video video.mp4 --color --charset detailed --width 160 --smoothing 0.65
```

Use a smaller, silent render for a slower terminal:

```powershell
ascii-art video video.mp4 --width 80 --fps 20 --no-audio
```

Adjust audio timing independently of the startup delay:

```powershell
# Start audio half a second after the video
ascii-art video $videoPath --audio-delay 0.5

# Give audio a half-second head start
ascii-art video $videoPath --audio-delay=-0.5
```

`--start-delay` waits after the initial file and dependency checks, before starting either media process. It accepts fractional seconds, works with `--no-audio`, and can be cancelled with `Ctrl+C`. `--audio-delay` changes the relative timing of sound and picture.

### Convert an image

Print an image as ASCII:

```powershell
ascii-art image $imagePath --width 100
```

Save a detailed render to a UTF-8 text file:

```powershell
ascii-art image $imagePath --width 120 --charset detailed --output ".\output\photo.txt"
```

The output folder is created if needed; an existing file at that path is replaced. Open the text in a monospaced font to keep the characters aligned.

Set both size limits and reverse the brightness mapping:

```powershell
ascii-art image $imagePath --width 100 --height 40 --charset detailed --invert
```

Images preserve their visual aspect ratio, account for tall terminal cells, and respect EXIF orientation and transparency. Image output, including saved text, is sized to fit the current terminal.

### Run a 3D demo

These examples need no media files. Run one, stop it with `Ctrl+C`, then try another:

```powershell
ascii-art demo cube
ascii-art demo sphere --charset detailed
ascii-art demo donut --fps 30
ascii-art demo planet --width 120 --charset detailed
ascii-art demo blackhole --width 140 --height 50
```

## All commands and options

All commands and options supported by `ascii-art` are listed here. Put options after the relevant subcommand, for example `ascii-art video $videoPath --fps 30`. Replace `PATH`, `NAME`, and `N` with your own values; do not type those placeholders literally.

| Command or option | Applies to | Purpose / accepted values | Default |
| --- | --- | --- | --- |
| `ascii-art list` | Main command | List the image/video renderers and all demos. | — |
| `ascii-art image PATH` | Main command | Convert a still image to monochrome ASCII. | Print to terminal |
| `ascii-art video PATH` | Main command | Play a video as ASCII. | Monochrome, audio enabled |
| `ascii-art demo NAME` | Main command | Run one of the five demos below. | Name required |
| `ascii-art demo cube` | Demo | Rotating filled cube with lighting and depth buffering. | Width `80` |
| `ascii-art demo sphere` | Demo | Shaded sphere with an orbiting light. | Width `80` |
| `ascii-art demo donut` | Demo | Rotating torus with lighting and depth buffering. | Width `80` |
| `ascii-art demo planet` | Demo | Rotating procedural terrain, a night side, and an atmospheric rim. | Width `90` |
| `ascii-art demo blackhole` | Demo | Stylized accretion disk, stars, and photon ring. | Width `100` |
| `--version` | `ascii-art` | Show the installed code's version and exit. | — |
| `-h`, `--help` | Main command or any subcommand | Show help and exit, e.g. `ascii-art video --help`. | — |
| `--width N` | `image`, `video`, `demo` | Maximum character columns; positive integer, limited by terminal size. | Image: `100`; video: `160`; demo: widths above |
| `--height N` | `image`, `demo` | Image: maximum rows. Demo: requested rows, limited by terminal size. Positive integer. | Calculated from source ratio or demo |
| `--charset NAME` | `image`, `video`, `demo` | Character ramp: `classic`, `detailed`, or `letters`. | `classic` |
| `--invert` | `image`, `video`, `demo` | Reverse the chosen dark-to-bright character ramp. | Off |
| `-o PATH`, `--output PATH` | `image` | Write or replace a UTF-8 text file; create parent folders if needed. | Print to terminal |
| `--color` | `video` | Enable ANSI 24-bit foreground colors. | Off |
| `--mono` | `video` | Force monochrome; compatibility option. If combined with `--color`, the last flag wins. | Monochrome |
| `--fps N` | `video`, `demo` | Target frames per second; positive finite number. | `30` |
| `--smoothing N` | `video` | Blend small changes in still areas: `0` is strongest, `1` disables blending. | `1` |
| `--quant N` | `video` with `--color` | Positive integer color quantization step; larger values reduce color detail and ANSI output. | `4` |
| `--max-frame-skip N` | `video` | Maximum consecutive frames dropped to catch up; nonnegative integer. | `5` |
| `--no-audio` | `video` | Disable FFplay audio. | Audio enabled |
| `--start-delay N` | `video` | Wait before starting video and audio; nonnegative finite seconds, decimals allowed. | `0` |
| `--audio-delay N` | `video` | Audio offset from `-30` to `30` seconds; positive delays audio, negative gives it a head start. | `0` |
| `python -m terminal_ascii_art ...` | Alternative entry point | Use the same subcommands and options through Python. | Same as `ascii-art` |

## Quality and performance

- **Character detail:** `classic` uses ` .:-=+*#%@`; `detailed` provides more tonal steps; `letters` gives a dense, text-like appearance. All are ordered from dark to bright.
- **Resolution:** try widths of `80`, `120`, or `160` first. A wider terminal or smaller font allows more detail. For a 16:9 source, `--width 250` needs roughly 252 terminal columns and 72 rows, including margins.
- **Motion:** match the source frame rate when practical; use `--fps 30` for a 30 FPS clip. Lower FPS or width if your terminal struggles. Smoothing reduces shimmer, not frame-rate judder.
- **Color overhead:** monochrome is cheaper to display. In color mode, a larger `--quant` value reduces color changes at the cost of color precision.

## Development

The terminal acts as a character-based framebuffer: brightness or lighting selects a character, with optional ANSI foreground color.

```text
image → Pillow → grayscale → ASCII text
video → FFmpeg → scaled frames → NumPy → ASCII / ANSI terminal output
      └ FFplay → audio
demo  → geometry + projection + lighting → ASCII terminal output
```

## License

This project is distributed under the [MIT License](https://github.com/TFQ0/ASCII-Art/blob/main/LICENSE).
