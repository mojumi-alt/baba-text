from baba_text.animated_text import AnimatedText
import argparse
from baba_text.constants import COLOR_PALETTE, TRANSPARENT_COLOR

def main_cli():
    parser = argparse.ArgumentParser(
        prog="baba-says",
        description="Render a sentence as a baba text style gif."
        "Use uppercase letter to denote adjectives."
        "Use \\n and \\t for text layout",
    )
    parser.add_argument("input_text", help="The input text to render")
    parser.add_argument("output_file", help="Where to write the output gif to")
    parser.add_argument(
        "-s",
        "--solid",
        action="store_true",
        default=False,
        help="Make background solid instead of transparent",
    )
    args = parser.parse_args()

    AnimatedText(
        args.input_text.replace("\\n", "\n").replace("\\t", "\t"),
        background_color=TRANSPARENT_COLOR
        if not args.solid
        else COLOR_PALETTE["black"],
    ).write_to_gif(args.output_file)
