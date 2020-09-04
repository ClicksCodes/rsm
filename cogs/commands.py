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
        def createEmbed(title, description, color=0x000000):
            return discord.Embed(
                title=title,
                description=description,
                color=color
            )
        async def reasonHandler(m, dict):
            await m.delete()
            m = await ctx.send(embed=createEmbed(dict["prompt"]["title"], dict["prompt"]["desc"] + "\n" + f"Select {emojis['tick']} to provide no reason or {emojis['cross']} to cancel", dict["prompt"]["col"]))
            for emoji in [729064531107774534, 729064530310594601]: await m.add_reaction(ctx.bot.get_emoji(emoji))
            try:
                done, _ = await asyncio.wait([
                    ctx.bot.wait_for('message', timeout=120, check=lambda message : message.author == ctx.author),
                    ctx.bot.wait_for('reaction_add', timeout=120, check=lambda _, user : user == ctx.author)
                ], return_when=asyncio.FIRST_COMPLETED)
            except Exception as e: print(e)

            try:
                reason = None
                response = done.pop().result()
                if type(response) == discord.message.Message:
                    reason = '\n' + str(response.content)
                    await response.delete()
                else:
                    if response[0].emoji.name == 'Tick': reason = False
                    if response[0].emoji.name == 'Cross': await m.edit(embed=createEmbed(dict["cancel"]["title"], dict["cancel"]["desc"], dict["cancel"]["col"]), delete_after=10)
                if reason is not None:
                    return reason, m
                await m.clear_reactions()
            except Exception as e:
                await m.edit(embed=createEmbed(dict["cancel"]["title"], dict["cancel"]["desc"], dict["cancel"]["col"]), delete_after=10)
                await m.clear_reactions()
                return None
            for future in done: future.exception()
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
            msg = await ctx.bot.wait_for('message', timeout=60, check=lambda message : message.author == ctx.author)
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
            description=("Select punishment type:\n" + ('\n'.join( [f"{ctx.bot.get_emoji(int(emojiids[t][0]))} | {emojiids[t][1]}" for t in emojiids] ))),
            color=colours["create"]
        )
        eTimed = discord.Embed (
            title=f'{events["nsfw_update"][2]} Punishing user *{member.name}*',
            description=("Select punishment type:\n" + ('\n'.join( [f"{ctx.bot.get_emoji(int(emojiids[t][0]))} | {emojiids[t][1]}" for t in emojiids] ))),
            color=colours["edit"]
        )
        eClosed = discord.Embed (
            title=f'{events["nsfw_update"][2]} Punishing user *{member.name}*',
            description=("Select punishment type:\n" + ('\n'.join( [f"{ctx.bot.get_emoji(int(emojiids[t][0]))} | {emojiids[t][1]}" for t in emojiids] ))),
            color=colours["delete"]
        )
        if m == None: m = await ctx.send(embed=e)
        else: await m.edit(embed=e)
        try:
            try: menu = menus.Menu(timeout=60)
            except: pass
            for emoji in emojiids: 
                try: menu + ctx.bot.get_emoji(emojiids[emoji][0])
                except: pass
            try: o = await menu(ctx.bot, m, ctx.author)
            except: pass
            if o.name == "Stop": 
                await m.edit(embed=eClosed)
                return await m.clear_reactions()
            else: 
                if o.name == "PunishWarn": 
                    if not ctx.author.guild_permissions.kick_members: 
                        return await ctx.send(embed=createEmbed(f"{emojis['PunWarn']} Looks like you don't have permissions", "You need the `kick_members` permission to warn someone.", colours["delete"]))
                        await m.delete()
                    reason, m = await reasonHandler(m, {
                            "cancel": {"title": f"{emojis['PunWarn']} Warning", "desc": f"Warning cancelled.", "col": colours["delete"]},
                            "prompt": {"title": f"{emojis['PunWarn']} Warning", "desc": f"Please enter a reason for warning {member.mention}.", "col": colours["create"]}
                        })
                    if reason != None:
                        await member.send(embed=createEmbed(f"{emojis['PunWarn']} Warning", f"You were warned in {ctx.guild.name} for {reason if reason is not False else 'No reason provided'}.", colours["edit"]))
                        await m.edit(embed=createEmbed(f"{emojis['PunWarn']} Warning", f"User {member.mention} was successfully warned for {reason if reason is not False else 'No reason provided'}.", colours["create"]))
                        await m.clear_reactions()
                elif o.name == "PunishKick": 
                    if not ctx.author.guild_permissions.kick_members: 
                        await ctx.send(embed=createEmbed(f"{emojis['PunKick']} Looks like you don't have permissions", "You need the `kick_members` permission to kick someone.", colours["delete"]))
                        return await m.delete()
                    reason, m = await reasonHandler(m, {
                            "cancel": {"title": f"{emojis['PunKick']} Kick", "desc": f"Kick cancelled.", "col": colours["delete"]},
                            "prompt": {"title": f"{emojis['PunKick']} Kick", "desc": f"Please enter a reason for kicking {member.mention}.", "col": colours["create"]}
                        })
                    if reason != None:
                        try:
                            try: if reason is not False: await member.send(embed=createEmbed(f"{emojis['PunKick']} Kicked", f"You were kicked from {ctx.guild.name} for {reason}.", colours["delete"]))
                            except: pass
                            await member.kick(member, reason=reason)
                            await m.edit(embed=createEmbed(f"{emojis['PunKick']} Kick", f"User {member.mention} was successfully kicked{' for' + str(reason) if reason is not False else ''}.", colours["create"]))
                        except:
                            await m.edit(embed=createEmbed(f"{emojis['PunKick']} Kick", f"Something went wrong. I may not have permissions, or the user couldn't be kicked.", colours["delete"]))
                        await m.clear_reactions()
                elif o.name == "PunishBan": 
                    if not ctx.author.guild_permissions.ban_members: 
                        await ctx.send(embed=createEmbed(f"{emojis['PunBan']} Looks like you don't have permissions", "You need the `ban_members` permission to ban someone.", colours["delete"]))
                        return await m.delete()
                    reason, m = await reasonHandler(m, {
                            "cancel": {"title": f"{emojis['PunBan']} Ban", "desc": f"Ban cancelled.", "col": colours["delete"]},
                            "prompt": {"title": f"{emojis['PunBan']} Ban", "desc": f"Please enter a reason for banning {member.mention}.", "col": colours["create"]}
                        })
                    if reason != None:
                        try: 
                            try: if reason is not False: await member.send(embed=createEmbed(f"{emojis['PunBan']} Banned", f"You were banned from {ctx.guild.name} for {reason}.", colours["delete"]))
                            except: pass
                            await ctx.guild.ban(member, reason=reason, delete_message_days=7)
                            await m.edit(embed=createEmbed(f"{emojis['PunBan']} Ban", f"User {member.mention} was successfully banned{' for' + str(reason) if reason is not False else ''}.", colours["create"]))
                        except Exception as e:
                            await m.edit(embed=createEmbed(f"{emojis['PunBan']} Ban", f"Something went wrong. I may not have permissions, or the user couldn't be banned.", colours["delete"]))
                            print(e)
                        await m.clear_reactions()

        except asyncio.TimeoutError:
            await m.edit(embed=eTimed)
            return await m.clear_reactions()

def setup(bot):
    bot.add_cog(Commands(bot))