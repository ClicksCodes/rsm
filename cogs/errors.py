import asyncio
import random
from typing import final

from discord.errors import Forbidden
from discord.ext.commands.errors import CommandInvokeError

import bot as customBot
import discord
from discord.ext import commands
import traceback

from cogs import consts
from cogs.dmCommands import DMs


class Errors(commands.Cog):
    def __init__(self, bot: customBot.Bot):
        self.bot = bot
        self.emojis = consts.Emojis
        self.dms = DMs()
        self.colours = consts.Cols()

    async def send_error(self, ctx, message):
        try:
            return await ctx.author.send(embed=discord.Embed(
                title=f"{self.emojis().control.cross} I don't have permission",
                description=message,
                colour=self.colours.red,
            ))
        except discord.Forbidden:
            pass
        try:
            return await ctx.message.add_reaction(self.emojis().control.cross)
        except discord.Forbidden:
            pass
        try:
            return await ctx.message.add_reaction("❌")
        except discord.Forbidden:
            pass

    async def _on_error(self, ctx, error):
        Colours = consts.Colours
        try:
            # Normal Green
            # Warning Yellow
            # Critical Red
            # Status Blue
            if not ctx.channel.permissions_for(ctx.me).send_messages:
                return await self.send_error(ctx, "I tried to send a message, but I didn't have permission to send it. Make sure I have `send_messages`")
            elif not ctx.channel.permissions_for(ctx.me).embed_links:
                if ctx.channel.permissions_for(ctx.me).read_message_history:
                    return await ctx.reply("I don't have permission to send an embed. Make sure I have `embed_links`")
                return await ctx.send("I don't have permission to send an embed. Make sure I have `embed_links` and `read_message_history`")
            elif not ctx.channel.permissions_for(ctx.me).external_emojis:
                return await ctx.send(ctx, "I tried to use a nitro emoji, but didn't have permission. Make sure I have `use_external_emojis`")
            elif not ctx.channel.permissions_for(ctx.me).add_reactions:
                return await ctx.send(ctx, "I tried to add a reaction, but didn't have permission. Make sure I have `add_reactions`")

            if isinstance(error, commands.errors.NoPrivateMessage):
                if not ctx.guild:
                    return await ctx.send(await self.dms.genResponse(ctx.message.content))
            elif isinstance(error, commands.errors.CommandOnCooldown):
                return await ctx.send(embed=discord.Embed(
                    title="You're on cooldown",
                    description="Please try again in a few seconds",
                    color=self.colours.red
                ))
            elif isinstance(error, commands.errors.BotMissingPermissions) or isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
                return await ctx.send(
                    embed=discord.Embed(
                        title=f"{self.emojis().control.cross} Missing permissions",
                        description=str(error),
                        colour=self.colours.red,
                    )
                )
            elif isinstance(error, commands.errors.CommandNotFound):
                if not ctx.guild:
                    return await ctx.send(
                        (await self.dms.genResponse(ctx.message.content))
                        .replace("{mention}", ctx.author.mention)
                    )
            elif isinstance(error, asyncio.TimeoutError):
                return print(f"{Colours.GreenDark}[N] {Colours.Green}{str(error)}{Colours.c}")
            elif isinstance(error, commands.errors.NotOwner):
                return print(f"{Colours.GreenDark}[N] {Colours.Green}{str(error)}{Colours.c}")
            elif isinstance(error, commands.errors.TooManyArguments):
                return print(f"{Colours.GreenDark}[N] {Colours.Green}{str(error)}{Colours.c}")
            elif isinstance(error, commands.errors.MissingPermissions) and ctx:
                return await ctx.send(
                    embed=discord.Embed(
                        title=f"{self.emojis().control.cross} Missing permissions",
                        description=str(error),
                        colour=self.colours.red,
                    )
                )
            else:
                self.bot.errors += 1
                tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
                tb2 = "\n".join([
                    f"{Colours.RedDark}[C] {Colours.Red}" + line for line in (
                        f"Command ran: {ctx.message.content if ctx else ''}\nUser id:{ctx.author.id if ctx else ''}\n"
                        f"Guild id:{(ctx.guild.id if ctx.guild else 'N/A') if ctx else ''}\n\n{tb}".split("\n")
                    )
                ])
                with open("./words.txt") as f:
                    words = f.read().split("\n")
                code = "-".join([random.choice(words) for _ in range(3)])
                s = f"`{code}`: ```\n```"
                cut = 1900 - len(s)
                print(f"{Colours.RedDark}[C] {Colours.Red}FATAL:\n{tb2}{Colours.c}")
                await self.bot.get_channel(776418051003777034).send(
                    embed=discord.Embed(
                        title="Error",
                        description=f"`{code}`: ```\n" + tb[:cut] + "```",
                        colour=self.colours.red,
                    )
                )
                if ctx:
                    await ctx.channel.send(
                        embed=discord.Embed(
                            title=f"{self.emojis().control.cross} It looks like I messed up",
                            description=f"It looks like there was an error. Just send the [developers](https://discord.gg/bPaNnxe) code `{code}`",
                            colour=self.colours.red,
                        )
                    )
                    return await self.bot.get_user(438733159748599813).send(
                        embed=discord.Embed(
                            title=f"{self.emojis().control.cross} It looks wike you did a fucky wucky >w<",
                            description=f"You did a shit job programming and someone just got the error code `{code}` you fucking"
                                        f" donkey\n\n`Line 1 Brain.py: raise IncompetenceError`",
                            colour=self.colours.red,
                        )
                    )
                else:
                    return
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_error(self, error):
        await self._on_error(_, error)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await self._on_error(ctx, error)

    #  pyright: reportUndefinedVariable=false
    @commands.command()
    @commands.is_owner()
    async def error(self, ctx):
        return f"{myhopesanddreams}"

    @commands.command()
    @commands.is_owner()
    async def raiseerror(self, ctx):
        raise ModuleNotFoundError("My hopes and dreams")


def setup(bot):
    bot.add_cog(Errors(bot))
