import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus

from cogs.consts import *

class InfoCommands(commands.Cog):
    @commands.Command
    async def info(self, ctx: commands.Context):
        page = 0
        descriptions = [
            f"**Commands** - {emojis['about']} - {emojis['support']}\n\n"
            f"{emojis['rsm']     } `info    ` Shows all commands and info.\n"
            f"{emojis['PunWarn'] } `punish  ` Punishes a user. Asks for punishment type.\n"
            f"{emojis['settings']} `settings` Shows what events your server is logging.\n",

            f"{emojis['commands']} - **About** - {emojis['support']}\n\n"
            f"RSM by [ClicksMinutePer](https://clicksminuteper.net)\n"
            f"Designed to make moderation easier.",

            f"{emojis['commands']} - {emojis['about']} - **Support**\n\n"
            f"For support, visit the [ClicksMinutePer Support](https://clicksminuteper.net/contact-us.html) page."
        ]

        m = await ctx.send(embed=discord.Embed(title="Loading"))

        for _ in range(0,25):
            emb = discord.Embed (
                title=emojis["rsm"] + " RSM",
                description=descriptions[page],
                color=colours["create"]
            )
            await m.edit(embed=emb)

            for emoji in [729762938411548694, 729762938843430952, 729064530310594601]: await m.add_reaction(ctx.bot.get_emoji(emoji))

            reaction = None
            try: reaction = await ctx.bot.wait_for('reaction_add', timeout=60, check=lambda _, user : user == ctx.author)
            except asyncio.TimeoutError: break

            try: await m.remove_reaction(reaction[0].emoji, ctx.author)
            except: pass

            if reaction == None: break
            elif reaction[0].emoji.name == "Left":  page -= 1
            elif reaction[0].emoji.name == "Right": page += 1
            else: break

            page = min(len(descriptions)-1, max(0, page))

        emb = discord.Embed (
            title=emojis["rsm"] + " RSM",
            description=descriptions[page],
            color=colours["delete"]
        )
        await m.clear_reactions()
        await m.edit(embed=emb)

def setup(bot):
    bot.add_cog(InfoCommands(bot))