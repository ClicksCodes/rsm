import asyncio
from hashlib import sha256

import bot as customBot
import discord
from discord.ext import commands
import traceback

from cogs.consts import *
from cogs.dmCommands import DMs


class Errors(commands.Cog):
    def __init__(self, bot: customBot.Bot):
        self.bot = bot
        self.dms = DMs()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            # Normal Green
            # Warning Yellow
            # Critical Red
            # Status Blue
            try:
                code = str(sha256(str.encode(str(ctx.message.id))).hexdigest())[20:]
            except Exception as e:
                print(e)
                code = ctx.message.id

            if isinstance(error, commands.errors.NoPrivateMessage):
                return print(f"{Colours.GreenDark}[N] {Colours.Green}{str(error)}{Colours.c}")
            elif isinstance(error, commands.errors.BotMissingPermissions):
                return print(f"{Colours.GreenDark}[N] {Colours.Green}{str(error)}{Colours.c}")
            elif isinstance(error, commands.errors.CommandNotFound):
                if not ctx.guild:
                    await ctx.send(await self.dms.genResponse(ctx.message.content))
            elif isinstance(error, asyncio.TimeoutError):
                return print(f"{Colours.GreenDark}[N] {Colours.Green}{str(error)}{Colours.c}")
            elif isinstance(error, commands.errors.NotOwner):
                return print(f"{Colours.GreenDark}[N] {Colours.Green}{str(error)}{Colours.c}")
            elif isinstance(error, commands.errors.TooManyArguments):
                return print(f"{Colours.GreenDark}[N] {Colours.Green}{str(error)}{Colours.c}")
            elif isinstance(error, commands.errors.MissingPermissions):
                return await ctx.send(
                    embed=discord.Embed(
                        title=f"{emojis['cross']} Missing permissions",
                        description=str(error),
                        colour=Colours.red,
                    )
                )
            else:
                self.bot.errors += 1
                tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
                tb = "\n".join([
                    f"{Colours.RedDark}[C] {Colours.Red}" + line for line in (
                        f"Command ran: {ctx.message.content}\nUser id:{ctx.author.id}\nGuild id:{ctx.guild.id if ctx.guild else 'N/A'}\n\n{tb}".split("\n")
                    )
                ])
                print(f"{Colours.RedDark}[C] {Colours.Red}FATAL:\n{tb}{Colours.c}\n{code}")
                # url = await postbin.postAsync(tb)
                #     await self.bot.get_channel(776418051003777034).send(
                #         embed=discord.Embed(
                #             title="Error",
                #             description=f"`{code}`: " + url,
                #             colour=colours["delete"],
                #         )
                #     )
                if int(self.bot.user.id) == 715989276382462053:
                    return await ctx.channel.send(
                        embed=discord.Embed(
                            title="It looks like I messed up",
                            description=f"It looks like there was an error. Just send the [developers](https://discord.gg/bPaNnxe) code `{code}`",
                            colour=colours["delete"],
                        )
                    )
                else:
                    return
        except Exception as e:
            print(e)

    #  pyright: reportUndefinedVariable=false
    @commands.command()
    @commands.is_owner()
    async def error(self, ctx):
        return f"{myhopesanddreams}"


def setup(bot):
    bot.add_cog(Errors(bot))
