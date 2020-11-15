import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus

from cogs.consts import *

class c:
    c = '\033[0m'

    RedDark = '\033[31m'
    GreenDark = '\033[32m'
    YellowDark = '\033[33m'
    BlueDark = '\033[34m'
    PinkDark = '\033[35m'
    CyanDark = '\033[36m'

    Red = '\033[91m'
    Green = '\033[92m'
    Yellow = '\033[93m'
    Blue = '\033[94m'
    Pink = '\033[95m'
    Cyan = '\033[96m'

class Errors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Normal Green
        # Warning Yellow
        # Critical Red
        # Status Blue

        if   isinstance(error, commands.errors.NoPrivateMessage):      return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
        elif isinstance(error, commands.errors.BotMissingPermissions): return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
        elif isinstance(error, commands.errors.CommandNotFound):       return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
        elif isinstance(error, commands.errors.MissingPermissions):    return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
        elif isinstance(error, asyncio.TimeoutError):                  return print(f"{c.GreenDark}[ ] {c.Green}{str(error)}{c.c}")
        elif isinstance(error, commands.errors.NotOwner):              return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
        elif isinstance(error, commands.errors.TooManyArguments):      return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
        else:
            tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            tb = f"Command ran: {ctx.message.content}\nUser id:{ctx.author.id}\nGuild id:{ctx.guild.id}\n\n{tb}"
            return print(f"{c.RedDark}[C] {c.Red}Error Below\n\n{tb}{c.c}")
        
    @commands.Cog.listener()
    async def on_error(event, *args, **kwargs):
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        tb = f"Command ran: {ctx.message.content}\nUser id:{ctx.author.id}\nGuild id:{ctx.guild.id}\n\n{tb}"
        return print(f"{c.RedDark}[C] {c.Red}Error Below\n\n{tb}{c.c}")

    # @commands.command()
    # @commands.check(lambda message: message.author.id == 487443883127472129)
    # async def throwerr(self, ctx):
    #     a = {
    #         'lol': 'gg'
    #     }
    #     return a["asddsa(asdda)"]

def setup(bot):
    bot.add_cog(Errors(bot))