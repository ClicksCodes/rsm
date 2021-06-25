import typing
from discord.ext import commands, tasks

from cogs.consts import *
from cogs.handlers import Handlers


class Loops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)
        self.bot.expectedPresence = ("", False)

        self.checkPing.start()

    def cog_unload(self):
        self.checkPing.cancel()

    async def setStatus(self, status):
        if status != self.bot.expectedPresence:
            if status == "online":
                await self.bot.change_presence(
                    status=discord.Status.online,
                    activity=discord.Activity(type=discord.ActivityType.watching, name="All systems operational")
                )
                self.bot.expectedPresence = (status, False)
            elif status == "idle":
                await self.bot.change_presence(
                    status=discord.Status.idle,
                    activity=discord.Activity(type=discord.ActivityType.watching, name="High latency")
                )
                self.bot.expectedPresence = (status, False)
            elif status == "dnd":
                await self.bot.change_presence(
                    status=discord.Status.dnd,
                    activity=discord.Activity(type=discord.ActivityType.playing, name="Something went wrong | Contacting developers")
                )
            elif status == "invisible":
                await self.bot.change_presence(
                    status=discord.Status.invisible
                )
                self.bot.expectedPresence = (status, False)

    @tasks.loop(seconds=1)
    async def checkPing(self):
        if self.bot.expectedPresence[1]:
            return await self.setStatus(self.bot.expectedPresence[0])
        latency = self.bot.latency
        if not latency:
            await self.setStatus("idle")
        elif latency * 1000 > 250:
            await self.setStatus("idle")
        elif latency * 1000 <= 250:
            await self.setStatus("online")

    @commands.command()
    @commands.is_owner()
    async def dnd(self, ctx, toggle: typing.Optional[str]):
        if toggle:
            self.bot.expectedPresence = ("online", False)
        else:
            self.bot.expectedPresence = ("dnd", True)

    @commands.command()
    @commands.is_owner()
    async def mem(self, ctx):
        await ctx.send(str(self.bot.mem)[:2000])


def setup(bot):
    bot.add_cog(Loops(bot))
