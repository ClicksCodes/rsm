import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus

from cogs.consts import *

class InfoCommands(commands.Cog):
    @commands.command(aliases=["help"])
    async def info(self, ctx: commands.Context):
        page = 0
        descriptions = [
            f"**Commands** - {emojis['PunWarn']} - {emojis['about']} - {emojis['support']}\n\n"
            f"{emojis['rsm']           } `m!info       ` Shows all commands and info.\n"
            f"{emojis['settings']      } `m!settings   ` Shows your servers log settings.\n"
            f"{emojis['PunWarn']       } `m!punish     ` Punishes a user.\n"
            f"{emojis['mod_update']    } `m!server     ` Shows all information about your server.\n"
            f"{emojis['role_create']   } `m!role [Role]` With `Text`: Shows information about a role.\n"
            f"{emojis['role_create']   } `m!role [@]   ` With `Mention`: Lets you edit or view a users roles.\n"
            f"{emojis['channel_create']} `m!viewas [@] ` Shows the channels that [@] can see.\n",

            f"{emojis['commands']} - **Moderation** - {emojis['about']} - {emojis['support']}\n\n"
            f"{emojis['PunWarn']     } `m!warn    [*@] [*T] ` Warns [@] for reason [T].\n"
          # f"{emojis['PunMute']     } `m!mute    [*@] [*T] ` Mutes [@] for time [T].\n"
          # f"{emojis['PunVoiceMute']} `m!warn    [*@] [*T] ` Mutes [@] in voice channels for time [T].\n"
            f"{emojis['PunHistory']  } `m!clear   [*@] [*N] ` Clears [N] messages from [@].\n"
            f"{emojis['PunKick']     } `m!kick    [*@] [*T] ` Kicks [@] for reason [T].\n"
            f"{emojis['PunSoftBan']  } `m!softban [*@] [*T] ` Soft bans [@] for reason [T].\n"
            f"{emojis['PunBan']      } `m!ban     [*@] [*T] ` Bans [@] for reason [T].\n"
            f"{emojis['purge']       } `m!purge        [*N] ` Deletes [N] messages in the channel.\n",

            f"{emojis['commands']} - {emojis['PunWarn']} - **About** - {emojis['support']}\n\n"
            f"RSM by [ClicksMinutePer](https://clicksminuteper.net)\n"
            f"Designed to make moderation easier.",

            f"{emojis['commands']} - {emojis['PunWarn']} - {emojis['about']} - **Support**\n\n"
            f"For support, visit the [ClicksMinutePer Support](https://clicksminuteper.net/contact-us.html) page."
        ]

        m = await ctx.send(embed=discord.Embed(title="Loading"))

        for _ in range(0,25):
            emb = discord.Embed (
                title=emojis["rsm"] + " RSM",
                description=descriptions[page],
                color=colours["create"]
            )
            emb.set_footer(text="[@] = Mention | [T] = Text | [N] = Number | [* ] = Optional")
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
        emb.set_footer(text="[@] = Mention | [T] = Text | [N] = Number | [* ] = Optional")
        await m.clear_reactions()
        await m.edit(embed=emb)

def setup(bot):
    bot.add_cog(InfoCommands(bot))