DEV = 1

import discord
import config
from cogs.consts import C
import bot

intents = discord.Intents.all()

print(f"{C.Cyan}[S] {C.CyanDark}Launching {'dev' if DEV else 'normal'} mode")


bot = bot.Bot(
    owner_ids=[
        438733159748599813,
        421698654189912064,
        261900651230003201,
        317731855317336067,
    ],
    case_insensitive=True,
    presence=None,
    intents=intents,
)
bot.errors = 0

bot.run(config.token if not DEV else config.dtoken)
