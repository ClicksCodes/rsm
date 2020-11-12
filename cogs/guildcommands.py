import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, io, math

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus
from create_machine_utils.minidiscord import menus
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from re import findall

from cogs.consts import *

class GuildCommands(commands.Cog):
    @commands.command(aliases=["server"])
    @commands.guild_only()
    async def guild(self, ctx):
        g = ctx.guild
        n = '\n'        
        async def GraphRoles(ctx, m, g, final=False):
            g = ctx.guild
            n = '\n'

            joins_x_values = sorted(m.created_at for m in g.roles)
            plt.grid(True)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(joins_x_values, tuple(range(1, len(joins_x_values) + 1)), 'k', lw=2, label="Roles in server")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d-%m-%Y"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=round(len(ctx.guild.roles)/(len(ctx.guild.roles)/20))))
            fig.autofmt_xdate()
            plt.title("Guild Roles")
            plt.xlabel('Time (UTC)')
            plt.ylabel('Roles')
            plt.legend()
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            image = discord.File(buf, filename="growth.png")
            buf.close()
            plt.close()

            e=discord.Embed(
                title="Server stats",
                color=colours["create"] if not final else colours["delete"],
                image=discord.File(buf, "growth.png")
            )

            e.set_image(url="attachment://growth.png")
            if final == False:
                await m.delete()
                m = await ctx.send(
                    embed=e,
                    file=image
                )
                return m
            else:
                await m.edit(
                    embed=e
                )
                return await n.clear_reactions()
        
        async def GraphChannels(ctx, m, g, final=False):
            g = ctx.guild
            n = '\n'

            joins_x_values = sorted(m.created_at for m in g.channels)
            plt.grid(True)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(joins_x_values, tuple(range(1, len(joins_x_values) + 1)), 'k', lw=2, label="Channels in server")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d-%m-%Y"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=round(len(ctx.guild.channels)/(len(ctx.guild.channels)/20))))
            fig.autofmt_xdate()
            plt.title("Guild Channels")
            plt.xlabel('Time (UTC)')
            plt.ylabel('Channels')
            plt.legend()
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            image = discord.File(buf, filename="growth.png")
            buf.close()
            plt.close()

            e=discord.Embed(
                title="Server stats",
                color=colours["create"] if not final else colours["delete"],
                image=discord.File(buf, "growth.png")
            )

            e.set_image(url="attachment://growth.png")
            if final == False:
                await m.delete()
                m = await ctx.send(
                    embed=e,
                    file=image
                )
                return m
            else:
                await m.edit(
                    embed=e
                )
                return await n.clear_reactions()
        
        async def GraphEmojis(ctx, m, g, final=False):
            g = ctx.guild
            n = '\n'

            joins_x_values = sorted(m.created_at for m in g.emojis)
            plt.grid(True)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(joins_x_values, tuple(range(1, len(joins_x_values) + 1)), 'k', lw=2, label="Emojis")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d-%m-%Y"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=round(len(ctx.guild.emojis)/(len(ctx.guild.emojis)/20))))
            fig.autofmt_xdate()
            plt.title("Guild Emojis")
            plt.xlabel('Time (UTC)')
            plt.ylabel('Emojis')
            plt.legend()
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            image = discord.File(buf, filename="growth.png")
            buf.close()
            plt.close()

            e=discord.Embed(
                title="Server stats",
                color=colours["create"] if not final else colours["delete"],
                image=discord.File(buf, "growth.png")
            )

            e.set_image(url="attachment://growth.png")
            if final == False:
                await m.delete()
                m = await ctx.send(
                    embed=e,
                    file=image
                )
                return m
            else:
                await m.edit(
                    embed=e
                )
                return await m.clear_reactions()

        async def genInfo(ctx, m, g, final=False):
            g = ctx.guild
            n = '\n'
            flags = {
                "amsterdam":     ":flag_nl:", "brazil":      ":flag_br:", "dubai":       ":flag_ae:", "eu-central": ":flag_eu:",
                "eu-west":       ":flag_eu:", "europe":      ":flag_eu:", "frankfurt":   ":flag_de:", "hongkong":   ":flag_hk:",
                "india":         ":flag_in:", "japan":       ":flag_jp:", "london":      ":flag_gb:", "russia":     ":flag_ru:",
                "singapore":     ":flag_sg:", "southafrica": ":flag_za:", "south-korea": ":flag_kr:", "us_central": ":flag_us:",
                "us-east":       ":flag_us:", "us-south":    ":flag_us:", "us-west":     ":flag_us:", "sidney":     ":flag_au:",
                "vip-amsterdam": ":flag_nl:", "vip-us-east": ":flag_us:", "vip-us-west": ":flag_us:"
            }
            try: flag = flags[str(g.region)]
            except Exception as e: flag = ""; print(e)

            e=discord.Embed(
                title="Server stats",
                description=f"**Name:** {g.name}{n}"
                            f"**Region:** {flag} {str(g.region).replace('-', ' ').capitalize()}{n}"
                            f"**Emojis:** {len(g.emojis)}{n}"
                            f"**Icon:** [Discord.com](https://cdn.discordapp.com/icons/{g.id}/{g.icon}){n}"
                            f"**ID:** `{g.id}`{n}"
                            #f"**Owner:** {g.owner.mention}{n}"
                            f"**2FA Required:** {emojis['tick'] if g.mfa_level else emojis['cross']}{n}"
                            f"**Verification Level:** {str(g.verification_level).replace('_', ' ').capitalize()}{n}"
                            f"**Explicit Content Filter:** {'Nobody' if g.explicit_content_filter == 0 else 'Only members with no role' if g.explicit_content_filter == 1 else 'Everyone'}{n}"
                            f"**Default Notifications:** {'All messages' if g.default_notifications == discord.NotificationLevel.all_messages else 'Only mentions'}{n}"
                            f"**Nitro Boost Level:** {g.premium_tier}{n}"
                            f"**Channels:** {len(g.channels)-len(g.categories)}{n}"
                            f"**Categories:** {len(g.categories)}{n}"
                            f"**Roles:** {len(g.roles)}{n}"
                            f"**Members:** {g.member_count}{n}",

                color=colours["create"] if not final else colours["delete"]
            )
            if final == False:
                await m.delete()
                m = await ctx.send(
                    embed=e
                )
                return m
            else:
                await m.edit(
                    embed=e
                )
                return await m.clear_reactions()
            return m

        m = await ctx.send(embed=discord.Embed(title="Loading"))
        m = await genInfo(ctx, m, g)
        page = 1

        for x in range(0,25):
            if 729762939023917086 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729762939023917086))
            if 752214059159650396 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(752214059159650396))
            if 729064530310594601 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729064530310594601))
            if page == 1:
                if 729763053352124529 in [r.id for r in m.reactions]: await m.remove_reaction(ctx.bot.get_emoji(729763053352124529))
                if 729066924943737033 in [r.id for r in m.reactions]: await m.remove_reaction(ctx.bot.get_emoji(729066924943737033))
                if 729066518549233795 in [r.id for r in m.reactions]: await m.remove_reaction(ctx.bot.get_emoji(729066518549233795))
            if page > 1:
                if 729763053352124529 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729763053352124529))
                if 729066924943737033 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729066924943737033))
                if 729066518549233795 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729066518549233795))

            reaction = None
            try: reaction = await ctx.bot.wait_for('reaction_add', timeout=60, check=lambda r, user : r.message.id == m.id and user == ctx.author)
            except asyncio.TimeoutError: break

            try: await m.remove_reaction(reaction[0].emoji, ctx.author)
            except: pass

            if reaction == None: break
            elif reaction[0].emoji.name == "Settings":               page = 1
            elif reaction[0].emoji.name == "Graphs":                 page = 2
            elif reaction[0].emoji.name == "ServerModerationUpdate": page = 3
            elif reaction[0].emoji.name == "ChannelCreate":          page = 4
            elif reaction[0].emoji.name == "EmojisUpdate":           page = 5
            else: break
            
            if   page == 1: m = await genInfo(ctx, m, g)
            elif page == 2: m = await GraphRoles(ctx, m, g)
            elif page == 3: m = await GraphChannels(ctx, m, g)
            elif page == 4: m = await GraphEmojis(ctx, m, g)
            else: break

        if page == 2: m = await GraphRoles(ctx, m, g, True)
        elif page == 3: m = await GraphChannels(ctx, m, g, True)
        elif page == 4: m = await GraphEmojis(ctx, m, g, True)
        else:           m = await genInfo(ctx, m, g, True)
    
    @commands.command(aliases=["roles"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def role(self, ctx, *, r:typing.Union[discord.Role, discord.Member]):
        if type(r) == discord.Role:
            n = '\n'
            p = r.permissions
            def getBool(val):
                return (emojis['tick'] if val else emojis['cross'])

            perms = {
                "Server": [
                    f"**View audit logs:** {getBool(p.view_audit_log) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**View server insights:** {getBool(p.view_guild_insights) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Manage server:** {getBool(p.manage_guild) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Manage roles:** {getBool(p.manage_roles) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Manage channels:** {getBool(p.manage_channels) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Manage webhooks:** {getBool(p.manage_webhooks) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Manage emojis:** {getBool(p.manage_emojis) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Create instant invite:** {getBool(p.create_instant_invite) if not p.administrator else getBool(p.administrator)}{n}"
                ],
                "Members": [
                    f"**Kick members:** {getBool(p.kick_members) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Ban members:** {getBool(p.ban_members) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Change nickname:** {getBool(p.change_nickname) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Change other people's nicknames:** {getBool(p.manage_nicknames) if not p.administrator else getBool(p.administrator)}{n}"
                ],
                "Messages": [
                    f"**Read channels and see Voice channels:** {getBool(p.read_messages) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Send messages:** {getBool(p.read_messages) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Send TTS messages:** {getBool(p.send_tts_messages) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Manage messages:** {getBool(p.manage_messages) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Embed links:** {getBool(p.embed_links) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Attach files:** {getBool(p.attach_files) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Read message history:** {getBool(p.read_message_history) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Mention @everyone, @here and @roles:** {getBool(p.mention_everyone) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Use nitro emojis:** {getBool(p.use_external_emojis) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Add reactions:** {getBool(p.add_reactions) if not p.administrator else getBool(p.administrator)}{n}"
                ],
                "Voice": [
                    f"**Join voice channels:** {getBool(p.connect) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Talk in voice channels:** {getBool(p.speak) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Stream in voice channels:** {getBool(p.stream) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Server mute members:** {getBool(p.mute_members) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Server deafen members:** {getBool(p.deafen_members) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Move members between voice channels:** {getBool(p.move_members) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Use voice activity:** {getBool(p.use_voice_activation) if not p.administrator else getBool(p.administrator)}{n}",
                    f"**Priority speaker:** {getBool(p.priority_speaker) if not p.administrator else getBool(p.administrator)}{n}"
                ]
            }

            async def genInfo(ctx, m, final=False):
                await m.edit(embed=discord.Embed(
                    title="Role Info",
                    description=f"**ID:** `{r.id}`{n}"
                                f"**Name:** {r.name}{n}"
                                f"**Shown in member list:** {getBool(r.hoist)}{n}"
                                f"**Mentionable by anyone:** {getBool(r.mentionable)}{n}"
                                f'**Colour:** {("[#" + str(hex(r.colour.value))[2:] + "](https://apps.clicksminuteper.net/colours/" + str(hex(r.colour.value))[2:] + ")" + n) if r.colour.value > 0 else ("**Colour:** None" + n)}'
                                f"**Made:** {humanize.naturaldate(r.created_at)}{n}"
                                f"**People with this role:** {len(r.members)}",
                    color=colours["create"] if not final else colours["delete"]
                ))
                return
            
            async def genPage(ctx, m, page, final=False):
                await m.edit(embed=discord.Embed(
                    title="Role Info",
                    description=page + n + ''.join([thing for thing in perms[page]]),
                    color=colours["create"] if not final else colours["delete"]
                ))
                return m
            
            m = await ctx.send(embed=discord.Embed(title="Loading"))
            page = 0
            for re in [729762938411548694, 729762938843430952, 729064530310594601, 752570111256297496, 752570111063228507, 752570111373606942, 752570111281594509, 752570111088525354]: await m.add_reaction(ctx.bot.get_emoji(re))
            for _ in range(0, 50):
                page = min(4, max(0, page))
                
                pages = {1: "Server", 2: "Messages", 3: "Members", 4: "Voice"}
                if page == 0: m = await genInfo(ctx, m)
                else:         m = await genPage(ctx, m, pages[page])

                reaction = None
                try: reaction = await ctx.bot.wait_for('reaction_add', timeout=60, check=lambda r, user : r.message.id == m.id and user == ctx.author)
                except asyncio.TimeoutError: break

                try: await m.remove_reaction(reaction[0].emoji, ctx.author)
                except: pass
                reaction = reaction[0].emoji

                if   reaction.name == "Left":  page -= 1
                elif reaction.name == "Right": page += 1

                elif reaction.name == "GeneralRole":  page = 0
                elif reaction.name == "ServerRole":   page = 1
                elif reaction.name == "MessagesRole": page = 2
                elif reaction.name == "MembersRole":  page = 3
                elif reaction.name == "VoiceRole":    page = 4
                else: break
            
            pages = {1: "Server", 2: "Messages", 3: "Members", 4: "Voice"}
            if page == 0: m = await genInfo(ctx, m, True)
            else:         m = await genPage(ctx, m, pages[page], True)
            await m.clear_reactions()
        elif type(r) == discord.Member:
            bot = ctx.bot
            if len(ctx.guild.roles) == 0: await ctx.send(embed=discord.Embed(title="Your server has no roles", color=colours["delete"]))
            roles = r.roles
            groles = ctx.guild.roles
            groles.reverse()
            groleIDs = [r.id for r in groles]
            pages = math.ceil(len(groles)/10)
            page = 0

            numbers = {
                1: 753259025990418515,
                2: 753259024409034896,
                3: 753259024358703205,
                4: 753259024555835513,
                5: 753259024744579283,
                6: 753259024354639994,
                7: 753259024530800661,
                8: 753259024895574037,
                9: 753259024681533553,
                0: 753259024404840529
            }
            PILNumbers = {
                "True": {
                    0: 753312608378945648,
                    1: 753312608550912112,
                    2: 753312608513294366,
                    3: 753312608815284426,
                    4: 753312608735461457,
                    5: 753312608630604017,
                    6: 753312608656031806,
                    7: 753312608718815322,
                    8: 753312608790249646,
                    9: 753312608899170365
                },
                "False": {
                    0: 753312609075462246,
                    1: 753312608890650664,
                    2: 753312608680935446,
                    3: 753312609377320966,
                    4: 753312609255686223,
                    5: 753312609138376777,
                    6: 753312609465270412,
                    7: 753312609104822313,
                    8: 753312609477984319,
                    9: 753312609557545089
                }
            }
            tick = 753314339082993832
            cross = 753314339389309100

            m = await ctx.send(embed=discord.Embed(title="Loading"))
            for reaction in [729762938411548694, 729762938843430952, 729064530310594601]: await m.add_reaction(ctx.bot.get_emoji(reaction))
            reaction = None

            for _ in range(0, 50):
                rolesOnPage = (len(groles)%10 if page == pages-1 else 9)
                m = await ctx.channel.fetch_message(m.id)
                currentReactions = [(r.emoji.name if r.me else "") for r in m.reactions]
                reactions = [item for item in currentReactions if item != ""]

                for x in range(0, 10):
                    if (rolesOnPage <= x if page == pages-1 else rolesOnPage < x)  and (f"{x}_" in reactions): await m.clear_reaction(bot.get_emoji(numbers[x]))
                    if (rolesOnPage >= x) and (f"{x}_" not in reactions): await m.add_reaction(bot.get_emoji(numbers[x]))

                desc = f'Page {page+1} of {pages}\n'
                for x in range((page*10), (page*10)+(rolesOnPage+(0 if page == pages-1 else 1))): 
                    desc += f"{bot.get_emoji(tick if groles[x] in roles else cross)}{bot.get_emoji(PILNumbers[str(groles[x] in roles)][x%10])} {groles[x]}\n"
                await m.edit(embed=discord.Embed(title="Roles", description=desc, color=colours["create"]))

                try: await m.remove_reaction(reaction, ctx.author)
                except: pass

                out = None
                try: reaction = await ctx.bot.wait_for('reaction_add', timeout=60, check=lambda r, user : r.message.id == m.id and user == ctx.author)
                except asyncio.TimeoutError: break

                try: await m.remove_reaction(reaction[0].emoji, ctx.author)
                except: pass

                reaction = reaction[0].emoji

                if   reaction.name == "Left":  page -= 1
                elif reaction.name == "Right": page += 1
                elif reaction.name == "Cross": break
                else:
                    try: 
                        roleToChange = ctx.guild.get_role(groleIDs[(page*10)+int(reaction.name[:1])])
                        if       ctx.guild.me.top_role.position <= roleToChange.position: await ctx.send(embed=discord.Embed(title=f"{emojis['PunWarn']} I can't do that", description="I can't change that role", colour=colours["delete"]), delete_after=5)
                        elif     ctx.author.top_role.position   <= roleToChange.position: await ctx.send(embed=discord.Embed(title=f"{emojis['PunWarn']} You can't do that", description="You can't change that role", colour=colours["delete"]), delete_after=5)
                        elif     roleToChange.position          == 0:                     await ctx.send(embed=discord.Embed(title=f"{emojis['PunWarn']} You can't do that", description="You can't remove this role", colour=colours["delete"]), delete_after=5)
                        elif     roleToChange.managed:                                    await ctx.send(embed=discord.Embed(title=f"{emojis['PunWarn']} You can't do that", description="This role is for a bot", colour=colours["delete"]), delete_after=5)
                        elif not ctx.author.guild_permissions.manage_roles:               await ctx.send(embed=discord.Embed(title=f"{emojis['PunWarn']} Looks like you don't have permissions", description="You need the `manage_roles` permission to change roles.", colour=colours["delete"]), delete_after=5)
                        elif not ctx.guild.me.guild_permissions.manage_roles:             await ctx.send(embed=discord.Embed(title=f"{emojis['PunWarn']} Looks like I don't have permissions", description="I need the `manage_roles` permission to change roles.", colour=colours["delete"]), delete_after=5)
                        else: 
                            if roleToChange in r.roles: await r.remove_roles(roleToChange)
                            else: await r.add_roles(roleToChange)
                            r = await ctx.guild.fetch_member(r.id)
                            roles = r.roles
                            groles = ctx.guild.roles
                            groles.reverse()
                            groleIDs = [r.id for r in groles]
                    except Exception as e: print(e); break
            await m.edit(embed=discord.Embed(title="Roles", description=desc, color=colours["delete"]))
            await m.clear_reactions()

    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(
                title="I couldn't find that role", 
                description=f"Make sure it is capitalised correctly.\nYou can use the role ID to make sure that I can find it.", 
                color=colours["delete"]
            ))
    
    @commands.command(aliases=['viewas', 'serveras', 'serverfrom'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def viewfrom(self, ctx, m:typing.Optional[discord.Member]):
        tooMany = discord.Embed(
            title=f'{events["nsfw_update"][2]} You mentioned too many people there',
            description="You can only view from one person at a time.",
            color=colours["delete"]
        )
        noPing = discord.Embed(
            title=f"Who would you like to view the server from?",
            description="Please mention the user you'd like to see the server as.",
            color=colours["create"]
        )
        if not m: 
            m = await ctx.send(embed=noPing)
            msg = await ctx.bot.wait_for('message', timeout=60, check=lambda message : message.author == ctx.author)
            await msg.delete()
            await m.delete()
            if len(msg.mentions) != 1: return await ctx.send(embed=tooMany)
            else: m = msg.mentions[0]
        
        mess = await ctx.send(embed=discord.Embed(title="Loading"))

        server = {0: []}
        visible = {0: []}
        g = ctx.guild
        for cat in g.categories: server[cat] = []; visible[cat] = []
        for c in g.channels:       server[c.category if c.category else 0].append(c)

        for cat in server:
            for channel in server[cat]:
                if channel.type in [discord.ChannelType.news, discord.ChannelType.text, discord.ChannelType.voice]:
                    if (m.permissions_in(channel).read_messages) or (channel.type is discord.ChannelType.voice and m.permissions_in(channel).connect):
                        visible[cat].append(channel)
        
        desc = ""
        n = '\n'
        findescs, descs = [], []
        page, i = 0, 0

        visibleCopy = visible.copy()
        totalcats = set()
        for key, value in visibleCopy.items():
            if value != []: totalcats.add(key)
        for key in totalcats:
            del visibleCopy[key]

        for key, value in visible.items():
            if len(value) > 0: i += 1
            desc = ""
            if len(value) == 0: continue
            elif key == 0: desc += f"**Uncategorised:** {n}"
            else: desc += f"**{key.name}:** {n}"
            for item in value:
                desc += f"{emojis['vicon'] if item.type == discord.ChannelType.voice else emojis['cicon']}{item.name}{n}"

            e1 = discord.Embed(
                title=f"Channels {m.name} can see:",
                description=''.join(desc),
                color=colours["create"]
            )
            e2 = discord.Embed(
                title=f"Channels {m.name} can see:",
                description=''.join(desc),
                color=colours["delete"]
            )
            e2.set_footer(text=f"Category {i} of {len(totalcats)}")
            e1.set_footer(text=f"Category {i} of {len(totalcats)}")

            descs.append(e1)
            findescs.append(e2)

        for r in [729762938411548694, 729762938843430952, 729064530310594601]: await mess.add_reaction(ctx.bot.get_emoji(r))
        for _ in range(0, 50):
            await mess.edit(embed=descs[page])

            reaction = None
            try: reaction = await ctx.bot.wait_for('reaction_add', timeout=60, check=lambda r, user : r.message.id == mess.id and user == ctx.author)
            except asyncio.TimeoutError: break
            reaction = reaction[0].emoji

            if   reaction.name == "Left":  page -= 1
            elif reaction.name == "Right": page += 1
            else: break

            page = min(len(descs)-1, max(0, page))

            try: await mess.remove_reaction(reaction, ctx.author)
            except Exception as e: print(e)

        await mess.edit(embed=findescs[page])
        await mess.clear_reactions()

    @viewfrom.error
    async def viewfrom_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title="Looks like you don't have permissions", 
                description=f"Make sure you have the `manage_messages` permission to use this command.", 
                color=colours["delete"]
            ))
        else:
            print('\n'.join(['[x] ' + n for n in (str(error).split('\n'))]))

def setup(bot):
    bot.add_cog(GuildCommands(bot))