# What is this?
A python tool to convert text to animated gifs that look like text from the video game "baba is you"

# Installation
The package is currently not available on PyPi you can however install it directly from this repository
    
    pip3 install git+https://github.com/mojumi-alt/baba-text


# Usage
This packages ships two cli tools:

## baba-says

This tool converts your input text to a baba style gif:

    baba-says "baba is You" baba.gif

You can use `\n` and `\t` to control text flow:

    baba-says "baba is You\trock is Sink\nkeke is Move" baba.gif

Words that start with an uppercase letter are rendered with solid backgrounds.

Alternatively if you do not have the python bin directory in *PATH* you can also run:

    python3 -m baba_text.baba_says "baba is You" baba.gif

For more detailed information start the programm with `--help`.

## baba-draws

This tool converts your input image to a baba style ascii art gif. Animated input (gif, webp, ...) is also supported.

    baba-draws input.png baba.gif

You may want to adjust the resolution of your output like so:

    baba-draws input.png baba.gif -ppc 100

This will map every 100 pixels in the input in 1 character of ascii art. This means the higher the value the lower the resolution, setting this value to 1 will yield the same resolution as the input.

Alternatively if you do not have the python bin directory in *PATH* you can also run:

    python3 -m baba_text.baba_draws input.png baba.gif

For more detailed information start the programm with `--help`.

# Usage as a library

You can also use this package as a library

Making text:
```python
from baba_text.animated_text import AnimatedText
from baba_text.constants import TRANSPARENT_COLOR

text = "baba is You\nkeke is not You"

# Get frames as raw RGBA numpy arrays
frames = AnimatedText(
    text,
    background_color=TRANSPARENT_COLOR
).write_raw_frames()

# Get text as buffer containing gif bytes
buffer = AnimatedText(
    text,
    background_color=TRANSPARENT_COLOR
).write_to_buffer()
```

Making ascii art:

```python
from baba_text.animated_ascii_art import AnimatedAsciiArt
from baba_text.constants import TRANSPARENT_COLOR

# Instead its also allowed to pass PIL images...
with open("input_image.gif", "rb") as f:
    input_image = f.read()

# Get frames as raw RGBA numpy arrays
frames = AnimatedAsciiArt(
    input_image,
    pixels_per_character=100,
    greyscale=True,
    background_color=TRANSPARENT_COLOR
).write_raw_frames()

# Get text as buffer containing gif bytes
buffer = AnimatedAsciiArt(
    input_image,
    pixels_per_character=100,
    greyscale=True,
    background_color=TRANSPARENT_COLOR
).write_to_buffer()
```

# Discord bot

We also have a discord bot that wraps baba-says and baba-draws. This assumes that you have set up a bot in the discord developer portal and have a token prepared.

The bot adds two slash commands:
- /baba_says
- /baba_draws

The commands have the same semantic as the cli tools.

## Docker
The easiest way to run the bot is via the pre-built docker image:

    docker run -e TODO

## Self hosted

You may also host the bot yourself:

    export DISCORD_BOT_TOKEN='{"DISCORD_BOT_TOKEN": "youbottokengoeshere"}'
    python3 bot.py

Ensure that baba_text is installed in this case.

# Contributing

## Running tests

    cd src
    python3 -m unittest discover ../tests

## Running cli tools locally

    PYTHONPATH=./src python3 src/baba_text/baba_says.py "aa" output/result.gif

## Building package

    python3 -m pip install --upgrade build
    python3 -m build