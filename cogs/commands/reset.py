import discord
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed
from cogs import interactions


class Reset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)
        self.interactions = interactions

    @commands.command()
    @commands.guild_only()
    async def reset(self, ctx):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_guild", self.emojis().punish.warn, "reset settings", me=False), Failed):
            return
        v = self.interactions.createUI(ctx, [
            self.interactions.Button(self.bot, emojis=self.emojis, id="ye", title="Yes", style="success"),
            self.interactions.Button(self.bot, emojis=self.emojis, id="no", title="No", style="danger"),
        ])
        await m.edit(embed=discord.Embed(
            title="Are you sure",
            description=f"By clicking Yes, all of your server settings will be reset. This cannot be reversed.",
            colour=self.colours.red
        ), view=v)
        await v.wait()
        if v.selected == "ye":
            self.handlers.fileManager(ctx.guild, action="RESET")
            return await m.edit(embed=discord.Embed(
                title="Reset",
                description=f"All settings reset successfully",
                colour=self.colours.green
            ), view=None)
        await m.edit(embed=discord.Embed(
            title="Reset",
            description=f"Cancelled",
            colour=self.colours.green
        ), view=None)


def setup(bot):
    bot.add_cog(Reset(bot))
