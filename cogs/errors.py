import asyncio
import postbin
import sys
from hashlib import sha256

from cogs.consts import *
import bot as customBot


class Errors(commands.Cog):
    def __init__(self, bot: customBot.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            # Normal Green
            # Warning Yellow
            # Critical Red
            # Status Blue
            try:
                code = str(sha256(str.encode(str(ctx.message.id))).hexdigest())[20:]
            except:
                code = ctx.message.id

            if isinstance(error, commands.errors.NoPrivateMessage):
                return print(f"{C.GreenDark}[N] {C.Green}{str(error)}{C.c}")
            elif isinstance(error, commands.errors.BotMissingPermissions):
                return print(f"{C.GreenDark}[N] {C.Green}{str(error)}{C.c}")
            elif isinstance(error, commands.errors.CommandNotFound):
                return print(f"{C.GreenDark}[N] {C.Green}{str(error)}{C.c}")
            elif isinstance(error, asyncio.TimeoutError):
                return print(f"{C.GreenDark}[N] {C.Green}{str(error)}{C.c}")
            elif isinstance(error, commands.errors.NotOwner):
                return print(f"{C.GreenDark}[N] {C.Green}{str(error)}{C.c}")
            elif isinstance(error, commands.errors.TooManyArguments):
                return print(f"{C.GreenDark}[N] {C.Green}{str(error)}{C.c}")
            elif isinstance(error, commands.errors.MissingPermissions):
                return await ctx.send(
                    embed=discord.Embed(
                        title=f"{emojis['cross']} Missing permissions",
                        description=str(error),
                        color=colours["delete"],
                    )
                )
            else:
                self.bot.errors += 1
                try:
                    with open(f"data/guilds/{ctx.guild.id}.json") as f:
                        pass
                except FileNotFoundError:
                    return await ctx.channel.send(
                        embed=discord.Embed(
                            title="You aren't set up",
                            description=f"You need to run `{ctx.prefix}setup` to get your server set up.",
                            color=colours["delete"],
                        )
                    )
                tb = "".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                )
                if "clear_reactions()" in tb:
                    return
                tb = "\n".join(
                    [
                        f"{C.RedDark}[C] {C.Red}" + line
                        for line in (
                            f"Command ran: {ctx.message.content}\nUser id:{ctx.author.id}\nGuild id:{ctx.guild.id if ctx.guild else 'N/A'}\n\n{tb}".split(
                                "\n"
                            )
                        )
                    ]
                )
                url = await postbin.postAsync(tb)
                print(f"{C.RedDark}[C] {C.Red}FATAL:\n{tb}{C.c}\n{code}")
                if self.bot.user.id == 715989276382462053:
                    await self.bot.get_channel(776418051003777034).send(
                        embed=discord.Embed(
                            title="Error",
                            description=f"`{code}`: " + url,
                            color=colours["delete"],
                        )
                    )
                    return await ctx.channel.send(
                        embed=discord.Embed(
                            title="It looks like I messed up",
                            description=f"It looks like there was an error. Just send the [developers](https://discord.gg/bPaNnxe) code `{code}`",
                            color=colours["delete"],
                        )
                    )
                else:
                    return
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        exc_type, exc, tb_type = sys.exc_info()
        tb = "".join(traceback.format_exception(exc_type, exc, tb_type))
        tb = f"Event ran: {event}\nArgs:{', '.join(args)}\n\n{tb}"
        return print(f"{C.RedDark}[C] {C.Red}Error Below\n{tb}{C.c}")

    # noinspection PyUnresolvedReferences
    @commands.command()
    @commands.is_owner()
    async def error(self, ctx):
        return f"{notexistslol}"


def setup(bot):
    bot.add_cog(Errors(bot))
