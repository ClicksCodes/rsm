import discord
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed


class Reset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.command()
    @commands.guild_only()
    async def reset(self, ctx):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_guild", self.emojis().punish.warn, "reset settings", me=False), Failed):
            return
        await m.edit(embed=discord.Embed(
            title="Are you sure",
            description=f"By clicking {self.emojis().control.tick}, all of your server settings will be reset. This cannot be reversed.",
            colour=self.colours.red
        ))
        emoji = await self.handlers.reactionCollector(ctx, m, ["control.cross", "control.tick"])
        await m.clear_reactions()
        if isinstance(emoji, Failed):
            await m.edit(embed=discord.Embed(
                title="Reset",
                description=f"Cancelled",
                colour=self.colours.green
            ))
        if emoji.emoji.name == "Tick":
            self.handlers.fileManager(ctx.guild, action="RESET")
            return await m.edit(embed=discord.Embed(
                title="Reset",
                description=f"All settings reset successfully",
                colour=self.colours.green
            ))
        await m.edit(embed=discord.Embed(
            title="Reset",
            description=f"Cancelled",
            colour=self.colours.green
        ))


def setup(bot):
    bot.add_cog(Reset(bot))
