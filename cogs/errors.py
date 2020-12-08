import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, postbin, os

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from hashlib import sha256
from cogs.consts import *

class c:
    c = '\033[0m'

    RedDark = '\033[31m'
    GreenDark = '\033[32m'
    YellowDark = '\033[33m'
    BlueDark = '\033[34m'
    PinkDark = '\033[35m'
    CyanDark = '\033[36m'

    Red = '\033[91m'
    Green = '\033[92m'
    Yellow = '\033[93m'
    Blue = '\033[94m'
    Pink = '\033[95m'
    Cyan = '\033[96m'

class Errors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            # Normal Green
            # Warning Yellow
            # Critical Red
            # Status Blue
            try: code = str(sha256(str.encode(str(ctx.message.id))).hexdigest())[10:]
            except: code=ctx.message.id

            if   isinstance(error, commands.errors.NoPrivateMessage):      return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
            elif isinstance(error, commands.errors.BotMissingPermissions): return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
            elif isinstance(error, commands.errors.CommandNotFound):       return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
            elif isinstance(error, asyncio.TimeoutError):                  return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
            elif isinstance(error, commands.errors.NotOwner):              return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
            elif isinstance(error, commands.errors.TooManyArguments):      return print(f"{c.GreenDark}[N] {c.Green}{str(error)}{c.c}")
            elif isinstance(error, commands.errors.MissingPermissions):    
                return await ctx.send(embed=discord.Embed(
                    title=f"{emojis['cross']} Missing permissions",
                    description=str(error),
                    color=colours["delete"]
                ))
            else:
                try: 
                    with open(f"data/guilds/{ctx.guild.id}.json") as f: pass
                except FileNotFoundError:
                    return await ctx.channel.send(embed=discord.Embed(
                        title="You aren't set up",
                        description=f"You need to run `m!setup` to get your server set up.",
                        color=colours["delete"]
                    ))
                tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
                if "clear_reactions()" in tb: return
                tb = "\n".join([f"{c.RedDark}[C] {c.Red}" + line for line in (f"Command ran: {ctx.message.content}\nUser id:{ctx.author.id}\nGuild id:{ctx.guild.id}\n\n{tb}".split("\n"))])
                url = await postbin.postAsync(tb)
                print(f"{c.RedDark}[C] {c.Red}FATAL:\n{tb}{c.c}\n{code}")
                if self.bot.user.id == 715989276382462053:
                    await self.bot.get_channel(776418051003777034).send(embed=discord.Embed(
                        title="Error",
                        description=f"`{code}`: " + url,
                        color=colours["delete"]
                    ))
                    return await ctx.channel.send(embed=discord.Embed(
                        title="It looks like I messed up",
                        description=f"It looks like there was an error. Just send the [developers](https://discord.gg/bPaNnxe) code `{code}`",
                        color=colours["delete"]
                    ))
                else: return
        except: pass #print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
        
    @commands.Cog.listener()
    async def on_error(event, *args, **kwargs):
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        tb = f"Command ran: {ctx.message.content}\nUser id:{ctx.author.id}\nGuild id:{ctx.guild.id}\n\n{tb}"
        return print(f"{c.RedDark}[C] {c.Red}Error Below\n{tb}{c.c}")

def setup(bot):
    bot.add_cog(Errors(bot))