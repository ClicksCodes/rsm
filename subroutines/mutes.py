import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, os

from datetime import datetime
from discord.ext import commands
from textwrap import shorten

from cogs.consts import *
ariadne

async def mute(ctx, user, duration=None):
    """As soon as you mute someone
    1 -- You store information about the mute: what was the state before? when will the mute expire? when was it created? by who? for who? what's the reason?; You add the mute to the unmute list
    2 -- You mute the user by changing user-specific channel permissions. You do not change permission on channels that have a :white_check_mark: as a user-specific send-messages permission for that user, as those are normally only used on modmail threads and other channels that the user needs access to
    3 -- You send a DM telling the user they were muted
    --- end of part ---

    Meanwhile, every minute
    1 -- You go over all the mutes in the unmute list
    --- for any people that will be unmuted in the next 5 minutes ---
    2 -- You remove them from the unmute list
    3 -- You create a task to unmute them. Note: the task must not be awaited by this thread or it will block it
    please remember to try-except steps 2 and 3. If 3 fails (and it shouldn't), step 2 must be reverted
    --- end of part ---

    In the unmute tasks
    1 -- You asyncio.sleep until the person needs to be unmuted
    2 -- You revert to the stored state. Do not change permissions that have been changed by a user (for example ones that are not :x:, or ones that are :x: but were originally :white_check_mark:)
    3 -- You edit the data to reflect that they have been unmuted
    4 -- You send a DM telling the user they were unmuted
    --- end of part ---

    When the bot restarts. Note: Not in on_ready as that can be run multiple times. At the start before the bot even loads
    1 -- You recreate the unmute list from stored data
    """
    