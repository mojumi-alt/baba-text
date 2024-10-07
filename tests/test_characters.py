import unittest
import string
import os

from baba_text.animated_text import AnimatedText

OUTPUT_DIR = "../output"


class TestCharacters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def test_alphabet(self):
        AnimatedText(" ".join(string.ascii_lowercase)).write_to_gif(
            os.path.join(OUTPUT_DIR, "alphabet.gif")
        )

    def test_numbers(self):
        AnimatedText(" ".join(str(i) for i in range(0, 10))).write_to_gif(
            os.path.join(OUTPUT_DIR, "numbers.gif")
        )

    def test_special_characters(self):
        special_chars = [
            "-",
            "}",
            "(",
            "#",
            "{",
            "%",
            "@",
            "_",
            ",",
            "*",
            ">",
            ")",
            "]",
            "<",
            ";",
            "=",
            ":",
            "\\",
            "[",
            "!",
            "|",
            "'",
            '"',
            "+",
            "?",
            "$",
            "&",
            "~",
            "^",
            ".",
        ]
        AnimatedText(" ".join(special_chars)).write_to_gif(
            os.path.join(OUTPUT_DIR, "special.gif")
        )
