import unittest
import os

from baba_text.animated_text import AnimatedText
from baba_text.color import Color

OUTPUT_DIR = "./output"


class TestColor(unittest.TestCase):
    def test_different_background_color(self):
        AnimatedText("A B C", Color(128, 128, 128)).write_to_gif(
            os.path.join(OUTPUT_DIR, "background_color.gif")
        )
