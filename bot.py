import json
import discord
import os

from discord.ext import commands

from config import config
from cogs.consts import C


class Context(commands.Context):
    @property
    def prefix(self):
        try:
            return self.bot.sync_get_prefix(self)[2]
        except Exception as e:
            print(f"{C.RedDark}[C] {C.Red}FATAL:\n{C.c}\n{e}, please message Minion3665")
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
        _, th = os.popen('stty size', 'r').read().split()
        width = int(th)
        failed = []
        for cog in config.cogs:
            x += 1
            try:
                start = f"{C.YellowDark.value}[S] {C.Yellow.value}Loading cog {cog}"
                end = f"{C.Yellow.value}[{C.Red.value}{'='*(len(failed))}{C.Green.value}{'='*(x-len(failed))}>{' '*(m-x)}{C.Yellow.value}] [{' '*(len(str(m))-len(str(x)))}{x}/{m}]"
                print(f"{start}{' '*(width-len(start)-len(end)+(len(C.Yellow.value*4)))}{end}", end="\r")
                self.load_extension(cog)
                start = f"{C.GreenDark.value}[S] {C.Green.value}Loaded cog {cog}"
                end = f"[{' '*(len(str(m))-len(str(x)))}{x}/{m}]"
                print(f"{start}{' '*(width-len(start)-len(end))}{end}")
            except Exception as exc:
                failed.append(exc)
                start = f"{C.RedDark.value}[S] {C.Red.value}Failed to load cog {cog}"
                end = f"[{' '*(len(str(m))-len(str(x)))}{x}/{m}]"
                print(f"{start}{' '*(width-len(start)-len(end))}{end}")
        x = 0
        for error in failed:
            x += 1
            print(f"{C.RedDark.value}[{x}/{len(failed)}] {C.Red.value}{error.__class__.__name__}: {C.RedDark.value}{error}{C.c.value}")
        lc = (len(failed), m)
        print(f"{C[config.colour].value}[S] {C[str(config.colour) + 'Dark'].value}Starting with ({lc[1]-lc[0]}/{lc[1]}) cogs loaded")

    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)

    async def get_prefix(self, ctx):
        return self.sync_get_prefix(ctx)

    def sync_get_prefix(self, ctx):
        try:
            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
                if "prefix" in entry and entry["prefix"]:
                    prefixes = (entry["prefix"],)
                else:
                    prefixes = config.prefixes.copy()
        except (FileNotFoundError, AttributeError):
            prefixes = config.prefixes.copy()
        if not ctx.guild:
            prefixes += ("",)
        return commands.when_mentioned_or(*prefixes)(self, ctx)

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="over your servers."
            ),
            status=discord.Status.idle,
        )
        print(f"{C[config.colour].value}[S] {C[str(config.colour) + 'Dark'].value}Logged on as {self.user} [ID: {self.user.id}]{C.c.value}")
