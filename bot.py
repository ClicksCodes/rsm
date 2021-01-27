import json

import discord
from discord.ext import commands

import config
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
        for cog in config.cogs:
            x += 1
            try:
                print(f"{C.Cyan}[S] {C.CyanDark}Loading cog {x}/{m} ({cog})", end="\r")
                self.load_extension(cog)
                print(f"{C.Green}[S] {C.GreenDark}Loaded cog {x}/{m} ({cog}).")
            except Exception as exc:
                print(f"{C.RedDark}[E] {C.Red}Failed cog {x}/{m} ({cog}) > {exc.__class__.__name__}: {exc}{C.c}")
        print()

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
                    prefixes = ("t!", "t1" if config.development else "m!", "m1")
        except (FileNotFoundError, AttributeError):
            prefixes = ("t!", "t1" if config.development else "m!", "m1")
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
        print(f"{C.Pink if config.development else C.Cyan}[S] {C.PinkDark if config.development else C.CyanDark}Logged on as {self.user} [ID: {self.user.id}]{C.c}")