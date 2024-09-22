from .animated_letter import AnimatedLetter
from math import sqrt, floor, ceil
from .constants import (
    MAX_LETTER_HEIGHT,
    LETTER_WIDTH_TO_HEIGHT_RATIO,
    BACKGROUND_COLOR,
    BACKGROUND_SPRITE_FILENAME,
)
from .animated_object import AnimatedObject
from .rect import Rect
from .color import Color
import numpy as np


class AnimatedWord(AnimatedObject):
    def __init__(
        self,
        text: str,
        box: Rect,
        text_color: Color,
        background_color: Color,
    ) -> None:
        self.__text = text
        assert self.__text
        self.__box = box
        self.__letters = [
            AnimatedLetter(c, b, text_color, background_color)
            for c, b in zip(text, self.__fit_text_to_this_box())
        ]
        super().__init__(
            BACKGROUND_SPRITE_FILENAME, box, background_color, BACKGROUND_COLOR
        )

    def advance_animation(self):
        super().advance_animation()
        for letter in self.__letters:
            letter.advance_animation()

    def draw(self, surface: np.ndarray) -> None:
        super().draw(surface)
        for letter in self.__letters:
            letter.draw(surface)

    def __fit_text_to_this_box(self) -> list[Rect]:
        row_count = int(floor(sqrt(len(self.__text))))
        per_row = int(ceil(len(self.__text) / row_count))

        # Magic scale function to make it look more similar
        # to baba text with low letter count...
        if len(self.__text) == 1:
            scale = 1.0
        elif len(self.__text) == 2:
            scale = 1.0
        elif 3 <= len(self.__text) <= 4:
            scale = 1.0
        else:
            scale = 0.75

        want_letter_height = min(
            (self.__box.height / row_count) * scale, MAX_LETTER_HEIGHT
        )
        want_letter_width = min(
            (self.__box.width / per_row) * scale,
            MAX_LETTER_HEIGHT * LETTER_WIDTH_TO_HEIGHT_RATIO,
        )

        if want_letter_height > want_letter_width * (1 / LETTER_WIDTH_TO_HEIGHT_RATIO):
            letter_height = want_letter_width * (1 / LETTER_WIDTH_TO_HEIGHT_RATIO)
            letter_width = want_letter_width
        else:
            letter_height = want_letter_height
            letter_width = letter_height * LETTER_WIDTH_TO_HEIGHT_RATIO

        offset_x = (self.__box.width - per_row * (letter_width)) / 2
        offset_y = (self.__box.height - row_count * (letter_height)) / 2

        assert offset_x >= 0, self.__text
        assert offset_y >= 0, self.__text

        rectangles = []
        for i in range(row_count - 1):
            for j in range(per_row):
                rectangles.append(
                    Rect(
                        offset_x + self.__box.left + j * (letter_width),
                        offset_y + self.__box.top + i * (letter_height),
                        letter_width,
                        letter_height,
                    )
                )

        if len(self.__text) != row_count * per_row:
            remaining = len(self.__text) - ((row_count - 1) * per_row)
            width_of_remaining = letter_width * remaining
            width_of_full_row = letter_width * per_row
            extra_x_offset = (width_of_full_row - width_of_remaining) / 2
            for j in range(remaining):
                rectangles.append(
                    Rect(
                        extra_x_offset + offset_x + self.__box.left + j * letter_width,
                        offset_y + self.__box.top + (row_count - 1) * letter_height,
                        letter_width,
                        letter_height,
                    )
                )
        else:
            for j in range(per_row):
                rectangles.append(
                    Rect(
                        offset_x + self.__box.left + j * letter_width,
                        offset_y + self.__box.top + (row_count - 1) * letter_height,
                        letter_width,
                        letter_height,
                    )
                )

        assert len(rectangles) > 0, self.__text

        return rectangles
