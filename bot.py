import json
import discord
import os

from discord.ext import commands

from config import config
from cogs.consts import Colours


class Context(commands.Context):
    @property
    def prefix(self):
        try:
            return self.bot.sync_get_prefix(self)[2]
        except Exception as e:
            print(f"{Colours.RedDark}[C] {Colours.Red}FATAL:\n{Colours.c}\n{e}, please message Minion3665")
            return "@RSM "  # This should **never** trigger

    @prefix.setter
    def prefix(self, _):
        pass


class Bot(commands.Bot):
    def __init__(self, **kwargs):

        super().__init__(command_prefix=self.get_prefix, help_command=None, **kwargs)

        self.errors = 0
        x = 0
        m = len(config.cogs)
        try:
            _, th = os.popen('stty size', 'r').read().split()
            width = int(th)
        except ValueError:
            width = 50
        failed = []
        for cog in config.cogs:
            x += 1
            try:
                start = f"{Colours.YellowDark}[S] {Colours.Yellow}Loading cog {cog}"
                end = f"{Colours.Yellow}[{Colours.Red}{'='*(len(failed))}{Colours.Green}{'='*(x-len(failed)-1)}>{' '*(m-x)}{Colours.Yellow}] " + \
                    f"[{' '*(len(str(m))-len(str(x)))}{x}/{m}]"
                print(f"{start}{' '*(width-len(start)-len(end)+(len(Colours.Yellow*4)))}{end}", end="\r")
                self.load_extension(cog)
                start = f"{Colours.GreenDark}[S] {Colours.Green}Loaded cog {cog}"
                end = f"[{' '*(len(str(m))-len(str(x)))}{x}/{m}]"
                print(f"{start}{' '*(width-len(start)-len(end))}{end}")
            except Exception as exc:
                failed.append(exc)
                start = f"{Colours.RedDark}[S] {Colours.Red}Failed to load cog {cog}"
                end = f"[{' '*(len(str(m))-len(str(x)))}{x}/{m}]"
                print(f"{start}{' '*(width-len(start)-len(end))}{end}")
        x = 0
        for error in failed:
            x += 1
            print(f"{Colours.RedDark}[{x}/{len(failed)}] {Colours.Red}{error.__class__.__name__}: {Colours.RedDark}{error}{Colours.c}")
        lc = (len(failed), m)
        print(f"{getattr(Colours, config.colour)}[S] {getattr(Colours, str(config.colour) + 'Dark')}Starting with ({lc[1]-lc[0]}/{lc[1]}) cogs loaded")

    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)

    async def get_prefix(self, ctx):
        return self.sync_get_prefix(ctx)

    def sync_get_prefix(self, ctx):
        try:
            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
                if "prefix" in entry and entry["prefix"]:
                    if isinstance(entry["prefix"], str):
                        prefixes = (entry["prefix"],)
                    elif isinstance(entry["prefix"], list):
                        prefixes = entry["prefix"]
                else:
                    prefixes = config.prefixes.copy()
        except (FileNotFoundError, AttributeError):
            prefixes = config.prefixes.copy()
        if not ctx.guild:
            prefixes += ("",)
        return commands.when_mentioned_or(*prefixes)(self, ctx)

    async def on_ready(self):
        print(f"{getattr(Colours, config.colour)}[S] {getattr(Colours, str(config.colour) + 'Dark')}Logged on as {self.user} [ID: {self.user.id}]{Colours.c}")
