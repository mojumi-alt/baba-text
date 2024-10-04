import os
from glob import glob
import urllib
from .color import Color
from PIL import Image
import numpy as np

NEWLINE = "\n"
TAB = "\t"
SPACE = " "
MASK_COLOR = Color(255, 255, 255)
SPRITE_SIZE = 100
TRANSPARENT_COLOR = Color(0, 0, 0, 0)
ANIMATION_FPS = 4
MAX_LETTER_HEIGHT = 55
LETTER_WIDTH_TO_HEIGHT_RATIO = 0.8
RESOURCE_LETTER_HEIGHT = 25
RESOURCE_LETTER_WIDTH = RESOURCE_LETTER_HEIGHT * LETTER_WIDTH_TO_HEIGHT_RATIO
RESOURCE_DIR = "./resources"
ANIMATION_FRAME_COUNT = 6
COLOR_WHITE = Color(255, 255, 255)
BACKGROUND_SPRITE_FILENAME = "sprite"
COLOR_BYTE_DEPTH = 4
GIF_DISPOSAL_MODE_TRANSPARENT = 2
GIF_DISPOSAL_MODE_SOLID = 0
FULL_ALPHA = 255
GIF_LOOP_MODE = 0
GIF_PLUGIN = "pillow"
GIF_FORMAT_HINT = ".gif"
LETTER_SAMPLE_MODE = Image.Resampling.NEAREST
DOWNSCALE_SAMPLE_MODE = Image.Resampling.NEAREST
DEFAULT_PIXEL_PER_CHARACTERS = 30


def get_allowed_characters() -> set[str]:
    """
    Automatically determine what characters we support for text.
    """

    allowed = set()

    for file in os.listdir(RESOURCE_DIR):
        file = os.path.join(RESOURCE_DIR, file)

        letter = os.path.basename(file)

        # Underscore is special because its a valid letter but also separator...
        if letter.startswith("_") or letter.startswith(BACKGROUND_SPRITE_FILENAME):
            continue

        decoded = urllib.parse.unquote(letter.split("_")[0])

        # We lower case letter are also allowed...
        allowed.add(decoded)
        if decoded.lower() != decoded.upper():
            allowed.add(decoded.lower())

    allowed.update([SPACE, TAB, NEWLINE, "_"])

    return allowed


def generate_ascii_color_ramp() -> str:
    """
    Converts all available letters into a color ramp, ordering them
    by "brightness" (which is just the total coverage of the letter over the background)
    """

    letter_to_brightness: dict[str, int] = {}

    for file in os.listdir(RESOURCE_DIR):
        file = os.path.join(RESOURCE_DIR, file)
        letter = os.path.basename(file)

        # Underscore is special because its a valid letter but also separator...
        if letter.startswith(BACKGROUND_SPRITE_FILENAME):
            continue
        elif letter.startswith("_"):
            decoded = "_"
        else:
            decoded = urllib.parse.unquote(letter.split("_")[0])

        image = np.array(Image.open(file).convert("RGBA"))
        foreground_mask = np.any(image != MASK_COLOR, axis=2)

        letter_to_brightness.setdefault(decoded, 0)
        letter_to_brightness[decoded] += np.count_nonzero(foreground_mask)

    return "".join(
        [i for i, _ in sorted(letter_to_brightness.items(), key=lambda item: item[1])]
    )


COLOR_PALETTE = {
    "grey": Color(128, 128, 128),
    "yellow": Color(255, 255, 60),
    "orange": Color(250, 120, 60),
    "dark_red": Color(255, 60, 60),
    "red": Color(255, 50, 120),
    "pale_red": Color(255, 120, 120),
    "dark_purple": Color(160, 20, 160),
    "purple": Color(120, 120, 255),
    "dark_blue": Color(20, 20, 200),
    "blue": Color(60, 60, 255),
    "black": Color(0, 0, 0),
    "pink": Color(255, 120, 255),
    "dark_pink": Color(255, 60, 255),
    "dark_green": Color(60, 160, 60),
    "green": Color(60, 255, 60),
    "light_green": Color(120, 255, 120),
    "brown": Color(150, 100, 70),
    "light_blue": Color(60, 160, 255),
}

KNOWN_WORDS_TO_COLOR = {
    "baba": COLOR_PALETTE["red"],
    "You": COLOR_PALETTE["red"],
    "keke": COLOR_PALETTE["orange"],
    "rock": COLOR_PALETTE["brown"],
    "Sink": COLOR_PALETTE["light_blue"],
    "text": COLOR_PALETTE["red"],
    "is": COLOR_WHITE,
    "and": COLOR_WHITE,
    "not": COLOR_PALETTE["red"],
    "or": COLOR_WHITE,
    "on": COLOR_WHITE,
    "can": COLOR_WHITE,
    "the": COLOR_WHITE,
    "has": COLOR_WHITE,
    "wall": COLOR_PALETTE["grey"],
    "Float": COLOR_PALETTE["light_blue"],
    "flag": COLOR_PALETTE["yellow"],
    "Blue": COLOR_PALETTE["blue"],
    "Red": COLOR_PALETTE["dark_red"],
    "Green": COLOR_PALETTE["green"],
    "Yellow": COLOR_PALETTE["yellow"],
    "Pink": COLOR_PALETTE["pink"],
    "Orange": COLOR_PALETTE["orange"],
    "Purple": COLOR_PALETTE["purple"],
    "White": COLOR_WHITE,
    "Black": COLOR_PALETTE["black"],
    "blue": COLOR_PALETTE["blue"],
    "red": COLOR_PALETTE["red"],
    "green": COLOR_PALETTE["green"],
    "yellow": COLOR_PALETTE["yellow"],
    "pink": COLOR_PALETTE["pink"],
    "orange": COLOR_PALETTE["orange"],
    "purple": COLOR_PALETTE["purple"],
    "white": COLOR_WHITE,
    "black": COLOR_PALETTE["black"],
    "violet": COLOR_PALETTE["blue"],
    "rose": COLOR_PALETTE["dark_red"],
    "Win": COLOR_PALETTE["yellow"],
}
