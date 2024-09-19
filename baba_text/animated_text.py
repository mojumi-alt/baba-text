from .animated_word import AnimatedWord
import pygame
import imageio
from io import BytesIO
from .constants import (
    BACKGROUND_COLOR,
    SPRITE_SIZE,
    ANIMATION_FPS,
    ANIMATION_FRAME_COUNT,
    COLOR_PALETTE,
    KNOWN_WORDS_TO_COLOR,
)
import re


class AnimatedText:
    def __init__(self, text: str) -> None:
        assert text, "Text must not be empty"
        self.__text = AnimatedText.__preprocess_input_text(text)

        word_layout = self.__generate_word_layout()
        self.__size = (
            max(w.right for w in word_layout),
            max(w.bottom for w in word_layout),
        )

        self.__words = [
            AnimatedWord(word, box, *AnimatedText.__get_word_color(word))
            for word, box in zip(
                filter(lambda x: x != "\t", re.split(" |\n", self.__text)), word_layout
            )
        ]

    @staticmethod
    def __preprocess_input_text(text) -> str:
        result = ""
        consolidate_characters = (" ", "\n")
        for i in range(len(text)):
            if (
                len(result) > 0
                and result[-1] in consolidate_characters
                and text[i] in consolidate_characters
            ):
                continue
            else:
                result += text[i]

        delimiters = (" ", "\n")
        for delimiter in delimiters:
            result = delimiter.join(
                filter(lambda x: len(x) > 0, result.split(delimiter))
            )

        return result

    def write_to_gif(self, filename: str) -> None:
        with open(filename, "wb") as f:
            f.write(self.write_to_buffer().getbuffer())

    def write_to_buffer(self):
        pygame.init()
        screen = pygame.Surface(self.__size)

        frames = []

        for _ in range(ANIMATION_FRAME_COUNT):
            screen.fill(BACKGROUND_COLOR)
            for word in self.__words:
                word.draw(screen)
                word.advance_animation()

            frame = BytesIO()
            pygame.image.save(screen, frame)
            frame.seek(0)
            frames.append(imageio.v3.imread(frame))

        result = BytesIO()
        imageio.mimsave(result, [*frames], format="gif", fps=ANIMATION_FPS, loop=0)
        result.seek(0)
        pygame.quit()
        return result

    def __generate_word_layout(self) -> list[pygame.Rect]:
        result = []
        for y, row in enumerate(self.__text.split("\n")):
            for x, word in enumerate(row.split(" ")):
                # Tab is skip character to allow aligning text
                if word == "\t":
                    continue

                result.append(
                    pygame.Rect(
                        x * SPRITE_SIZE, y * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE
                    )
                )

        return result

    @staticmethod
    def __get_word_hash(word):
        return sum(ord(c) for c in word)

    @staticmethod
    def __get_word_color(word: str) -> tuple[pygame.Color, pygame.Color]:
        color_values = list(COLOR_PALETTE.values())
        lookup_color = (
            KNOWN_WORDS_TO_COLOR[word]
            if word in KNOWN_WORDS_TO_COLOR
            else color_values[AnimatedText.__get_word_hash(word) % len(color_values)]
        )
        if word[0].isupper():
            return BACKGROUND_COLOR, lookup_color
        else:
            return lookup_color, BACKGROUND_COLOR
