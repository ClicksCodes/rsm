import asyncio
from hashlib import sha256

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

    async def _on_error(self, ctx, error):
        Colours = consts.Colours
        try:
            # Normal Green
            # Warning Yellow
            # Critical Red
            # Status Blue
            if ctx:
                try:
                    code = str(sha256(str.encode(str(ctx.message.id))).hexdigest())[20:]
                except Exception as e:
                    print(e)
                    code = ctx.message.id
            else:
                code = str(sha256(str.encode(random.randint(0, 10000000))).hexdigest())[20:]

            if isinstance(error, commands.errors.NoPrivateMessage):
                if not ctx.guild:
                    return await ctx.send(await self.dms.genResponse(ctx.message.content))
            elif isinstance(error, commands.errors.CommandOnCooldown):
                return await ctx.send(embed=discord.Embed(
                    title="You're on cooldown",
                    description="Please try again in a few seconds",
                    color=self.colors.red
                ))
            elif isinstance(error, commands.errors.BotMissingPermissions) or isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
                return print(f"{Colours.GreenDark}[N] {Colours.Green}{str(error)}{Colours.c}")
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
                tb = "\n".join([
                    f"{Colours.RedDark}[C] {Colours.Red}" + line for line in (
                        f"Command ran: {ctx.message.content if ctx else ''}\nUser id:{ctx.author.id if ctx else ''}\n"
                        f"Guild id:{(ctx.guild.id if ctx.guild else 'N/A') if ctx else ''}\n\n{tb}".split("\n")
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
                if int(self.bot.user.id) == 715989276382462053 and ctx:
                    return await ctx.channel.send(
                        embed=discord.Embed(
                            title=f"{self.emojis().control.cross} It looks like I messed up",
                            description=f"It looks like there was an error. Just send the [developers](https://discord.gg/bPaNnxe) code `{code}`",
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


def setup(bot):
    bot.add_cog(Errors(bot))
