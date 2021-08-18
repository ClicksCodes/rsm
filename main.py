import discord
import datetime
from config import config
from cogs.consts import *
from global_vars import bot
# from api import server

bot.errors = 0
bot.allowed_mentions = discord.AllowedMentions(users=True, roles=True, replied_user=True, everyone=False)

bot.uptime = datetime.datetime.now()
bot.mem = {}
bot.version = "2.1.0-E:BETA1"

bot.run(config.token)
