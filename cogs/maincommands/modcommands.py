import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, postbin, re

from datetime import datetime
from discord.ext import commands
from textwrap import shorten

from cogs.consts import *

class Commands(commands.Cog):
    def __init__(self, bot):
        self.emojiids = {
            "PunWarn":      [729764054897524768, "Warn"],
            # "PunMute":      [729764053865463840, "Mute"],
            # "PunVoiceMute": [729764054855450697, "Voice Mute"],
            "PunHistory":   [729764062270980096, "Delete message history"],
            "PunKick":      [729764053794422896, "Kick"],
            "PunSoftBan":   [729764053941223476, "Soft ban"],
            "PunBan":       [729764053861400637, "Ban"],
            "Stop":         [751161404442279966, "Cancel"]
        }
        self.bot = bot
        self.loadingEmbed = loadingEmbed

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
        except: pass

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
        except: pass

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
            if not ctx.author.guild_permissions.kick_members:   return await m.edit(embed=createEmbed(f"{emojis['PunWarn']} Looks like you don't have permissions", "You need the `kick_members` permission to warn someone.", colours["delete"]))
            if not ctx.guild.me.guild_permissions.kick_members: return await m.edit(embed=createEmbed(f"{emojis['PunWarn']} Looks like I don't have permissions", "I need the `kick_members` permission to warn someone.", colours["delete"]))
        except: return

        with open(f"data/stats.json", 'r') as entry:
                entry = json.load(entry)
                entry["warns"] += 1
        with open(f"data/stats.json", 'w') as f:
            json.dump(entry, f, indent=2)

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
        try:
            if not ctx.author.guild_permissions.kick_members:   return await m.edit(embed=createEmbed(f"{emojis['PunKick']} Looks like you don't have permissions", "You need the `kick_members` permission to kick someone.", colours["delete"]))
            if not ctx.guild.me.guild_permissions.kick_members: return await m.edit(embed=createEmbed(f"{emojis['PunKick']} Looks like I don't have permissions", "I need the `kick_members` permission to kick someone.", colours["delete"]))
        except: return

        with open(f"data/stats.json", 'r') as entry:
                entry = json.load(entry)
                entry["kicks"] += 1
        with open(f"data/stats.json", 'w') as f:
            json.dump(entry, f, indent=2)

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
        try:
            if not ctx.author.guild_permissions.ban_members:   return await m.edit(embed=createEmbed(f"{emojis['PunBan']} Looks like you don't have permissions", "You need the `ban_members` permission to ban someone.", colours["delete"]))
            if not ctx.guild.me.guild_permissions.ban_members: return await m.edit(embed=createEmbed(f"{emojis['PunBan']} Looks like I don't have permissions", "I need the `ban_members` permission to ban someone.", colours["delete"]))
        except: return

        with open(f"data/stats.json", 'r') as entry:
                entry = json.load(entry)
                entry["bans"] += 1
        with open(f"data/stats.json", 'w') as f:
            json.dump(entry, f, indent=2)

        if reason == None or len(reason) < 2:
            try:
                reason, m = await self.reasonHandler(
                    m, 
                    {
                        "cancel": {"title": f"{emojis['PunBan']} Ban", "desc": f"Ban cancelled.", "col": colours["delete"]},
                        "prompt": {"title": f"{emojis['PunBan']} Ban", "desc": f"Please enter a reason for banning {member.mention}.", "col": colours["create"]}
                    },
                    ctx
                )
            except: pass
        if reason != None:
            try: 
                if ctx.guild.me.top_role.position <= member.top_role.position or ctx.author.top_role.position <= member.top_role.position: int("return an error, quite clearly")
                try: 
                    if reason is not False: bm = await member.send(embed=createEmbed(f"{emojis['PunBan']} Banned", f"You were banned from {ctx.guild.name} for {reason}.", colours["delete"]))
                except: pass
                await ctx.guild.ban(member, reason=reason, delete_message_days=7)
                await m.edit(embed=createEmbed(f"{emojis['PunBan']} Ban", f"User {member.mention} was successfully banned{' for ' + str(reason) if reason is not False else ''}.", colours["create"]))
            except:
                await m.edit(embed=createEmbed(f"{emojis['PunBan']} Ban", f"Something went wrong. I may not have permissions, or the user couldn't be banned.", colours["delete"]))
                try: bm.edit(embed=createEmbed(f"{emojis['PunBan']} Ban", f"The ban in {ctx.guild.name} failed.", colours["create"]))
                except: pass
            await m.clear_reactions()
    
    async def softBanPun(self, m, member, ctx, reason=None):
        createEmbed = self.createEmbed
        try:
            if not ctx.author.guild_permissions.ban_members:   return await m.edit(embed=self.createEmbed(f"{emojis['PunSoftBan']} Looks like you don't have permissions", "You need the `ban_members` permission to soft ban someone.", colours["delete"]))
            if not ctx.guild.me.guild_permissions.ban_members: return await m.edit(embed=self.createEmbed(f"{emojis['PunSoftBan']} Looks like I don't have permissions", "I need the `ban_members` permission to soft ban someone.", colours["delete"]))
        except: return

        with open(f"data/stats.json", 'r') as entry:
                entry = json.load(entry)
                entry["softbans"] += 1
        with open(f"data/stats.json", 'w') as f:
            json.dump(entry, f, indent=2)

        if reason == None or len(reason) < 2:
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
            except:
                await m.edit(embed=createEmbed(f"{emojis['PunSoftBan']} Soft Ban", f"Something went wrong. I may not have permissions, or the user couldn't be banned.", colours["delete"]))
            await m.clear_reactions()

    async def delHistoryPun(self, m, member, ctx, out=None, mod=None):
        createEmbed = self.createEmbed
        try:
            if not ctx.author.guild_permissions.manage_messages:   return await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Looks like you don't have permissions", "You need the `manage_messages` permission to delete someone's history.", colours["delete"]))
            if not ctx.guild.me.guild_permissions.manage_messages: return await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Looks like I don't have permissions", "I need the `manage_messages` permission to delete someone's history.", colours["delete"]))
        except: return

        with open(f"data/stats.json", 'r') as entry:
                entry = json.load(entry)
                entry["clears"] += 1
        with open(f"data/stats.json", 'w') as f:
            json.dump(entry, f, indent=2)

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
                if mod not in ["!", "not", "only"]: deleted = await ctx.channel.purge(limit=int(out), check=lambda m: m.author == member)
                else:                               deleted = await ctx.channel.purge(limit=int(out), check=lambda m: m.author != member)
                try: await ctx.channel.send(embed=createEmbed(f"{emojis['PunHistory']} Delete History", f"I deleted {len(deleted)} messages {'not ' if mod in ['only', 'not', '!'] else ''}by {member.mention}.", colours["create"]))
                except discord.ext.commands.errors.CommandInvokeError: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Delete History", f"I deleted {len(deleted)} of {member.mention}'s messages.", colours["create"]))
            except:
                await ctx.channel.send(embed=createEmbed(f"{emojis['PunHistory']} Delete History", f"Something went wrong. I may not have permissions, or the users history couldn't be deleted.", colours["delete"]))
            await m.clear_reactions()
            try:
                await m.delete()
            except: pass
    
    async def setSlowmode(self, ctx, channel, time):
        createEmbed = self.createEmbed
        try: await ctx.delete()
        except: pass

        try:
            if not ctx.author.guild_permissions.manage_messages:   return await ctx.send(embed=createEmbed(f"{emojis['slowmodeOn']} Slowmode", "You need the `manage_messages` permission to set slowmode.", colours["delete"]), delete_after=10)
            if not ctx.guild.me.guild_permissions.manage_messages: return await ctx.send(embed=createEmbed(f"{emojis['slowmodeOn']} Slowmode", "I need the `manage_messages` permission to set slowmode.", colours["delete"]), delete_after=10)
            if time > 21600:                                       return await ctx.send(embed=createEmbed(f"{emojis['slowmodeOn']} Slowmode", "Slowmode delay must be smaller than 21600.", colours["delete"]), delete_after=10)
            if time < 0:                                           return await ctx.send(embed=createEmbed(f"{emojis['slowmodeOn']} Slowmode", "Slowmode delay must be bigger than 0.", colours["delete"]), delete_after=10)
            await ctx.channel.edit(slowmode_delay=time)
            return await ctx.send(embed=createEmbed(f"{emojis['slowmodeOn'] if time > 0 else emojis['slowmodeOff']} Slowmode", f"Slowmode time has been successfully set to {time}s.", colours["create"]))
        except:
            await ctx.send(embed=createEmbed(f"{emojis['slowmodeOn'] if time > 0 else emojis['slowmodeOff']} Slowmode", "An unknown error occurred and slowmode could not be set.", colours["delete"]), delete_after=10)
            return
        
    async def lockdown(self, lock, channel, ctx):
        createEmbed = self.createEmbed
        if not ctx.author.guild_permissions.manage_channels:   return await ctx.send(embed=createEmbed(f"{emojis['lock']} Lock", "You need the `manage_channels` permission to set lockdown.", colours["delete"]), delete_after=10)
        if not ctx.guild.me.guild_permissions.manage_channels: return await ctx.send(embed=createEmbed(f"{emojis['lock']} Lock", "I need the `manage_channels` permission to set lockdown.", colours["delete"]), delete_after=10)
        with open(f"data/stats.json", 'r') as entry:
            entry = json.load(entry)
            entry["locks"] += 1
        with open(f"data/stats.json", 'w') as f:
            json.dump(entry, f, indent=2)
        m = await ctx.send(embed=createEmbed(f"{emojis['lock']} Lock", f"Please wait as the channel gets {'un' if lock is None else ''}locked.", colours["edit"]))
        for role in ctx.guild.roles: 
            await asyncio.sleep(1)
            if not role.permissions.manage_messages:
                override = channel.overwrites_for(role)
                override.send_messages = lock
                try: await channel.set_permissions(role, overwrite=override)
                except: pass
            else:
                override = channel.overwrites_for(role)
                override.send_messages = True
                try: await channel.set_permissions(role, overwrite=override)
                except: pass
        return await m.edit(embed=createEmbed(f"{emojis['lock']} Lock", f"The channel is now {'un' if lock is None else ''}locked for everyone without `manage_messages` permission.", colours["create"]))
            
    async def purgeChannel(self, m, ctx, out=None):
        createEmbed = self.createEmbed
        try:
            if not ctx.author.guild_permissions.manage_messages: 
                await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Looks like you don't have permissions", "You need the `manage_messages` permission to purge a channel.", colours["delete"]))
                return await m.delete()
        except: return
        
        with open(f"data/stats.json", 'r') as entry:
                entry = json.load(entry)
                entry["purges"] += 1
        with open(f"data/stats.json", 'w') as f:
            json.dump(entry, f, indent=2)

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
                deleted = await ctx.channel.purge(limit=int(out), check=lambda m : not m.pinned)
                try: await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"I deleted {len(deleted)-2} messages.", colours["create"]), delete_after=10)
                except discord.ext.commands.errors.CommandInvokeError: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"I deleted {len(deleted)-2} messages.", colours["create"]), delete_after=10)
                except discord.errors.NotFound: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"I deleted {len(deleted)-2} messages.", colours["create"]), delete_after=10)
            except:
                try: await m.edit(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"Something went wrong. I may not have permission to do that.", colours["delete"]), delete_after=10)
                except discord.ext.commands.errors.CommandInvokeError: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"Something went wrong. I may not have permission to do that.", colours["delete"]), delete_after=10)
                except discord.NotFound: await ctx.send(embed=createEmbed(f"{emojis['PunHistory']} Purge Channel", f"Something went wrong. I may not have permission to do that.", colours["delete"]), delete_after=10)
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
        eClosed = discord.Embed (
            title=f'{events["nsfw_update"][2]} Punishing user *{member.name}*',
            description=(f"Select punishment for {member.mention}:" + "\n" + ('\n'.join( [f"{ctx.bot.get_emoji(int(self.emojiids[t][0]))} | {self.emojiids[t][1]}" for t in self.emojiids] ))),
            color=colours["delete"]
        )

        if m == None: m = await ctx.send(embed=e)
        else: await m.edit(embed=e)

        try:
            for emoji in self.emojiids: 
                try: await m.add_reaction(self.bot.get_emoji(self.emojiids[emoji][0]))
                except: pass

            reaction = None
            try: reaction = await ctx.bot.wait_for('reaction_add', timeout=120, check=lambda emoji, user : emoji.message.id == m.id and user == ctx.author)
            except asyncio.TimeoutError: 
                m.edit(embed=eClosed)
                return await m.clear_reactions()

            try: await m.remove_reaction(reaction[0].emoji, ctx.author)
            except: pass

            o = reaction[0].emoji

            if o.name == "Stop": 
                await m.edit(embed=eClosed)
                return await m.clear_reactions()
            else: 
                if   o.name == "PunishWarn":    await self.warnPun(m, member, ctx)
                elif o.name == "PunishKick":    await self.kickPun(m, member, ctx)
                elif o.name == "PunishBan":     await self.banPun(m, member, ctx)
                elif o.name == "PunishSoftBan": await self.softBanPun(m, member, ctx)
                elif o.name == "PunishHistory": await self.delHistoryPun(m, member, ctx)
                else: print(o.name)
        except:
            await m.edit(embed=eClosed)
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
    async def warn(self, ctx, member: typing.Optional[discord.Member], *, reason:typing.Optional[str]):
        try: reason = str(''.join(reason))
        except: reason = None
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
        m = await ctx.send(embed=self.loadingEmbed)
        await self.warnPun(m, member, ctx, reason)
    
    @commands.command()
    @commands.guild_only()
    async def kick(self, ctx, member: typing.Optional[discord.Member], *, reason:typing.Optional[str]):
        try: reason = str(''.join(reason))
        except: reason = ""
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
        m = await ctx.send(embed=self.loadingEmbed)
        await self.kickPun(m, member, ctx, reason)
    
    @commands.command()
    @commands.guild_only()
    async def clear(self, ctx, member: typing.Optional[discord.Member], t:typing.Optional[int], mod: typing.Optional[str]):
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
        m = await ctx.send(embed=self.loadingEmbed)
        await self.delHistoryPun(m, member, ctx, t, mod=mod)
    
    @commands.command()
    @commands.guild_only()
    async def purge(self, ctx, t:typing.Optional[int]):
        m = await ctx.send(embed=self.loadingEmbed)
        await self.purgeChannel(m, ctx, t)
    
    @commands.command()
    @commands.guild_only()
    async def softBan(self, ctx, member: typing.Optional[discord.Member], *, reason:typing.Optional[str]):
        try: reason = str(''.join(reason))
        except: reason = ""
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
        m = await ctx.send(embed=self.loadingEmbed)
        await self.softBanPun(m, member, ctx, reason)
    
    @commands.command()
    @commands.guild_only()
    async def ban(self, ctx, member: typing.Optional[discord.Member], *, reason:typing.Optional[str]):
        try: reason = str(''.join(reason))
        except: reason = ""
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
        m = await ctx.send(embed=self.loadingEmbed)
        await self.banPun(m, member, ctx, reason)
        
    @commands.command(aliases=["slow"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def slowmode(self, ctx, channel: typing.Optional[discord.TextChannel], time: typing.Optional[str]):
        if not channel: channel = ctx.channel
        if time is not None: time = re.sub(r"[^0-9]*", "", str(time))
        try: 
            time = int(time)
        except:
            if time == "toggle" or time == None:
                if channel.slowmode_delay > 0: time = 0 
                else:                          time = 10
            elif time == "on":  time = 10
            elif time == "off": time = 0 
            else:               time = channel.slowmode_delay

        await self.setSlowmode(ctx, channel, time) 
        
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def lock(self, ctx, channel: typing.Optional[discord.TextChannel], s: typing.Optional[str]):
        if not channel: channel = ctx.channel
        lock = False
        
        if s == "off": lock = None  
        
        await self.lockdown(lock, channel, ctx)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def unlock(self, ctx, channel: typing.Optional[discord.TextChannel]):
        if not channel: channel = ctx.channel

        await self.lockdown(None, channel, ctx)   
    
    @commands.command(aliases=["user", "whois"])
    @commands.guild_only()
    async def userinfo(self, ctx, member: typing.Optional[discord.Member]):
        if not member: member = ctx.author

        ms = []
        guild = self.bot.get_guild(684492926528651336)
        role = guild.get_role(760896837866749972)

        flags = []
        if member.id in [317731855317336067, 438733159748599813, 715989276382462053, 261900651230003201, 421698654189912064, 487443883127472129]: flags.append("rsm_developer")
        if member in role.members: flags.append("clicks_developer")
        if member.id in ms: flags.append("rsm_developer")
        if member in guild.premium_subscribers: flags.append("booster")
        if member.is_avatar_animated() or str(member.discriminator).startswith("000"): flags.append("nitro")
        if member.bot: flags.append("bot")
        for flag, val in member.public_flags:
            if val: flags.append(flag)

        flagemojis = {
            "hypesquad_bravery": ["<:hypesquad_bravery:775783765930016789>", "Hypesquad Bravery"],
            "early_supporter": ["<:early_supporter:775783766055452693>", "Early Supporter"],
            "bug_hunter_2": ["<:bug_hunter_2:775783766130950234>", "Bug Hunter level 2"],
            "booster": ["<:Boosting1y:775783766131605545>", "Server Booster"],
            "rsm_developer": ["<:rsm_developer:775783766147858534>", "**RSM Developer**"],
            "hypesquad_brilliance": ["<:hypesquad_brilliance:775783766152577095>", "Hypesquad Brilliance"],
            "partner": ["<:partner:775783766178005033>", "Partner"],
            "hypesquad": ["<:hypesquad:775783766194126908>", "Hypesquad Events"],
            "bug_hunter_1": ["<:bug_hunter_1:775783766252847154>", "Bug Hunter level 1"],
            "hypesquad_balance": ["<:hypesquad_balance:775783766303440937>", "Hypesquad Balance"],
            "staff": ["<:staff:775783766383788082>", "Discord Staff"],
            "verified_bot_developer": ["<:verified_bot_developer:775783766425600060>", "Verified Bot Developer"],
            "clicks_developer": ["<:clicks_developer:776140126156881950>", "Clicks Developer"],
            "nitro": ["<:Nitro:776149266775146546>", "Nitro"],
            "bot": ["<:Bot:776375959108190239>", "Bot"]
        }

        flagstring = ""
        for flag in flags:
            try: flagstring += flagemojis[flag][0] + f" | {flagemojis[flag][1]}\n"
            except: print(flag)
        perms = dict(member.guild_permissions)

        embeds = {
            0: [
                flagstring,
                f"**ID:** `{member.id}`",
                f"**Mention:** {member.mention}",
                f"**Name:** {member.name}",
                f"**Nickname:** {member.display_name if member.display_name != member.name else 'No nickname'}",
                f"**Status:** {emojis[member.status.name]} {member.status.name.capitalize() if member.status.name != 'dnd' else 'DND'}" + (' - Mobile' if member.mobile_status.name == 'online' else ''),
                f"**Started boosting:** {humanize.naturaltime(member.premium_since) if member.premium_since != None else 'Not boosting'}" ,
                f"**Joined Discord:** {humanize.naturaltime(member.created_at)}",
                f"**Joined the server:** {humanize.naturaltime(datetime.utcnow()-member.joined_at)}"
            ],
            1: [
                f"**ID:** `{member.id}`",
                f"**Mention:** {member.mention}",
                f"**Roles:** {len(member.roles)}",
                f"{', '.join(reversed([r.mention for r in member.roles]))}"
            ],
            2: [
                "**Server**",
                f"{emojis['tick'] if perms['view_audit_log'        ] else emojis['cross']} View audit logs",
                f"{emojis['tick'] if perms['view_guild_insights'   ] else emojis['cross']} View server insights",
                f"{emojis['tick'] if perms['manage_guild'          ] else emojis['cross']} Manage server",
                f"{emojis['tick'] if perms['manage_roles'          ] else emojis['cross']} Manage roles",
                f"{emojis['tick'] if perms['manage_channels'       ] else emojis['cross']} Manage channels",
                f"{emojis['tick'] if perms['manage_webhooks'       ] else emojis['cross']} Manage webhooks",
                f"{emojis['tick'] if perms['manage_emojis'         ] else emojis['cross']} Manage emojis",
                f"{emojis['tick'] if perms['create_instant_invite' ] else emojis['cross']} Create instant invite"
            ],
            3: [
                "**Messages**",
                f"{emojis['tick'] if perms['read_messages'        ] else emojis['cross']} Read channels and see Voice channels",
                f"{emojis['tick'] if perms['send_messages'        ] else emojis['cross']} Send messages",
                f"{emojis['tick'] if perms['send_tts_messages'    ] else emojis['cross']} Send TTS messages",
                f"{emojis['tick'] if perms['manage_messages'      ] else emojis['cross']} Manage messages",
                f"{emojis['tick'] if perms['embed_links'          ] else emojis['cross']} Embed links",
                f"{emojis['tick'] if perms['attach_files'         ] else emojis['cross']} Attach files",
                f"{emojis['tick'] if perms['read_message_history' ] else emojis['cross']} Read message history",
                f"{emojis['tick'] if perms['mention_everyone'     ] else emojis['cross']} Mention @everyone, @here and @roles",
                f"{emojis['tick'] if perms['external_emojis'      ] else emojis['cross']} Use nitro emojis",
                f"{emojis['tick'] if perms['add_reactions'        ] else emojis['cross']} Add reactions"
            ],
            4: [
                "**Members**",
                f"{emojis['tick'] if perms['kick_members'     ] else emojis['cross']} Kick members",
                f"{emojis['tick'] if perms['ban_members'      ] else emojis['cross']} Ban members",
                f"{emojis['tick'] if perms['change_nickname'  ] else emojis['cross']} Change nickname",
                f"{emojis['tick'] if perms['manage_nicknames' ] else emojis['cross']} Change other people's nicknames"
            ],
            5: [
                "**Voice**",
                f"{emojis['tick'] if perms['connect'              ] else emojis['cross']} Join voice channels",
                f"{emojis['tick'] if perms['speak'                ] else emojis['cross']} Talk in voice channels",
                f"{emojis['tick'] if perms['stream'               ] else emojis['cross']} Stream in voice channels",
                f"{emojis['tick'] if perms['mute_members'         ] else emojis['cross']} Server mute members",
                f"{emojis['tick'] if perms['deafen_members'       ] else emojis['cross']} Server deafen members",
                f"{emojis['tick'] if perms['move_members'         ] else emojis['cross']} Move members between voice channels",
                f"{emojis['tick'] if perms['use_voice_activation' ] else emojis['cross']} Use voice activity",
                f"{emojis['tick'] if perms['priority_speaker'     ] else emojis['cross']} Priority speaker"
            ]
        }

        m = await ctx.send(embed=loadingEmbed)
        for r in [ 729064530310594601, 729762938411548694, 729762938843430952 ]: await m.add_reaction(self.bot.get_emoji(r))
        p = 0

        for _ in range(50):
            e = discord.Embed(
                title=f"Userinfo for {member.name}",
                description="\n".join(embeds[p]),
                color=colours["create"]
            )
            if p == 0: e.set_thumbnail(url=member.avatar_url)
            await m.edit(embed=e)

            reaction = None
            try: reaction = await ctx.bot.wait_for('reaction_add', timeout=60, check=lambda r, user : r.message.id == m.id and user == ctx.author)
            except asyncio.TimeoutError: break
            reaction = reaction[0].emoji

            if   reaction.name == "Left":  p -= 1
            elif reaction.name == "Right": p += 1
            else: break

            p = min(len(embeds)-1, max(0, p))

            try: await m.remove_reaction(reaction, ctx.author)
            except: pass

        e = discord.Embed(
            title=f"Userinfo for {member.name}",
            description="\n".join(embeds[p]),
            color=colours["delete"]
        )
        if p: e.set_thumbnail(url=member.avatar_url)
        await m.clear_reactions()
        return await m.edit(embed=e)
    
    @commands.command(aliases=["nickname", "setnick", "name"])
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, target:typing.Optional[discord.Member], *, name:typing.Optional[str]):
        m = await ctx.send(embed=loadingEmbed)
        if not target: target = ctx.author
        if not name:
            for r in [729064531107774534, 729064530310594601]: await m.add_reaction(self.bot.get_emoji(r))
            await m.edit(embed=discord.Embed(
                title=f"{emojis['nickname_change']} What nickname should {target.display_name} have?",
                description=f"Please enter the nickname for {target.display_name}. \nReact {emojis['tick']} to clear {'their' if ctx.author.id != target.id else 'your'} nickname or {emojis['cross']} to close.",
                color=colours['create']
            ))
            try:
                done, pending = await asyncio.wait([
                        self.bot.wait_for('reaction_add',    timeout=120, check=lambda emoji, user : emoji.message.id == m.id and user == ctx.author),
                        self.bot.wait_for('message',         timeout=120, check=lambda message : message.author == ctx.author)
                    ], return_when=asyncio.FIRST_COMPLETED)
            except:
                return await m.edit(embed=discord.Embed(
                    title=f"{emojis['nickname_change']} What nickname should {target.display_name} have?",
                    description=f"Please enter the nickname for {target.display_name}. \nReact {emojis['tick']} to clear {'their' if ctx.author.id != target.id else 'your'} nickname or {emojis['cross']} to close.",
                    color=colours['delete']
                ))

            try: out = done.pop().result()
            except Exception as e:
                return await m.edit(embed=discord.Embed(
                    title=f"{emojis['nickname_change']} What nickname should {target.display_name} have?",
                    description=f"Please enter the nickname for {target.display_name}. \nReact {emojis['tick']} to clear {'their' if ctx.author.id != target.id else 'your'} nickname or {emojis['cross']} to close.",
                    color=colours['delete']
                ))

            for future in done: future.exception()
            for future in pending: future.cancel()

            await m.clear_reactions()
            if isinstance(out, tuple): 
                await m.clear_reactions()
                if   out[0].emoji.name == "Tick":  name = None
                elif out[0].emoji.name == "Cross": 
                    return await m.edit(embed=discord.Embed(
                        title=f"{emojis['nickname_change']} What nickname should {target.display_name} have?",
                        description=f"Please enter the nickname for {target.display_name}. \nReact {emojis['tick']} to clear {'their' if ctx.author.id != target.id else 'your'} nickname or {emojis['cross']} to close.",
                        color=colours['delete']
                    ))
                else: return

            elif isinstance(out, discord.Message): 
                name = out.content
                await out.delete()
            else: name = None
        try: 
            await target.edit(nick=name)
            return await m.edit(embed=discord.Embed(
                title=f"{emojis['nickname_change']} Nickname",
                description="Successfully changed nickname",
                color=colours["create"]
            ))
        except:
            return await m.edit(embed=discord.Embed(
                title=f"{emojis['nickname_change']} Nickname",
                description="I can't change that person's nickname",
                color=colours["delete"]
            ))

def setup(bot):
    bot.add_cog(Commands(bot))