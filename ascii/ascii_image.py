from PIL import Image

# -----------------------------
# SETTINGS
# -----------------------------

IMAGE_PATH = "assets\\bw_goku.jpg"

# Dark → bright
ASCII_CHARS = "@%#*+=-:. "

WIDTH = 100


# -----------------------------
# LOAD IMAGE
# -----------------------------

image = Image.open(IMAGE_PATH)

# Convert to grayscale
image = image.convert("L")


# -----------------------------
# RESIZE
# -----------------------------

original_width, original_height = image.size

aspect_ratio = (
    original_height / original_width
)

# Terminal characters are taller
new_height = int(
    WIDTH * aspect_ratio * 0.5
)

image = image.resize(
    (WIDTH, new_height)
)


# -----------------------------
# ASCII CONVERSION
# -----------------------------

pixels = image.getdata()

ascii_image = ""

for i, pixel in enumerate(pixels):

    index = int(
        pixel
        / 255
        * (len(ASCII_CHARS) - 1)
    )

    ascii_image += ASCII_CHARS[index]

    if (i + 1) % WIDTH == 0:
        ascii_image += "\n"


# -----------------------------
# DISPLAY
# -----------------------------

print(ascii_image)