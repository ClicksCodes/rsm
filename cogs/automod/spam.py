import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus

from cogs.consts import *

class Spam(commands.Cog):
    pass

def setup(bot):
    bot.add_cog(Spam(bot))