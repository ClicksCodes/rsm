import copy
import discord
import json
import humanize
import aiohttp
import traceback
import typing
import time
import asyncio
import os

from datetime import datetime
from discord.ext import commands
from textwrap import shorten

from cogs.consts import *


class InfoCommands(commands.Cog):
    def __init__(self, bot):
        self.loadingEmbed = loadingEmbed
        self.bot = bot

    def createEmbed(self, title, description, color=0x000000):
        return discord.Embed(
            title=title,
            description=description,
            color=color
        )

    @commands.command()
    async def ping(self, ctx):
        m = await ctx.send(embed=self.loadingEmbed)
        time = m.created_at - ctx.message.created_at
        await m.edit(content=None, embed=self.createEmbed(f"<:SlowmodeOn:777138171301068831> Ping", f"Latency is: `{int(time.microseconds / 1000)}ms`", colours['create']))

    @commands.command()
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def suggest(self, ctx, *, msg: typing.Optional[str]):
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
        if not msg:
            return await ctx.send(embed=discord.Embed(
                title=f"{emojis['cross']} No suggestion",
                description=f"Please enter a suggestion after `{ctx.prefix}suggest`.",
                color=colours["delete"]
            ), delete_after=10)
        r = await self.bot.get_channel(777214577187487744).send(embed=discord.Embed(
            title="Suggestion",
            description=f"Ticket: `{ctx.author.id}`\nName: `{ctx.author.name}`\n\n" + str(msg),
            color=colours["create"]
        ))
        await r.add_reaction(self.bot.get_emoji(729064531107774534))
        await r.add_reaction(self.bot.get_emoji(729064530310594601))
        await ctx.send(embed=discord.Embed(
            title=f"{emojis['tick']} Success",
            description="Your suggestion was sent to the dev team.",
            color=colours["create"]
        ), delete_after=10)

    @commands.command(aliases=["support"])
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def contact(self, ctx, *, msg: typing.Optional[str]):
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
        if not msg:
            return await ctx.send(embed=discord.Embed(
                title=f"{emojis['cross']} No message",
                description=f"Please enter a message after `{ctx.prefix}contact`.",
                color=colours["delete"]
            ), delete_after=10)
        await self.bot.get_channel(777220967315406929).send(embed=discord.Embed(
            title="Support",
            description=f"Ticket: `{ctx.author.id}`\nName: `{ctx.author.name}`\n\n" + str(msg),
            color=colours["delete"]
        ))
        await ctx.send(embed=discord.Embed(
            title=f"{emojis['tick']} Success",
            description="Your ticket was sent to the mod team.",
            color=colours["create"]
        ), delete_after=10)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id != 715989276382462053 and reaction.message.channel.id == 777214577187487744 and reaction.emoji.name == 'Tick':
            await reaction.message.delete()
            r = await self.bot.get_channel(777224376051040310).send(embed=discord.Embed(
                title="Suggestion",
                description='\n'.join(reaction.message.embeds[0].description.split("\n")[2:]),
                color=colours["create"]
            ))
            await r.add_reaction(self.bot.get_emoji(729064531107774534))
            await r.add_reaction(self.bot.get_emoji(729064530310594601))
        elif user.id != 715989276382462053 and reaction.message.channel.id == 777214577187487744 and reaction.emoji.name == 'Cross':
            await reaction.message.delete()


def setup(bot):
    bot.add_cog(InfoCommands(bot))
