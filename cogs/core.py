import asyncio
import json
import random
import secrets
import time
import typing

import aiohttp
import config
import discord
import mongoengine
from config import config
from discord.ext import commands

from cogs.consts import *

deepAiKey = config.deepAIkey


class User(mongoengine.Document):
    code = mongoengine.StringField(required=True)
    user = mongoengine.StringField(required=True)
    role = mongoengine.StringField(required=True)
    role_name = mongoengine.StringField(required=True)
    guild = mongoengine.StringField(required=True)
    guild_name = mongoengine.StringField(required=True)
    guild_icon_url = mongoengine.StringField(required=True)
    guild_size = mongoengine.StringField(required=True)
    timestamp = time.time()

    meta = {'collection': 'rsmv-tokens'}


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
        return (
            f'Not logging event "{self.etype}" for reason: {self.reason}. See extra details in __repr__.'
            ""
        )

    def __repr__(self):
        return f"NotLogging(etype={self.etype} reason={self.reason} details={self.details})"

    def __bool__(self):
        return False


class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loadingEmbed = loadingEmbed

    def is_logging(
        self,
        guild: discord.Guild,
        *,
        eventname,
        channel=None,
        member: discord.Member = None,
    ):
        if not os.path.exists(f"data/guilds/{guild.id}.json"):
            return bool(
                NotLogging(eventname, "Guild not configured.", cog=self, guild=guild)
            )
        if eventname not in events.keys():
            return bool(
                NotLogging(
                    eventname,
                    "Event Name is not in registered events.",
                    cog=self,
                    guild=guild,
                )
            )
        if not guild:
            return bool(
                NotLogging(
                    eventname,
                    "Event occurred in DMs, thus has no targeted channel.",
                    cog=self,
                    guild=guild,
                )
            )

        try:
            with open(f"data/guilds/{guild.id}.json") as entry:
                entry = json.load(entry)
                if member:
                    if member.bot and entry["ignore_info"]["ignore_bots"] is True:
                        return bool(
                            NotLogging(
                                eventname,
                                f"You are ignoring bots.",
                                cog=self,
                                guild=guild,
                            )
                        )
                    if member.id in entry["ignore_info"]["members"]:
                        return bool(
                            NotLogging(
                                eventname,
                                f'Member "{member}" is being ignored.',
                                cog=self,
                                guild=guild,
                            )
                        )
                    if member == self.bot.user:
                        return bool(
                            NotLogging(
                                eventname,
                                f"Not logging bot actions",
                                cog=self,
                                guild=guild,
                            )
                        )

                if channel:
                    if channel.id in entry["ignore_info"]["channels"]:
                        return bool(
                            NotLogging(
                                eventname,
                                f'Channel "{channel}" is being ignored.',
                                cog=self,
                                guild=guild,
                            )
                        )
                    if channel.id == entry["log_info"]["log_channel"]:
                        return bool(
                            NotLogging(
                                eventname,
                                f"This is the log channel.",
                                cog=self,
                                guild=guild,
                            )
                        )
                if eventname.lower() not in entry["log_info"]["to_log"]:
                    return bool(
                        NotLogging(
                            eventname,
                            f'Guild is ignoring event "{eventname}".',
                            cog=self,
                            guild=guild,
                        )
                    )
                if not entry["enabled"]:
                    return bool(
                        NotLogging(
                            eventname,
                            f"This guild has disabled logs.",
                            cog=self,
                            guild=guild,
                        )
                    )
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
        try:
            with open(f"data/guilds/{guild}.json", "r") as entry:
                entry = json.load(entry)
                logID = len(entry) - 4
                entry[logID] = {
                    "logType": logType,
                    "occurredAt": occurredAt,
                    "content": content,
                }
            with open(f"data/guilds/{guild}.json", "w") as f:
                json.dump(entry, f, indent=2)
        except Exception as e:
            print(e)

    @commands.command(aliases=["config"])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def settings(self, ctx: commands.Context):
        page = 0
        catList = [*categories]
        entry = None
        m = await ctx.send(embed=self.loadingEmbed)
        for emoji in [
            729065958584614925,
            729066924943737033,
            729762939023917086,
            729066519337762878,
            784785219391193138,
        ]:
            await m.add_reaction(ctx.bot.get_emoji(emoji))
        bn = "\n"
        with open(f"data/guilds/{ctx.guild.id}.json", "r") as e:
            entry = json.load(e)["log_info"]["to_log"]
        for _ in range(0, 50):
            header = (
                " | ".join(
                    [
                        f"**{item}**" if catList[page] == item else categories[item]
                        for item in catList
                    ]
                )
                + "\nYou can edit your log settings [here](https://rsm.clcks.dev/dashboard)\n"
            )
            description = "".join(
                [
                    (
                        (
                            (emojis["tick"] if item in entry else emojis["cross"])
                            + " | "
                            + events[item][1]
                            + bn
                        )
                        if events[item][3] == catList[page]
                        else ""
                    )
                    for item in list(events.keys())
                ]
            )
            emb = discord.Embed(
                title=emojis["settings"] + " Settings",
                description=header + description,
                color=colours["create"],
            )
            await m.edit(embed=emb)

            reaction = None
            try:
                reaction = await ctx.bot.wait_for(
                    "reaction_add", timeout=60, check=lambda _, user: user == ctx.author
                )
            except asyncio.TimeoutError:
                break

            try:
                await m.remove_reaction(reaction[0].emoji, ctx.author)
            except Exception as e:
                print(e)

            if reaction is None:
                break
            elif reaction[0].emoji.name == "Left":
                page -= 1
            elif reaction[0].emoji.name == "Right":
                page += 1
            elif reaction[0].emoji.name == "MessageEdit":
                page = 0
            elif reaction[0].emoji.name == "ChannelCreate":
                page = 1
            elif reaction[0].emoji.name == "Settings":
                page = 2
            elif reaction[0].emoji.name == "MemberJoin":
                page = 3
            elif reaction[0].emoji.name == "Connect":
                page = 4

            page = min(len(catList) - 1, max(0, page))

        emb = discord.Embed(
            title=emojis["settings"] + " Settings",
            description=header + description,
            color=colours["delete"],
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
                color=colours["delete"],
            )
            await ctx.send(embed=e)

            try:
                m = await ctx.bot.wait_for(
                    "message",
                    timeout=60,
                    check=lambda m: m.author.id == ctx.author.id
                    and m.channel.id == ctx.channel.id,
                )
            except asyncio.TimeoutError:
                return

            if len(m.channel_mentions):
                channel = m.channel_mentions[0]
            elif len(str(re.sub(r"[^0-9]*", "", str(m.content)))):
                try:
                    channel = ctx.guild.get_channel(
                        int(re.sub(r"[^0-9]*", "", str(m.content)))
                    )
                except Exception as e:
                    return print(e)
                if channel is None:
                    return
            else:
                return
        try:
            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
                entry["log_info"]["log_channel"] = int(channel.id)
            with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                json.dump(entry, f, indent=2)

            e = discord.Embed(
                title="<:ChannelCreate:729066924943737033> You set your log channel",
                description=f"Your log channel is now {channel.mention}",
                color=colours["create"],
            )
            await ctx.send(embed=e)
        except Exception as e:
            print(e)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ignore(
        self,
        ctx,
        toIgnore: commands.Greedy[
            typing.Union[discord.TextChannel, discord.Member, discord.Role]
        ],
        bots: bool = True,
    ):
        try:
            members = []
            roles = []
            channels = []

            for thing in toIgnore:
                if isinstance(thing, discord.Member):
                    members.append(thing.id)
                elif isinstance(thing, discord.Role):
                    roles.append(thing.id)
                elif isinstance(thing, discord.TextChannel):
                    channels.append(thing.id)

            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
                entry["ignore_info"]["bots"] = bots
                entry["ignore_info"]["members"] = members
                entry["ignore_info"]["roles"] = roles
                entry["ignore_info"]["channels"] = channels
            with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                json.dump(entry, f, indent=2)

            e = discord.Embed(
                title="<:ChannelCreate:729066924943737033> You are now ignoring the following things:",
                description=f"**Roles:** {', '.join([ctx.guild.get_role(r).mention for r in roles])}\n"
                            f"**Member:** {', '.join([ctx.guild.get_member(r).mention for r in members])}\n"
                            f"**Channels:** {', '.join([ctx.guild.get_channel(r).mention for r in channels])}\n"
                            f"**Bots:** {'yes' if bots else 'no'}",
                color=colours["create"],
            )
            await ctx.send(embed=e)
        except Exception as e:
            print(e)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def ignored(self, ctx):
        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
            entry = json.load(entry)
            bots = entry["ignore_info"]["bots"]
            members = entry["ignore_info"]["members"]
            roles = entry["ignore_info"]["roles"]
            channels = entry["ignore_info"]["channels"]
        e = discord.Embed(
            title="<:ChannelCreate:729066924943737033> You are ignoring the following things:",
            description=f"**Roles:** {', '.join([ctx.guild.get_role(r).mention for r in roles])}\n"
                        f"**Member:** {', '.join([ctx.guild.get_member(r).mention for r in members])}\n"
                        f"**Channels:** {', '.join([ctx.guild.get_channel(r).mention for r in channels])}\n"
                        f"**Bots:** {'yes' if bots else 'no'}",
            color=colours["create"],
        )
        await ctx.send(embed=e)

    @commands.command()
    async def stats(self, ctx):
        m = await ctx.send(embed=loadingEmbed)
        await m.edit(
            embed=discord.Embed(
                title="<:Graphs:752214059159650396> Stats",
                description=f"**Servers:** {len(self.bot.guilds)}\n"
                f"**Members:** {len(self.bot.users)}\n"
                f"**Emojis:** {len(self.bot.emojis)}\n"
                f"**Ping:** {round(self.bot.latency*1000)}ms\n",
                color=colours["create"],
            )
        )

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx):
        await ctx.send(
            embed=discord.Embed(
                title=f"{emojis['PunMute']} Prefix",
                description=f"Your bot prefix is: `{ctx.prefix}`"
                + (
                    f"\nYou can use `{ctx.prefix}setprefix` to change your prefix"
                    if ctx.author.guild_permissions.manage_guild
                    else ""
                ),
                color=colours["create"],
            )
        )

    @commands.command()
    @commands.guild_only()
    async def setprefix(self, ctx, prefix: typing.Optional[str]):
        w = False
        try:
            if not ctx.author.guild_permissions.manage_guild:
                await ctx.send(
                    embed=discord.Embed(
                        title=f"{emojis['PunMute']} Looks like you don't have permissions",
                        description="You need the `manage_server` permission to change the servers prefix.",
                        color=colours["delete"],
                    )
                )
        except Exception as e:
            return print(e)
        if not prefix:
            m = await ctx.send(
                embed=discord.Embed(
                    title=f"{emojis['PunMute']} What prefix would you like to use?",
                    description=f"Please enter the prefix you would like to use.\nReact {emojis['cross']} to clear your custom prefix",
                    color=colours["create"],
                )
            )
            await m.add_reaction(self.bot.get_emoji(729064530310594601))
            try:
                done, _ = await asyncio.wait(
                    [
                        ctx.bot.wait_for(
                            "message",
                            timeout=120,
                            check=lambda message: message.author == ctx.author,
                        ),
                        ctx.bot.wait_for(
                            "reaction_add",
                            timeout=120,
                            check=lambda _, user: user == ctx.author,
                        ),
                    ],
                    return_when=asyncio.FIRST_COMPLETED,
                )
            except asyncio.TimeoutError:
                await m.edit(
                    embed=discord.Embed(
                        title=f"{emojis['PunMute']} What prefix would you like to use?",
                        description=f"Please enter the prefix you would like to use.\nReact {emojis['cross']} to clear your custom prefix",
                        color=colours["create"],
                    )
                )
            await m.delete()
            response = done.pop().result()
            if isinstance(response, discord.message.Message):
                prefix = msg.content
                if len(prefix) != len(msg.content):
                    w = True
                await msg.delete()
            else:
                prefix = False
        if prefix:
            if len(prefix) > 5:
                w = True
            prefix = prefix[:5]
            if "`" in prefix:
                await ctx.send(
                    embed=discord.Embed(
                        title=f"{emojis['PunMute']} Prefix",
                        description=f"You cannot use ` in your prefix.",
                        color=colours["delete"],
                    )
                )
            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
                entry["prefix"] = prefix
        else:
            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
                entry["prefix"] = False
        with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
            json.dump(entry, f, indent=2)
        await ctx.send(
            embed=discord.Embed(
                title=f"{emojis['PunMute']} Prefix",
                description=f"Your bot prefix is now: `{prefix if prefix else 'm!'}`"
                + ("\nWe had to shorten your prefix to 5 characters." if w else ""),
                color=colours["create"],
            )
        )

    @commands.command()
    @commands.guild_only()
    async def verify(self, ctx):
        with open(f"data/guilds/{ctx.guild.id}.json", "r") as e:
            try:
                roleid = json.load(e)["verify_role"]
            except KeyError:
                return await ctx.send(
                    embed=discord.Embed(
                        title=f"{emojis['cross']} Not set up",
                        description=f"You do not have a verify role set. You can use `{ctx.prefix}setverify` to choose the role assigned on verification.",
                        color=colours["delete"],
                    )
                )
        if roleid in [r.id for r in ctx.author.roles]:
            return await ctx.send(
                embed=discord.Embed(
                    title=f"{emojis['cross']} You are already verified",
                    description=f"You already have the verified role, and cannot get it again.",
                    color=colours["delete"],
                )
            )
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
        try:
            with open(f"data/guilds/{ctx.guild.id}.json") as entry:
                entry = json.load(entry)
        except FileNotFoundError:
            pass
        if "nsfw" in entry:
            if not entry["nsfw"]:
                m = await ctx.send(embed=discord.Embed(
                    title="Please wait",
                    description="We are just checking that your profile picture is safe for work",
                    color=colours["edit"]
                ))
                reason = None
                confidence = "80"
                page = requests.get(ctx.author.avatar_url)
                f_name = f"{random.randint(0,9999999999999999)}.png"
                with open(f_name, "wb") as f:
                    f.write(page.content)
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://api.deepai.org/api/nsfw-detector",
                        data={"image": page.url},
                        headers={"api-key": deepAiKey},
                    ) as r:
                        try:
                            resp = await r.json()
                            if len(resp['output']['detections']):
                                nsfw = True
                            else:
                                nsfw = False
                            try:
                                score = resp['output']['nsfw_score'] * 100
                            except Exception as e:
                                print(e)
                            if "Exposed" in [x['name'] if float(x['confidence']) > 75 else "" for x in resp['output']['detections']]:
                                nsfw = True
                            if int(score) > int(confidence):
                                nsfw = True
                            else:
                                nsfw = False
                        except Exception as e:
                            print(e)
                try:
                    os.remove(f_name)
                except Exception as e:
                    print(e)
                await m.delete()
                if nsfw:
                    backn = "\n"
                    if "staff" in entry["log_info"]:
                        backn = "\n"
                        await self.bot.get_channel(entry["log_info"]["staff"]).send(embed=discord.Embed(
                            title="NSFW profile picture",
                            description=f"User {ctx.author.mention} ({ctx.author.display_name}, {ctx.author.id}) had an NSFW profile picture when verifying. [View here]({ctx.author.avatar_url})\n\n"
                                        f"{backn.join([(r['name'] + ' Confidence: ' + str(round(float(r['confidence'])*100, 2)) + '%') for r in resp['output']['detections']])}\n\n"
                                        f"Overall confidence: {round(float(resp['output']['nsfw_score'])*100)}%",
                            color=colours["delete"]
                        ))
                    return await ctx.author.send(embed=discord.Embed(
                        title="NSFW profile picture detected",
                        description=f"Your profile picture was flagged when you verified in {ctx.guild.name}, as NSFW protection is enabled",
                        color=colours["delete"]
                    ).set_footer(text="No NSFW filter is 100% accurate, but yours was flagged. If it is not NSFW, you do not need to worry - Just let the moderators you were flagged"))
        roleid = None
        with open(f"data/guilds/{ctx.guild.id}.json", "r") as e:
            try:
                roleid = json.load(e)["verify_role"]
            except KeyError:
                return await ctx.send(
                    embed=discord.Embed(
                        title=f"{emojis['cross']} Not set up",
                        description=f"You do not have a verify role set. You can use `{ctx.prefix}setverify` to choose the role assigned on verification.",
                        color=colours["delete"],
                    )
                )
        if roleid in [r.id for r in ctx.author.roles]:
            return await ctx.send(
                embed=discord.Embed(
                    title=f"{emojis['cross']} You are already verified",
                    description=f"You already have the verified role, and cannot get it again.",
                    color=colours["delete"],
                )
            )
        try:
            mongoengine.connect(
                'rsm',
                host=config.mongoUrl
            )
            code = secrets.token_urlsafe(16)
            entry = User(
                code=str(code),
                user=str(ctx.author.id),
                role=str(roleid),
                role_name=str(ctx.guild.get_role(roleid).name),
                guild=str(ctx.guild.id),
                guild_name=str(ctx.guild.name),
                guild_icon_url=str(ctx.guild.icon_url),
                guild_size=str(len(ctx.guild.members))
            ).save()
        except Exception as e:
            print(e)
            return await ctx.channel.send(
                embed=discord.Embed(
                    title=f"{emojis['cross']} Verify",
                    description=f"Our database appears to be down, and could not connect",
                    color=colours["delete"],
                ), delete_after=10
            )
        try:
            await ctx.author.send(
                embed=discord.Embed(
                    title=f"{emojis['tick']} Verify",
                    description=f"In order to verify yourself in {ctx.guild.name}, you need to go [here](https://clicksminuteper.net/rsmv?code={code}) and complete the CAPTCHA.",
                    color=colours["create"],
                )
            )
        except Exception as e:
            print(e)
            await ctx.channel.send(
                embed=discord.Embed(
                    title=f"{emojis['cross']} Verify",
                    description=f"Your DMs are disabled - We need to DM your code in order to keep verification secure. Please enable them and try again.",
                    color=colours["delete"],
                ), delete_after=10
            )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def setverify(self, ctx, c: typing.Optional[discord.Role]):
        if not c:
            return await ctx.send(
                embed=discord.Embed(
                    title=f"{emojis['join']} You need to enter a role",
                    description=f"Type `{ctx.prefix}setverify`, followed by the role a user should get when they successfully verify. This is normally something like `member`.",
                    color=colours["delete"],
                )
            )
        if c.guild.id == ctx.guild.id and not c.managed:
            m = await ctx.send(embed=loadingEmbed)
            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
                entry["verify_role"] = c.id
            with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                json.dump(entry, f, indent=2)
            return await m.edit(
                embed=discord.Embed(
                    title=f"{emojis['join']} Your verify role was set",
                    description=f"People can now type `{ctx.prefix}verify` to get the {c.mention} role.",
                    color=colours["create"],
                )
            )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def resetprefix(self, ctx):
        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
            entry = json.load(entry)
            del entry["prefix"]
        with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
            json.dump(entry, f, indent=2)
        return await ctx.send(embed=discord.Embed(
            title="Your prefix has been reset - It is now m!",
            color=colours["edit"]
        ))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def resetauto(self, ctx):
        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
            entry = json.load(entry)
            try:
                entry["wordfilter"] = {"ignore": {"roles": [], "members": [], "channels": []}, "banned": [], "soft": []}
            except KeyError:
                pass
            try:
                entry["nsfw"] = True
            except KeyError:
                pass
            try:
                del entry["verifyrole"]
            except KeyError:
                pass
            try:
                entry["welcome"] = {"message": {},"role": None}
            except KeyError:
                pass
            try:
                entry["invite"] = {"enabled": False, "whitelist": {"members": [], "channels": [], "roles": []}}
            except KeyError:
                pass
            try:
                entry["images"] = {"toosmall": True}
            except KeyError:
                pass
        with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
            json.dump(entry, f, indent=2)
        return await ctx.send(embed=discord.Embed(
            title="All your automations have been reset",
            color=colours["edit"]
        ))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def resetfilter(self, ctx):
        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
            entry = json.load(entry)
            entry["wordfilter"]["banned"] = []
            entry["wordfilter"]["soft"] = []
        with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
            json.dump(entry, f, indent=2)
        return await ctx.send(embed=discord.Embed(
            title="All your banned words have been reset",
            color=colours["edit"]
        ))


def setup(bot):
    bot.add_cog(Core(bot))
