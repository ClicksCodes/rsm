import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus
from create_machine_utils.minidiscord import menus

from cogs.consts import *

class Commands(commands.Cog):
    def __init__(self, bot):
        self.emojiids = {
            "PunWarn": [729764054897524768, "Warn"],
            "PunMute": [729764053865463840, "Mute"],
            "PunVoiceMute": [729764054855450697, "Voice Mute"],
            "PunHistory": [729764062270980096, "Delete message history"],
            "PunKick": [729764053794422896, "Kick"],
            "PunSoftBan": [729764053941223476, "Soft ban"],
            "PunBan": [729764053861400637, "Ban"],
            "Stop": [751161404442279966, "Cancel"]
        }
    def createEmbed(self, title, description, color=0x000000):
        return discord.Embed(
            title=title,
            description=description,
            color=color
        )
    async def reasonHandler(self, m, dict, ctx):
        createEmbed = self.createEmbed
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

    async def intHandler(self, m, dict, ctx):
        await m.delete()
        m = await ctx.send(embed=self.createEmbed(
            dict["prompt"]["title"], 
            dict["prompt"]["desc"] + "\n" + f"Select {emojis['tick']} to select {dict['default']} or {emojis['cross']} to cancel", 
            dict["prompt"]["col"]
        ))
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
                if response[0].emoji.name == 'Tick': reason = dict["default"]
                if response[0].emoji.name == 'Cross': await m.edit(embed=self.createEmbed(dict["cancel"]["title"], dict["cancel"]["desc"], dict["cancel"]["col"]), delete_after=10)
            if reason is not None:
                return reason, m
            await m.clear_reactions()
        except Exception as e:
            await m.edit(embed=self.createEmbed(dict["cancel"]["title"], dict["cancel"]["desc"], dict["cancel"]["col"]), delete_after=10)
            await m.clear_reactions()
            return None
        for future in done: future.exception()

    async def warnPun(self, m, member, ctx, reason=None):
        createEmbed = self.createEmbed
        try:
            if not ctx.author.guild_permissions.kick_members: 
                await ctx.send(embed=createEmbed(f"{emojis['PunWarn']} Looks like you don't have permissions", "You need the `kick_members` permission to warn someone.", colours["delete"]))
        except Exception as e: print(e)

        if reason == None:
            reason, m = await self.reasonHandler(
                m, 
                {
                    "cancel": {"title": f"{emojis['PunWarn']} Warning", "desc": f"Warning cancelled.", "col": colours["delete"]},
                    "prompt": {"title": f"{emojis['PunWarn']} Warning", "desc": f"Please enter a reason for warning {member.mention}.", "col": colours["create"]}
                },
                ctx
            )
        if reason != None:
            try: await member.send(embed=createEmbed(f"{emojis['PunWarn']} Warning", f"You were warned in {ctx.guild.name} {('for ' + reason) if reason is not False else 'with no reason provided'}.", colours["edit"]))
            except: return
            await m.edit(embed=createEmbed(f"{emojis['PunWarn']} Warning", f"User {member.mention} was successfully warned for {reason if reason is not False else 'No reason provided'}.", colours["create"]))
            await m.clear_reactions()
    
    async def kickPun(self, m, member, ctx, reason=None):
        createEmbed = self.createEmbed
        if not ctx.author.guild_permissions.kick_members: 
            await ctx.send(embed=createEmbed(f"{emojis['PunKick']} Looks like you don't have permissions", "You need the `kick_members` permission to kick someone.", colours["delete"]))
            return await m.delete()
        if reason == None:
            reason, m = await self.reasonHandler(
                m, 
                {
                    "cancel": {"title": f"{emojis['PunKick']} Kick", "desc": f"Kick cancelled.", "col": colours["delete"]},
                    "prompt": {"title": f"{emojis['PunKick']} Kick", "desc": f"Please enter a reason for kicking {member.mention}.", "col": colours["create"]}
                },
                ctx
            )
        if reason != None:
            try:
                try: 
                    if reason is not False: await member.send(embed=createEmbed(f"{emojis['PunKick']} Kicked", f"You were kicked from {ctx.guild.name} for {reason}.", colours["delete"]))
                except: pass
                await member.kick(member, reason=reason)
                await m.edit(embed=createEmbed(f"{emojis['PunKick']} Kick", f"User {member.mention} was successfully kicked{' for' + str(reason) if reason is not False else ''}.", colours["create"]))
            except:
                await m.edit(embed=createEmbed(f"{emojis['PunKick']} Kick", f"Something went wrong. I may not have permissions, or the user couldn't be kicked.", colours["delete"]))
            await m.clear_reactions()
    
    async def banPun(self, m, member, ctx, reason=None):
        createEmbed = self.createEmbed
        if not ctx.author.guild_permissions.ban_members: 
            await ctx.send(embed=createEmbed(f"{emojis['PunBan']} Looks like you don't have permissions", "You need the `ban_members` permission to ban someone.", colours["delete"]))
            return await m.delete()
        if reason == None:
            reason, m = await self.reasonHandler(
                m, 
                {
                    "cancel": {"title": f"{emojis['PunBan']} Ban", "desc": f"Ban cancelled.", "col": colours["delete"]},
                    "prompt": {"title": f"{emojis['PunBan']} Ban", "desc": f"Please enter a reason for banning {member.mention}.", "col": colours["create"]}
                },
                ctx
            )
        if reason != None:
            try: 
                try: 
                    if reason is not False: await member.send(embed=createEmbed(f"{emojis['PunBan']} Banned", f"You were banned from {ctx.guild.name} for {reason}.", colours["delete"]))
                except: pass
                await ctx.guild.ban(member, reason=reason, delete_message_days=7)
                await m.edit(embed=createEmbed(f"{emojis['PunBan']} Ban", f"User {member.mention} was successfully banned{' for' + str(reason) if reason is not False else ''}.", colours["create"]))
            except Exception as e:
                await m.edit(embed=createEmbed(f"{emojis['PunBan']} Ban", f"Something went wrong. I may not have permissions, or the user couldn't be banned.", colours["delete"]))
                print(e)
            await m.clear_reactions()
    
    async def softBanPun(self, m, member, ctx, reason=None):
        createEmbed = self.createEmbed
        if not ctx.author.guild_permissions.ban_members: 
            await ctx.send(embed=self.createEmbed(f"{emojis['PunSoftBan']} Looks like you don't have permissions", "You need the `ban_members` permission to soft ban someone.", colours["delete"]))
            return await m.delete()
        if reason == None:
            reason, m = await self.reasonHandler(
                m, 
                {
                    "cancel": {"title": f"{emojis['PunSoftBan']} Soft Ban", "desc": f"Soft ban cancelled.", "col": colours["delete"]},
                    "prompt": {"title": f"{emojis['PunSoftBan']} Soft Ban", "desc": f"Please enter a reason for soft banning {member.mention}.", "col": colours["create"]}
                },
                ctx
            )
        if reason != None:
            try: 
                try: 
                    if reason is not False: await member.send(embed=createEmbed(f"{emojis['PunBan']} Banned", f"You were banned from {ctx.guild.name} for {reason}.", colours["delete"]))
                except: pass
                await ctx.guild.ban(member, reason=reason, delete_message_days=7)
                await ctx.guild.unban(member, reason="RSM Soft Ban")
                await m.edit(embed=createEmbed(f"{emojis['PunSoftBan']} Soft Ban", f"User {member.mention} was successfully soft banned{' for' + str(reason) if reason is not False else ''}.", colours["create"]))
            except Exception as e:
                await m.edit(embed=createEmbed(f"{emojis['PunSoftBan']} Soft Ban", f"Something went wrong. I may not have permissions, or the user couldn't be banned.", colours["delete"]))
                print(e)
            await m.clear_reactions()
    async def delHistoryPun(self, m, member, ctx, out=None):
        createEmbed = self.createEmbed
        if not ctx.author.guild_permissions.manage_messages: 
            await ctx.send(embed=createEmbed(f"{emojis['PunishHistory']} Looks like you don't have permissions", "You need the `manage_messages` permission to delete someone's history.", colours["delete"]))
            return await m.delete()
        if out == None:
            out, m = await self.intHandler(
                m, 
                {
                    "cancel": {"title": f"{emojis['PunHistory']} Delete History", "desc": f"Delete history cancelled.", "col": colours["delete"]},
                    "prompt": {"title": f"{emojis['PunHistory']} Delete History", "desc": f"How many messages in this channel should I check? Max 100", "col": colours["create"]},
                    "default": 50
                },
                ctx
            )
        if out != None:
            try: 
                try: out = int(out)
                except: return await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Delete History", f"Something went wrong, I couldn't delete that many messages.", colours["create"]))
                deleted = await ctx.channel.purge(limit=int(out), check=lambda m: m.author == member)
                try: await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Delete History", f"I deleted {len(deleted)} of {member.mention}'s messages.", colours["create"]))
                except discord.ext.commands.errors.CommandInvokeError: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Delete History", f"I deleted {len(deleted)} of {member.mention}'s messages.", colours["create"]))
            except Exception as e:
                await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Delete History", f"Something went wrong. I may not have permissions, or the users history couldn't be deleted.", colours["delete"]))
                print(e)
            await m.clear_reactions() 
    
    async def purgeChannel(self, m, ctx, out=None):
        createEmbed = self.createEmbed
        if not ctx.author.guild_permissions.manage_messages: 
            await ctx.send(embed=createEmbed(f"{emojis['PunishHistory']} Looks like you don't have permissions", "You need the `manage_messages` permission to purge a channel.", colours["delete"]))
            return await m.delete()
        if out == None:
            out, m = await self.intHandler(
                m, 
                {
                    "cancel": {"title": f"{emojis['PunHistory']} Purge Channel", "desc": f"Purge Channel cancelled.", "col": colours["delete"]},
                    "prompt": {"title": f"{emojis['PunHistory']} Purge Channel", "desc": f"How many messages in this channel should I clear? Max 100", "col": colours["create"]},
                    "default": 50
                },
                ctx
            )
        if out != None:
            try: 
                try: out = int(out)
                except: return await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"Something went wrong, I couldn't delete that many messages.", colours["create"]))
                out += 2
                if out > 100: out = 100
                deleted = await ctx.channel.purge(limit=int(out))
                try: await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"I deleted {len(deleted)-2} messages.", colours["create"]), delete_after=10)
                except discord.ext.commands.errors.CommandInvokeError: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"I deleted {len(deleted)-2} messages.", colours["create"]), delete_after=10)
                except discord.errors.NotFound: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"I deleted {len(deleted)-2} messages.", colours["create"]), delete_after=10)
            except Exception as e:
                try: await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"Something went wrong. I may not have permission to do that.", colours["delete"]), delete_after=10)
                except discord.ext.commands.errors.CommandInvokeError: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"Something went wrong. I may not have permission to do that.", colours["delete"]), delete_after=10)
                except discord.NotFound: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"Something went wrong. I may not have permission to do that.", colours["delete"]), delete_after=10)
                print(e)
            try: await m.clear_reactions() 
            except: pass

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def punish(self, ctx, *member: discord.Member):
        m = None
        tooMany = discord.Embed(
            title=f'{events["nsfw_update"][2]} You mentioned too many people there',
            description="You can only punish one person at a time.",
            color=colours["delete"]
        )
        noPing = discord.Embed(
            title=f"Who do you want to punish?",
            description="Please mention the user you'd like to punish.",
            color=colours["create"]
        )
        if len(member) > 1: 
            return await ctx.send(embed=tooMany)
        if not member: 
            m = await ctx.send(embed=noPing)
            msg = await ctx.bot.wait_for('message', timeout=60, check=lambda message : message.author == ctx.author)
            await msg.delete()
            if len(msg.mentions) != 1: return await ctx.send(embed=tooMany)
            else: member = msg.mentions[0]
        else: member = member[0]
        

        e = discord.Embed (
            title=f'{events["nsfw_update"][2]} Punishing user *{member.name}*',
            description=(f"Select punishment for {member.mention}:" + "\n" + ('\n'.join( [f"{ctx.bot.get_emoji(int(self.emojiids[t][0]))} | {self.emojiids[t][1]}" for t in self.emojiids] ))),
            color=colours["create"]
        )
        eTimed = discord.Embed (
            title=f'{events["nsfw_update"][2]} Punishing user *{member.name}*',
            description=(f"Select punishment for {member.mention}:" + "\n" + ('\n'.join( [f"{ctx.bot.get_emoji(int(self.emojiids[t][0]))} | {self.emojiids[t][1]}" for t in self.emojiids] ))),
            color=colours["edit"]
        )
        eClosed = discord.Embed (
            title=f'{events["nsfw_update"][2]} Punishing user *{member.name}*',
            description=(f"Select punishment for {member.mention}:" + "\n" + ('\n'.join( [f"{ctx.bot.get_emoji(int(self.emojiids[t][0]))} | {self.emojiids[t][1]}" for t in self.emojiids] ))),
            color=colours["delete"]
        )
        if m == None: m = await ctx.send(embed=e)
        else: await m.edit(embed=e)
        try:
            try: menu = menus.Menu(timeout=60)
            except: pass
            for emoji in self.emojiids: 
                try: menu + ctx.bot.get_emoji(self.emojiids[emoji][0])
                except: pass
            try: o = await menu(ctx.bot, m, ctx.author)
            except: o = None
            if o.name == "Stop": 
                await m.edit(embed=eClosed)
                return await m.clear_reactions()
            else: 
                if   o.name == "PunishWarn":    await self.warnPun(m, member, ctx)
                elif o.name == "PunishKick":    await self.kickPun(m, member, ctx)
                elif o.name == "PunishBan":     await self.banPun(m, member, ctx)
                elif o.name == "PunishSoftBan": await self.softBanPun(m, member, ctx)
                elif o.name == "PunishHistory": await self.delHistoryPun(m, member, ctx)
                else: return

        except asyncio.TimeoutError:
            await m.edit(embed=eTimed)
            return await m.clear_reactions()

    @punish.error
    async def _on_punish_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            notFound = discord.Embed(
                title=f'{events["nsfw_update"][2]} I couldn\'t find that user',
                description="I may not be able to see them. Try mentioning them instead.",
                color=colours["edit"]
            )
            await ctx.send(embed=notFound)
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: typing.Optional[discord.Member], reason:typing.Optional[str]):
        reason = str(' '.join(reason))
        tooMany = discord.Embed(
            title=f'{events["nsfw_update"][2]} You mentioned too many people there',
            description="You can only punish one person at a time.",
            color=colours["delete"]
        )
        noPing = discord.Embed(
            title=f"Who do you want to warn?",
            description="Please mention the user you'd like to warn.",
            color=colours["create"]
        )
        if not member: 
            m = await ctx.send(embed=noPing)
            msg = await ctx.bot.wait_for('message', timeout=60, check=lambda message : message.author == ctx.author)
            await msg.delete()
            await m.delete()
            if len(msg.mentions) != 1: return await ctx.send(embed=tooMany)
            else: member = msg.mentions[0]
        m = await ctx.send(embed=discord.Embed(title="Loading"))
        await self.warnPun(m, member, ctx, reason if len(reason) > 0 else None)
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: typing.Optional[discord.Member], reason:typing.Optional[str]):
        reason = str(' '.join(reason))
        tooMany = discord.Embed(
            title=f'{events["nsfw_update"][2]} You mentioned too many people there',
            description="You can only punish one person at a time.",
            color=colours["delete"]
        )
        noPing = discord.Embed(
            title=f"Who do you want to kick?",
            description="Please mention the user you'd like to kick.",
            color=colours["create"]
        )
        if not member: 
            m = await ctx.send(embed=noPing)
            msg = await ctx.bot.wait_for('message', timeout=60, check=lambda message : message.author == ctx.author)
            await msg.delete()
            await m.delete()
            if len(msg.mentions) != 1: return await ctx.send(embed=tooMany)
            else: member = msg.mentions[0]
        m = await ctx.send(embed=discord.Embed(title="Loading"))
        await self.kickPun(m, member, ctx, reason)
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, member: typing.Optional[discord.Member], t:typing.Optional[int]):
        tooMany = discord.Embed(
            title=f'{events["nsfw_update"][2]} You mentioned too many people there',
            description="You can only punish one person at a time.",
            color=colours["delete"]
        )
        noPing = discord.Embed(
            title=f"Who's history would you like to clear?",
            description="Please mention the user you'd like to clear the history of.",
            color=colours["create"]
        )
        if not member: 
            m = await ctx.send(embed=noPing)
            msg = await ctx.bot.wait_for('message', timeout=60, check=lambda message : message.author == ctx.author)
            await msg.delete()
            await m.delete()
            if len(msg.mentions) != 1: return await ctx.send(embed=tooMany)
            else: member = msg.mentions[0]
        m = await ctx.send(embed=discord.Embed(title="Loading"))
        await self.delHistoryPun(m, member, ctx, t)
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, t:typing.Optional[int]):
        m = await ctx.send(embed=discord.Embed(title="Loading"))
        await self.purgeChannel(m, ctx, t)
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def softBan(self, ctx, member: typing.Optional[discord.Member], reason:typing.Optional[str]):
        reason = str(' '.join(reason))
        tooMany = discord.Embed(
            title=f'{events["nsfw_update"][2]} You mentioned too many people there',
            description="You can only punish one person at a time.",
            color=colours["edit"]
        )
        noPing = discord.Embed(
            title=f"Who do you want to soft ban?",
            description="Please mention the user you'd like to soft ban.",
            color=colours["create"]
        )
        if not member: 
            m = await ctx.send(embed=noPing)
            msg = await ctx.bot.wait_for('message', timeout=60, check=lambda message : message.author == ctx.author)
            await msg.delete()
            await m.delete()
            if len(msg.mentions) != 1: return await ctx.send(embed=tooMany)
            else: member = msg.mentions[0]
        m = await ctx.send(embed=discord.Embed(title="Loading"))
        await self.softBanPun(m, member, ctx, reason)
    
    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: typing.Optional[discord.Member], reason:typing.Optional[str]):
        reason = str(' '.join(reason))
        tooMany = discord.Embed(
            title=f'{events["nsfw_update"][2]} You mentioned too many people there',
            description="You can only punish one person at a time.",
            color=colours["delete"]
        )
        noPing = discord.Embed(
            title=f"Who do you want to ban?",
            description="Please mention the user you'd like to ban.",
            color=colours["create"]
        )
        if not member: 
            m = await ctx.send(embed=noPing)
            msg = await ctx.bot.wait_for('message', timeout=60, check=lambda message : message.author == ctx.author)
            await msg.delete()
            await m.delete()
            if len(msg.mentions) != 1: return await ctx.send(embed=tooMany)
            else: member = msg.mentions[0]
        m = await ctx.send(embed=discord.Embed(title="Loading"))
        await self.banPun(m, member, ctx, reason)

def setup(bot):
    bot.add_cog(Commands(bot))