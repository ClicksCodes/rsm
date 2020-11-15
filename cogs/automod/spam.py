import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus

from cogs.consts import *


class CooldownByContent(commands.CooldownMapping):
    def _bucket_key(self, message):
        return (message.channel.id, message.content)

class SpamChecker:
    """This spam checker does a few things.
    1) It checks if a user has spammed more than 10 times in 12 seconds
    2) It checks if the content has been spammed 15 times in 17 seconds.
    3) It checks if new users have spammed 30 times in 35 seconds.
    4) It checks if "fast joiners" have spammed 10 times in 12 seconds.
    The second case is meant to catch alternating spam bots while the first one
    just catches regular singular spam bots.
    From experience these values aren't reached unless someone is actively spamming.
    """
    def __init__(self):
        self.by_content = CooldownByContent.from_cooldown(15, 17.0, commands.BucketType.member)
        self.by_user = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)
        self.last_join = None
        self.new_user = commands.CooldownMapping.from_cooldown(30, 35.0, commands.BucketType.channel)

        # user_id flag mapping (for about 30 minutes)
        self.fast_joiners = cache.ExpiringCache(seconds=1800.0)
        self.hit_and_run = commands.CooldownMapping.from_cooldown(10, 12, commands.BucketType.channel)

    def is_new(self, member):
        now = datetime.datetime.utcnow()
        seven_days_ago = now - datetime.timedelta(days=7)
        ninety_days_ago = now - datetime.timedelta(days=90)
        return member.created_at > ninety_days_ago and member.joined_at > seven_days_ago

    def is_spamming(self, message):
        if message.guild is None:
            return False

class Spam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Spam(bot))