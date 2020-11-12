import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

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
        with open("./data/template.json") as rfile:
            for guild in bot.guilds:
                if str(guild.id) not in self.data: self.data[str(guild.id)] = json.load(rfile)
    
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

    @commands.group(aliases=["config"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def settings(self, ctx: commands.Context):
        page = 0
        catList = [*categories]
        entry = self.data.get(str(ctx.guild.id))['toLog']
        m = await ctx.send(embed=discord.Embed(title="Loading"))
        for emoji in [729762938411548694, 729762938843430952, 729064530310594601]: await m.add_reaction(ctx.bot.get_emoji(emoji))
        bn = '\n'
        for x in range(0,50):
            if x == 0: 
                for emoji in [729065958584614925, 729066924943737033, 729762939023917086, 729066519337762878]: await m.add_reaction(ctx.bot.get_emoji(emoji))
            header = " | ".join([f"**{item}**" if catList[page] == item else categories[item] for item in catList]) + '\nYou can edit your log settings [here](https://rsm.clcks.dev/dashboard)\n'
            description = "".join([ (((emojis['tick'] if item in entry else emojis['cross']) + " | " + events[item][1] + bn) if events[item][3] == catList[page] else '') for item in list(events.keys())])
            emb = discord.Embed (
                title=emojis["settings"] + " Settings",
                description=header + description,
                color=colours["create"]
            )
            await m.edit(embed=emb)
            
            reaction = None
            try: reaction = await ctx.bot.wait_for('reaction_add', timeout=60, check=lambda _, user : user == ctx.author)
            except asyncio.TimeoutError: break

            try: await m.remove_reaction(reaction[0].emoji, ctx.author)
            except: pass

            if reaction == None: break
            elif reaction[0].emoji.name == "Left":          page -= 1
            elif reaction[0].emoji.name == "Right":         page += 1
            elif reaction[0].emoji.name == "MessageEdit":   page =  0
            elif reaction[0].emoji.name == "ChannelCreate": page =  1
            elif reaction[0].emoji.name == "Settings":      page =  2
            elif reaction[0].emoji.name == "MemberJoin":    page =  3
            else: break

            page = min(len(catList)-1, max(0, page))
        
        emb = discord.Embed (
            title=emojis["settings"] + " Settings",
            description=header + description,
            color=colours["delete"]
        )
        await m.clear_reactions()
        await m.edit(embed=emb)

    @settings.command(name="ignore")
    @commands.has_permissions(manage_guild=True)

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
        self.data[str(ctx.guild.id)]["ignoredChannels"] = channels # these 4 jsons dont work
        self.data[str(ctx.guild.id)]["ignoredRoles"] = roles # 2
        self.data[str(ctx.guild.id)]["ignoredMembers"] = members # 3
    
    @settings.command(name="log")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def log(self, ctx, channel: discord.TextChannel):
        try:
            e = discord.Embed(
                title="You set your log channel",
                description=f"Your log channel is now {channel.mention}"
            )
            await ctx.send(embed=e)
            self.data[str(ctx.guild.id)]["logChannel"] = channel.id # 4
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Logs(bot))