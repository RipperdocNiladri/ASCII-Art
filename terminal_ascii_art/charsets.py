"""Shared brightness-to-character ramps."""

CHARSETS = {
    "classic": " .:-=+*#%@",
    "detailed": " .`^\\,:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "letters": ".,:;irsXA253hMHGS#9B&@",
}

DEFAULT_CHARSET = "classic"


def get_charset(name: str = DEFAULT_CHARSET, *, invert: bool = False) -> str:
    """Return a named dark-to-bright character ramp."""
    try:
        ramp = CHARSETS[name]
    except KeyError as exc:
        choices = ", ".join(sorted(CHARSETS))
        raise ValueError(f"Unknown charset '{name}'. Choose from: {choices}.") from exc
    return ramp[::-1] if invert else ramp


def brightness_to_index(brightness: float, ramp_length: int) -> int:
    """Map a brightness in the 0..255 range to a safe ramp index."""
    if ramp_length < 1:
        raise ValueError("A character ramp cannot be empty.")
    value = max(0.0, min(255.0, float(brightness)))
    return int(value * (ramp_length - 1) / 255.0)


def brightness_to_char(brightness: float, ramp: str) -> str:
    return ramp[brightness_to_index(brightness, len(ramp))]
