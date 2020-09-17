import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus
from create_machine_utils.minidiscord import menus

from cogs.consts import *

class Owners(commands.Cog):
    @commands.command()
    async def maintenance(self, ctx, b: typing.Optional[bool]):
        if ctx.author.id in ctx.bot.owner_ids:
            await ctx.bot.change_presence(    
                activity=discord.Activity(
                    name=" maintenance mode.",
                    type=discord.ActivityType.playing
                ),
                status=discord.Status.dnd
            )

def setup(bot):
    bot.add_cog(Owners(bot))