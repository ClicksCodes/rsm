DEV = 0
import discord 

import sys
import traceback

from discord.ext import commands
import discord
import config
import json

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

intents = discord.Intents.all()

print(f"{c.Cyan}[S] {c.CyanDark}Launching {'dev' if DEV else 'normal'} mode")

class Bot(commands.Bot):
    def __init__(self, **kwargs):

        super().__init__(command_prefix=self.get_prefix, help_command=None, **kwargs)

        x = 0
        m = len(config.cogs)
        for cog in config.cogs:
            x += 1
            try:
                print(f"{c.Cyan}[S] {c.CyanDark}Loading cog {x}/{m} ({cog})", end="\r")
                self.load_extension(cog)
                print(f"{c.Green}[S] {c.GreenDark}Loaded cog {x}/{m} ({cog}).")
            except Exception as exc:
                print(f'{c.RedDark}[E] {c.Red}Failed cog {x}/{m} ({cog}) > {exc.__class__.__name__}: {exc}{c.c}')
        print()

    async def get_prefix(self, ctx):
        try:
            with open(f"data/guilds/{ctx.guild.id}.json", 'r') as entry:
                entry = json.load(entry)
                if "prefix" in entry and entry["prefix"]:
                    prefixes = (entry["prefix"],)
                else:
                    prefixes = ('t!', 't1' if DEV else 'm!', 'm1')
        except (FileNotFoundError, AttributeError):
            prefixes = ('t!', 't1' if DEV else 'm!', 'm1')
        if not ctx.guild:
            prefixes += ("",)
        return commands.when_mentioned_or(*prefixes)(self, ctx)

    @property
    def prefix(self):
        try:
            return self.get_prefix(ctx)[2]
        except Exception as e:
            print(f"{c.RedDark}[C] {c.Red}FATAL:\n{c.c}\n{e}, please message Minion3665")
            return "@RSM "  # This should **never** trigger

    async def on_ready(self):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="over your servers."), status=discord.Status.idle)
        print(f'{c.Pink if DEV else c.Cyan}[S] {c.PinkDark if DEV else c.CyanDark}Logged on as {self.user} [ID: {self.user.id}]{c.c}')

bot = Bot(
    owner_ids=[438733159748599813, 421698654189912064, 261900651230003201, 317731855317336067], 
    case_insensitive=True, 
    presence=None,
    intents=intents
)

bot.run(config.token if not DEV else config.dtoken)
