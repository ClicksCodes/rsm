import discord
import datetime
from config import config
from cogs.consts import *
import bot
# from api import server


print(f"{Colours.Cyan}[S] {Colours.CyanDark}Launching {config.stage.name} mode")

bot = bot.Bot(
    owner_ids=[
        438733159748599813,  # Pineapplefan
        421698654189912064,  # Eek
        261900651230003201,  # Coded
        317731855317336067,  # Minion
    ],
    case_insensitive=True,
    presence=None,
    intents=discord.Intents.all(),
)
bot.errors = 0
bot.allowed_mentions = discord.AllowedMentions(users=True, roles=True, replied_user=True, everyone=False)

bot.uptime = datetime.datetime.now()
bot.run(config.token)
