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

    async def _help(self, ctx, m, mob):
        task = asyncio.create_task(self.handlers.reactionCollector(
            ctx,
            m,
            reactions=[
                "control.cross", "control.left", "control.right"
            ],
            collect=False
        ))
        n = "\n"
        p = ctx.prefix
        descriptions = [
            [
                f"{self.emojis().rsm.help               } `{p}info     [*T] {'' if mob else '|'} ` {n if mob else ''}Shows all commands and info. Give [T] for mobile.",
                f"{self.emojis().guild.graphs           } `{p}stats         {'' if mob else '|'} ` {n if mob else ''}Shows the bot statistics",
                f"{self.emojis().guild.settings         } `{p}settings      {'' if mob else '|'} ` {n if mob else ''}Shows your servers log settings.",
                f"{self.emojis().member.join            } `{p}user     [*@] {'' if mob else '|'} ` {n if mob else ''}Shows information about a user.",
                f"{self.emojis().mod.images.too_big     } `{p}avatar   [*@] {'' if mob else '|'} ` {n if mob else ''}Shows a users avatar.",
                f"{self.emojis().role.edit              } `{p}roleall  [*T] {'' if mob else '|'} ` {n if mob else ''}Role all humans or bots in the server. [T] to search",
                f"{self.emojis().guild.modmail.open     } `{p}suggest   [T] {'' if mob else '|'} ` {n if mob else ''}Sends [T] to the staff to add to the bot for voting.",
                f"{self.emojis().slowmode.on            } `{p}ping          {'' if mob else '|'} ` {n if mob else ''}Checks the bots ping time.",
                f"{self.emojis().guild.moderation_update} `{p}server        {'' if mob else '|'} ` {n if mob else ''}Shows all information about your server.",
                f"{self.emojis().channel.store.create   } `{p}tag      [*T] {'' if mob else '|'} ` {n if mob else ''}`{p}tag create/delete` `title text`, or `{p}tag title`",
                f"{self.emojis().role.create            } `{p}role      [R] {'' if mob else '|'} ` {n if mob else ''}With `Role`: Shows information about a role.",
                f"{self.emojis().role.edit              } `{p}role      [@] {'' if mob else '|'} ` {n if mob else ''}With `Mention`: Lets you edit or view a users roles.",
                f"{self.emojis().channel.text.create    } `{p}viewas    [@] {'' if mob else '|'} ` {n if mob else ''}Shows the channels that [@] can see.",
                f"{self.emojis().member.bot.join        } `{p}verify    [@] {'' if mob else '|'} ` {n if mob else ''}Lets users verify in your server.",
                f"{self.emojis().member.bot.join        } `{p}setverify [R] {'' if mob else '|'} ` {n if mob else ''}Sets the role given when you `{p}verify`. Name or ID.",
                f"{self.emojis().guild.modmail.archive  } `{p}mail          {'' if mob else '|'} ` {n if mob else ''}Creates a modmail ticket if set up."
            ],
            [
                f"{self.emojis().punish.mute         } `{p}prefix            {'' if mob else '|'} ` {n if mob else ''}Shows the bots prefix. Use @ if unknown.",
                f"{self.emojis().punish.mute         } `{p}setprefix     [T] {'' if mob else '|'} ` {n if mob else ''}Sets the bots prefix. You can always @ the bot.",
                f"{self.emojis().punish.warn         } `{p}warn    [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Warns [@] for reason [T].",
                f"{self.emojis().punish.clear_history} `{p}clear   [*@] [*N] {'' if mob else '|'} ` {n if mob else ''}Clears [N] messages from [@].",
                f"{self.emojis().punish.kick         } `{p}kick    [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Kicks [@] for reason [T].",
                f"{self.emojis().punish.soft_ban     } `{p}softban [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Soft bans [@] for reason [T].",
                f"{self.emojis().punish.ban          } `{p}ban     [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Bans [@] for reason [T].",
                f"{self.emojis().member.unban        } `{p}unban        [*@] {'' if mob else '|'} ` {n if mob else ''}Unbans [@].",
                f"{self.emojis().channel.purge       } `{p}purge        [*N] {'' if mob else '|'} ` {n if mob else ''}Deletes [N] messages in the channel.",
                f"{self.emojis().punish.soft_ban     } `{p}punish       [*@] {'' if mob else '|'} ` {n if mob else ''}Punishes a user.",
                f"{self.emojis().channel.text.create } `{p}setlog       [ C] {'' if mob else '|'} ` {n if mob else ''}Sets the servers log channel to [C].",
                f"{self.emojis().commands.ignore     } `{p}ignore     [*CR@] {'' if mob else '|'} ` {n if mob else ''}Stops logging users, roles and channels provided.",
                f"{self.emojis().commands.ignore     } `{p}ignored           {'' if mob else '|'} ` {n if mob else ''}Shows the ignored users, roles and channels.",
                f"{self.emojis().channel.text.delete } `{p}stafflog     [*C] {'' if mob else '|'} ` {n if mob else ''}Sets the staff log channel for reports and messages.",
                f"{self.emojis().webhook.create      } `{p}auto              {'' if mob else '|'} ` {n if mob else ''}Lets you edit your server automations.",
                f"{self.emojis().guild.modmail.close } `{p}modmail           {'' if mob else '|'} ` {n if mob else ''}Shows the setup for the mail command."
            ],
            [
                f"{self.emojis().slowmode.on  } `{p}slowmode [*N] {'' if mob else '|'} ` {n if mob else ''}Sets the channel slowmode to [N]. Toggles if [N] is not provided.",
                f"{self.emojis().commands.lock} `{p}lock     [*T] {'' if mob else '|'} ` {n if mob else ''}Locks the channel. Applies slowmode and stops messages being sent.",
                f"{self.emojis().commands.lock} `{p}unlock        {'' if mob else '|'} ` {n if mob else ''}Unlocks the channel. Slowmode is removed and messages can be sent.",
            ],
            [
                f"{self.emojis().control.cross} `{p}reset {'' if mob else '|'} ` {n if mob else ''}Reset any words that have been set to be automatically deleted.",
            ]
        ]
        page = 0
        x = 0
        headings = [
            f"{self.emojis().rsm.commands} Commands\n",
            f"{self.emojis().rsm.support} Moderation\n",
            f"{self.emojis().commands.lock} Emergency\n",
            f"{self.emojis().punish.warn} Failsafes\n"
        ]
        split = [[headings[x]]]
        for desc in descriptions:
            for command in desc:
                if len("\n".join([split[-1][-1]])) + len(command) > 2000 - 200:
                    split.append([headings[x]])
                split[-1].append(command)
            split[-1].append("[[Invite]](https://discord.com/api/oauth2/authorize?client_id=715989276382462053&permissions=121295465718&scope=bot%20applications.commands) | [[Support]](https://discord.gg/bPaNnxe)")
            x += 1
            if x == len(headings):
                break
            split.append([headings[x]])
        while True:
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().rsm.help} Help",
                description="\n".join([desc for desc in split[page]]),
                colour=self.colours.green
            ))
            reaction = await self.handlers.reactionCollector(ctx, m, task=task)
            if isinstance(reaction, Failed):
                break
            match reaction.emoji.name:
                case "Left": page -= 1
                case "Right": page += 1
                case _: break
            page = max(0, min(page, len(split)))
        if ctx.guild:
            await m.clear_reactions()
        embed = m.embeds[0]
        embed.colour = self.colours.red
        await m.edit(embed=embed)

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
    async def info(self, ctx, arg: typing.Union[discord.Member, str, None]):
        m = await ctx.send(embed=loading_embed)
        if isinstance(arg, discord.Member) and ctx.guild:
            await self._userinfo(ctx, m, arg)
        else:
            await self._help(ctx, m, bool(arg))


def setup(bot):
    bot.add_cog(Public(bot))
