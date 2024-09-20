import multiprocessing.queues
import sys
import discord
from discord.ext import commands
import multiprocessing
import os
import json
import queue
import traceback

BOT_REQUEST_TIMEOUT_SECONDS = 10

def run_baba_text_gen(text: str, output_queue: multiprocessing.Queue):
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
    from baba_text.animated_text import AnimatedText

    try:
        animated_text = AnimatedText(text)
        output_queue.put(animated_text.write_to_buffer())
    except:
        print(traceback.format_exc(), flush=True)
        output_queue.put(None)

def main():
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    if DISCORD_BOT_TOKEN is None:
        print("Set DISCORD_BOT_TOKEN to bot token.", flush=True)
        sys.exit(1)

    DISCORD_BOT_TOKEN = json.loads(DISCORD_BOT_TOKEN)["DISCORD_BOT_TOKEN"]

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.command()
    async def baba(ctx: discord.ext.commands.context.Context):
        output_queue: multiprocessing.Queue = multiprocessing.Queue()
        message = (
            ctx.message.content[len("!baba") :]
            .replace("\\t", "\t")
            .replace("\\n", "\n")
        )
        process = multiprocessing.Process(
            target=run_baba_text_gen, args=(message, output_queue)
        )
        process.start()
        try:
            result = output_queue.get(timeout=BOT_REQUEST_TIMEOUT_SECONDS)
        except queue.Empty:
            await ctx.send("message is long. baba is sad.")
            return

        process.join(timeout=1)
        if process.exitcode != 0 or result is None:
            await ctx.send("message has error. baba is sad.")
        else:
            await ctx.send(file=discord.File(result, filename="baba_text.gif"))

    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
