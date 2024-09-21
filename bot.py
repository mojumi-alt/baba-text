import multiprocessing.queues
import sys
import discord
from discord.ext import commands
import multiprocessing
import os
import json
import queue
import traceback
import logging

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from baba_text.constants import get_allowed_characters

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s (%(funcName)s): %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
)

BOT_REQUEST_TIMEOUT_SECONDS = 10
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


def preprocess_message(message: str) -> str:
    for sequence, replacement in UNESCAPE_SEQUENCES:
        message = message.replace(sequence, replacement)
    return message


def run_baba_text_gen(text: str, output_queue: multiprocessing.Queue) -> None:
    from baba_text.animated_text import AnimatedText

    try:
        animated_text = AnimatedText(text)
        output_queue.put(animated_text.write_to_buffer())
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
        logging.info(f"Synced {len(synced)} to build '{guild}'")

    @bot.event
    async def on_guild_remove(guild: discord.Guild) -> None:
        logging.info(f"Bot removed from guild '{guild}'")

    # Commands
    @bot.tree.command()
    async def baba_says(interaction: discord.Interaction, text: str) -> None:
        """
        Converts your message to baba style gif.
        Use \\t for horizontal and \\n for vertical spacing.
        """
        # Do not remove docstring, it holds the help text displayed in discord.
        logging.info(
            f"Processing message of length {len(text)} for guild '{interaction.guild}'"
        )

        # Validate input text
        message = preprocess_message(text)
        for c in message:
            if c not in ALLOWED_CHARACTERS:
                logging.error(
                    f"Message in guild '{interaction.guild}' contains invalid character '{c}'"
                )
                await interaction.response.send_message(
                    f"message has error. '{c}' is not allowed.", ephemeral=True
                )
                return

        # Run conversion in separate process, this way we ensure
        # no potential pygame issues leak into the bot.
        output_queue: multiprocessing.Queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=run_baba_text_gen, args=(message, output_queue)
        )
        process.start()

        try:
            result = output_queue.get(timeout=BOT_REQUEST_TIMEOUT_SECONDS)
        except queue.Empty:
            await interaction.response.send_message(
                "message is long. baba is sad.", ephemeral=True
            )
        else:
            process.join(timeout=1)
            if process.exitcode != 0 or result is None:
                await interaction.response.send_message(
                    "message has error. baba is sad.", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    file=discord.File(result, filename="baba_text.gif")
                )
        finally:
            logging.info(
                f"Processed message of length {len(text)} for guild '{interaction.guild}'"
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
