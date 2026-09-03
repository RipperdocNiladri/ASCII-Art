import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from terminal_ascii_art.cli import main


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


if __name__ == "__main__":
    unittest.main()
