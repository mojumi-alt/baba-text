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
    NEWLINE,
    TAB,
    SPACE,
)


class AnimatedText:
    def __init__(self, text: str) -> None:
        assert text, "Text must not be empty"
        self.__tokens = AnimatedText.__tokenize_input_text(text)

        word_layout = self.__generate_word_layout()
        self.__size = (
            max(w.right for w in word_layout),
            max(w.bottom for w in word_layout),
        )

        self.__words = [
            AnimatedWord(word, box, *AnimatedText.__get_word_color(word))
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
                pygame.Rect(x * SPRITE_SIZE, y * SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE)
            )
            x += 1

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
