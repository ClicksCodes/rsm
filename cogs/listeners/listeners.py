import aiohttp
import discord
import datetime
import io
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild:
            if message.channel.slowmode_delay:
                if self.handlers.is_channel_locked(message.channel) and not message.author.permissions_in(message.channel).manage_messages:
                    return await message.delete()
        if self.handlers.is_text_banned(message.content, message.guild, message.author, message.channel):
            return await message.delete()
        if message.channel.nsfw:
            for attachment in message.attachments:
                nsfw, detections, score, image = await self.handlers.is_pfp_nsfw(attachment.proxy_url)
                image.show()
                if nsfw:
                    data = self.handlers.fileManager(message.guild)
                    if data["log_info"]["staff"]:
                        buf = io.BytesIO()
                        image.save(buf, format="png")
                        buf.seek(0)
                        await self.bot.get_channel(data["log_info"]["staff"]).send(embed=discord.Embed(
                            title=f"{self.emojis().punish.warn} NSFW image sent",
                            description=f"**User:** {message.author.name} ({message.author.mention})\n**Confidence:** "
                                        f"{round(score, 2)}%\n[[View here]]({str(message.author.avatar_url_as(format='png'))})",
                            color=self.colours.red
                        ))
                        # ), file=discord.File(buf, filename="image.png", spoiler=True))
                    return await message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        data = self.handlers.fileManager(member.guild)

        if data["welcome"]["message"]["channel"] and data["welcome"]["message"]["text"]:
            text = data["welcome"]["message"]["text"].replace("[mc]", str(len(member.guild.members))).replace("[@]", member.mention)
            if isinstance(data["welcome"]["message"]["channel"], str):
                await member.send(embed=discord.Embed(
                    title=f"Welcome to {member.guild.name}",
                    description=text,
                    color=self.colours.green
                ))
            else:
                await self.bot.get_channel(data["welcome"]["message"]["channel"]).send(embed=discord.Embed(
                    title=f"Welcome to {member.guild.name}",
                    description=text,
                    color=self.colours.green
                ))

        if data["welcome"]["role"]:
            await member.add_roles(member.guild.get_role(data["welcome"]["role"]))

        if self.handlers.is_text_banned(member.name, member.guild, member):
            match data["wordfilter"]["punishment"]:
                case "change":
                    await member.edit(nick="[!] Username broke rules")
                    await member.send(embed=discord.Embed(
                        title=f"{self.emojis().control.cross} Username did not follow rules",
                        description=f"You joined {member.guild.name}, but your name contained word(s) that aren't allowed. Please contact the moderators for more information",
                        color=self.colours.red
                    ))
                case "kick":
                    try:
                        await member.send(embed=discord.Embed(
                            title=f"{self.emojis().control.cross} Username did not follow rules",
                            description=f"You joined {member.guild.name}, but your name contained word(s) that aren't allowed. You have been automatically kicked",
                            color=self.colours.red
                        ))
                    except discord.Forbidden:
                        pass
                    return await member.kick(reason="RSM - Username broke rules")
                case "ban":
                    try:
                        await member.send(embed=discord.Embed(
                            title=f"{self.emojis().control.cross} Username did not follow rules",
                            description=f"You joined {member.guild.name}, but your name contained word(s) that aren't allowed. You have been automatically banned",
                            color=self.colours.red
                        ))
                    except discord.Forbidden:
                        pass
                    return await member.ban(reason="RSM - Username broke rules")
        nsfw, _, score, image = await self.handlers.is_pfp_nsfw(str(member.avatar_url_as(format="png")))
        if nsfw:
            try:
                await member.send(embed=discord.Embed(
                    title=f"{self.emojis().control.cross} Profile picture did not follow rules",
                    description=f"You joined {member.guild.name}, but your profile was flagged as NSFW. Please contact the moderators if you believe this is a mistake",
                    color=self.colours.red
                ))
            except discord.Forbidden:
                pass
            data = self.handlers.fileManager(member.guild.id)
            if data["log_info"]["staff"]:
                buf = io.BytesIO()
                image.save(buf, format="png")
                buf.seek(0)
                await self.bot.get_channel(data["log_info"]["staff"]).send(embed=discord.Embed(
                    title=f"{self.emojis().control.cross} Profile picture flagged",
                    description=f"**User:** {member.name} ({member.mention})\n**Confidence:** {round(score, 2)}%\n[[View here]]({str(member.avatar_url_as(format='png'))})",
                    color=self.colours.red
                ), file=discord.File(buf, filename="image.png", spoiler=True))

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            if self.handlers.is_text_banned(after.display_name, after.guild, after):
                audit = await self.handlers.getAuditLogEntry(after.guild, type=discord.AuditLogAction.member_update)
                if not audit.user.bot:
                    await after.edit(nick="[!] Username broke rules")


def setup(bot):
    bot.add_cog(Listeners(bot))
