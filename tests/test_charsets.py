import unittest

from terminal_ascii_art.charsets import (
    brightness_to_char,
    brightness_to_index,
    get_charset,
)


class CharsetTests(unittest.TestCase):
    def test_brightness_is_clamped_to_ramp(self) -> None:
        self.assertEqual(brightness_to_index(-10, 10), 0)
        self.assertEqual(brightness_to_index(255, 10), 9)
        self.assertEqual(brightness_to_index(999, 10), 9)

    def test_invert_reverses_named_ramp(self) -> None:
        normal = get_charset("classic")
        self.assertEqual(get_charset("classic", invert=True), normal[::-1])

    def test_character_mapping_uses_both_endpoints(self) -> None:
        ramp = " .#"
        self.assertEqual(brightness_to_char(0, ramp), " ")
        self.assertEqual(brightness_to_char(255, ramp), "#")

    def test_empty_ramp_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            brightness_to_index(100, 0)


if __name__ == "__main__":
    unittest.main()
