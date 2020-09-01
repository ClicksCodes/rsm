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


class Logs(commands.Cog):
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
            json.dump(f"{guild.id}: {template}", open(f"data/core.json", "w+"), indent=2)
            entry = self.data[str(guild.id)]
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

    @commands.group(aliases=["config"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def settings(self, ctx: commands.Context):
        """Shows all settings"""
        entry = self.data.get(str(ctx.guild.id))
        desc = []
        for event in events:
            ev = events[event]
            desc.append(f"{ev[2]} {ev[1]} | {emojis['tick'] if event in entry['toLog'] else emojis['cross']}")
        descs = []
        descx = ''
        for x in range(0, len(entry['toLog'])):
            if x % 14 == 0:
                if descx != '': descs.append(descx)
                descx = ''
            descx += f"{desc[x]}\n"
        descs.append(descx)
        for x in range(0, len(descs)):
            message = discord.Embed(
                title=f"{'Here is what you are logging:' if x == 0 else ''}",
                description=f"{'[You can edit your guild settings here](https://rsm.clicksminuteper.net/dashboard)' if x == 0 else ''}\n{descs[x]}",
                color=colours['create']
            )
            await ctx.channel.send(embed=message)

    @settings.command(name="ignore")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def ignore(self, ctx: commands.Context, things: commands.Greedy[typing.Union[discord.Member, discord.TextChannel, discord.Role]]):
        """[write docstring here]"""
        channels, members, roles = [], [], []
        for thing in things:
            if isinstance(thing, (discord.TextChannel)):
                channels.append(thing.id)
            elif isinstance(thing, (discord.Member)):
                members.append(thing.id)
            elif isinstance(thing, (discord.Role)):
                roles.append(thing.id)
        await ctx.send(f"{channels, members, roles}")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage): return await ctx.send(f"Sorry, but you need to use this command in a server so I know what data to read!")
        else:
            try: await ctx.send(f"```py\n{traceback.format_exc()}\n```")
            except: await ctx.send(error)
            raise error


def setup(bot):
    bot.add_cog(Logs(bot))