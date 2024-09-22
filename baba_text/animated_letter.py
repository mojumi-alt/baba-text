from .animated_object import AnimatedObject
import urllib.parse
from .rect import Rect
from .color import Color


class AnimatedLetter(AnimatedObject):
    def __init__(
        self,
        letter: str,
        box: Rect,
        text_color: Color,
        background_color: Color,
    ) -> None:
        try:
            super().__init__(
                AnimatedLetter.url_encode(letter.upper()), box, text_color, background_color
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Got illegal character: {letter}")
        
    @staticmethod   
    def url_encode(character):
        if character == "/":
            return "%2F"
        else:
            return urllib.parse.quote(character)