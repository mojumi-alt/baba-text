import sys
from baba_text.animated_text import AnimatedText

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise ValueError(
            f"Expected 2 arguments (input string to convert and output file name), got {len(sys.argv) - 1} instead!"
        )

    AnimatedText(sys.argv[1]).write_to_gif(sys.argv[2])
