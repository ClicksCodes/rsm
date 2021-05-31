import discord
import json
import re
import datetime
import asyncio

from discord.ext import commands

from cogs.consts import *


class RPicker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loadingEmbed = loadingEmbed

    @commands.command(aliases=["rmenu"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def rolemenu(self, ctx):
        pass


def setup(bot):
    bot.add_cog(RPicker(bot))
