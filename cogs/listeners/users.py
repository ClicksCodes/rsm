import discord
import json
import humanize
import os
import aiohttp
import os
import time
import re

from datetime import datetime
from discord.ext import commands

from cogs.consts import *


class NotLogging:
    def __init__(self, etype, reason, details="No Further Info", *, cog, guild):
        self.etype = etype
        self.reason = reason
        self.details = details
        if cog and guild:
            cog.bot.loop.create_task(cog.vbl(guild, self))
        else:
            self.cog = None
            self.guild = None

    def __str__(self):
        return f"Not logging event \"{self.etype}\" for reason: {self.reason}. See extra details in __repr__."""

    def __repr__(self):
        return f"NotLogging(etype={self.etype} reason={self.reason} details={self.details})"

    def __bool__(self):
        return False


async def get_alog_entry(ctx, *, type: discord.AuditLogAction, check=None):
    """Retrieves the first matching audit log entry for the specified type.

    If you provide a check it MUST take an auditLogEntry as its only argument."""
    if not ctx.guild.me.guild_permissions.view_audit_log:
        raise commands.BotMissingPermissions("view_audit_log")
    async for log in ctx.guild.audit_logs(action=type):
        if check:
            if check(log):
                return log
            else:
                continue
        else:
            return log
    else:
        return None


class Users(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10.0))

    def tohex(self, i):
        return hex(i).split('x')[-1]

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    def checkWith(self, entry, user, name):
        if "wordfilter" in entry:
            if user.id not in entry["wordfilter"]["ignore"]["members"]:
                for role in user.roles:
                    if role.id in entry["wordfilter"]["ignore"]["roles"]:
                        return
                for word in [x.group().lower() for x in re.finditer( r'[a-zA-Z]+', str(name))]:
                    if word in entry["wordfilter"]["soft"]:
                        return True
                for word in entry["wordfilter"]["banned"]:
                    if word in name:
                        return True

    def is_logging(self, guild: discord.Guild, *, channel=None, member: discord.Member = None, eventname):
        if not os.path.exists(f'data/guilds/{guild.id}.json'):
            return bool(NotLogging(eventname, "Guild not configured.", cog=self, guild=guild))
        if not guild:
            return bool(NotLogging(eventname, "Event occurred in DMs, thus has no targeted channel.", cog=self, guild=guild))

        try:
            with open(f"data/guilds/{guild.id}.json") as entry:
                entry = json.load(entry)
                if member:
                    if member.bot and entry["ignore_info"]["ignore_bots"] is True:
                        bool(NotLogging(eventname, f"You are ignoring bots.", cog=self, guild=guild))
                    if member.id in entry["ignore_info"]["members"]:
                        return bool(NotLogging(eventname, f"Member \"{member}\" is being ignored.", cog=self, guild=guild))
                    if member == self.bot.user:
                        return bool(NotLogging(eventname, f"Not logging bot actions", cog=self, guild=guild))

                if channel:
                    if channel.id in entry["ignore_info"]["channels"]:
                        return bool(NotLogging(eventname, f"Channel \"{channel}\" is being ignored.", cog=self, guild=guild))
                    if channel.id == entry["log_info"]["log_channel"]:
                        return bool(NotLogging(eventname, f"This is the log channel.", cog=self, guild=guild))
                if eventname.lower() not in entry["log_info"]["to_log"]:
                    return bool(NotLogging(eventname, f"Guild is ignoring event \"{eventname}\".", cog=self, guild=guild))
                if not entry["enabled"]:
                    return bool(NotLogging(eventname, f"This guild has disabled logs.", cog=self, guild=guild))
                return True
        except Exception as e:
            print(e)

    def get_log(self, guild: discord.Guild):
        with open(f"data/guilds/{guild.id}.json") as f:
            entry = json.load(f)
            return self.bot.get_channel(entry["log_info"]["log_channel"])

    async def vbl(self, guild, e: NotLogging):
        """VerboseLog: Log NotLogging events if verbose is enabled"""
        return True

    async def log(self, logType: str, guild: int, occurredAt: int, content: dict):
        pass
        # try:
        #     with open(f"data/guilds/{guild}.json", 'r') as entry:
        #         entry = json.load(entry)
        #         logID = len(entry)-4
        #         entry[logID] = {"logType": logType, "occurredAt": occurredAt, "content": content}
        #     with open(f"data/guilds/{guild}.json", 'w') as f:
        #         json.dump(entry, f, indent=2)
        #     try:
        #         json.loads(f"data/guilds/{guild}.json")
        #     except ValueError:
        #         with open(f"data/guilds/{guild}.json", 'w') as f:
        #             json.dump(entry, f, indent=2)
        # except Exception as e:
        #     print(e)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            with open(f"data/guilds/{member.guild.id}.json") as entry:
                entry = json.load(entry)
            if self.checkWith(entry, member, member.display_name):
                if "nameban" in entry:
                    if entry["nameban"] == "none":
                        pass
                    elif entry["nameban"] == "change":
                        await member.edit(nick="[!] Nickname broke rules")
                        await member.send(embed=discord.Embed(
                            title="Nickname did not follow rules",
                            description=f"You joined {member.guild.name}, but your name contained word(s) that aren't allowed. Please contact the moderators for more information",
                            color=colours["delete"]
                        ))
                    elif entry["nameban"] == "kick":
                        await member.send(embed=discord.Embed(
                            title="Nickname did not follow rules",
                            description=f"You joined {member.guild.name}, but your name contained word(s) that aren't allowed. You have been automatically kicked",
                            color=colours["delete"]
                        ))
                        await member.kick(reason="Nickname contained banned word")
                    elif entry["nameban"] == "ban":
                        await member.send(embed=discord.Embed(
                            title="Nickname did not follow rules",
                            description=f"You joined {member.guild.name}, but your name contained word(s) that aren't allowed. You have been automatically banned",
                            color=colours["delete"]
                        ))
                        await member.ban(reason="Nickname contained banned word")
        except FileNotFoundError:
            pass
        if not self.is_logging(member.guild, member=member, eventname="member_join"):
            return
        e = discord.Embed(
            title=(emojis["bot_join"] if member.bot else emojis["join"]) + f" Member Joined",
            description=f"**Name:** {member.mention}\n"
                        f"**Server member count:** {member.guild.member_count}\n"
                        f"**Mutual servers:** {len([x for x in self.bot.guilds if member in x.members])}\n"
                        f"**Account Created:** {humanize.naturaltime(datetime.utcnow()-member.created_at)}\n"
                        f"**ID:** `{member.id}`",
            color=events["member_join"][0],
            timestamp=datetime.utcnow()
        )
        log = self.get_log(member.guild)
        await log.send(embed=e)
        return await self.log(
            logType="memberJoin",
            occurredAt=round(time.time()),
            guild=member.guild.id,
            content={
                "username": member.id,
                "memberCount": member.guild.member_count,
                "mutuals": len([x for x in self.bot.guilds if member in x.members]),
                "created": humanize.naturaltime(datetime.utcnow()-member.created_at),
            }
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not self.is_logging(member.guild, member=member, eventname="member_leave"):
            return
        audit = await get_alog_entry(member.guild.roles[0], type=discord.AuditLogAction.ban)
        try:
            if not audit.user.id == member.id:
                return
        except AttributeError:
            pass
        e = discord.Embed(
            title=(emojis["bot_leave"] if member.bot else emojis["leave"]) + f" Member Left",
            description=f"**Name:** {member.name}\n"
                        f"**Server member count:** {member.guild.member_count}\n"
                        f"**Mutual servers:** {len([x for x in self.bot.guilds if member in x.members])}\n"
                        f"**Account Created:** {humanize.naturaltime(datetime.utcnow()-member.created_at)}\n"
                        f"**ID:** `{member.id}`\n"
                        f"**Joined the server:** {humanize.naturaltime(datetime.utcnow()-member.joined_at)}",
            color=events["member_leave"][0],
            timestamp=datetime.utcnow()
        )
        log = self.get_log(member.guild)
        await log.send(embed=e)
        return await self.log(
            logType="memberLeave",
            occurredAt=round(time.time()),
            guild=member.guild.id,
            content={
                "username": member.id,
                "memberCount": member.guild.member_count,
                "mutuals": len([x for x in self.bot.guilds if member in x.members]),
                "created": humanize.naturaltime(datetime.utcnow()-member.created_at),
                "joined": humanize.naturaltime(datetime.utcnow()-member.joined_at)
            }
        )

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member: discord.Member):
        if not self.is_logging(guild, member=member, eventname="member_ban"):
            return
        audit = await get_alog_entry(guild.roles[0], type=discord.AuditLogAction.ban)
        e = discord.Embed(
            title=emojis["ban"] + f" Member Banned",
            description=f"**Name:** {member.name}\n"
                        f"**Banned By:** {audit.user.mention}\n"
                        f"**Reason:** {audit.reason if audit.reason is not None else 'No reason provided'}",
            color=events["member_ban"][0],
            timestamp=datetime.utcnow()
        )
        log = self.get_log(guild)
        await log.send(embed=e)
        return await self.log(
            logType="memberBan",
            occurredAt=round(time.time()),
            guild=guild.id,
            content={
                "username": member.id,
                "bannedBy": audit.user.id,
                "reason": audit.reason if audit.reason is not None else 'No reason provided'
            }
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member: discord.Member):
        if not self.is_logging(guild, member=member, eventname="member_unban"):
            return
        audit = await get_alog_entry(guild.channels[0], type=discord.AuditLogAction.unban)
        e = discord.Embed(
            title=emojis["unban"] + f" Member Unbanned",
            description=f"**Name:** {member.name}\n"
                        f"**Unbanned By:** {audit.user.mention}",
            color=events["member_unban"][0],
            timestamp=datetime.utcnow()
        )
        log = self.get_log(guild)
        await log.send(embed=e)
        return await self.log(
            logType="memberUnban",
            occurredAt=round(time.time()),
            guild=guild.id,
            content={
                "username": member.id,
                "unbannedBy": audit.user.id
            }
        )

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not self.is_logging(after.guild, eventname="nickname_change"):
            return
        if before.nick == after.nick:
            return
        audit = await get_alog_entry(after, type=discord.AuditLogAction.member_update)
        if before.nick != after.nick and audit.user.id != self.bot.user.id:
            try:
                with open(f"data/guilds/{after.guild.id}.json") as entry:
                    entry = json.load(entry)
                if await self.checkWith(entry, after, after.nick):
                    await after.edit(nick=before.nick)
                    return
            except FileNotFoundError:
                pass
        e = discord.Embed(
            title=emojis["nickname_change"] + f" Nickname Changed",
            description=f"**User:** {after.mention}\n"
                        f"**Name before:** {before.display_name}\n"
                        f"**Now:** {after.display_name}\n"
                        f"**Changed by:** {audit.user.mention}",
            color=events["nickname_change"][0],
            timestamp=datetime.utcnow()
        )
        log = self.get_log(after.guild)
        await log.send(embed=e)
        return await self.log(
            logType="nickChange",
            occurredAt=round(time.time()),
            guild=before.guild.id,
            content={
                "username": audit.user.id,
                "nameBefore": before.display_name,
                "nameAfter": after.display_name,
                "user": after.id
            }
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self, m, before, after):
        if before.channel is None and after.channel is not None:
            if not self.is_logging(after.channel.guild, eventname="connect"):
                return
            e = discord.Embed(
                title=emojis["Connect"] + f" Joined voice channel",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {after.channel.name}",
                color=events["connect"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="connect",
                occurredAt=round(time.time()),
                guild=after.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )
        elif before.channel is not None and after.channel is None:
            if not self.is_logging(before.channel.guild, eventname="disconnect"):
                return
            e = discord.Embed(
                title=emojis["Leave"] + f" Left voice channel",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name}",
                color=events["disconnect"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(before.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="leave",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": before.channel.name
                }
            )
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            if not self.is_logging(after.channel.guild, eventname="move"):
                return
            e = discord.Embed(
                title=emojis["Change"] + f" Change voice channel",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name} > {after.channel.name}",
                color=events["move"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="disconnect",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )
        elif after.deaf and not before.deaf:
            if not self.is_logging(after.channel.guild, eventname="server_deafen"):
                return
            e = discord.Embed(
                title=emojis["Deafen"] + f" Server deafen",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name}",
                color=events["server_deafen"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="server_deafen",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )
        elif before.deaf and not after.deaf:
            if not self.is_logging(after.channel.guild, eventname="server_undeafen"):
                return
            e = discord.Embed(
                title=emojis["Undeafen"] + f" Server undeafen",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name}",
                color=events["server_undeafen"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="server_undeafen",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )
        elif after.mute and not before.mute:
            if not self.is_logging(after.channel.guild, eventname="server_mute"):
                return
            e = discord.Embed(
                title=emojis["Mute"] + f" Server mute",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name}",
                color=events["server_mute"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="server_mute",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )
        elif before.mute and not after.mute:
            if not self.is_logging(after.channel.guild, eventname="server_unmute"):
                return
            e = discord.Embed(
                title=emojis["Unmute"] + f" Server unmute",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name}",
                color=events["server_unmute"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="server_unmute",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )
        elif after.self_deaf and not before.self_deaf:
            if not self.is_logging(after.channel.guild, eventname="deafen"):
                return
            e = discord.Embed(
                title=emojis["Deafen"] + f" Deafen",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name}",
                color=events["deafen"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="deafen",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )
        elif before.self_deaf and not after.self_deaf:
            if not self.is_logging(after.channel.guild, eventname="undeafen"):
                return
            e = discord.Embed(
                title=emojis["Undeafen"] + f" Undeafen",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name}",
                color=events["undeafen"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="undeafen",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )
        elif after.self_mute and not before.self_mute:
            if not self.is_logging(after.channel.guild, eventname="mute"):
                return
            e = discord.Embed(
                title=emojis["Mute"] + f" Mute",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name}",
                color=events["mute"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="mute",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )
        elif before.self_mute and not after.self_mute:
            if not self.is_logging(after.channel.guild, eventname="unmute"):
                return
            e = discord.Embed(
                title=emojis["Unmute"] + f" Unmute",
                description=f"**User:** {m.mention}\n"
                            f"**Channel:** {before.channel.name}",
                color=events["unmute"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(after.channel.guild)
            await log.send(embed=e)
            return await self.log(
                logType="unmute",
                occurredAt=round(time.time()),
                guild=before.channel.guild.id,
                content={
                    "username": m.id,
                    "channel": after.channel.name
                }
            )


def setup(bot):
    bot.add_cog(Users(bot))
