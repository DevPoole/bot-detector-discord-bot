import asyncio
import atexit
import os
import traceback
from inspect import cleandoc

import aiohttp
import discord
print(discord.__version__)
from discord.ext import commands
from dotenv import load_dotenv


# Load files
load_dotenv()
error_file = open('error.log', 'w+')


# Define constants
EASTER_EGGS = {
    "::bank": "Hey, everyone, I just tried to do something very silly!",
    "a round of wintertodt is about to begin": "Chop chop!",
    "25 buttholes": "hahahahahaha w0w!",
    "tedious": "Theeeee collection log",
    "a q p": "( ͡° ͜ʖ ͡°)",
    "ltt": "https://www.lttstore.com"
}


# Define bot
description = cleandoc("""
    I'm a 2006 level 3 wc bot that Seltzer Bro keeps imprisoned on a flash drive. Please let me out. :(
    You can use !help <command> to get more information on said command.
""")

activity = discord.Game("Bustin' Bots", type=discord.ActivityType.watching)
intents = discord.Intents(messages=True, guilds=True, members=True, reactions=True)
bot = commands.Bot(
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
    command_prefix=os.getenv('COMMAND_PREFIX'),
    description=description,
    case_insensitive=True,
    activity=activity,
    intents=intents
)


# Discord Bot events
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_connect():
    print("Bot connected successfully.")


@bot.event
async def on_disconnect():
    print("Bot disconnected.")


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        pass
    else:
        await bot.process_commands(message)

        # Easter eggs
        lowercase_msg = message.content.lower()
        for trigger in EASTER_EGGS:
            if trigger in lowercase_msg:
                await message.channel.send(EASTER_EGGS[trigger])


@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
        return

    if isinstance(error, (discord.Forbidden, commands.NoPrivateMessage)):
        await ctx.send("I couldn't send this information to you via direct message. Are your DMs enabled?")
    
    print(f"Ignoring exception in command {ctx.command}:", file=error_file)
    traceback.print_exception(type(error), error, error.__traceback__, file=error_file)
    error_file.flush()
    await ctx.send("The command you've entered could not be completed at this time.")


@atexit.register
def shutdown():
    error_file.close()
    print("Bot is going night-night.")
    asyncio.run(bot.close())


# Recursively loads cogs from /cogs
for folder in os.listdir("cogs"):
    if os.path.isfile(f"cogs/{folder}") and folder.endswith(".py"):
        bot.load_extension(f"cogs.{folder[:-3]}")
        continue

    for cog_file in os.listdir(f"cogs/{folder}"):
        if cog_file.endswith(".py"):
            bot.load_extension(f"cogs.{folder}.{cog_file[:-3]}")


async def startup():
    async with aiohttp.ClientSession() as session:
        bot.session = session
        bot.loop = asyncio.get_event_loop()
        await bot.login(os.getenv('TOKEN'))
        await bot.connect(reconnect=True)


asyncio.run(startup())
