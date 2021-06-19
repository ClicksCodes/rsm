import aiohttp
import discord
import datetime
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild:
            if message.channel.slowmode_delay:
                if self.handlers.is_channel_locked(message.channel) and not message.author.permissions_in(message.channel).manage_messages:
                    await message.delete()


def setup(bot):
    bot.add_cog(Listeners(bot))
