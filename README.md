# ASCII Art & Terminal Renderer

A small command-line application for rendering images, videos, and procedural 3D experiments directly in a terminal.

The project treats the terminal as a character-based framebuffer. Pixel brightness selects an ASCII character, ANSI escape sequences provide true color and screen updates, and mathematical renderers supply geometry, projection, lighting, and depth.

```text
source pixels or 3D geometry
              ↓
      brightness / lighting
              ↓
        character mapping
              ↓
       optional ANSI color
              ↓
            terminal
```

## Features

- One `ascii-art` command for every renderer.
- Still-image conversion with automatic aspect-ratio correction.
- Monochrome and ANSI true-color video playback.
- Optional synchronized audio through FFplay.
- Frame dropping to limit long-term audio/video drift.
- Configurable FPS, width, character ramp, color smoothing, and inversion.
- Automatic fitting to the current terminal.
- Five procedural demos: cube, sphere, donut, planet, and black hole.
- Safe terminal cleanup after completion, errors, or `Ctrl+C`.
- Compatibility entry points for the original scripts.

## Requirements

- Python 3.10 or newer.
- Pillow for still images.
- NumPy for video frame processing.
- FFmpeg for video decoding.
- FFplay for audio playback, unless `--no-audio` is used.
- FFprobe is recommended for detecting the source video's dimensions. A 16:9 fallback is used when it is unavailable.

Check the external video tools:

```powershell
ffmpeg -version
ffplay -version
ffprobe -version
```

On Windows, install an FFmpeg distribution containing all three programs and ensure its executable directory is on `PATH`.

## Installation

Install the published package from PyPI:

```powershell
python -m pip install --upgrade pip
python -m pip install terminal-ascii-art
```

Confirm that the command is available:

```powershell
ascii-art --version
ascii-art list
```

If `ascii-art` is not found because your Python scripts directory is not on `PATH`, use the module form:

```powershell
python -m terminal_ascii_art list
```

Python installations normally include pip. If `python -m pip --version` reports that pip is missing, bootstrap it with:

```powershell
python -m ensurepip --upgrade
```

### Install from source

Clone the repository and enter it:

```powershell
git clone https://github.com/TFQ0/ASCII-Art.git
cd ASCII-Art
```

Create and activate a virtual environment:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the project in editable mode:

```powershell
python -m pip install -e .
```

The editable installation provides the `ascii-art` command. The same interface can also be invoked as a Python module:

```powershell
python -m terminal_ascii_art list
```

## Quick start

Replace the example paths below with paths to your own image and video files.

List every available renderer:

```powershell
ascii-art list
```

Convert an image:

```powershell
ascii-art image "C:\path\to\photo.jpg" --width 100
```

Play a monochrome video with audio:

```powershell
ascii-art video "C:\path\to\video.mp4"
```

Play a true-color video:

```powershell
ascii-art video "C:\path\to\video.mp4" --color --fps 20 --width 120
```

Run a procedural demo:

```powershell
ascii-art demo cube
```

Press `Ctrl+C` to stop an animation or video.

Input files do not need to be inside the repository. Quote paths that contain spaces. For example, in PowerShell:

```powershell
ascii-art video "E:\Videos\Rena Circulation.mp4" --color --charset detailed --fps 20 --width 120
```

The equivalent Git Bash path is:

```bash
ascii-art video "/e/Videos/Rena Circulation.mp4" --color --charset detailed --fps 20 --width 120
```

## Image rendering

```powershell
ascii-art image IMAGE [options]
```

Examples:

```powershell
# Print the result in the terminal
ascii-art image photo.png --width 120

# Write plain ASCII to a UTF-8 text file
ascii-art image photo.png --width 120 --output output\photo.txt

# Use a longer character ramp and reverse its brightness direction
ascii-art image photo.png --charset detailed --invert
```

Options:

| Option | Purpose |
| --- | --- |
| `--width N` | Maximum output width. Default: `100`. |
| `--height N` | Optional maximum output height. |
| `--charset NAME` | `classic`, `detailed`, or `letters`. |
| `--invert` | Reverse the dark-to-bright ramp. |
| `-o`, `--output PATH` | Write the rendered text to a file. |

The source ratio is preserved while accounting for terminal cells being approximately twice as tall as they are wide.

## Video rendering

```powershell
ascii-art video VIDEO [options]
```

The default mode is monochrome with audio enabled. Add `--color` to preserve approximate source colors using ANSI 24-bit foreground codes.

Examples:

```powershell
# Monochrome video without audio
ascii-art video clip.mp4 --no-audio

# Detailed true-color playback
ascii-art video clip.mp4 --color --charset detailed --width 160 --fps 20

# Add motion trails
ascii-art video clip.mp4 --color --smoothing 0.35

# Delay audio by 0.5 seconds
ascii-art video clip.mp4 --audio-delay 0.5
```

Options:

| Option | Purpose |
| --- | --- |
| `--color` | Enable ANSI true-color output. |
| `--fps N` | Target playback rate. Default: `20`. |
| `--width N` | Maximum render width. Default: `160`. |
| `--smoothing N` | Temporal blend from `0` to `1`; `1` is crisp. |
| `--quant N` | Color quantization step used to reduce ANSI output. Default: `4`. |
| `--max-frame-skip N` | Consecutive frames that may be dropped to catch up. Default: `5`. |
| `--no-audio` | Do not start FFplay. |
| `--audio-delay N` | Shift audio by -30 to +30 seconds; positive values delay it. |
| `--charset NAME` | `classic`, `detailed`, or `letters`. |
| `--invert` | Reverse the selected brightness ramp. |

The video pipeline is:

```text
                       ┌─ FFmpeg → scaled raw frames → NumPy → ASCII → terminal
source video ──────────┤
                       └─ FFplay → audio
```

The renderer uses a wall-clock schedule. When terminal rendering falls behind, it can discard a bounded number of decoded frames instead of allowing drift to grow continuously.

## Procedural demos

```powershell
ascii-art demo NAME [options]
```

Available names:

| Demo | Technique |
| --- | --- |
| `cube` | Vertex rotation, perspective projection, face normals, back-face culling, triangle filling, and interpolated depth buffering. |
| `sphere` | Per-cell sphere reconstruction and directional lighting. |
| `donut` | Parametric torus sampling, normal-based lighting, perspective, and depth buffering. |
| `planet` | Rotating sphere with procedural terrain, a night side, and an atmospheric rim. |
| `blackhole` | Polar-coordinate accretion disk, deterministic stars, asymmetric glow, and a photon-ring effect. |

Examples:

```powershell
ascii-art demo donut --fps 30
ascii-art demo planet --width 120 --charset detailed
ascii-art demo blackhole --width 140 --height 50
```

Every demo accepts `--width`, `--height`, `--fps`, `--charset`, and `--invert`. Dimensions are reduced when necessary to fit the terminal.

## Character ramps

Character ramps are ordered from dark to bright:

```text
classic:   " .:-=+*#%@"
detailed:  a longer ramp with finer brightness changes
letters:   a dense, text-like ramp
```

To add a procedural demo:

1. Create a module under `terminal_ascii_art/renderers/`.
2. Implement `render_frame(frame_index, width, height, ramp) -> str`.
3. Register it in `terminal_ascii_art/renderers/__init__.py`.
4. Add a renderer-contract or algorithm-specific test.
5. Document the new demo here.

## Testing

Install the project and run the test suite from the repository root:

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Publishing a release

Releases are published from `TFQ0/ASCII-Art` by `.github/workflows/publish.yml`. The workflow runs the tests on the supported Python versions, builds and validates the wheel and source distribution, and publishes them to PyPI through Trusted Publishing.

Before the first release, configure a PyPI Trusted Publisher for the `terminal-ascii-art` project with these exact values:

- Owner: `RipperdocNiladri`
- Repository: `ASCII-Art`
- Workflow: `publish.yml`
- Environment: `pypi`

The GitHub `pypi` environment permits tags matching `v*`. If the account that creates the release is its only required reviewer, **Prevent self-review** must be disabled or another reviewer must be added.

For every release:

1. Update `__version__` in `terminal_ascii_art/__init__.py`. Package metadata reads the version from this single source.
2. Run the tests.
3. Build and validate the distributions locally:

   ```powershell
   python -m pip install --upgrade build twine
   python -m build
   python -m twine check dist/*
   ```

4. Commit and push the release changes.
5. Create a GitHub release whose tag exactly matches the package version with a `v` prefix, such as `v0.1.1`.

Publishing a GitHub release triggers the workflow. PyPI does not allow an existing release file or version to be overwritten, so each published version must be unique.

## Performance and limitations

Terminal output is much slower than GPU rendering. Performance depends on the CPU, terminal emulator, selected width, FPS, character ramp, and whether ANSI color is enabled.

Useful starting points:

- `80` columns for low overhead.
- `120` columns for balanced detail.
- `160` columns for high detail on a capable terminal.
- Monochrome mode when color output is too expensive.
- A larger `--quant` value to reduce ANSI color changes.

## License

This project is distributed under the [MIT License](https://github.com/TFQ0/ASCII-Art/blob/main/LICENSE).

