import discord
import datetime
import asyncio
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers


class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await asyncio.sleep(1)
        audit = await self.handlers.getAuditLogEntry(channel.guild, type=discord.AuditLogAction.channel_create)
        if not audit or audit.user.bot:
            return
        if isinstance(channel, discord.CategoryChannel):
            return await self.handlers.sendLog(
                emoji=self.emojis().channel.category.create,
                type=f"Category created",
                server=channel.guild.id,
                colour=self.colours.green,
                data={
                    "Name": f"{channel.name}",
                    "Created": self.handlers.strf(datetime.datetime.now()),
                    "Created by": f"{audit.user.name} ({audit.user.mention})",
                    "ID": f"`{channel.id}`"
                }
            )
        icon = None
        t = ""
        match channel.type.name:
            case "text":
                icon = self.emojis().channel.text.create
                t = "Text"
            case "news":
                icon = self.emojis().channel.text.create
                t = "Announcement"
            case "voice":
                icon = self.emojis().channel.voice.create
                t = "Voice"
            case "stage_voice":
                icon = self.emojis().channel.voice.create
                t = "Stage"
            case _:
                icon = self.emojis().channel.text.create
                t = "Unknown"
        return await self.handlers.sendLog(
            emoji=icon,
            type=f"{t} channel created",
            server=channel.guild.id,
            colour=self.colours.green,
            data={
                "Name": f"{channel.name} ({channel.mention})",
                "Category": channel.category.name if channel.category else 'Uncategorised',
                "Created": self.handlers.strf(datetime.datetime.now()),
                "Created by": f"{audit.user.name} ({audit.user.mention})",
                "ID": f"`{channel.id}`"
            }
        )

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await asyncio.sleep(1)
        audit = await self.handlers.getAuditLogEntry(channel.guild, type=discord.AuditLogAction.channel_delete)
        if not audit or audit.user.bot:
            return
        if isinstance(channel, discord.CategoryChannel):
            return await self.handlers.sendLog(
                emoji=self.emojis().channel.category.delete,
                type=f"Category deleted",
                server=channel.guild.id,
                colour=self.colours.red,
                data={
                    "Name": f"#{channel.name}",
                    "Deleted": self.handlers.strf(datetime.datetime.now()),
                    "Deleted by": f"{audit.user.name} ({audit.user.mention})",
                    "ID": f"`{channel.id}`"
                }
            )
        icon = None
        t = ""
        match channel.type.name:
            case "text":
                icon = self.emojis().channel.text.delete
                t = "Text"
            case "news":
                icon = self.emojis().channel.text.delete
                t = "Announcement"
            case "voice":
                icon = self.emojis().channel.voice.delete
                t = "Voice"
            case "stage_voice":
                icon = self.emojis().channel.voice.delete
                t = "Stage"
            case _:
                icon = self.emojis().channel.text.delete
                t = "Unknown"
        return await self.handlers.sendLog(
            emoji=icon,
            type=f"{t} channel deleted",
            server=channel.guild.id,
            colour=self.colours.red,
            data={
                "Name": f"{channel.name}",
                "Category": channel.category.name if channel.category else 'Uncategorised',
                "Deleted": self.handlers.strf(datetime.datetime.now()),
                "Deleted by": f"{audit.user.name} ({audit.user.mention})",
                "ID": f"`{channel.id}`"
            }
        )

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        await asyncio.sleep(1)
        audit = await self.handlers.getAuditLogEntry(after.guild, type=discord.AuditLogAction.channel_update)
        if not audit or audit.user.bot:
            return
        if isinstance(after, discord.CategoryChannel):
            changes = []
            if before.name != after.name:
                changes.append(f"> **Name:** {before.name} -> {after.name}")
            if not len(changes):
                return
            return await self.handlers.sendLog(
                emoji=self.emojis().channel.category.delete,
                type=f"Category updated",
                server=after.guild.id,
                colour=self.colours.yellow,
                data={  # ok ok
                    "Category": f"{after.name}",
                    "Changes": "\n".join(changes),
                    "Updated": self.handlers.strf(datetime.datetime.now()),
                    "Updated by": f"{audit.user.name} ({audit.user.mention})",
                    "ID": f"`{after.id}`"
                }
            )
        if after.type.name in ["text", "news"]:
            changes = []
            t = None
            icon = self.emojis().channel.title_update
            if before.name != after.name:
                t = "Title"
                changes.append(f"**Changes:**\n> **Name:** {before.name} -> {after.name} ({after.mention})")
            if before.topic != after.topic:
                icon = self.emojis().channel.topic_update
                t = "Topic"
                changes.append(f"> **Topic:** ```{self.handlers.cleanMessageContent(before.topic, max_length=100)}```↓"
                               f"```{self.handlers.cleanMessageContent(after.topic, max_length=100)}```")
            if before.category != after.category:
                t = "Category"
                changes.append(f"> **Category:** {before.category} -> {after.category}")
            if before.is_nsfw() != after.is_nsfw():
                if after.is_nsfw():
                    icon = self.emojis().options.nsfw.on
                else:
                    icon = self.emojis().options.nsfw.off
                t = "NSFW"
                changes.append(f"> **NSFW:** {'Yes' if before.is_nsfw() else 'No'} -> {'Yes' if after.is_nsfw() else 'No'}")
            if before.is_news() != after.is_news():
                t = "Type"
                changes.append(f"> **Type:** {'Announcement' if before.is_news() else 'Text'} -> {'Announcement' if after.is_news() else 'Text'}")
            if before.slowmode_delay != after.slowmode_delay:
                t = "Slowmode"
                changes.append(f"> **Slowmode:** {before.slowmode_delay}s -> {after.slowmode_delay}s")
            if not len(changes):
                return
            return await self.handlers.sendLog(
                emoji=icon,
                type=f"{t} updated",
                server=after.guild.id,
                colour=self.colours.yellow,
                data={
                    "Channel": f"{after.name} ({after.mention})\n" + "\n".join(changes),
                    "Updated": self.handlers.strf(datetime.datetime.now()),
                    "Updated by": f"{audit.user.name} ({audit.user.mention})",
                    "ID": f"`{after.id}`"
                }
            )
        if after.type.name == "voice":
            changes = []
            t = None
            if before.name != after.name:
                t = "Title"
                changes.append(f"**Changes:**\n> **Name:** {before.name} -> {after.name} ({after.mention})")
            if before.bitrate != after.bitrate:
                t = "Bitrate"
                changes.append(f"> **Bitrate:** {before.bitrate/1000}kbps -> {after.bitrate/1000}kbps")
            if before.rtc_region != after.rtc_region:
                t = "Region"
                changes.append(f"> **Region:** {'Auto' if not before.rtc_region else before.rtc_region.name} -> "
                               f"{'Auto' if not after.rtc_region else after.rtc_region.name}")
            if before.user_limit != after.user_limit:
                t = "User limit"
                changes.append(f"> **User limit:** {before.user_limit} -> {after.user_limit}")
            if before.category != after.category:
                t = "Category"
                changes.append(f"> **Category:** {before.category} -> {after.category}")
            if not len(changes):
                return
            return await self.handlers.sendLog(
                emoji=self.emojis().channel.title_update,
                type=f"{t} updated",
                server=after.guild.id,
                colour=self.colours.yellow,
                data={
                    "Channel": f"{after.name} ({after.mention})\n" + "\n".join(changes),
                    "Updated": self.handlers.strf(datetime.datetime.now()),
                    "Updated by": f"{audit.user.name} ({audit.user.mention})",
                    "ID": f"`{after.id}`"
                }
            )
        if after.type.name == "stage_voice":
            changes = []
            t = None
            if before.name != after.name:
                t = "Title"
                changes.append(f"**Changes:**\n> **Name:** {before.name} -> {after.name} ({after.mention})")
            if before.topic != after.topic:
                t = "Topic"
                changes.append(f"> **Topic:** ```{self.handlers.cleanMessageContent(before.topic, max_length=100)}```↓"
                               f"```{self.handlers.cleanMessageContent(after.topic, max_length=100)}```")
            if before.bitrate != after.bitrate:
                t = "Bitrate"
                changes.append(f"> **Bitrate:** {before.bitrate/1000}kbps -> {after.bitrate/1000}kbps")
            if before.rtc_region != after.rtc_region:
                t = "Region"
                changes.append(f"> **Region:** {'Auto' if not before.rtc_region else before.rtc_region.name} -> "
                               f"{'Auto' if not after.rtc_region else after.rtc_region.name}")
            if before.user_limit != after.user_limit:
                t = "User limit"
                changes.append(f"> **User limit:** {before.user_limit} -> {after.user_limit}")
            if before.category != after.category:
                t = "Category"
                changes.append(f"> **Category:** {before.category} -> {after.category}")
            if not len(changes):
                return
            return await self.handlers.sendLog(
                emoji=self.emojis().channel.title_update,
                type=f"{t} updated",
                server=after.guild.id,
                colour=self.colours.yellow,
                data={
                    "Channel": f"{after.name} ({after.mention})\n" + "\n".join(changes),
                    "Updated": self.handlers.strf(datetime.datetime.now()),
                    "Updated by": f"{audit.user.name} ({audit.user.mention})",
                    "ID": f"`{after.id}`"
                }
            )

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await asyncio.sleep(1)
        audit = await self.handlers.getAuditLogEntry(invite.guild, type=discord.AuditLogAction.invite_create)
        if not audit or audit.user.bot:
            return
        return await self.handlers.sendLog(
            emoji=self.emojis().invite.create,
            type=f"Invite created",
            server=invite.guild.id,
            colour=self.colours.green,
            data={
                "Channel": f"{invite.channel.name} ({invite.channel.mention})",
                "Link": f"{invite.url}",
                "Max uses": invite.max_uses if invite.max_uses else "No limit",
                "Expires": self.handlers.strf(datetime.datetime.utcnow() + datetime.timedelta(seconds=invite.max_age)) if invite.max_age else "Never",
                "Created": self.handlers.strf(datetime.datetime.now()),
                "Created by": f"{audit.user.name} ({audit.user.mention})"
            }
        )

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await asyncio.sleep(1)
        audit = await self.handlers.getAuditLogEntry(invite.guild, type=discord.AuditLogAction.invite_delete)
        if not audit or audit.user.bot:
            return
        return await self.handlers.sendLog(
            emoji=self.emojis().invite.delete,
            type=f"Invite deleted",
            server=invite.guild.id,
            colour=self.colours.red,
            data={
                "Channel": f"{invite.channel.name} ({invite.channel.mention})",
                "Link": f"{invite.url}",
                "Max uses": invite.max_uses if invite.max_uses else "No limit",
                "Uses": invite.uses,
                "Deleted": self.handlers.strf(datetime.datetime.now()),
                "Deleted by": f"{audit.user.name} ({audit.user.mention})"
            }
        )

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        await asyncio.sleep(1)
        audit = await self.handlers.getAuditLogEntry(after, type=discord.AuditLogAction.guild_update)
        if not audit or audit.user.bot:
            return
        changes = []
        t = None
        if before.name != after.name:
            if not t:
                t = ("Server name changed", "guild.moderation_update")
            changes.append(f"**Name:** {before.name} -> {after.name}")
        if before.icon.url != after.icon.url:
            if not t:
                t = ("Server image changed", "guild.icon_change")
            changes.append(f"**Icon:** [[Before]]({before.icon.url}) -> [[After]]({after.icon.url})")
        if before.verification_level != after.verification_level:
            if not t:
                t = ("Verification level changed", "guild.moderation_update")
            changes.append(f"**Moderation level:** {before.verification_level} -> {after.verification_level}")
        if len(changes):
            return await self.handlers.sendLog(
                emoji=self.emojis()(t[1]),
                type=t[0],
                server=after.id,
                colour=self.colours.yellow,
                data={
                    "Changes": "\n" + ("".join([f"> {change}\n" for change in changes])),
                    "Changed by": f"{audit.user.name} ({audit.user.mention})"
                }
            )

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await asyncio.sleep(1)
        audit = await self.handlers.getAuditLogEntry(role.guild, type=discord.AuditLogAction.role_create)
        if not audit or audit.user.bot:
            return
        return await self.handlers.sendLog(
            emoji=self.emojis().role.create,
            type="Role created",
            server=role.guild.id,
            colour=self.colours.green,
            data={
                "Role": f"{role.name} ({role.mention})",
                "ID": f"`{role.id}`",
                "Created": self.handlers.betterDelta(datetime.datetime.utcnow()),
                "Created by": f"{audit.user.name} ({audit.user.mention})"
            }
        )

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await asyncio.sleep(1)
        audit = await self.handlers.getAuditLogEntry(role.guild, type=discord.AuditLogAction.role_delete)
        if not audit or audit.user.bot:
            return
        return await self.handlers.sendLog(
            emoji=self.emojis().role.delete,
            type="Role delete",
            server=role.guild.id,
            colour=self.colours.red,
            data={
                "Role": f"{role.name}",
                "Permissions": f"[[View here]](https://discordapi.com/permissions.html#{role.permissions.value})",
                "Colour": f"#{str(hex(role.colour.value))[2:]}",
                "Position": f"{role.position}",
                "Show in member list": "Yes" if role.hoist else "No",
                "Mentionable by anyone": "Yes" if role.mentionable else "No",
                "Members who had this role": len(role.members),
                "ID": f"`{role.id}`",
                "Created": self.handlers.betterDelta(role.created_at.replace(tzinfo=None)),
                "Deleted": self.handlers.betterDelta(datetime.datetime.utcnow()),
                "Deleted by": f"{audit.user.name} ({audit.user.mention})"
            }
        )

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        await asyncio.sleep(1)
        audit = await self.handlers.getAuditLogEntry(after.guild, type=discord.AuditLogAction.role_update)
        if not audit or audit.user.bot:
            return
        changes = []
        dontShow = True
        if before.name != after.name:
            dontShow = False
            changes.append(f"**Name:** {before.name} -> {after.name}")
        if before.permissions != after.permissions:
            dontShow = False
            pre = "[[View here]](https://discordapi.com/permissions.html#"
            changes.append(f"**Permissions:** {pre}{before.permissions.value}) -> {pre}{after.permissions.value})")
        if before.colour != after.colour:
            dontShow = False
            changes.append(f"**Colour:** #{str(hex(before.colour.value))[2:]} -> #{str(hex(after.colour.value))[2:]}")
        if before.position != after.position:
            changes.append(f"**Position:** {before.position} -> {after.position}")
        if before.hoist != after.hoist:
            dontShow = False
            changes.append(f"**Show in member list:** {'Yes' if before.hoist else 'No'} -> {'Yes' if after.hoist else 'No'}")
        if before.mentionable != after.mentionable:
            dontShow = False
            changes.append(f"**Mentionable by anyone:** {'Yes' if before.mentionable else 'No'} -> {'Yes' if after.mentionable else 'No'}")
        if not dontShow and len(changes):
            return await self.handlers.sendLog(
                emoji=self.emojis().role.edit,
                type=f"Role edited",
                server=after.guild.id,
                colour=self.colours.yellow,
                data={
                    "Role": f"{after.name} ({after.mention})",
                    "Changes": "\n" + ("".join([f"> {change}\n" for change in changes])),
                    "Changed": self.handlers.betterDelta(datetime.datetime.utcnow()),
                    "Changed by": f"{audit.user.name} ({audit.user.mention})"
                }
            )

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        await asyncio.sleep(1)
        if len(after):
            g = after[0].guild
        elif len(before):
            g = before[0].guild
        else:
            return
        audit = await self.handlers.getAuditLogEntry(g, type=discord.AuditLogAction.emoji_update)
        if not audit or audit.user.bot:
            return
        added = []
        removed = []
        changed = []
        for b in before:
            for a in after:
                if b.id == a.id and b.name != a.name:
                    changed.append((b, a))
                    break
            if b.id not in [e.id for e in after]:
                removed.append(b)
        for a in after:
            if a.id not in [e.id for e in before]:
                added.append(a)
        data = {}
        if len(added):
            data["Added"] = " ".join([f"<{'a' if e.animated else ''}:a:{e.id}>" for e in added])
        if len(changed):
            data["Updated"] = "\n" + ("\n".join([f"> <{'a' if e[0].animated else ''}:a:{e[0].id}> `:{e[0].name}:` -> `:{e[1].name}:`" for e in changed]))
        if len(removed):
            data["Removed"] = " ".join([f"`:{e.name}:`" for e in removed])
        if not len(added) and not len(changed) and not len(removed):
            return
        data["Changed"] = self.handlers.betterDelta(datetime.datetime.utcnow())
        data["Changed by"] = f"{audit.user.name} ({audit.user.mention})"

        return await self.handlers.sendLog(
            emoji=self.emojis()("guild.emojis"),
            type=f"Emojis updated",
            server=g.id,
            colour=self.colours.yellow,
            data=data
        )


def setup(bot):
    bot.add_cog(Guild(bot))
