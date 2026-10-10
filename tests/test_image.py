import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from terminal_ascii_art.cli import main
from terminal_ascii_art.charsets import get_charset
from terminal_ascii_art.media.image import ImageRenderError, get_image_dimensions, render_image


class ImageCommandTests(unittest.TestCase):
    def test_image_command_accepts_an_absolute_external_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_directory = Path(directory)
            source = temporary_directory / "source image.png"
            destination = temporary_directory / "output" / "image.txt"
            Image.new("L", (2, 2), color=255).save(source)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(
                    [
                        "image",
                        str(source.resolve()),
                        "--width",
                        "4",
                        "--height",
                        "2",
                        "--output",
                        str(destination),
                    ]
                )

            self.assertEqual(result, 0)
            self.assertEqual(destination.read_text(encoding="utf-8"), "@@@@\n@@@@\n")
            self.assertIn("Wrote 4 x 2 ASCII image", output.getvalue())


class ImageRenderingTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.source = Path(directory.name) / "image.png"

    def test_uniform_midtones_use_the_nearest_character(self) -> None:
        Image.new("L", (8, 8), 128).save(self.source)
        self.assertEqual(
            render_image(self.source, width=4, height=2, ramp=get_charset("classic")),
            "++++\n++++",
        )

    def test_exif_orientation_is_used_for_dimensions_and_rendering(self) -> None:
        image = Image.new("L", (3, 2))
        image.paste(255, (0, 1, 3, 2))
        exif = Image.Exif()
        exif[274] = 6
        image.save(self.source, exif=exif)
        self.assertEqual(get_image_dimensions(self.source), (2, 3))
        self.assertEqual(
            render_image(self.source, width=2, height=3, ramp=" .#"),
            "# \n# \n# ",
        )

    def test_transparent_pixels_are_blank_with_normal_and_inverted_ramps(self) -> None:
        for invert, color in ((False, 255), (True, 0)):
            with self.subTest(invert=invert):
                image = Image.new("RGBA", (2, 1), (color, color, color, 0))
                image.putpixel((1, 0), (color, color, color, 255))
                image.save(self.source)
                self.assertEqual(
                    render_image(
                        self.source, width=2, height=1,
                        ramp=get_charset("classic", invert=invert),
                    ),
                    " @",
                )

    def test_palette_transparency_is_respected(self) -> None:
        image = Image.new("P", (2, 1))
        image.putpalette([255, 255, 255, 255, 255, 255] + [0] * (768 - 6))
        image.putpixel((1, 0), 1)
        image.save(self.source, transparency=0)
        self.assertEqual(render_image(self.source, width=2, height=1, ramp=" .#"), " #")

    def test_partial_transparency_preserves_intermediate_shading(self) -> None:
        Image.new("RGBA", (4, 4), (255, 255, 255, 128)).save(self.source)
        self.assertEqual(render_image(self.source, width=2, height=1, ramp=" .#"), "..")

    def test_invalid_dimensions_and_empty_ramp_have_clear_errors(self) -> None:
        Image.new("L", (2, 2)).save(self.source)
        for width, height in ((0, 2), (2, 0), (-1, 2)):
            with self.subTest(width=width, height=height):
                with self.assertRaisesRegex(ImageRenderError, "dimensions must be positive"):
                    render_image(self.source, width=width, height=height, ramp=" .#")
        with self.assertRaisesRegex(ImageRenderError, "ramp cannot be empty"):
            render_image(self.source, width=2, height=2, ramp="")

    def test_invalid_image_has_a_clear_error(self) -> None:
        self.source.write_bytes(b"not an image")
        with self.assertRaisesRegex(ImageRenderError, "Could not render image"):
            render_image(self.source, width=2, height=2, ramp=" .#")


if __name__ == "__main__":
    unittest.main()
