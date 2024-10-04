from baba_text.animated_ascii_art import AnimatedAsciiArt
import argparse
from baba_text.constants import COLOR_PALETTE, TRANSPARENT_COLOR

def main_cli():
    parser = argparse.ArgumentParser(
        prog="baba-draws",
        description="Render a static image or video to a baba ascii art gif",
    )
    parser.add_argument(
        "input_file",
        help="Input file, can either by an image (png, bmp, ...) or a video (gif, mp4, ...)",
    )
    parser.add_argument("output_file", help="Where to write the output gif to")
    parser.add_argument(
        "-s",
        "--solid",
        action="store_true",
        default=False,
        help="Make background solid instead of transparent",
    )
    parser.add_argument(
        "-ppc",
        "--pixels_per_character",
        default=30,
        type=int,
        help="How many pixels to reduce to one ascii char, higher = less resolution",
    )
    parser.add_argument(
        "-c",
        "--color",
        action="store_true",
        default=False,
        help="Whether to render in color or greyscale",
    )
    args = parser.parse_args()

    AnimatedAsciiArt(
        args.input_file,
        pixels_per_character=args.pixels_per_character,
        greyscale=not args.color,
        background_color=TRANSPARENT_COLOR
        if not args.solid
        else COLOR_PALETTE["black"],
    ).write_to_gif(args.output_file)

if __name__ == '__main__':
    main_cli()