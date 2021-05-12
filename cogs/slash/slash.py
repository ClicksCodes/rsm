from discord.ext import commands
import discord
import aiohttp
import asyncio
from config import config
from cogs.slash import interp
from cogs.consts import *


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_interaction_create(self, data):
        command = interp.Command(data, bot=self.bot)
        await command.run(interp.fetchFunction(command.guild_id, command.name))

def setup(bot):
    bot.add_cog(Slash(bot))
