import asyncio
import typing
import discord
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed


class Public(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    async def _userinfo(self, ctx, m, user):
        task = asyncio.create_task(self.handlers.reactionCollector(
            ctx,
            m,
            reactions=[
                "control.cross", "control.left", "control.right",
                "member.join", "role.create", "guild.settings",
                "role.messages", "member.bot.join", "channel.voice.create"
            ],
            collect=False
        ))
        page = 0
        while True:
            permList = dict(user.guild_permissions)
            page = max(0, min(page, 5))
            match page:
                case 0:
                    flags = []
                    if user.id in self.bot.owner_ids:
                        flags.append("rsm_developer")

                    role = self.bot.get_guild(684492926528651336).get_role(760896837866749972)
                    if user.id in [u.id for u in role.members]:
                        flags.append("clicks_developer")

                    for flag, val in user.public_flags:
                        if val:
                            flags.append(flag)

                    if user.bot:
                        flags.append("bot")

                    if user in ctx.guild.premium_subscribers:
                        flags.append("booster")

                    flagemojis = {
                        "rsm_developer": "**RSM Developer**",
                        "clicks_developer": "Clicks Developer",
                        "hypesquad_brilliance": "Hypesquad Brilliance",
                        "hypesquad_bravery": "Hypesquad Bravery",
                        "hypesquad_balance": "Hypesquad Balance",
                        "early_supporter": "Early Supporter",
                        "bug_hunter_1": "Bug Hunter level 1",
                        "bug_hunter_2": "Bug Hunter level 2",
                        "booster": "Server Booster",
                        "partner": "Partner",
                        "hypesquad": "Hypesquad Events",
                        "staff": "Discord Staff",
                        "verified_bot_developer": "Verified Bot Developer",
                        "bot": "Bot"
                    }

                    flagstring = ""
                    for flag in flags:
                        try:
                            flagstring += f"{getattr(self.emojis().badges, flag)} {flagemojis[flag]}\n"
                        except KeyError:
                            print(flag)

                    match user.status.name:
                        case "online":
                            if user.is_on_mobile:
                                status = f"{self.emojis().status.online} Online (Mobile)"
                            else:
                                status = f"{self.emojis().status.online} Online"
                        case "idle": status = f"{self.emojis().status.idle} Idle"
                        case "dnd": status = f"{self.emojis().status.dnd} Do not disturb"
                        case "offline": status = f"{self.emojis().status.offline} Offline"
                        case _: status = f"{self.emojis().status.offline} Unknown"
                    for activity in user.activities:
                        if isinstance(activity, discord.Streaming):
                            status += f"\n> {self.emojis().status.streaming} Streaming on {activity.platform}\n" + \
                                f"> [[Watch {activity.twitch_name}]]({activity.url})\n" + \
                                f"> **Stream:** {activity.name}\n" + \
                                f"> **Game:** {activity.game}"
                        elif activity.type.name == "custom":
                            status += f"\n> {activity.emoji if activity.emoji else ''} {activity.name if activity.name else ''}"
                        else:
                            status += f"\n> **{activity.type.name.capitalize()}** {activity.name}"

                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().member.join} User info",
                        description=f"{flagstring}\n"
                                    f"**ID:** `{user.id}`\n"
                                    f"**Mention:** {user.mention}\n"
                                    f"**Name:** {user.name}#{user.discriminator}\n"
                                    f"**Nickname:** {user.nick if user.nick else '*None set*'}\n"
                                    f"**Status:** {status}\n"
                                    f"**Joined Discord:** {self.handlers.betterDelta(user.created_at)}\n"
                                    f"**Joined this server:** {self.handlers.betterDelta(user.joined_at)}\n"
                                    f"**Join position:** {sum(m.joined_at < user.joined_at for m in ctx.guild.members if m.joined_at is not None)}\n",
                        colour=self.colours.green
                    ).set_thumbnail(url=user.avatar_url).set_footer(text="Bots cannot detect if a user has Nitro"))
                case 1:
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().member.join} User info",
                        description=f"**Name:** {user.name}#{user.discriminator}\n"
                                    f"**Mention:** {user.mention}\n"
                                    f"**Roles:** {len(user.roles)-1}\n" +
                                    ", ".join([r.mention for r in reversed(user.roles[1:])]),
                        colour=self.colours.green
                    ).set_thumbnail(url=user.avatar_url))
                case 2:
                    perms = [
                        "view_audit_log", ("view_guild_insights", "View server insights"), ("manage_guild", "Manage server"),
                        "manage_roles", "manage_channels", "manage_webhooks",
                        "manage_emojis", ("create_instant_invite", "Create invite")
                    ]
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().member.join} User info",
                        description=f"**Name:** {user.name}#{user.discriminator}\n"
                                    f"**Mention:** {user.mention}\n"
                                    f"**Server**\n"
                                    f"{self.handlers.genPerms(perms, permList)}",
                        colour=self.colours.green
                    ).set_thumbnail(url=user.avatar_url))
                case 3:
                    perms = [
                        "read_messages", "send_messages", ("send_tts_messages", "Send TTS messages"),
                        "manage_messages", "embed_links", "attach_files",
                        "read_message_history", ("mention_everyone", "Mention @everyone, @here and @roles"), ("external_emojis", "Use nitro emojis"),
                        "add_reactions"
                    ]
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().member.join} User info",
                        description=f"**Name:** {user.name}#{user.discriminator}\n"
                                    f"**Mention:** {user.mention}\n"
                                    f"**Messages**\n"
                                    f"{self.handlers.genPerms(perms, permList)}",
                        colour=self.colours.green
                    ).set_thumbnail(url=user.avatar_url))
                case 4:
                    perms = [
                        "kick_members", "ban_members",
                        "change_nickname", ("manage_nicknames", "Change other people's nicknames")
                    ]
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().member.join} User info",
                        description=f"**Name:** {user.name}#{user.discriminator}\n"
                                    f"**Mention:** {user.mention}\n"
                                    f"**Members**\n"
                                    f"{self.handlers.genPerms(perms, permList)}",
                        colour=self.colours.green
                    ).set_thumbnail(url=user.avatar_url))
                case 5:
                    perms = [
                        ("connect", "Join voice chats"), ("speak", "Talk in voice chats"), ("stream", "Stream in voice chats"),
                        ("mute_members", "Server mute members"), ("deafen_members", "Server deafen members"),
                        "move_members", ("use_voice_activation", "Use voice activity"), "priority_speaker"
                    ]
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().member.join} User info",
                        description=f"**Name:** {user.name}#{user.discriminator}\n"
                                    f"**Mention:** {user.mention}\n"
                                    f"**Voice**\n"
                                    f"{self.handlers.genPerms(perms, permList)}",
                        colour=self.colours.green
                    ).set_thumbnail(url=user.avatar_url))
            reaction = await self.handlers.reactionCollector(
                ctx,
                m,
                task=task
            )
            if isinstance(reaction, Failed):
                break
            match reaction.emoji.name:
                case "Left": page -= 1
                case "Right": page += 1
                case "MemberJoin": page = 0
                case "RoleCreate": page = 1
                case "ServerRole": page = 2
                case "MessagesRole": page = 3
                case "BotJoin": page = 4
                case "VoiceCreate": page = 5
                case _: break
        await asyncio.sleep(0.1)
        await m.clear_reactions()
        embed = m.embeds[0]
        embed.colour = self.colours.red
        await m.edit(embed=embed)

    async def _help(self, ctx, m, mobile):
        pass

    @commands.command(aliases=["userinfo", "whois"])
    @commands.guild_only()
    async def user(self, ctx, member: typing.Optional[discord.Member]):
        m = await ctx.send(embed=loading_embed)
        if not member:
            member = ctx.author
        await self._userinfo(ctx, m, member)

    @commands.command()
    async def help(self, ctx, mobile: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        await self._help(ctx, m, bool(mobile))

    @commands.command()
    async def info(self, ctx, arg: typing.Union[discord.Member, str]):
        m = await ctx.send(embed=loading_embed)
        if isinstance(arg, discord.Memebr) and ctx.guild:
            await self._userinfo(ctx, m, arg)
        else:
            await self._help(ctx, m, bool(arg))


def setup(bot):
    bot.add_cog(Public(bot))
