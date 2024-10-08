import multiprocessing.queues
import discord
from discord.ext import commands
import multiprocessing
import os
import json
import queue
import traceback
import logging
from io import BytesIO
from PIL import Image
import math

from baba_text.constants import get_allowed_characters, TRANSPARENT_COLOR
from baba_text.color import Color
from baba_text.animated_text import AnimatedText
from baba_text.animated_ascii_art import AnimatedAsciiArt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s (%(funcName)s): %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
)

BOT_SAY_REQUEST_TIMEOUT_SECONDS = 10
BOT_DRAW_REQUEST_TIMEOUT_SECONDS = 30
ASCII_MAX_DIMENSION = 64
ALLOWED_CHARACTERS = get_allowed_characters()
DISCORD_BOT_TOKEN_ENV_VAR = "DISCORD_BOT_TOKEN"
DISCORD_BOT_TOKEN_SECRET_KEY = "DISCORD_BOT_TOKEN"


# Certain sequences arrive in escaped form from discord.
# The following sequences are "unescaped" with their replacements:
UNESCAPE_SEQUENCES = [
    ("\\n", "\n"),
    ("\\t", "\t"),
    ("\\:", ":"),
    # hmmmm....
    ("🙂", ":)"),
    ("😦", ":("),
]

ALTERNATE_BACKGROUND_COLOR = Color(49, 51, 56)


class YesNoDialog(discord.ui.View):
    def __init__(self, attachment: discord.File, original_interaction: discord.Interaction, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.__attachment = attachment
        self.__original_interaction = original_interaction

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.edit_message(
            content="message is send", attachments=[], view=None
        )
        self.__attachment.reset()
        await self.__original_interaction.edit_original_response(content="", attachments=[self.__attachment])

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.edit_message(
            content="message is not send", attachments=[], view=None
        )
        await self.__original_interaction.delete_original_response()


def preprocess_message(message: str) -> str:
    for sequence, replacement in UNESCAPE_SEQUENCES:
        message = message.replace(sequence, replacement)
    return message


def run_baba_says(
    text: str, transparent_background: bool, output_queue: multiprocessing.Queue
) -> None:

    try:
        animated_text = AnimatedText(
            text,
            TRANSPARENT_COLOR if transparent_background else ALTERNATE_BACKGROUND_COLOR,
        )
        output_queue.put(animated_text.write_to_buffer())
    except:
        logging.error(traceback.format_exc())
        output_queue.put(None)


def run_baba_draws(
    input_image: BytesIO,
    transparent_background: bool,
    greyscale: bool,
    output_queue: multiprocessing.Queue,
) -> None:

    image = Image.open(input_image)
    longer_side = max(image.width, image.height)
    pixels_per_character = (
        math.ceil(longer_side / ASCII_MAX_DIMENSION)
        if longer_side > ASCII_MAX_DIMENSION
        else 1
    )

    logging.info(
        f"Image: ({image.width}, {image.height}) -> ppc = {pixels_per_character}"
    )
    try:
        art = AnimatedAsciiArt(
            input_image,
            pixels_per_character=pixels_per_character,
            greyscale=greyscale,
            background_color=TRANSPARENT_COLOR
            if transparent_background
            else ALTERNATE_BACKGROUND_COLOR,
        )
        output_queue.put(art.write_to_buffer())
    except:
        logging.error(traceback.format_exc())
        output_queue.put(None)


def load_bot_token() -> str:
    bot_token = os.getenv(DISCORD_BOT_TOKEN_ENV_VAR)

    if bot_token is None:
        raise ValueError(
            f'Failed to start. Set {DISCORD_BOT_TOKEN_ENV_VAR} to \'{{"{DISCORD_BOT_TOKEN_SECRET_KEY}": "yourtokengoeshere"}}\''
        )

    parsed_bot_token = json.loads(bot_token)[DISCORD_BOT_TOKEN_SECRET_KEY]
    if parsed_bot_token is None:
        raise ValueError("Bot token was provided but is None")

    return parsed_bot_token


if __name__ == "__main__":
    discord_bot_token = load_bot_token()

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Events
    @bot.event
    async def on_ready() -> None:
        logging.info(f"Logged in as: {bot.user}")

    @bot.event
    async def on_guild_join(guild: discord.Guild) -> None:
        logging.info(f"Joined guild {guild} as '{bot.user}'")
        logging.info("Setting up slash commands...")
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        logging.info(f"Synced {len(synced)} commands to guild '{guild}'")

    @bot.event
    async def on_guild_remove(guild: discord.Guild) -> None:
        logging.info(f"Bot removed from guild '{guild}'")

    # Commands
    @bot.tree.command()
    async def baba_says(
        interaction: discord.Interaction, text: str, transparent_background: bool = True
    ) -> None:
        """
        Converts your message to baba style gif.
        Use \\t for horizontal and \\n for vertical spacing.
        """
        # Do not remove docstring, it holds the help text displayed in discord.
        logging.info(
            f"Processing message of length {len(text)} for guild '{interaction.guild}'"
        )
        await interaction.response.defer(ephemeral=False)

        # Validate input text
        message = preprocess_message(text)
        for c in message:
            if c not in ALLOWED_CHARACTERS:
                logging.error(
                    f"Message in guild '{interaction.guild}' contains invalid character '{c}'"
                )
                await interaction.delete_original_response()
                await interaction.followup.send(
                    f"message has error. '{c}' is not allowed.", ephemeral=True
                )
                return

        # Run conversion in separate process, this way we ensure
        # no potential issues leak into the bot.
        output_queue: multiprocessing.Queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=run_baba_says,
            args=(message, transparent_background, output_queue),
        )
        process.start()

        try:
            result = output_queue.get(timeout=BOT_SAY_REQUEST_TIMEOUT_SECONDS)
        except queue.Empty:
            await interaction.delete_original_response()
            await interaction.followup.send(
                "text is long. baba is sad.", ephemeral=True
            )
        else:
            process.join(timeout=1)
            if process.exitcode != 0 or result is None:
                await interaction.delete_original_response()
                await interaction.followup.send(
                    "text has error. baba is sad.",
                    ephemeral=True,
                )
            else:
                await interaction.edit_original_response(content="baba is considering...")
                result_attachment = discord.File(result, filename="baba_text.gif")
                await interaction.followup.send(
                    content="baba has preview. message is send?",
                    file=result_attachment,
                    view=YesNoDialog(result_attachment, interaction),
                    ephemeral=True
                )
        finally:
            logging.info(
                f"Processed message of length {len(text)} for guild '{interaction.guild}'"
            )

    @bot.tree.command()
    async def baba_draws(
        interaction: discord.Interaction,
        image: discord.Attachment,
        transparent_background: bool = True,
        greyscale: bool = False,
    ) -> None:
        logging.info(
            f"Processing image '{image.filename}' for guild '{interaction.guild}'"
        )
        await interaction.response.defer(ephemeral=False)

        # Lets hope discord limits the size for us...
        buffer = BytesIO()
        buffer.write(await image.read())
        logging.info(f"Image size in bytes: {buffer.tell()}")

        # Run conversion in separate process, this way we ensure
        # no potential issues leak into the bot.
        output_queue: multiprocessing.Queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=run_baba_draws,
            args=(buffer, transparent_background, greyscale, output_queue),
        )
        process.start()

        try:
            result = output_queue.get(timeout=BOT_DRAW_REQUEST_TIMEOUT_SECONDS)
        except queue.Empty:
            await interaction.delete_original_response()
            await interaction.followup.send(
                "image is big. baba is sad.", ephemeral=True
            )
        else:
            process.join(timeout=1)
            if process.exitcode != 0 or result is None:
                await interaction.delete_original_response()
                await interaction.followup.send(
                    "image has error. baba is sad. format is not supported.", ephemeral=True
                )
            else:
                await interaction.edit_original_response(content="baba is considering...")
                result_attachment = discord.File(result, filename="baba_text.gif")
                await interaction.followup.send(
                    content="baba has preview. message is send?",
                    file=result_attachment,
                    view=YesNoDialog(result_attachment, interaction),
                    ephemeral=True
                )
        finally:
            logging.info(
                f"Processed image '{image.filename}' for guild '{interaction.guild}'"
            )

    @bot.command()
    @commands.guild_only()
    @discord.ext.commands.has_permissions(ban_members=True)
    async def disable_baba(ctx: discord.ext.commands.context.Context) -> None:
        logging.info(f"Clearing slash commands for guild '{ctx.guild}'")
        try:
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
        except Exception as e:
            logging.error(f"Error while clearing commands on guild {ctx.guild}: {e}")
            await ctx.send(f"baba is not stop. baba has error. you is wait.")
        else:
            logging.info(f"Cleared slash commands for guild '{ctx.guild}'")
            await ctx.send("baba is stop")

    @bot.command()
    @commands.guild_only()
    @discord.ext.commands.has_permissions(ban_members=True)
    async def enable_baba(ctx: discord.ext.commands.context.Context) -> None:
        try:
            logging.info(f"Manual slash command sync for guild '{ctx.guild}'")
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        except Exception as e:
            logging.error(f"Error while syncing commands on guild {ctx.guild}: {e}")
            await ctx.send(f"baba is not go. baba has error. you is wait.")
        else:
            logging.info(f"Synced {len(synced)} commands for guild {ctx.guild}")
            await ctx.send(f"baba is go")

    bot.run(discord_bot_token, log_handler=None)
