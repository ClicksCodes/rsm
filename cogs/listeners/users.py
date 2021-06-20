import humanize
import discord
import datetime
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.handlers.sendLog(
            emoji=self.emojis().member.bot.join if member.bot else self.emojis().member.join,
            type=f"{'Bot' if member.bot else 'Member'} joined",
            server=member.guild.id,
            colour=self.colours.green,
            data={
                "Name": f"{member.name} ({member.mention})",
                "Joined": self.handlers.strf(member.joined_at),
                "Account created": self.handlers.betterDelta(member.created_at),
                "ID": f"`{member.id}`",
                "Server member count": len(member.guild.members)
            }
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        kick = await self.handlers.getAuditLogEntry(member.guild, type=discord.AuditLogAction.kick)
        ban = await self.handlers.getAuditLogEntry(member.guild, type=discord.AuditLogAction.ban)
        if not kick or not ban:
            return
        if datetime.datetime.utcnow() - datetime.timedelta(seconds=5) < kick.created_at < datetime.datetime.utcnow() + datetime.timedelta(seconds=5):
            await self.handlers.sendLog(
                emoji=self.emojis().member.kick,
                type=f"Member kicked",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Name": f"{member.name} ({member.mention})",
                    "Joined": self.handlers.betterDelta(member.joined_at),
                    "Kicked": self.handlers.strf(datetime.datetime.utcnow()),
                    "Kicked by": f"{kick.user.name} ({kick.user.mention})",
                    "Reason": f"\n> {kick.reason}",
                    "Time in server": humanize.naturaldelta(datetime.datetime.utcnow()-member.joined_at),
                    "Account created": self.handlers.betterDelta(member.created_at),
                    "ID": f"`{member.id}`",
                    "Server member count": len(member.guild.members)
                }
            )
        elif datetime.datetime.utcnow() - datetime.timedelta(seconds=5) < ban.created_at < datetime.datetime.utcnow() + datetime.timedelta(seconds=5):
            if ban.reason.startswith("RSM Softban"):
                return
            await self.handlers.sendLog(
                emoji=self.emojis().member.ban,
                type=f"Member banned",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Name": f"{member.name} ({member.mention})",
                    "Joined": self.handlers.betterDelta(member.joined_at),
                    "Banned": self.handlers.strf(datetime.datetime.utcnow()),
                    "Banned by": f"{ban.user.name} ({ban.user.mention})",
                    "Reason": f"\n> {kick.reason}",
                    "Time in server": humanize.naturaldelta(datetime.datetime.utcnow()-member.joined_at),
                    "Account created": self.handlers.betterDelta(member.created_at),
                    "ID": f"`{member.id}`",
                    "Server member count": len(member.guild.members)
                }
            )
        else:
            await self.handlers.sendLog(
                emoji=self.emojis().member.leave,
                type=f"Member left",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Name": f"{member.name} ({member.mention})",
                    "Joined": self.handlers.betterDelta(member.joined_at),
                    "Left": self.handlers.strf(datetime.datetime.utcnow()),
                    "Time in server": humanize.naturaldelta(datetime.datetime.utcnow()-member.joined_at),
                    "Account created": self.handlers.betterDelta(member.created_at),
                    "ID": f"`{member.id}`",
                    "Server member count": len(member.guild.members)
                }
            )

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        audit = await self.handlers.getAuditLogEntry(guild, type=discord.AuditLogAction.unban)
        if not audit:
            return
        if audit.reason:
            if audit.reason.startswith("RSM Softban"):
                return
        await self.handlers.sendLog(
            emoji=self.emojis().member.unban,
            type=f"Member unban",
            server=guild.id,
            colour=self.colours.green,
            data={
                "Name": f"{user.name} ({user.mention})",
                "Unbanned": self.handlers.strf(datetime.datetime.utcnow()),
                "Unbanned by": f"{audit.user.name} ({audit.user.mention})",
                "Reason": f"\n> {audit.reason}",
                "Account created": self.handlers.betterDelta(user.created_at),
                "ID": f"`{user.id}`"
            }
        )

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            audit = await self.handlers.getAuditLogEntry(after.guild, type=discord.AuditLogAction.member_update)
            if not audit:
                return
            await self.handlers.sendLog(
                emoji=self.emojis().member.nickname_change,
                type=f"Nickname changed",
                server=after.guild.id,
                colour=self.colours.yellow,
                data={
                    "User": f"{after.mention}",
                    "Name before": f"{before.nick if before.nick else '*No nickname set*'}",
                    "Name after": f"{after.nick if after.nick else '*No nickname set*'}",
                    "Changed by": f"{audit.user.name} ({audit.user.mention})",
                    "Changed": self.handlers.strf(datetime.datetime.utcnow()),
                    "ID": f"`{after.id}`"
                }
            )
        if before.roles != after.roles:
            audit = await self.handlers.getAuditLogEntry(after.guild, type=discord.AuditLogAction.member_role_update)
            if not audit or audit.user.bot:
                return
            added = []
            removed = []
            for role in before.roles:
                if role not in after.roles:
                    removed.append(role)
            for role in after.roles:
                if role not in before.roles:
                    added.append(role)

            if len(added) and not len(removed):
                await self.handlers.sendLog(
                    emoji=self.emojis().role.create,
                    type=f"Roles added",
                    server=after.guild.id,
                    colour=self.colours.green,
                    data={
                        "User": f"{after.name} ({after.mention})",
                        "Added by": f"{audit.user.name} ({audit.user.mention})",
                        "Added": self.handlers.strf(datetime.datetime.utcnow()),
                        "ID": f"`{after.id}`",
                        "Roles added": " ".join([r.mention for r in added])
                    }
                )
            elif not len(added) and len(removed):
                await self.handlers.sendLog(
                    emoji=self.emojis().role.delete,
                    type=f"Roles removed",
                    server=after.guild.id,
                    colour=self.colours.red,
                    data={
                        "User": f"{after.name} ({after.mention})",
                        "Removed by": f"{audit.user.name} ({audit.user.mention})",
                        "Removed": self.handlers.strf(datetime.datetime.utcnow()),
                        "ID": f"`{after.id}`",
                        "Roles removed": " ".join([r.mention for r in removed])
                    }
                )
            else:
                await self.handlers.sendLog(
                    emoji=self.emojis().role.edit,
                    type=f"Roles updated",
                    server=after.guild.id,
                    colour=self.colours.yellow,
                    data={
                        "User": f"{after.name} ({after.mention})",
                        "Changed by": f"{audit.user.name} ({audit.user.mention})",
                        "Changed": self.handlers.strf(datetime.datetime.utcnow()),
                        "ID": f"`{after.id}`",
                        "Roles added": " ".join([r.mention for r in added]),
                        "Roles removed": " ".join([r.mention for r in removed])
                    }
                )


def setup(bot):
    bot.add_cog(Logs(bot))
