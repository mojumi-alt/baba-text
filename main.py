import os
import sys

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from baba_text.animated_text import AnimatedText

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError(
            f"Expected 2 arguments (input string to convert and output file name), got {len(sys.argv)} instead!"
        )

    AnimatedText(sys.argv[1]).write_to_gif(sys.argv[2])
