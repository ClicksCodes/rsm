import copy
import discord
import json
import humanize
import aiohttp
import traceback
import subprocess
import functools
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
        self.assignees = "PineaFan"

        self.head = str(subprocess.check_output(["git", "rev-parse", "HEAD"]))[2:-3]
        self.branch = str(subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]))[2:-3]
        self.commit = str(subprocess.check_output(["git", "show-branch", self.branch]))[(5+(len(self.branch))):-3]
        self.url = str(subprocess.check_output(["git", "config", "--get", "remote.origin.url"]))[2:-3]

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

    async def run_sync(self, func: callable, *args, **kwargs):
        return await self.bot.loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

    @commands.command(aliases=["v"])
    async def version(self, ctx):
        total_size = 0
        for path, dirs, files in os.walk("./data/guilds"):
            for f in files:
                fp = os.path.join(path, f)
                total_size += os.path.getsize(fp)

        await ctx.send(embed=discord.Embed(
            title=f"{self.bot.user.name}",
            description=f"**Repository:** {self.url.split('/')[-2]}/{self.url.split('/')[-1]}\n"
                        f"**Branch:** `{self.branch}`\n"
                        f"**HEAD:** `{self.head}`\n"
                        f"**Commit:** `{self.commit}`\n"
                        f"**Server size:** `{humanize.naturalsize(os.path.getsize(f'./data/guilds/{ctx.guild.id}.json'))}` • `{humanize.naturalsize(total_size)}`\n"
                        f"**Uptime:** `{str(datetime.datetime.now()-self.bot.uptime).split('.')[0]}`",
            color=colours["delete"],
            url="https://discord.gg/bPaNnxe"
        ).set_footer(
            text=f"You probably don't know what most of this means - "
                 f"If you do know what this means, you can become a programmer of {self.bot.user.name} and other bots at https://discord.gg/bPaNnxe",
            icon_url=self.bot.user.avatar_url
        ))

    @commands.command()
    @commands.is_owner()
    async def git(self, ctx):
        m = await ctx.send(embed=loadingEmbed)
        for r in [834127343206400021, 834148997324472391, 834127343533555713, 834127343525822474, 834127343244673055, 834139266921267211]:  # 834127343576023130
            await m.add_reaction(self.bot.get_emoji(r))

        gc = {
            "commit": 834127343525822474,
            "pull": 834148997324472391,
            "merge": 834127343533555713,
            "push": 834127343244673055,
            "fetch": 834127343206400021,
            "fork": 834127343576023130,
            "reload": 834139266921267211
        }

        self.head = str(subprocess.check_output(["git", "rev-parse", "HEAD"]))[2:-3]
        self.branch = str(subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]))[2:-3]
        self.commit = str(subprocess.check_output(["git", "show-branch", self.branch]))[(5+(len(self.branch))):-3]
        self.url = str(subprocess.check_output(["git", "config", "--get", "remote.origin.url"]))[2:-3]
        while True:
            await m.edit(embed=discord.Embed(
                title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                description=f"Current version for `{self.url.split('/')[-2]}/{self.url.split('/')[-1]}`\n"
                            f"**Branch:** `{self.branch}`\n"
                            f"**HEAD:** `{self.head}`\n"
                            f"**Commit:** `{self.commit}`\n\n"
                            f"{self.bot.get_emoji(gc['fetch'])} **Fetch** latest commit\n"
                            f"{self.bot.get_emoji(gc['pull'])} **Pull** fetched version\n"
                            f"{self.bot.get_emoji(gc['merge'])} **Merge** with current version\n"
                            f"{self.bot.get_emoji(gc['commit'])} **Commit** current code\n"
                            f"{self.bot.get_emoji(gc['push'])} **Push** current commit\n\n"
                            f"{self.bot.get_emoji(gc['reload'])} **PM2 reload**",
                color=colours["create"]
            ))
            try:
                reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
            except asyncio.TimeoutError:
                break

            try:
                await m.remove_reaction(reaction[0].emoji, ctx.author)
            except Exception as e:
                print(e)

            if reaction is None:
                break
            elif reaction[0].emoji.name == "Fetch":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['fetch'])} Fetch\n\n>>> Fetching",
                    color=colours["create"]
                ))
                out = subprocess.run(["git", "fetch"], stdout=subprocess.PIPE)
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['fetch'])} Fetch\n\n>>> {'Fetched successfully' if out.returncode == 0 else 'Exited with code `' + out.returncode +'`'}",
                    color=colours["create"]
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "Pull":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['pull'])} Pull\n\n>>> Pulling",
                    color=colours["create"]
                ))
                out = subprocess.run(["git", "pull"], stdout=subprocess.PIPE)
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['pull'])} Pull\n\n>>> {'Pulled successfully' if out.returncode == 0 else 'Exited with code `' + out.returncode +'`'}",
                    color=colours["create"]
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "Merge":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['merge'])} Merge\n\n>>> Merging",
                    color=colours["create"]
                ))
                out = subprocess.run(["git", "merge"], stdout=subprocess.PIPE)
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['merge'])} Merge\n\n>>> {'Merged successfully' if out.returncode == 0 else 'Exited with code `' + out.returncode +'`'}",
                    color=colours["create"]
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "Commit":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['commit'])} Commit\n\n>>> Enter a commit message",
                    color=colours["create"]
                ))
                try:
                    message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.author.id == ctx.author.id)
                except asyncio.TimeoutError:
                    break

                try:
                    await message.delete()
                except Exception as e:
                    print(e)
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['commit'])} Commit\n\n>>> Committing",
                    color=colours["create"]
                ))
                out = subprocess.run(["git", "commit", "-am", f'{message.content}'], stdout=subprocess.PIPE)
                backn = "\n"
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['commit'])} Commit\n\n>>> {f'Committed successfully with message:{backn} {message.content}' if out.returncode == 0 else 'Exited with code `' + out.returncode +'`'}",
                    color=colours["create"]
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "Push":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['push'])} Push\n\n>>> Pushing",
                    color=colours["create"]
                ))
                out = subprocess.run(["git", "push"], stdout=subprocess.PIPE)
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['push'])} Push\n\n>>> {'Pushed successfully' if out.returncode == 0 else 'Exited with code `' + out.returncode +'`'}",
                    color=colours["create"]
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "reload":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['reload'])} PM2 Reload\n\n>>> Reloading",
                    color=colours["create"]
                ))
                try:
                    out = subprocess.run(["pm2", "reload", "3"], stdout=subprocess.PIPE).returncode
                except FileNotFoundError:
                    out = 1
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['reload'])} PM2 Reload\n\n>>> {'Reloaded successfully' if out == -2 else 'Exited with code `' + str(out) +'`'}",
                    color=colours["create"]
                ))
                return


def setup(bot):
    bot.add_cog(InfoCommands(bot))
