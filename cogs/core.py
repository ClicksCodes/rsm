import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, datetime

from datetime import datetime
from discord.ext import commands, tasks
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


class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_latency.start()
        self.loadingEmbed = loadingEmbed
    
    @tasks.loop(minutes=5.0)
    async def check_latency(self):
        print(f"\033[93m[P] {round(self.bot.latency,3)}\033[0m")
    
    @check_latency.before_loop
    async def before_check_latency(self):
        print(f"\033[93m[P] Starting latency test\033[0m")
        await self.bot.wait_until_ready()    
        print(f"\033[93m[P] Latency initialised\033[0m")


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

    @commands.command(aliases=["config"])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def settings(self, ctx: commands.Context):
        page = 0
        catList = [*categories]
        entry = None
        m = await ctx.send(embed=self.loadingEmbed)
        for emoji in [729762938411548694, 729762938843430952, 729064530310594601]: await m.add_reaction(ctx.bot.get_emoji(emoji))
        bn = '\n'
        with open(f"data/guilds/{ctx.guild.id}.json", 'r') as e:
            entry = json.load(e)["log_info"]["to_log"]
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
    
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def setlog(self, ctx, channel: typing.Optional[discord.TextChannel]):
        if not channel: 
            e = discord.Embed(
                title="<:ChannelDelete:729064529211686922> Something isn't right there",
                description=f"Please enter a valid channel to log in. This can be the ID or as {ctx.channel.mention}.",
                color=colours["delete"]
            )
            await ctx.send(embed=e)

            try: m = await ctx.bot.wait_for('message', timeout=60, check=lambda m : m.author.id == ctx.author.id and m.channel.id == ctx.channel.id)
            except asyncio.TimeoutError: return

            if len(m.channel_mentions): channel = m.channel_mentions[0]
            elif len(str(re.sub(r"[^0-9]*", "", str(m.content)))): 
                try:    channel = ctx.guild.get_channel(int(re.sub(r"[^0-9]*", "", str(m.content))))
                except: return
                if channel is None: return
            else: return
        try:
            with open(f"data/guilds/{ctx.guild.id}.json", 'r') as entry:
                entry = json.load(entry)
                entry["log_info"]["log_channel"] = int(channel.id)
            with open(f"data/guilds/{ctx.guild.id}.json", 'w') as f:
                json.dump(entry, f, indent=2)

            e = discord.Embed(
                title="<:ChannelCreate:729066924943737033> You set your log channel",
                description=f"Your log channel is now {channel.mention}",
                color=colours["create"]
            )
            await ctx.send(embed=e)
        except Exception as e: print(e)
    
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def ignore(self, ctx, toIgnore: commands.Greedy[typing.Union[discord.TextChannel, discord.Member, discord.Role]], bots: bool = True):
        try:
            members  = []
            roles    = []
            channels = []

            for thing in toIgnore:
                if   isinstance(thing, discord.Member      ): members.append(thing.id)
                elif isinstance(thing, discord.Role        ): roles.append(thing.id)
                elif isinstance(thing, discord.TextChannel ): channels.append(thing.id)

            with open(f"data/guilds/{ctx.guild.id}.json", 'r') as entry:
                entry = json.load(entry)
                entry["ignore_info"]["bots"] = bots
                entry["ignore_info"]["members"] = members
                entry["ignore_info"]["roles"] = roles
                entry["ignore_info"]["channels"] = channels
            with open(f"data/guilds/{ctx.guild.id}.json", 'w') as f:
                json.dump(entry, f, indent=2)

            e = discord.Embed(
                title="<:ChannelCreate:729066924943737033> You are now ignoring the following things:",
                description=f"**Roles:** {', '.join([ctx.guild.get_role(r).mention for r in roles])}\n**Member:** {', '.join([ctx.guild.get_member(r).mention for r in members])}\n**Channels:** {', '.join([ctx.guild.get_channel(r).mention for r in channels])}\n**Bots:** {'yes' if bots else 'no'}",
                color=colours["create"]
            )
            await ctx.send(embed=e)
        except Exception as e: print(e)

    @commands.command()
    async def stats(self, ctx):
        m = await ctx.send(embed=loadingEmbed)
        await m.edit(embed=discord.Embed(
            title="<:Graphs:752214059159650396> Stats",
            description=f"**Servers:** {len(self.bot.guilds)}\n"
                        f"**Members:** {len(self.bot.users)}\n"
                        f"**Emojis:** {len(self.bot.emojis)}\n"
                        f"**Ping:** {round(self.bot.latency*100)}ms\n",
            color=colours["create"]
        ))

def setup(bot):
    bot.add_cog(Core(bot))
