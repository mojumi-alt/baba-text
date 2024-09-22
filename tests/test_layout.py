import unittest
import os

from baba_text.animated_text import AnimatedText

OUTPUT_DIR = "./output"


class TestLayout(unittest.TestCase):
    def test_newlines(self):
        AnimatedText("\nA B C\nD E \n F \n\n X\nY\n").write_to_gif(
            os.path.join(OUTPUT_DIR, "newlines.gif")
        )

    def test_tabs(self):
        AnimatedText("\tA B C\tD E \t F \t X\tY\t").write_to_gif(
            os.path.join(OUTPUT_DIR, "tabs.gif")
        )

    def test_newlines_and_tabs(self):
        AnimatedText(
            "\n\t\tkeke\t\t\trock\n\t\tis\t\t\tis\n\t\tnot\t\t\tSink\nbaba is You\t\t\tand\n\t\t\t\t\t\tWin"
        ).write_to_gif(os.path.join(OUTPUT_DIR, "layout.gif"))
