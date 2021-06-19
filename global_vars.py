import discord
from bot import Bot


bot = Bot(
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
