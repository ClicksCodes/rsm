import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, io

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus
from create_machine_utils.minidiscord import menus
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from cogs.consts import *

class GuildCommands(commands.Cog):
    @commands.command()
    @commands.guild_only()
    async def guild(self, ctx):
        g = ctx.guild
        n = '\n'
        async def GraphUser(ctx, m, g, final=False):
            g = ctx.guild
            n = '\n'

            joins_x_values = sorted(m.joined_at for m in g.members)
            plt.grid(True)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(joins_x_values, tuple(range(1, len(joins_x_values) + 1)), 'k', lw=2, label="Members in server")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d-%m-%Y"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=round(len(g.members)/10)))
            fig.autofmt_xdate()
            plt.title("Guild Members")
            plt.xlabel('Time (UTC)')
            plt.ylabel('Members')
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
                m = await m.edit(
                    embed=e
                )
                return await m.remove_reactions()
        
        async def GraphRoles(ctx, m, g, final=False):
            g = ctx.guild
            n = '\n'

            joins_x_values = sorted(m.created_at for m in g.roles)
            plt.grid(True)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(joins_x_values, tuple(range(1, len(joins_x_values) + 1)), 'k', lw=2, label="Roles in server")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d-%m-%Y"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
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
                m = await m.edit(
                    embed=e
                )
                return await m.remove_reactions()
        
        async def GraphChannels(ctx, m, g, final=False):
            g = ctx.guild
            n = '\n'

            joins_x_values = sorted(m.created_at for m in g.channels)
            plt.grid(True)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(joins_x_values, tuple(range(1, len(joins_x_values) + 1)), 'k', lw=2, label="Channels in server")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d-%m-%Y"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
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
                m = await m.edit(
                    embed=e
                )
                return await m.remove_reactions()
        
        async def GraphEmojis(ctx, m, g, final=False):
            g = ctx.guild
            n = '\n'

            joins_x_values = sorted(m.created_at for m in g.emojis)
            plt.grid(True)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(joins_x_values, tuple(range(1, len(joins_x_values) + 1)), 'k', lw=2, label="Emojis")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d-%m-%Y"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
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
                m = await m.edit(
                    embed=e
                )
                return await m.remove_reactions()

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
                            f"**ID:**: `{g.id}`{n}"
                            f"**Owner**: {g.owner.mention}{n}"
                            f"**2FA Required:** {emojis['tick'] if g.mfa_level else emojis['cross']}{n}"
                            f"**Verification Level:**: {str(g.verification_level).replace('_', ' ').capitalize()}{n}"
                            f"**Explicit Content Filter:** {'Nobody' if g.explicit_content_filter == 0 else 'Only members with no role' if g.explicit_content_filter == 1 else 'Everyone'}{n}"
                            f"**Default Notifications:** {'All messages' if g.default_notifications == discord.NotificationLevel.all_messages else 'Only mentions'}{n}"
                            f"**Nitro Boost Level:** {g.premium_tier}{n}"
                            f"**Channels:** {len(g.channels)}{n}"
                            f"**Categories:**: {len(g.categories)}{n}"
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
                m = await m.edit(
                    embed=e
                )
                return await m.remove_reactions()
            return m

        m = await ctx.send(embed=discord.Embed(title="Loading"))
        m = await genInfo(ctx, m, g)
        page = 1

        for x in range(0,25):
            if 729762939023917086 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729762939023917086))
            if 752214059159650396 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(752214059159650396))
            if 729064530310594601 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729064530310594601))
            if page == 1:
                if 729066519337762878 in [r.id for r in m.reactions]: await m.remove_reaction(ctx.bot.get_emoji(729066519337762878))
                if 729763053352124529 in [r.id for r in m.reactions]: await m.remove_reaction(ctx.bot.get_emoji(729763053352124529))
                if 729066924943737033 in [r.id for r in m.reactions]: await m.remove_reaction(ctx.bot.get_emoji(729066924943737033))
                if 729066518549233795 in [r.id for r in m.reactions]: await m.remove_reaction(ctx.bot.get_emoji(729066518549233795))
            if page > 1:
                if 729066519337762878 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729066519337762878))
                if 729763053352124529 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729763053352124529))
                if 729066924943737033 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729066924943737033))
                if 729066518549233795 not in [r.id for r in m.reactions]: await m.add_reaction(ctx.bot.get_emoji(729066518549233795))

            reaction = None
            try: reaction = await ctx.bot.wait_for('reaction_add', timeout=60, check=lambda _, user : user == ctx.author)
            except asyncio.TimeoutError: break

            try: await m.remove_reaction(reaction[0].emoji, ctx.author)
            except: pass

            if reaction == None: break
            elif reaction[0].emoji.name == "Settings":               page = 1
            elif reaction[0].emoji.name == "Graphs":                 page = 2
            elif reaction[0].emoji.name == "MemeberJoin":            page = 2
            elif reaction[0].emoji.name == "ServerModerationUpdate": page = 3
            elif reaction[0].emoji.name == "ChannelCreate":          page = 4
            elif reaction[0].emoji.name == "EmojisUpdate":           page = 5
            else: break
            
            if   page == 1: m = await genInfo(ctx, m, g)
            elif page == 2: m = await GraphUser(ctx, m, g)
            elif page == 3: m = await GraphRoles(ctx, m, g)
            elif page == 4: m = await GraphChannels(ctx, m, g)
            elif page == 5: m = await GraphEmojis(ctx, m, g)
            else: break

        if   page == 2: m = await GraphUser(ctx, m, g, True)
        elif page == 3: m = await GraphRoles(ctx, m, g, True)
        elif page == 4: m = await GraphChannels(ctx, m, g, True)
        elif page == 5: m = await GraphEmojis(ctx, m, g, True)
        else:           m = await genInfo(ctx, m, g, True)

def setup(bot):
    bot.add_cog(GuildCommands(bot))