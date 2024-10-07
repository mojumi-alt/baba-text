import unittest
import os
from io import BytesIO

from baba_text.animated_text import AnimatedText
from baba_text.animated_ascii_art import AnimatedAsciiArt
from PIL import Image

OUTPUT_DIR = "../output"


class TestAsciiText(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def test_static_ascii(self):
        frame = AnimatedText("A").write_raw_frames()[0]
        buffer = BytesIO()
        Image.fromarray(frame).save(buffer, format="png")
        buffer.seek(0)
        AnimatedAsciiArt(buffer, 5).write_to_gif(
            os.path.join(OUTPUT_DIR, "ascii_art_static.gif")
        )

    def test_dynamic_ascii(self):
        gif = AnimatedText("A").write_to_buffer()
        AnimatedAsciiArt(gif, 5).write_to_gif(
            os.path.join(OUTPUT_DIR, "ascii_art_dynamic.gif")
        )
