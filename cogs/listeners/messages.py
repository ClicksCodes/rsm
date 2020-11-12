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


class Messages(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open("./data/core.json") as rfile: self.data = json.load(rfile)
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10.0))
    
    def cog_unload(self): 
        with open("./data/core.json", "w") as wfile: json.dump(self.data, wfile, indent=2)
        self.bot.loop.create_task(self.session.close())

    def is_logging(self, guild: discord.Guild, *, channel = None, member: discord.Member = None, eventname):
        if eventname not in events.keys():  # invalid event name
            return bool(NotLogging(eventname, "Event Name is not in registered events.", cog=self, guild=guild))
        if not guild:  # in DMs
            return bool(NotLogging(eventname, "Event occurred in DMs, thus has no targeted channel.", cog=self, guild=guild))
        if not self.data.get(str(guild.id)):
            return bool(NotLogging(eventname, "The guild where this event occured has not registered.", cog=self, guild=guild))
        
        try: entry = self.data[str(guild.id)]
        except: 
            # json.dump(f"{guild.id}: {template}", open(f"data/core.json", "w+"), indent=2)
            # entry = self.data[str(guild.id)]
            pass
        if member:
            if member.bot and entry["ignoreBots"] is True:
                return bool(NotLogging(eventname, f"You are ignoring bots.", cog=self, guild=guild))
            if member.id in entry["ignoredMembers"]:
                return bool(NotLogging(eventname, f"Member \"{member}\" is being ignored.", cog=self, guild=guild))
            if member == self.bot.user:
                return bool(NotLogging(eventname, f"Not logging bot actions", cog=self, guild=guild))
            
        if channel:
            if channel.id in entry["ignoredChannels"]:
                return bool(NotLogging(eventname, f"Channel \"{channel}\" is being ignored.", cog=self, guild=guild))
            if channel.id == entry["logChannel"]:
                return bool(NotLogging(eventname, f"This is the log channel.", cog=self, guild=guild))
        if eventname.lower() not in entry["toLog"]:
            return bool(NotLogging(eventname, f"Guild is ignoring event \"{eventname}\".", cog=self, guild=guild))
        return True
        
    def get_log(self, guild: discord.Guild): 
        return self.bot.get_channel(self.data[str(guild.id)]["logChannel"])

    async def vbl(self, guild, e: NotLogging):
        """VerboseLog: Log NotLogging events if verbose is enabled"""
        if not self.data[str(guild.id)]["verbose"]: return False
        # print(f"Not logging event {e.etype}:\n> {e.reason}\n\n> {e.details}")
        return True 
    
    async def log(self, logType:str, guild:int, occurredAt:int, content:dict):
        try: data = json.load(open(f"data/guilds/{guild}.json", 'r'))
        except Exception as e: data = {}
        logID = len(data)
        data[str(logID)] = {"logType": logType, "occurredAt": occurredAt, "content": content}
        try: json.dump(data, open(f"data/guilds/{guild}.json", "w+"), indent=2)
        except Exception as e: print(e)
    

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        guild = message.guild
        if message.mention_everyone and self.is_logging(guild, channel=message.channel, member=message.author, eventname="everyone_here"):
            log = self.get_log(message.guild)
            sent = humanize.naturaltime(message.created_at)
            edited = humanize.naturaltime(message.edited_at) if message.edited_at else "Never"
            e = discord.Embed(
                title=emojis['everyone_ping'] + f" {'Here' if '@here' in message.content else 'Everyone'} pinged",
                description=f"{('```' + discord.utils.escape_markdown(shorten(message.clean_content, 2042)) + '```')}"
                            f"**Where:** {message.channel.mention}\n"
                            f"**Sent:** {sent}\n"
                            f"**Edited:** {edited}\n"
                            f"**By:** {message.author.mention}",
                color=events["everyone_here"][0],
                timestamp=datetime.utcnow()
            )
            if len(message.attachments):
                v = ""
                for a in message.attachments: v += f"[{a.filename}]({a.proxy_url})\n"
                e.add_field(name="Attachments:", value=v, inline=False)
            await log.send(embed=e)
            return await self.log(
                logType="everyonePing", 
                occurredAt=round(time.time()),
                guild=message.guild.id,
                content={
                    "username": message.author.id, 
                    "messageContent": str(discord.utils.escape_markdown(message.content)),
                    "mentions": len(message.mentions), 
                    "occurredIn": message.channel.id, 
                    "sent": sent.capitalize(), 
                    "edited": edited.capitalize(), 
                    "attachments": [a.proxy_url for a in message.attachments]
                }
            )

        if len(message.role_mentions):
            log = self.get_log(message.guild)
            sent = humanize.naturaltime(message.created_at)
            edited = humanize.naturaltime(message.edited_at) if message.edited_at else "Never"
            e = discord.Embed(
                title=emojis['role_ping'] + f" Role pinged",
                description=f"{('```' + discord.utils.escape_markdown(shorten(message.clean_content, 2042)) + '```')}"
                            f"**Where:** {message.channel.mention}\n"
                            f"**Sent:** {sent}\n"
                            f"**Edited:** {edited}\n"
                            f"**By:** {message.author.mention}",
                color=events["roles"][0],
                timestamp=datetime.utcnow()
            )
            if len(message.attachments):
                v = ""
                for a in message.attachments: v += f"[{a.filename}]({a.proxy_url})\n"
                e.add_field(name="Attachments:", value=v, inline=False)
            await log.send(embed=e)      
            return await self.log(
                logType="rolePing", 
                occurredAt=round(time.time()),
                guild=message.guild.id,
                content={
                    "username": message.author.id, 
                    "messageContent": str(discord.utils.escape_markdown(message.content)),
                    "mentions": len(message.mentions), 
                    "occurredIn": message.channel.id, 
                    "sent": sent.capitalize(), 
                    "edited": edited.capitalize(), 
                    "attachments": [a.proxy_url for a in message.attachments]
                }
            )
        if len(message.mentions) > 4:
            sent = humanize.naturaltime(message.created_at)
            edited = humanize.naturaltime(message.edited_at) if message.edited_at else "Never"
            log = self.get_log(message.guild)
            e = discord.Embed(
                title=emojis['everyone_ping'] + f" Mass mention",
                description=f"{('```' + discord.utils.escape_markdown(shorten(message.clean_content, 2042)) + '```')}"
                            f"**Where:** {message.channel.mention}\n"
                            f"**Sent:** {sent}\n"
                            f"**Edited:** {edited}\n"
                            f"**By:** {message.author.mention}",
                color=events["mass_mention"][0],
                timestamp=datetime.utcnow()
            )
            if len(message.attachments):
                v = ""
                for a in message.attachments: v += f"[{a.filename}]({a.proxy_url})\n"
                e.add_field(name="Attachments:", value=v, inline=False)
            await log.send(embed=e)
            return await self.log(
                logType="massPing", 
                occurredAt=round(time.time()),
                guild=message.guild.id,
                content={
                    "username": message.author.id, 
                    "messageContent": str(discord.utils.escape_markdown(message.content)),
                    "mentions": len(message.mentions), 
                    "occurredIn": message.channel.id, 
                    "sent": sent.capitalize(), 
                    "edited": edited.capitalize(), 
                    "attachments": [a.proxy_url for a in message.attachments]
                }
            )
        
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not self.is_logging(guild=message.guild, channel=message.channel, member=message.author, eventname="message_delete"): return
        else:
            log = self.get_log(message.guild)
            sent = humanize.naturaltime(message.created_at)
            edited = humanize.naturaltime(message.edited_at) if message.edited_at else "Never"
            e = discord.Embed(
                title=emojis['delete'] + " Message Deleted",
                description=f"{f'**Content:** ```{shorten(discord.utils.escape_markdown(message.clean_content), 1024)}```' if len(message.clean_content) > 0 else ''}\n"
                            f"**Sent By:** {message.author.mention}\n"
                            f"**Mentions:** {len(message.mentions)}\n"
                            f"**Sent In:** {message.channel.mention}\n"
                            f"**Sent:** {sent.capitalize()}\n"
                            f"**Edited:** {edited.capitalize()}\n",
                color=events["message_delete"][0],
                timestamp=datetime.utcnow()
            )
            if len(message.attachments):
                v = ""
                for a in message.attachments: v += f"[{a.filename}]({a.proxy_url})\n"
                e.add_field(name="Attachments:", value=v, inline=False)
            await log.send(embed=e)
            return await self.log(
                logType="messageDelete", 
                occurredAt=round(time.time()),
                guild=message.guild.id,
                content={
                    "username": message.author.id, 
                    "messageContent": str(discord.utils.escape_markdown(message.content)),
                    "mentions": len(message.mentions), 
                    "occurredIn": message.channel.id, 
                    "sent": sent.capitalize(), 
                    "edited": edited.capitalize(), 
                    "attachments": [a.proxy_url for a in message.attachments]
                }
            )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content: return
        message = after
        if not self.is_logging(message.guild, channel=message.channel, member=message.author, eventname="message_edit"): return
        else:
            log = self.get_log(message.guild)
            sent = humanize.naturaltime(message.created_at)
            edited = humanize.naturaltime(message.edited_at) if message.edited_at else "Never"
            e = discord.Embed(
                title=emojis["edit"] + " Message Edited",
                description=f"**Before:** {('```' + shorten(discord.utils.escape_markdown(before.clean_content), 500) + '```') if len(before.clean_content) > 0 else ''}\n"
                            f"**After:** {('```' + shorten(discord.utils.escape_markdown(after.clean_content), 500) + '```') if len(after.clean_content) > 0 else ''}\n"
                            f"**Sent By:** {message.author.mention}\n"
                            f"**Sent In:** {message.channel.mention}\n"
                            f"**Sent:** {sent.capitalize()}\n"
                            f"**Edited:** {edited.capitalize()}\n"
                            f"[Jump to message]({after.jump_url})",
                color=events["message_edit"][0],
                timestamp=datetime.utcnow(),
            )
            await log.send(embed=e)
            return await self.log(
                logType="messageEdit", 
                occurredAt=round(time.time()),
                guild=before.guild.id,
                content={
                    "username": message.author.id, 
                    "messageContent": str(discord.utils.escape_markdown(before.content)),
                    "messageContentAfter": str(discord.utils.escape_markdown(after.content)),
                    "mentions": len(before.mentions), 
                    "mentionsAfter": len(after.mentions), 
                    "occurredIn": message.channel.id, 
                    "sent": sent.capitalize(), 
                    "edited": edited.capitalize(), 
                    "attachments": [a.proxy_url for a in message.attachments]
                }
            )
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        message = messages[0]
        if not self.is_logging(message.guild, channel=message.channel, member=message.author, eventname="bulk_message_delete"): return
        else:
            log = self.get_log(message.guild)
            audit = await get_alog_entry(message.channel, type=discord.AuditLogAction.message_bulk_delete)

            m = ""
            for message in messages: m += f"{str(message.author)} {message.created_at}: {message.clean_content}\n\n"
            response = await self.session.post("https://mystb.in/documents", data=m)
            if response.status != 200:
                dump = "\n*Unable to get delted messages dump*"
            else:
                dump = f"\n[View deleted messages](https://mystb.in/{(await response.json())['key']})"

            e = discord.Embed(
                title=emojis["purge"] + " Messages Purged",
                description=f"**Messages Deleted:** {len(messages)}\n"
                            f"**In:** {message.channel.mention}\n"
                            f"**Deleted By:** {audit.user.mention}"
                            f"{dump}",
                color=events["message_delete"][0],
                timestamp=datetime.utcnow()
            )
            await log.send(embed=e)
            return await self.log(
                logType="messagePurge", 
                occurredAt=round(time.time()),
                guild=message.guild.id,
                content={
                    "username": audit.user.id,
                    "messageContent": f"https://mystb.in/{(await response.json())['key']}",
                    "occurredIn": message.channel.id, 
                    "amount": len(messages)
                }
            )

    @commands.Cog.listener()
    async def on_reaction_clear(self, message, reactions): 
        if not self.is_logging(message.guild, channel=message.channel, member=message.author, eventname="reaction_clear"): return
        else:
            log = self.get_log(message.guild)
            e = discord.Embed(
                title=emojis["reaction_clear"] + " Reactions Cleared",
                description=f"**Content:** {('```' + shorten(message.clean_content, 1024) + '```') if len(message.clean_content) > 0 else ''}\n"
                            f"**Sent By:** {message.author.mention}\n"
                            f"**Sent In:** {message.channel.mention}\n"
                            f"**Reactions:** {', '.join(str(m) for m in reactions)}\n"
                            f"[Jump to message]({message.jump_url})",
                color=events["reaction_clear"][0],
                timestamp=datetime.utcnow()
            )
            await log.send(embed=e)
            return await self.log(
                logType="messageReactionClear", 
                occurredAt=round(time.time()),
                guild=message.guild.id,
                content={
                    "username": message.author.id,
                    "messageContent": str(discord.utils.escape_markdown(message.content)),
                    "occurredIn": message.channel.id, 
                    "reactions": [str(m) for m in reactions]
                }
            )
    
    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel: discord.TextChannel, last_pin: datetime):
        if not self.is_logging(channel.guild, eventname="channel_pins_update"): return
        else:
            audit = await get_alog_entry(channel, type=discord.AuditLogAction.message_pin, check=lambda l: l.extra.channel.id == channel.id)
            if not audit:
                return NotLogging("on_guild_channel_pins_update", "No audit log entry.", cog=self, guild=channel.guild)
            else:
                message = await channel.fetch_message(audit.extra.message_id)
            e = discord.Embed(
                title=emojis["pinned"] + f" Pins Updated",
                description=f"**Message:** {discord.utils.escape_markdown(message.content)}\n"
                            f"**Message by:** {message.author.mention}\n"
                            f"**In:** {message.channel.mention}\n",
                color=events["channel_pins_update"][0],
                timestamp=datetime.utcnow()
            )
            log = self.get_log(message.guild)
            await log.send(embed=e)
            return await self.log(
                logType="pinsUpdate", 
                occurredAt=round(time.time()),
                guild=channel.guild.id,
                content={
                    "username": audit.user.id,
                    "messageBy": message.author.id,
                    "in": message.channel.id,
                    "content": str(discord.utils.escape_markdown(message.content))
                }
            )

def setup(bot):
    bot.add_cog(Messages(bot))