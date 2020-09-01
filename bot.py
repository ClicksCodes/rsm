#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import traceback

from discord.ext import commands
import discord
import config

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('m!'), **kwargs)
        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as exc:
                print('Could not load extension {0} due to {1.__class__.__name__}: {1}'.format(cog, exc))

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))

    async def on_error(self, event_method, *args, **kwargs):
        fmt = traceback.format_exc()
        if "AttributeError: 'NoneType' object has no attribute 'send'" in fmt:
            return  # ignore
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()


bot = Bot(owner_ids=[438733159748599813, 421698654189912064, 261900651230003201, 317731855317336067], case_insensitive=True)

# write general commands here

bot.run(config.token)
