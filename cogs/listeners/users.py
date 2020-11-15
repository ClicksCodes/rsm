import copy, discord, json, humanize, aiohttp, traceback, typing, time

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus

from cogs.consts import *

class NotLogging:
    def __init__(self, etype, reason, details="No Further Info", *, cog, guild):
        self.etype = etype
        self.reason = reason
        self.details = details
        # print(self.__repr__())
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

async def get_alog_entry(ctx, *, type: discord.AuditLogAction, check = None):
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
    
    def tohex(self, i): return hex(i).split('x')[-1]
    
    def cog_unload(self): 
        self.bot.loop.create_task(self.session.close())

    def is_logging(self, guild: discord.Guild, *, channel = None, member: discord.Member = None, eventname):
        if not os.path.exists(f'data/guilds/{guild.id}.json'): return bool(NotLogging(eventname, "Guild not configured.", cog=self, guild=guild))
        if eventname not in events.keys():                     return bool(NotLogging(eventname, "Event Name is not in registered events.", cog=self, guild=guild))
        if not guild:                                          return bool(NotLogging(eventname, "Event occurred in DMs, thus has no targeted channel.", cog=self, guild=guild))
        
        try:    
            with open(f"data/guilds/{guild.id}.json") as entry:
                entry = json.load(entry)
                if member:
                    if member.bot and entry["ignore_info"]["ignore_bots"] is True: return bool(NotLogging(eventname, f"You are ignoring bots.", cog=self, guild=guild))
                    if member.id in entry["ignore_info"]["members"]:               return bool(NotLogging(eventname, f"Member \"{member}\" is being ignored.", cog=self, guild=guild))
                    if member == self.bot.user:                                    return bool(NotLogging(eventname, f"Not logging bot actions", cog=self, guild=guild))
                    
                if channel:
                    if channel.id in entry["ignore_info"]["channels"]:   return bool(NotLogging(eventname, f"Channel \"{channel}\" is being ignored.", cog=self, guild=guild))
                    if channel.id == entry["log_info"]["log_channel"]:   return bool(NotLogging(eventname, f"This is the log channel.", cog=self, guild=guild))
                if eventname.lower() not in entry["log_info"]["to_log"]: return bool(NotLogging(eventname, f"Guild is ignoring event \"{eventname}\".", cog=self, guild=guild))
                if not entry["enabled"]:                                 return bool(NotLogging(eventname, f"This guild has disabled logs.", cog=self, guild=guild))
                return True
        except Exception as e: print(e)
        
    def get_log(self, guild: discord.Guild): 
        with open(f"data/guilds/{guild.id}.json") as f:
            entry =  json.load(f)
            return self.bot.get_channel(entry["log_info"]["log_channel"])

    async def vbl(self, guild, e: NotLogging):
        """VerboseLog: Log NotLogging events if verbose is enabled"""
        return True 
    
    async def log(self, logType:str, guild:int, occurredAt:int, content:dict):
        try:
            with open(f"data/guilds/{guild}.json", 'r') as entry:
                entry = json.load(entry)
                logID = len(entry)-4
                entry[logID] = {"logType": logType, "occurredAt": occurredAt, "content": content}
            with open(f"data/guilds/{guild}.json", 'w') as f:
                json.dump(entry, f, indent=2)
        except Exception as e: print(e)  
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):  # Later: Make custom welcome/leave messages?
        if not self.is_logging(member.guild, member=member, eventname="member_join"): return
        else:
            e = discord.Embed(
                title=(emojis["bot_join"] if member.bot else emojis["join"]) + f" Member Joined",
                description=f"**Name:** {member.mention}\n"
                            f"**Server member count:** {member.guild.member_count}\n"
                            f"**Mutual servers:** {len([x for x in self.bot.guilds if member in x.members])}\n"
                            f"**Account Created:** {humanize.naturaltime(member.created_at)}\n"
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
                    "created": humanize.naturaltime(member.created_at),
                }
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):  # Later: Make custom welcome/leave messages?
        if not self.is_logging(member.guild, member=member, eventname="member_leave"): return
        else:
            e = discord.Embed(
                title=(emojis["bot_leave"] if member.bot else emojis["leave"]) + f" Member Left",
                description=f"**Name:** {member.name}\n"
                            f"**Server member count:** {member.guild.member_count}\n"
                            f"**Mutual servers:** {len([x for x in self.bot.guilds if member in x.members])}\n"
                            f"**Account Created:** {humanize.naturaltime(member.created_at)}\n"
                            f"**ID:** `{member.id}`\n"
                            f"**Joined the server:** {humanize.naturaltime(member.joined_at)}",
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
                    "created": humanize.naturaltime(member.created_at),
                    "joined": humanize.naturaltime(member.joined_at)
                }
            )

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member: discord.Member):
        if not self.is_logging(member, member=member, eventname="member_ban"): return
        else:
            audit = await get_alog_entry(member, type=discord.AuditLogAction.ban)
            e = discord.Embed(
                title=emojis["ban"] + f" Member Banned",
                description=f"**Name:** {member.name}\n"
                            f"**Banned By:** {audit.user.mention}"
                            f"**Reason:** {audit.reason if audit.reason != None else 'No reason provided'}",
                color=events["member_ban"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(member.guild)
            await log.send(embed=e)
            return await self.log(
                logType="memberBan", 
                occurredAt=round(time.time()),
                guild=member.guild.id,
                content={
                    "username": member.id,
                    "bannedBy": audit.user.id,
                    "reason": audit.reason if audit.reason != None else 'No reason provided'
                }
            )

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member: discord.Member):
        if not self.is_logging(member, member=member, eventname="member_unban"): return
        else:
            audit = await get_alog_entry(member, type=discord.AuditLogAction.unban)
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
                guild=member.guild.id,
                content={
                    "username": member.id,
                    "unbannedBy": audit.user.id
                }
            )
    

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not self.is_logging(after.guild, eventname="nickname_change"): return
        elif before.nick == after.nick: return
        else:
            audit = await get_alog_entry(after, type=discord.AuditLogAction.member_update)
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
    
    async def cog_command_error(self, ctx, error):
        if isinstance(error, AttributeError): pass
        else: self.bot.get_channel(776418051003777034).send(embed=discord.Embed(title="Error", description=str(error), color=colours["delete"]))

def setup(bot):
    bot.add_cog(Users(bot))