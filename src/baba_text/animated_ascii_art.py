from PIL import Image
from typing import BinaryIO
import numpy as np
import math
from .constants import (
    TRANSPARENT_COLOR,
    ANIMATION_FRAME_COUNT,
    COLOR_BYTE_DEPTH,
    GIF_DISPOSAL_MODE_TRANSPARENT,
    GIF_DISPOSAL_MODE_SOLID,
    GIF_LOOP_MODE,
    GIF_FORMAT_HINT,
    GIF_PLUGIN,
    FULL_ALPHA,
    ANIMATION_FPS,
    SPACE,
    generate_ascii_color_ramp,
    RESOURCE_LETTER_HEIGHT,
    DOWNSCALE_SAMPLE_MODE,
    RESOURCE_LETTER_WIDTH,
    DEFAULT_PIXEL_PER_CHARACTERS,
    COLOR_PALETTE,
)
from .animated_letter import AnimatedLetter
from .rect import Rect
from .color import Color
from io import BytesIO
import imageio


class AnimatedAsciiArt:
    def __init__(
        self,
        image: str | BinaryIO | Image.Image,
        pixels_per_character: int = DEFAULT_PIXEL_PER_CHARACTERS,
        greyscale: bool = False,
        color_ramp: str = generate_ascii_color_ramp(),
        background_color: Color = TRANSPARENT_COLOR,
    ) -> None:
        assert len(color_ramp) > 0
        assert pixels_per_character > 0

        self.__pixels_per_character = pixels_per_character
        self.__greyscale = greyscale
        self.__color_ramp = color_ramp
        self.__background_color = background_color

        self.__images = []
        self.__durations = []

        if type(image) == Image.Image:
            loaded_image = image
        else:
            loaded_image = Image.open(image)  # type: ignore

        # Check if input is iterable like a gif or similar...
        if hasattr(loaded_image, "n_frames") and loaded_image.n_frames > 1:
            for n in range(loaded_image.n_frames):
                loaded_image.seek(n)
                self.__images.append(self.__load_image(loaded_image))
                self.__durations.append(
                    loaded_image.info.get("duration", 1000 * 1 / ANIMATION_FPS)
                )
        else:
            self.__images.extend(
                [self.__load_image(loaded_image)] * ANIMATION_FRAME_COUNT
            )
            self.__durations = [1000 * 1 / ANIMATION_FPS] * ANIMATION_FRAME_COUNT

    def __load_image(self, image: Image.Image) -> np.ndarray:
        image = image.convert("RGBA")
        return np.array(
            image.resize(
                (
                    math.floor(image.width / self.__pixels_per_character),
                    math.floor(image.height / self.__pixels_per_character),
                ),
                resample=DOWNSCALE_SAMPLE_MODE,
            )
        )

    def __pixel_to_ascii(self, pixel: np.ndarray) -> str:
        # wikipedia says this is how to convert color to greyscale...
        greyscale = (0.21 * pixel[0] + 0.72 * pixel[1] + 0.07 * pixel[2]) * (
            0 if pixel[3] == 0 else 1
        )
        return self.__color_ramp[
            math.ceil((len(self.__color_ramp) - 1) * greyscale / 255)
        ]

    def write_raw_frames(self) -> list[np.ndarray]:
        # Make all letters we need only once in default position
        # with default color.
        available_letters = {
            letter: AnimatedLetter(
                letter,
                Rect(0, 0, RESOURCE_LETTER_WIDTH, RESOURCE_LETTER_HEIGHT),
                COLOR_PALETTE["grey"],
                self.__background_color,
            )
            for letter in self.__color_ramp
            if letter != SPACE
        }

        # Manually keep track of animation states.
        # Start each letter in a random state.
        animation_states = np.random.randint(3, size=self.__images[0].shape[0:2])

        frames = []
        for image in self.__images:
            # Convert input image to string array that holds the ascii chars to render.
            ascii_image = np.apply_along_axis(self.__pixel_to_ascii, 2, image)

            # Not a typo: We make the letter boxes square so we dont
            # change the image aspect ratio.
            result_width = ascii_image.shape[0] * (RESOURCE_LETTER_HEIGHT)
            result_height = ascii_image.shape[1] * RESOURCE_LETTER_HEIGHT

            screen = np.full(
                (result_width, result_height, COLOR_BYTE_DEPTH),
                self.__background_color,
                dtype=np.uint8,
            )

            # Go over ascii image convert string to letter objects.
            for x in range(ascii_image.shape[0]):
                for y in range(ascii_image.shape[1]):
                    if ascii_image[x][y] == SPACE:
                        continue

                    letter = available_letters[ascii_image[x][y]]

                    # Again not a typo. Make letters square.
                    letter.location = (
                        y * RESOURCE_LETTER_HEIGHT,
                        x * RESOURCE_LETTER_HEIGHT,
                    )

                    if not self.__greyscale:
                        letter.foreground_color = image[x, y]

                    letter.draw(screen)
                    animation_states[x][y] = letter.advance_animation(
                        animation_states[x][y]
                    )

            frames.append(screen)

        return frames

    def write_to_gif(self, filename: str) -> None:
        with open(filename, "wb") as f:
            f.write(self.write_to_buffer().getbuffer())

    def write_to_buffer(self) -> BytesIO:
        result = BytesIO()
        imageio.v3.imwrite(
            result,
            self.write_raw_frames(),
            extension=GIF_FORMAT_HINT,
            plugin=GIF_PLUGIN,
            duration=self.__durations,
            loop=GIF_LOOP_MODE,
            disposal=GIF_DISPOSAL_MODE_TRANSPARENT
            if self.__background_color.a != FULL_ALPHA
            else GIF_DISPOSAL_MODE_SOLID,
        )
        result.seek(0)
        return result
