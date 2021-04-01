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

import datetime
from discord.ext import commands
from textwrap import shorten

from cogs.consts import *


class InfoCommands(commands.Cog):
    def __init__(self, bot):
        self.loadingEmbed = loadingEmbed
        self.bot = bot

    async def fetch(self, guild, ctx):
        with open(f"data/guilds/{guild}.json") as f:
            entry = json.load(f)
        if "wordfilter" not in entry:
            entry["wordfilter"] = {
                "ignore": {
                    "roles": [],
                    "channels": [],
                    "members": [],
                    "delta": None
                },
                "banned": [
                ]
            }
            json.dump(entry, open(f"data/guilds/{guild}.json", "w"), indent=2)
        return entry

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def filter(self, ctx, args: typing.Optional[str]):
        while True:
            entry = await self.fetch(ctx.guild.id, ctx)
            m = await ctx.send(embed=discord.Embed(
                title=f"{emojis['image_swear']} Banned words",
                description=f"**Banned words:** {', '.join([word for word in entry['wordfilter']['banned']])}\n"
                            f"**Exempt users:** {', '.join([ctx.guild.get_member(m).mention for m in entry['wordfilter']['ignore']['members']])}\n"
                            f"**Exempt roles:** {', '.join([ctx.guild.get_role(m).mention for m in entry['wordfilter']['ignore']['roles']])}\n"
                            f"**Exempt channels:** {', '.join([ctx.guild.get_channel(m).mention for m in entry['wordfilter']['ignore']['channels']])}",
                color=colours["delete"]
            ))
            for r in [826823514904330251, 826823515268186152, 729066519337762878, 729064530709315715, 729066924943737033, 729064530310594601]:
                await m.add_reaction(self.bot.get_emoji(r))

            try:
                reaction = await ctx.bot.wait_for('reaction_add', timeout=60, check=lambda r, user: r.message.id == m.id and user == ctx.author)
            except asyncio.TimeoutError:
                break

            try:
                await m.remove_reaction(reaction[0].emoji, ctx.author)
            except Exception as e:
                print(e)
            r = reaction[0].emoji

            if r.name == "add":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(826823514904330251)} Enter words to add to your list",
                    description="Enter each word separated by a space, such as `one two`. Type `none` to cancel",
                    color=colours["create"]
                ))
                try:
                    message = await ctx.bot.wait_for('message', timeout=60, check=lambda message: message.channel.id == ctx.channel.id and message.author.id == ctx.author.id)
                except asyncio.TimeoutError:
                    break
                if message.content.lower() != "none":
                    words = message.content.split(" ")
                    for word in words:
                        if word not in entry["wordfilter"]["banned"]:
                            entry["wordfilter"]["banned"].append(word)
                    json.dump(entry, open(f"data/guilds/{ctx.guild.id}.json", "w"), indent=2)
            elif r.name == "remove":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(826823515268186152)} Enter words to remove to your list",
                    description="Enter each word separated by a space, such as `one two`. Type `none` to cancel",
                    color=colours["delete"]
                ))
                try:
                    message = await ctx.bot.wait_for('message', timeout=60, check=lambda message: message.channel.id == ctx.channel.id and message.author.id == ctx.author.id)
                except asyncio.TimeoutError:
                    break
                if message.content.lower() != "none":
                    words = message.content.split(" ")
                    for word in words:
                        if word in entry["wordfilter"]["banned"]:
                            entry["wordfilter"]["banned"].remove(word)
                    json.dump(entry, open(f"data/guilds/{ctx.guild.id}.json", "w"), indent=2)
            elif r.name == "MemberJoin":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(729066519337762878)} Enter users which should not be affected",
                    description="Enter each user as their mention, name or ID. Type `none` for no users",
                    color=colours["create"]
                ))
                try:
                    message = await ctx.bot.wait_for('message', timeout=60, check=lambda message: message.channel.id == ctx.channel.id and message.author.id == ctx.author.id)
                except asyncio.TimeoutError:
                    break
                users = []
                context = await self.bot.get_context(message)
                if message.content.lower() != "none":
                    for item in message.content.split(" "):
                        try:
                            r = await commands.MemberConverter().convert(context, item)
                            print(r)
                            users.append(r.id)
                        except commands.MemberNotFound:
                            pass
                entry["wordfilter"]["ignore"]["members"] = users
                json.dump(entry, open(f"data/guilds/{ctx.guild.id}.json", "w"), indent=2)
            elif r.name == "StoreCreate":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(729066519337762878)} Enter roles which should not be affected",
                    description="Enter each role as its mention, name or ID. Type `none` for no roles",
                    color=colours["create"]
                ))
                try:
                    message = await ctx.bot.wait_for('message', timeout=60, check=lambda message: message.channel.id == ctx.channel.id and message.author.id == ctx.author.id)
                except asyncio.TimeoutError:
                    break
                roles = []
                context = await self.bot.get_context(message)
                if message.content.lower() != "none":
                    for item in message.content.split(" "):
                        try:
                            r = await commands.RoleConverter().convert(context, item)
                            print(r)
                            roles.append(r.id)
                        except commands.MemberNotFound:
                            pass
                entry["wordfilter"]["ignore"]["roles"] = roles
                json.dump(entry, open(f"data/guilds/{ctx.guild.id}.json", "w"), indent=2)
            elif r.name == "ChannelCreate":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(729064530709315715)} Enter channel which should not be affected",
                    description="Enter each channel as its mention, name or ID. Type `none` for no channels",
                    color=colours["create"]
                ))
                try:
                    message = await ctx.bot.wait_for('message', timeout=60, check=lambda message: message.channel.id == ctx.channel.id and message.author.id == ctx.author.id)
                except asyncio.TimeoutError:
                    break
                channel = []
                context = await self.bot.get_context(message)
                if message.content.lower() != "none":
                    for item in message.content.split(" "):
                        try:
                            r = await commands.TextChannelConverter().convert(context, item)
                            print(r)
                            channel.append(r.id)
                        except commands.MemberNotFound:
                            pass
                entry["wordfilter"]["ignore"]["channels"] = channel
                json.dump(entry, open(f"data/guilds/{ctx.guild.id}.json", "w"), indent=2)
            else:
                break
        await m.clear_reactions()


def setup(bot):
    bot.add_cog(InfoCommands(bot))
