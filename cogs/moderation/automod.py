import discord
import re
import asyncio
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers


class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content:
            d = 0
            for c in message.content:
                if c.isupper():
                    d += 1
            if d / len(message.content) > 0.7:
                return await message.delete()


def setup(bot):
    bot.add_cog(Automod(bot))
