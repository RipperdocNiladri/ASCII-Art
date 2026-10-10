"""Still-image to ASCII conversion."""

from __future__ import annotations

from pathlib import Path

from terminal_ascii_art.charsets import brightness_to_char


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
            # EXIF orientations 5..8 rotate the displayed image by 90 degrees.
            if image.getexif().get(274) in (5, 6, 7, 8):
                return image.height, image.width
            return image.size
    except (OSError, ValueError) as exc:
        raise ImageRenderError(f"Could not open image '{path}': {exc}") from exc


def render_image(path: Path, *, width: int, height: int, ramp: str) -> str:
    try:
        from PIL import Image, ImageFilter, ImageOps
    except ImportError as exc:
        raise ImageRenderError(
            "Image rendering requires Pillow. Install the project dependencies first."
        ) from exc

    if not path.is_file():
        raise ImageRenderError(f"Image not found: {path}")
    if width <= 0 or height <= 0:
        raise ImageRenderError("Render dimensions must be positive.")
    if not ramp:
        raise ImageRenderError("A character ramp cannot be empty.")

    try:
        with Image.open(path) as source:
            source = ImageOps.exif_transpose(source)
            if "A" in source.getbands() or "transparency" in source.info:
                # Match a blank background for both normal and inverted ramps.
                background = 255 if ramp[-1] == " " else 0
                matte = Image.new("RGBA", source.size, (background,) * 3 + (255,))
                source = Image.alpha_composite(matte, source.convert("RGBA"))
            grayscale = source.convert("L")
            resampling = getattr(Image, "Resampling", Image).LANCZOS
            resized = grayscale.resize((width, height), resampling)
            # Recover a little edge contrast lost when reducing to a tiny grid.
            resized = resized.filter(ImageFilter.UnsharpMask(radius=0.6, percent=65, threshold=3))
            pixels = resized.tobytes()
    except (OSError, ValueError) as exc:
        raise ImageRenderError(f"Could not render image '{path}': {exc}") from exc

    palette = [brightness_to_char(value, ramp) for value in range(256)]
    lines = []
    for row_start in range(0, len(pixels), width):
        row = pixels[row_start : row_start + width]
        lines.append("".join(palette[value] for value in row))
    return "\n".join(lines)
