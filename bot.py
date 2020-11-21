import sys
import traceback

from discord.ext import commands
import discord
import config

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

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('t!', 'T!', 't1', 'T1'), **kwargs)
        #super().__init__(command_prefix=commands.when_mentioned_or('m!', 'M!', 'm1', 'M1'), **kwargs)

        self.remove_command('help')

        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as exc:
                print(f'{c.RedDark}[E] {c.Red}Could not load extension {cog} due to {exc.__class__.__name__}: {exc}{c.c}')

    async def on_ready(self):
        print(f'{c.Cyan}[S] {c.CyanDark}Logged on as {self.user} (ID: {self.user.id}){c.c}')

bot = Bot(owner_ids=[438733159748599813, 421698654189912064, 261900651230003201, 317731855317336067, 421698654189912064], case_insensitive=True, presence=None)

bot.run(config.token)
