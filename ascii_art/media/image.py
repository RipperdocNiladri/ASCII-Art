"""Still-image to ASCII conversion."""

from __future__ import annotations

from pathlib import Path

from ascii_art.charsets import brightness_to_char


class ImageRenderError(RuntimeError):
    pass


def get_image_dimensions(path: Path) -> tuple[int, int]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise ImageRenderError(
            "Image rendering requires Pillow. Install the project dependencies first."
        ) from exc

    try:
        with Image.open(path) as image:
            return image.size
    except (OSError, ValueError) as exc:
        raise ImageRenderError(f"Could not open image '{path}': {exc}") from exc


def render_image(path: Path, *, width: int, height: int, ramp: str) -> str:
    try:
        from PIL import Image
    except ImportError as exc:
        raise ImageRenderError(
            "Image rendering requires Pillow. Install the project dependencies first."
        ) from exc

    if not path.is_file():
        raise ImageRenderError(f"Image not found: {path}")

    try:
        with Image.open(path) as source:
            grayscale = source.convert("L")
            resampling = getattr(Image, "Resampling", Image).LANCZOS
            resized = grayscale.resize((width, height), resampling)
            pixels = list(resized.getdata())
    except (OSError, ValueError) as exc:
        raise ImageRenderError(f"Could not render image '{path}': {exc}") from exc

    lines = []
    for row_start in range(0, len(pixels), width):
        row = pixels[row_start : row_start + width]
        lines.append("".join(brightness_to_char(value, ramp) for value in row))
    return "\n".join(lines)
