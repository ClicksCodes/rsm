import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus
from create_machine_utils.minidiscord import menus

from cogs.consts import *

class Commands(commands.Cog):
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def punish(self, ctx):
        m = None
        tooMany = discord.Embed(
            title=f'{events["nsfw_update"][2]} You mentioned too many people there',
            description="You can only punish one person at a time.",
            color=colours["edit"]
        )
        noPing = discord.Embed(
            title=f"Who do you want to punish?",
            description="Please mention the user you'd like to punish.",
            color=colours["create"]
        )
        if len(ctx.message.mentions) > 1: 
            return await ctx.send(embed=tooMany)
        elif len(ctx.message.mentions) < 1: 
            m = await ctx.send(embed=noPing)
            msg = await ctx.bot.wait_for('message', timeout=60)
            await msg.delete()
            if len(msg.mentions) != 1: return await ctx.send(embed=tooMany)
            else: member = msg.mentions[0]
        else: member = ctx.message.mentions[0]
        emojiids = {
            "PunWarn": [729764054897524768, "Warn"],
            "PunMute": [729764053865463840, "Mute"],
            "PunVoiceMute": [729764054855450697, "Voice Mute"],
            "PunHistory": [729764062270980096, "Delete message history"],
            "PunKick": [729764053794422896, "Kick"],
            "PunSoftBan": [729764053941223476, "Soft ban"],
            "PunBan": [729764053861400637, "Ban"],
            "Stop": [751161404442279966, "Cancel"]
        }

        e = discord.Embed (
            title=f'{events["nsfw_update"][2]} Punishing user *{member.name}*',
            description=('\n'.join( [f"{ctx.bot.get_emoji(int(emojiids[t][0]))} | {emojiids[t][1]}" for t in emojiids] )),
            color=colours["create"]
        )
        eTimed = discord.Embed (
            title=f'{events["nsfw_update"][2]} Punishing user *{member.name}*',
            description=('\n'.join( [f"{ctx.bot.get_emoji(int(emojiids[t][0]))} | {emojiids[t][1]}" for t in emojiids] )),
            color=colours["edit"]
        )
        eClosed = discord.Embed (
            title=f'{events["nsfw_update"][2]} Punishing user *{member.name}*',
            description=('\n'.join( [f"{ctx.bot.get_emoji(int(emojiids[t][0]))} | {emojiids[t][1]}" for t in emojiids] )),
            color=colours["delete"]
        )
        if m == None: m = await ctx.send(embed=e)
        else: await m.edit(embed=e)
        try:
            menu = menus.Menu(timeout=60)
            for emoji in emojiids: menu + ctx.bot.get_emoji(emojiids[emoji][0])
            o = await menu(ctx.bot, m, ctx.author)
            if o.name == "Stop": 
                await m.edit(embed=eClosed)
                return await m.clear_reactions()
            else: await ctx.send(o)
        except asyncio.TimeoutError:
            await m.edit(embed=eTimed)
            return await m.clear_reactions()

def setup(bot):
    bot.add_cog(Commands(bot))