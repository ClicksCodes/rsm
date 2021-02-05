import discord
from config import config
from cogs.consts import C
import bot
#from api import server


print(f"{C.Cyan.value}[S] {C.CyanDark.value}Launching {config.stage.name} mode")

bot = bot.Bot(
    owner_ids=[
        438733159748599813,
        421698654189912064,
        261900651230003201,
        317731855317336067,
    ],
    case_insensitive=True,
    presence=None,
    intents=discord.Intents.all(),
)
bot.errors = 0
bot.runningPing = False

#server.start(bot.loop)

bot.run(config.token)
