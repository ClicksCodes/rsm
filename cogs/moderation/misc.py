import asyncio
import typing
import aiohttp
import datetime
import discord
from discord.ext import commands
from collections import OrderedDict

from cogs.consts import *
from cogs.handlers import Handlers, Failed


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.command()
    @commands.guild_only()
    async def purge(self, ctx, amount: typing.Optional[str]):
        try:
            amount = int(amount)
            if amount < 1:
                amount = "a"
        except ValueError:
            pass
        m = await ctx.send(embed=loading_embed)
        extra = 0

        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_messages", self.emojis().channel.purge, "purge the channel"), Failed):
            return

        if not isinstance(amount, int):
            amount = await self.handlers.intHandler(ctx, m, self.emojis().channel.purge, "Purge", "How many messages should be cleared?", default=50)
            if isinstance(amount, Failed):
                return
            extra = 1

        try:
            deleted = await ctx.channel.purge(limit=amount+2+extra, check=lambda message: not message.pinned)
            mlist = "\n\n".join([self.handlers.convertMessage(message) for message in deleted])
            async with aiohttp.ClientSession() as session:
                async with session.post('https://hastebin.com/documents', data=mlist) as r:
                    s = '"'
                    url = f'https://hastebin.com/{(await r.text()).split(s)[3]}'
            await self.handlers.sendLog(
                emoji=self.emojis().channel.purge,
                type="Messages purged",
                server=deleted[0].guild.id,
                colour=self.colours.red,
                data={
                    "Amount": len(deleted),
                    "Sent in": deleted[0].channel.mention,
                    "Purged by": ctx.author.mention,
                    "Purged": self.handlers.strf(datetime.datetime.utcnow()),
                    "Messages": url
                }
            )
            return await ctx.send(embed=discord.Embed(
                title=f"{self.emojis().channel.purge} Purge",
                description=f"Successfully purged {len(deleted)-2-extra} messages",
                colour=self.colours.green
            ), delete_after=10)
        except discord.errors.Forbidden:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().channel.purge} Purge",
                description=f"An error occurred while purging {ctx.channel.mention}",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"))

    @commands.command()
    @commands.guild_only()
    async def unban(self, ctx, member: typing.Optional[discord.User]):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "ban_members", self.emojis().member.unban, "unban someone"), Failed):
            returngreen

        if not member:
            member = await self.handlers.memberHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().member.unban),
                title="Unban",
                description="Who would you like to unban?"
            )
            if isinstance(member, Failed):
                return

        try:
            await ctx.guild.unban(member, reason="RSM Unban")
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().member.unban} Unban",
                description=f"{member.mention} was successfully unbanned",
                colour=self.colours.green
            ))
        except discord.errors.Forbidden:
            return await m.edit(embed=discord.Embedgreen(
                title=f"{self.emojis().member.unban} Unban",
                description=f"An error occurred while unbanning {member.mention}",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"))

    async def setSlowmode(self, ctx, m, speed):
        speed = max(0, min(speed, 21600))
        await ctx.channel.edit(slowmode_delay=speed)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().slowmode.on} Slowmode enabled" if ctx.channel.slowmode_delay else f"{self.emojis().slowmode.off} Slowmode disabled",
            description=f"Slowmode has been set to {ctx.channel.slowmode_delay}s",
            colour=self.colours.red if ctx.channel.slowmode_delay else self.colours.green
        ))

    @commands.command()
    @commands.guild_only()
    async def slowmode(self, ctx, speed: typing.Optional[str]):
        if not speed:
            speed = ""
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_messages", self.emojis().slowmode.on, "change slowmode"), Failed):
            return
        if speed.isdigit():
            await self.setSlowmode(ctx, m, int(speed))
        elif len(speed) and speed[-1] in ["s", "m", "h"]:
            match speed[-1]:
                case "s": speed = int(speed[:-1])
                case "m": speed = int(speed[:-1]) * 60
                case "h": speed = int(speed[:-1]) * 60 * 60
            await self.setSlowmode(ctx, m, speed)
        elif speed == "on":
            await self.setSlowmode(ctx, m, 10)
        elif speed == "off":
            await self.setSlowmode(ctx, m, 0)
        else:
            match ctx.channel.slowmode_delay:
                case 0: await self.setSlowmode(ctx, m, 10)
                case _: await self.setSlowmode(ctx, m, 0)

    @commands.command()
    @commands.guild_only()
    async def avatar(self, ctx, member: typing.Optional[discord.Member]):
        m = await ctx.send(embed=loading_embed)
        if not member:
            member = ctx.author
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().member.join} Avatar",
            description=f"**URL:** [[Open]]({member.avatar_url})\n"
                        f"**Member:** {member.mention}",
            colour=self.colours.green
        ).set_image(url=member.avatar_url))

    @commands.command(aliases=["viewfrom", "serveras", "serverfrom"])
    @commands.guild_only()
    async def viewas(self, ctx, target: typing.Union[discord.Member, discord.Role, None]):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_messages", self.emojis().channel.text.create, "view as someone else", me=False), Failed):
            return
        if not target:
            target = await self.handlers.memberHandler(ctx, m, emoji=self.emojis().channel.text.create, title="View as", description="Who would you like to view the server as?")
            if isinstance(target, Failed):
                return
        visible = {}
        if isinstance(target, discord.Member):
            for channel in ctx.guild.channels:
                if (
                    (channel.type in [discord.ChannelType.text, discord.ChannelType.store, discord.ChannelType.news] and target.permissions_in(channel).read_messages) or
                    (channel.type in [discord.ChannelType.voice, discord.ChannelType.stage_voice] and target.permissions_in(channel).connect)
                ) and (channel.type is not discord.ChannelType.category):
                    if channel.category not in visible:
                        visible[channel.category] = []
                    visible[channel.category].append(channel)
        elif isinstance(target, discord.Role):
            for channel in ctx.guild.channels:
                if (
                    (channel.type in [discord.ChannelType.text, discord.ChannelType.store] and (channel.overwrites_for(target).read_messages)) or
                    (channel.type in [discord.ChannelType.voice, discord.ChannelType.stage_voice] and (channel.overwrites_for(target).connect)) or
                    (target.permissions.administrator)
                ) and (channel.type is not discord.ChannelType.category):
                    if channel.category not in visible:
                        visible[channel.category] = []
                    visible[channel.category].append(channel)
        page = 0
        if not len(visible):
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().channel.text.create} View as",
                description=f"*No visible channels*",
                colour=self.colours.yellow
            ))
        await self.handlers.reactionCollector(
            ctx,
            m,
            reactions=[
                "control.cross",
                "control.left",
                "control.right"
            ],
            collect=False
        )
        ordered = OrderedDict(sorted(visible.items(), key=lambda x: (x[0].position if hasattr(x[0], "position") else -1) if isinstance(x, tuple) else -1))
        visible = {k: ordered[k] for k in ordered}
        for k in visible.keys():
            visible[k] = sorted(visible[k], key=lambda x: x.position if x.type.name == "text" else x.position + 50)
        while True:
            page = max(0, min(page, len(visible)-1))
            description = []
            if list(visible.keys())[page] is None:
                name = "Uncategorised"
            else:
                name = list(visible.keys())[page].name
            for channel in visible[list(visible.keys())[page]]:
                icon = ""
                match channel.type.name:
                    case "text": icon = self.emojis().icon.text_channel
                    case "voice": icon = self.emojis().icon.voice_channel
                    case "news": icon = self.emojis().icon.announcement_channel
                    case "store": icon = self.emojis().icon.store_channel
                    case "stage_voice": icon = self.emojis().icon.stage_channel
                    case _: icon = self.emojis().icon.text_channel
                description.append((icon, channel.mention))
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().channel.category.create} {name} ({page + 1}/{len(visible)})",
                description="\n".join([f"{c[0]} {c[1]}" for c in description]),
                colour=self.colours.green
            ))
            reaction = await self.handlers.reactionCollector(ctx, m, [])
            match reaction.emoji.name:
                case "Left": page -= 1
                case "Right": page += 1
                case _: break
        await asyncio.sleep(0.1)
        await m.clear_reactions()
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().channel.category.create} {name} ({page + 1}/{len(visible)})",
            description="\n".join([f"{c[0]} {c[1]}" for c in description]),
            colour=self.colours.red
        ))


def setup(bot):
    bot.add_cog(Mod(bot))
