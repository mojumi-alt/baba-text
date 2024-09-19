import pygame
from .animated_object import AnimatedObject
import urllib.parse


class AnimatedLetter(AnimatedObject):
    def __init__(
        self,
        letter: str,
        box: pygame.Rect,
        text_color: pygame.Color,
        background_color: pygame.Color,
    ) -> None:
        try:
            super().__init__(
                urllib.parse.quote(letter.upper()), box, text_color, background_color
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Got illegal character: {letter}")
