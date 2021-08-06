import asyncio
import datetime
import os
import subprocess

import discord
import humanize
import psutil
from cogs.consts import *
from cogs.handlers import Handlers
from discord.ext import commands


class Git(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.assignees = "PineaFan"
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

        self.head = str(subprocess.check_output(["git", "rev-parse", "HEAD"]))[2:-3]
        self.branch = str(subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]))[2:-3]
        self.commit = str(subprocess.check_output(["git", "show-branch", self.branch]))[(5+(len(self.branch))):-3]
        self.url = str(subprocess.check_output(["git", "config", "--get", "remote.origin.url"]))[2:-3]

    @commands.command(aliases=["v"])
    async def version(self, ctx):
        total_size = 0
        for path, _, files in os.walk("./data/guilds"):
            for f in files:
                fp = os.path.join(path, f)
                total_size += os.path.getsize(fp)

        await ctx.send(embed=discord.Embed(
            title=f"{self.bot.user.name}",
            description=f"**Repository:** {self.url.split('/')[-2]}/{self.url.split('/')[-1]}\n"
                        f"**Branch:** `{self.branch}`\n"
                        f"**HEAD:** `{self.head}`\n"
                        f"**Commit:** `{self.commit}`\n"
                        f"**Server size:** `{humanize.naturalsize(os.path.getsize(f'./data/guilds/{ctx.guild.id}.json')) if ctx.guild else 0}`"
                        f" • `{humanize.naturalsize(total_size)}`\n"
                        f"**Uptime:** `{str(datetime.datetime.now()-self.bot.uptime).split('.')[0]}`",
            colour=self.colours.red,
            url="https://discord.gg/bPaNnxe"
        ).set_footer(
            text=f"You probably don't know what most of this means - "
                 f"If you do know what this means, you can become a programmer of {self.bot.user.name} and other bots at https://discord.gg/bPaNnxe",
            icon_url=self.bot.user.avatar.url
        ))

    @commands.command()
    @commands.is_owner()
    async def git(self, ctx):
        m = await ctx.send(embed=loading_embed)
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
                colour=self.colours.green
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
                    colour=self.colours.green
                ))
                out = subprocess.run(["git", "fetch"], stdout=subprocess.PIPE)
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['fetch'])} Fetch\n\n>>> "
                                f"{'Fetched successfully' if out.returncode == 0 else 'Exited with code `' + str(out.returncode) +'`'}",
                    colour=self.colours.green
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "Pull":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['pull'])} Pull\n\n>>> Pulling",
                    colour=self.colours.green
                ))
                out = subprocess.run(["git", "pull"], stdout=subprocess.PIPE)
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['pull'])} Pull\n\n>>> {'Pulled successfully' if out.returncode == 0 else 'Exited with code `' + str(out.returncode) +'`'}",
                    colour=self.colours.green
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "Merge":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['merge'])} Merge\n\n>>> Merging",
                    colour=self.colours.green
                ))
                out = subprocess.run(["git", "merge"], stdout=subprocess.PIPE)
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['merge'])} Merge\n\n>>> "
                                f"{'Merged successfully' if out.returncode == 0 else 'Exited with code `' + str(out.returncode) +'`'}",
                    colour=self.colours.green
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "Commit":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['commit'])} Commit\n\n>>> Enter a commit message",
                    colour=self.colours.green
                ))
                try:
                    message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.author.id == ctx.author.id)
                except asyncio.TimeoutError:
                    break

                try:
                    await message.delete()
                except discord.HTTPException:
                    pass
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['commit'])} Commit\n\n>>> Committing",
                    colour=self.colours.green
                ))
                out = subprocess.run(["git", "commit", "-am", f'"{message.content}"'], stdout=subprocess.PIPE)
                backn = "\n"
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['commit'])} Commit\n\n>>> "
                                f"{f'Committed successfully with message:{backn} {message.content}' if out.returncode == 0 else 'Exited with code `' + str(out.returncode) +'`'}",
                    colour=self.colours.green
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "Push":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['push'])} Push\n\n>>> Pushing",
                    colour=self.colours.green
                ))
                out = subprocess.run(["git", "push"], stdout=subprocess.PIPE)
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['push'])} Push\n\n>>> "
                                f"{'Pushed successfully' if out.returncode == 0 else 'Exited with code `' + str(out.returncode) +'`'}",
                    colour=self.colours.green
                ))
                await asyncio.sleep(3)
            elif reaction[0].emoji.name == "reload":
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['reload'])} PM2 Reload\n\n>>> Reloading",
                    colour=self.colours.green
                ))
                try:
                    out = subprocess.run(["pm2", "reload", "3"], stdout=subprocess.PIPE).returncode
                except FileNotFoundError:
                    out = 1
                await m.edit(embed=discord.Embed(
                    title=f"{self.bot.get_emoji(gc['fork'])} Git Controls",
                    description=f"{self.bot.get_emoji(gc['reload'])} PM2 Reload\n\n>>> "
                                f"{'Reloaded successfully' if out == -2 else 'Exited with code `' + str(out) +'`'}",
                    colour=self.colours.green
                ))
                return

    @commands.command()
    async def usage(self, ctx):
        m = await ctx.send(embed=loading_embed)
        cpu = psutil.getloadavg()
        cpu = round(sum(cpu) / len(cpu) * 100, 2)
        mem = round((psutil.virtual_memory().used/psutil.virtual_memory().total)*100, 2)
        temp, count = 0, 0
        try:
            sensors = psutil.sensors_temperatures()
        except AttributeError:
            sensors = []
        for sensor in sensors:
            for each in sensors[sensor]:
                temp += each.current
                count += 1
        tempav = round(temp/count, 2)
        swap = round(psutil.swap_memory().percent, 2)
        disk = psutil.disk_usage('/').percent

        await m.edit(embed=discord.Embed(
            title="Usage statistics",
            description=f"**Server time:** {self.handlers.strf(datetime.datetime.now())}\n"
                        f"**CPU:** {cpu}%\n"
                        f"**Memory:** {mem}%\n"
                        f"**Swap:** {swap}%\n"
                        f"**Disk:** {disk}%\n"
                        f"**Temperature:** {tempav}°c",
            color=self.colours.green
        ))


def setup(bot):
    bot.add_cog(Git(bot))
