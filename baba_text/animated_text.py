from .animated_word import AnimatedWord
import imageio
from io import BytesIO
import numpy as np
from .rect import Rect
from .color import Color
from .constants import (
    TRANSPARENT_COLOR,
    SPRITE_SIZE,
    ANIMATION_FPS,
    ANIMATION_FRAME_COUNT,
    COLOR_PALETTE,
    KNOWN_WORDS_TO_COLOR,
    NEWLINE,
    TAB,
    SPACE,
    COLOR_BYTE_DEPTH,
    GIF_DISPOSAL_MODE_TRANSPARENT,
    GIF_DISPOSAL_MODE_SOLID,
    GIF_LOOP_MODE,
    GIF_FORMAT_HINT,
    GIF_PLUGIN,
    FULL_ALPHA,
)


class AnimatedText:
    def __init__(self, text: str, background_color: Color = TRANSPARENT_COLOR) -> None:
        assert text, "Text must not be empty"
        self.__tokens = AnimatedText.__tokenize_input_text(text)
        self.__background_color = background_color

        word_layout = self.__generate_word_layout()
        self.__size = (
            max(w.right for w in word_layout),
            max(w.bottom for w in word_layout),
        )

        self.__words = [
            AnimatedWord(word, box, *self.__get_word_color(word), background_color)
            for word, box in zip(
                AnimatedText.__remove_control_sequences(self.__tokens), word_layout
            )
        ]

    @staticmethod
    def __remove_control_sequences(tokens: list[str]) -> list[str]:
        return list(filter(lambda x: x not in (TAB, NEWLINE), tokens))

    @staticmethod
    def __tokenize_input_text(text: str) -> list[str]:
        # If we find a sequence of not space separated characters
        # control chars like newline or tab we make them into words
        result = text.replace(NEWLINE, SPACE + NEWLINE + SPACE).replace(
            TAB, SPACE + TAB + SPACE
        )

        # Ensure every word is separated by exactly one space
        return list(filter(lambda x: len(x) > 0, result.split(SPACE)))

    def write_raw_frames(self) -> list[np.ndarray]:
        frames = []

        for _ in range(ANIMATION_FRAME_COUNT):
            # Careful: Numpy is column major (we need to flip x and y)
            screen = np.full(
                (self.__size[1], self.__size[0], COLOR_BYTE_DEPTH),
                self.__background_color,
                dtype=np.uint8,
            )
            for word in self.__words:
                word.draw(screen)
                word.advance_animation()

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
            duration=(1000 * 1 / ANIMATION_FPS),
            loop=GIF_LOOP_MODE,
            disposal=GIF_DISPOSAL_MODE_TRANSPARENT
            if self.__background_color.a != FULL_ALPHA
            else GIF_DISPOSAL_MODE_SOLID,
        )
        result.seek(0)
        return result

    def __generate_word_layout(self) -> list[Rect]:
        result = []
        x = 0
        y = 0
        for token in self.__tokens:
            if token == NEWLINE:
                y += 1
                x = 0
                continue
            elif token == TAB:
                x += 1
                continue

            result.append(
                Rect(x * SPRITE_SIZE, y * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE)
            )
            x += 1

        return result

    @staticmethod
    def __get_word_hash(word):
        return sum(ord(c) for c in word)

    def __get_word_color(self, word: str) -> tuple[Color, Color]:
        color_values = list(COLOR_PALETTE.values())
        lookup_color = (
            KNOWN_WORDS_TO_COLOR[word]
            if word in KNOWN_WORDS_TO_COLOR
            else color_values[AnimatedText.__get_word_hash(word) % len(color_values)]
        )
        if word[0].isupper():
            return self.__background_color, lookup_color
        else:
            return lookup_color, self.__background_color
