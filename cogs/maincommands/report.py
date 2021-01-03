import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, datetime

from datetime import datetime
from discord.ext import commands, tasks
from textwrap import shorten

from cogs.consts import *


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def stafflog(
        self, ctx, channel: typing.Optional[typing.Union[discord.TextChannel, int]]
    ):
        m = await ctx.send(embed=loadingEmbed)
        if isinstance(channel, int):
            channel = self.bot.get_channel(channel)
        if not channel:
            await m.edit(
                embed=discord.Embed(
                    title=f"{emojis['channel_create']} Which channel?",
                    description=f"Please send a channel mention ({ctx.channel.mention}) or an id `{ctx.channel.id}` to set your staff log channel. Type `cancel` to cancel.",
                    color=colours["create"],
                )
            )
            if message.content.lower() == "cancel":
                return await m.edit(
                    embed=discord.Embed(
                        title=f"{emojis['channel_delete']} Which channel?",
                        description=f"Please send a channel mention ({ctx.channel.mention}) or an id `{ctx.channel.id}` to set your staff log channel.",
                        color=colours["delete"],
                    )
                )
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda message: message.author.id == ctx.author.id
                    and message.channel.id == ctx.channel.id,
                    timeout=60.0,
                )
            except asyncio.TimeoutError:
                return await m.edit(
                    embed=discord.Embed(
                        title=f"{emojis['channel_delete']} Which channel?",
                        description=f"Please send a channel mention ({ctx.channel.mention}) or an id `{ctx.channel.id}` to set your staff log channel.",
                        color=colours["delete"],
                    )
                )
            msg = msg
            try:
                channel = self.bot.get_channel(int(msg.content))
            except:
                try:
                    channel = msg.channel_mentions[0]
                except:
                    return await m.edit(
                        embed=discord.Embed(
                            title=f"{emojis['channel_delete']} Thats not a channel",
                            description=f"I couldn't convert `{msg.content}` into a channel. Are you sure you typed it right?",
                            color=colours["delete"],
                        )
                    )

        if ctx.guild.id == channel.guild.id:
            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
                try:
                    entry["log_info"]["staff"] = channel.id
                except KeyError:
                    entry["log_info"]["staff"] = None
            with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                json.dump(entry, f, indent=2)

            return await m.edit(
                embed=discord.Embed(
                    title=f"{emojis['channel_create']} Staff log channel set",
                    description=f"Your staff log channel is now set to {channel.mention}.",
                    color=colours["create"],
                )
            )
        else:
            return await m.edit(
                embed=discord.Embed(
                    title=f"{emojis['channel_delete']} That channel isn't in this server",
                    description=f"Make sure the channel you posted ({channel.mention}) is in this server.",
                    color=colours["delete"],
                )
            )

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def report(self, ctx, *, content=""):
        guild = None
        if isinstance(ctx.channel, discord.channel.DMChannel):
            m = await ctx.send(embed=loadingEmbed)
            mutuals = [g for g in self.bot.guilds if g.get_member(ctx.author.id)]
            if not len(mutuals):
                return await m.edit(
                    embed=discord.Embed(
                        title=f"{emojis['channel_delete']} We don't share a server",
                        description=f"I'm not in any servers that you are in.",
                        color=colours["delete"],
                    )
                )
            elif len(mutuals) < 2:
                await m.delete()
                guild = mutuals[0]
            else:

                def chunk(l):
                    for i in range(0, len(l), 5):
                        yield l[i : i + 5]

                chunked = list(chunk(mutuals))

                page = 0

                for e in [
                    729064530310594601,
                    729762938411548694,
                    729762938843430952,
                    753259025990418515,
                    753259024409034896,
                    753259024358703205,
                    753259024555835513,
                    753259024744579283,
                ]:
                    await m.add_reaction(self.bot.get_emoji(e))
                for _ in range(50):
                    chunk = [g.name for g in chunked[page]]
                    s = ""
                    for x in range(len(chunk)):
                        s += f"{emojis[str(x+1)]} {chunk[x]}\n"
                    await m.edit(
                        embed=discord.Embed(
                            title=f"{emojis['channel_create']} Which server?",
                            description=f"We share {len(mutuals)} servers. Which should I report in:\n{s}",
                            color=colours["create"],
                        )
                    )
                    reaction = None
                    done, pending = await asyncio.wait(
                        [
                            self.bot.wait_for(
                                "reaction_add",
                                timeout=120,
                                check=lambda emoji, user: emoji.message.id == m.id
                                and user == ctx.author,
                            ),
                            self.bot.wait_for(
                                "reaction_remove",
                                timeout=120,
                                check=lambda emoji, user: emoji.message.id == m.id
                                and user == ctx.author,
                            ),
                        ],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    try:
                        reaction, _ = done.pop().result()
                    except:
                        break

                    for future in done:
                        future.exception()
                    for future in pending:
                        future.cancel()

                    if reaction == None:
                        break
                    elif reaction.emoji.name == "Left":
                        page -= 1
                    elif reaction.emoji.name == "Right":
                        page += 1
                    elif len(reaction.emoji.name) == 2:
                        reaction = str(reaction.emoji.name)[:1]
                        await m.delete()
                        m = await ctx.send(embed=loadingEmbed)
                        guild = chunked[page][int(reaction)]
                        break
                    else:
                        break
                    page = min(len(chunked) - 1, max(0, page))
                if guild == None:
                    return await m.edit(
                        embed=discord.Embed(
                            title=f"{emojis['channel_delete']} Which server?",
                            description=f"We share {len(mutuals)} servers. Which should I report in:\n{s}",
                            color=colours["delete"],
                        )
                    )
        else:
            guild = ctx.guild
        m = await ctx.send(embed=loadingEmbed)
        with open(f"data/guilds/{guild.id}.json", "r") as entry:
            entry = json.load(entry)
            try:
                logchan = self.bot.get_channel(entry["log_info"]["staff"])
            except:
                logchan = None
        if not logchan:
            return await m.edit(
                embed=discord.Embed(
                    title=f"{emojis['channel_delete']} This server isn't accepting reports",
                    description=f"The server `{guild.name}` is not allowing reports. Your request was cancelled.",
                    color=colours["delete"],
                )
            )
        if not content:
            await m.edit(
                embed=discord.Embed(
                    title=f"{emojis['channel_create']} Report",
                    description=f"What text would you like to send to the mod team? Say `cancel` to cancel.",
                    color=colours["create"],
                )
            )
            try:
                msg = await ctx.bot.wait_for(
                    "message",
                    timeout=60,
                    check=lambda m: m.author.id == ctx.author.id
                    and m.channel.id == ctx.channel.id,
                )
            except asyncio.TimeoutError:
                return await m.edit(
                    embed=discord.Embed(
                        title=f"{emojis['channel_delete']} Report",
                        description=f"What text would you like to send to the mod team? Say `cancel` to cancel.",
                        color=colours["delete"],
                    )
                )
            content = msg.content
            if content.lower == "cancel":
                return await m.edit(
                    embed=discord.Embed(
                        title=f"{emojis['channel_delete']} Report",
                        description=f"What text would you like to send to the mod team? Say `cancel` to cancel.",
                        color=colours["delete"],
                    )
                )
        await logchan.send(
            embed=discord.Embed(
                title=f" {emojis['leave']} Request by {ctx.author.name}",
                description=f"**User:** {ctx.author.name}\n"
                f"**ID:** `{ctx.author.id}`\n"
                f"**Request:**\n"
                f"{content}",
                color=colours["edit"],
            )
        )
        return await m.edit(
            embed=discord.Embed(
                title=f"{emojis['channel_create']} Report",
                description=f"Your message was successfully sent.",
                color=colours["create"],
            )
        )


def setup(bot):
    bot.add_cog(Report(bot))
