import discord
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed
import io


class Emergency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.command()
    @commands.guild_only()
    async def lock(self, ctx):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_messages", self.emojis().commands.lock, "lock a channel"), Failed):
            return
        if self.handlers.is_channel_locked(ctx.channel):
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().commands.lock} Lock",
                description=f"This channel is already locked. You can `{ctx.prefix}unlock` to unlock it",
                colour=self.colours.red
            ))
        self.handlers.lock_channel(ctx.channel, True, str(ctx.channel.slowmode_delay))
        await ctx.channel.edit(slowmode_delay=21600)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().commands.lock} Lock",
            description=f"This channel has been locked. Use `{ctx.prefix}unlock` to unlock it",
            colour=self.colours.red
        ))

    @commands.command()
    @commands.guild_only()
    async def unlock(self, ctx):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_messages", self.emojis().commands.lock, "unlock a channel"), Failed):
            return
        if not self.handlers.is_channel_locked(ctx.channel):
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().commands.lock} Unlock",
                description=f"This channel is not locked. You can `{ctx.prefix}lock` to lock it",
                colour=self.colours.red
            ))
        time = self.handlers.lock_channel(ctx.channel, False)
        await ctx.channel.edit(slowmode_delay=int(time))
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().commands.lock} Unlock",
            description=f"This channel has been unlocked. Use `{ctx.prefix}lock` to lock it again",
            colour=self.colours.red
        ))


def setup(bot):
    bot.add_cog(Emergency(bot))
