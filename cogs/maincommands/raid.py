import copy, discord, json, humanize, aiohttp, traceback, typing, asyncio, postbin, re

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
import time as timeimp

from cogs.consts import *


class Raid(commands.Cog):
    def __init__(self, bot):
        self.emojiids = {
            "PunWarn":      [729764054897524768, "Warn"],
            "PunMute":      [729764053865463840, "Mute"],
            "PunVoiceMute": [729764054855450697, "Voice Mute"],
            "PunHistory":   [729764062270980096, "Delete message history"],
            "PunKick":      [729764053794422896, "Kick"],
            "PunSoftBan":   [729764053941223476, "Soft ban"],
            "PunBan":       [729764053861400637, "Ban"],
            "Stop":         [751161404442279966, "Cancel"]
        }
        with open("./data/emojis.json") as rfile: self.emojis = json.load(rfile)
        self.bot = bot
        self.loadingEmbed = loadingEmbed

    def createEmbed(self, title, description, color=0x000000):
        return discord.Embed(
            title=title,
            description=description,
            color=color
        )

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
                if m.content.lower() != "cancel":
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
    
    @commands.command()
    @commands.guild_only()
    async def raid(self, ctx, toggle: typing.Optional[str]):
        if not (ctx.author.guild_permissions.administrator or (ctx.author.guild_permissions.manage_channels and ctx.author.guild_permissions.manage_server)): return await ctx.send(embed=self.createEmbed(f"{emojis['raidlock']} Looks like you don't have permissions", "You need the `administrator` or both `manage_server` and `manage_channels` permissions to toggle raid.", colours["delete"]), delete_after=10)
        with open(f"data/stats.json", 'r') as entry:
            entry = json.load(entry)
            entry["raids"] += 1
        with open(f"data/stats.json", 'w') as f:
            json.dump(entry, f, indent=2)
        raidInProgress = True if discord.utils.get(ctx.guild.text_channels, name="rsm-raid-logs") else False
        if not raidInProgress: return await self.toggleRaid(True, ctx)
        elif toggle: return await self.toggleRaid(False, ctx)
        else: return await self.raidUI(ctx)
    
    @commands.command()
    @commands.guild_only()
    async def raidrestore(self, ctx, url: typing.Optional[str]):
        if not (ctx.author.guild_permissions.administrator or (ctx.author.guild_permissions.manage_channels and ctx.author.guild_permissions.manage_server)): return await ctx.send(embed=self.createEmbed(f"{emojis['raidlock']} Looks like you don't have permissions", "You need the `administrator` or both `manage_server` and `manage_channels` permissions to toggle raid.", colours["delete"]), delete_after=10)
        if not url:  return await ctx.send(embed=self.createEmbed(f"{emojis['raidlock']} No link", "Please provide a link to use for restoring your server.", colours["delete"]), delete_after=10)
        if not url.startswith("https://"): url = "https://" + str(url)
        url = str(url).replace("com/", "com/raw/")

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}") as resp:
                data = json.loads(await resp.text())
                for key in data:
                    perms = discord.Permissions()
                    perms.value = data[key]
                    try: await ctx.guild.get_role(int(key)).edit(permissions=perms)
                    except: pass
        return await ctx.send(embed=self.createEmbed(f"{emojis['raidlock']} Your server is restored", "Everything should be back to normal. If it isn't, just make sure you used the right link.", colours["create"]), delete_after=10)
        
    async def raidUI(self, ctx):
        createEmbed = self.createEmbed
        m = await ctx.send(embed=self.loadingEmbed)
        for r in [729764053861400637, 729764053941223476, 729064530797133875, 729764062270980096, 777143043711172608, 729064530310594601]: await m.add_reaction(self.bot.get_emoji(r))
        desc = \
            f"Note: if you cannot end a raid normally, you can do `{ctx.prefix}raidrestore` followed by the link I sent instead.\n" + \
            f"**Options:**\n\n" + \
            f"{emojis['PunBan']     } Mass ban mentioned users\n" + \
            f"{emojis['PunSoftBan'] } Ban members that joined recently\n" + \
            f"{emojis['purge']      } Purge chat\n" + \
            f"{emojis['PunHistory'] } Clear messages by users\n" + \
            f"{emojis['raidlock']   } End raid\n" + \
            f"{emojis['cross']      } Close"

        for _ in range(50):
            await m.clear_reactions()
            for r in [729764053861400637, 729764053941223476, 729064530797133875, 729764062270980096, 777143043711172608, 729064530310594601]: await m.add_reaction(self.bot.get_emoji(r))

            await m.edit(embed=createEmbed(title=f"{emojis['raidlock']} Raid in progress", description=desc, color=colours["create"]))

            reaction = None
            try: reaction = await ctx.bot.wait_for('reaction_add', timeout=120, check=lambda emoji, user : emoji.message.id == m.id and user == ctx.author)
            except asyncio.TimeoutError: break

            try: await m.remove_reaction(reaction[0].emoji, ctx.author)
            except: pass
            reactionname = reaction[0].emoji.name.lower()

            if reaction == None:                  break
            elif reactionname == "punishban":     await self.ban(m, ctx)
            elif reactionname == "punishsoftban": await self.timeban(m, ctx)
            elif reactionname == "purge":         await self.purge(m, ctx)
            elif reactionname == "punishhistory": await self.clear(m, ctx)
            elif reactionname == "raid":          await self.toggleRaid(False, ctx)
            else:                                 break

        await m.edit(embed=createEmbed(title=f"{emojis['raidlock']} Raid in progress", description=desc, color=colours["delete"]))
        await m.clear_reactions()

    async def timeban(self, m, ctx):
        await m.clear_reactions()
        createEmbed = self.createEmbed
        if not ctx.author.guild_permissions.ban_members: return await m.edit(embed=createEmbed(f"{emojis['raidlock']}","You don't have permission to use this function",color=colours["delete"]))
        await m.edit(embed=createEmbed(f"{emojis['raidlock']} Ban users","Ban users that joined in the last `x` minutes. Type `cancel` to cancel.",color=colours["create"]))
        mess = await ctx.bot.wait_for('message', timeout=120, check=lambda message : message.author == ctx.author)
        if m.content.lower() != "cancel":
            try: time = int(re.sub(r"[^0-9]*", "", str(mess.content))) * 60000
            except: time = 1800000
            if (ctx.guild.me.joined_at - datetime.now()).total_seconds() < time:
                return await m.edit(embed=createEmbed(f"{emojis['raidlock']} Banned users",f"I joined before this point, and I may ban a lot of members!",color=colours["create"]))
            for member in ctx.guild.members:
                d = datetime.strptime(str(member.joined_at), "%Y-%m-%d %H:%M:%S.%f").strftime('%s.%f')
                d_in_ms = int(float(d)*1000)
                if (int(timeimp.time()) - d_in_ms) <= time:
                    try: await ctx.guild.ban(member)
                    except: pass

            await m.edit(embed=createEmbed(f"{emojis['raidlock']} Banned users",f"Banned users that joined in the last {time/60000} minutes.",color=colours["create"]))
            await asyncio.sleep(3)
        return m

    async def ban(self, m, ctx):
        await m.clear_reactions()
        createEmbed = self.createEmbed
        if not ctx.author.guild_permissions.ban_members: return await m.edit(embed=createEmbed(f"{emojis['raidlock']}","You don't have permission to use this function",color=colours["delete"]))
        await m.edit(embed=createEmbed(f"{emojis['raidlock']} Ban users","Mention all the users you want to ban. Type `cancel` to cancel.",color=colours["create"]))
        mess = await ctx.bot.wait_for('message', timeout=120, check=lambda message : message.author == ctx.author)
        if m.content.lower() != "cancel":
            mentions = mess.mentions
            for mention in mentions:
                await ctx.guild.ban(mention)
            await m.edit(embed=createEmbed(f"{emojis['raidlock']} Banned users",f"{' '.join([mem.name for mem in mentions])}",color=colours["create"]))
            await ascyncio.sleep(3)
        return m

    async def clear(self, m, ctx):
        await m.clear_reactions()
        createEmbed = self.createEmbed
        await m.edit(embed=createEmbed(f"{emojis['raidlock']} Clear messages by user",f"Mention all the users to clear from this chat. Type `cancel` to cancel.", color=colours["create"]))
        mess = await ctx.bot.wait_for('message', timeout=120, check=lambda message : message.author == ctx.author)
        if m.content.lower() != "cancel":
            mentions = [x.id for x in mess.mentions]
            a = await ctx.channel.purge(limit=500, check=lambda mes : mes.author.id in mentions and mes.id != m.id)
            await m.edit(embed=createEmbed(f"{emojis['raidlock']} Cleared messages by users",f"Cleared {len(a)} messages by {' '.join([mem.name for mem in mess.mentions])}", color=colours["create"]))
            await asyncio.sleep(3)
        return m
    
    async def purge(self, m, ctx):
        await m.clear_reactions()
        createEmbed = self.createEmbed
        out, m = await self.intHandler(
            m, 
            {
                "cancel": {"title": f"{emojis['raidlock']} Purge Channel", "desc": f"Purge Channel cancelled.", "col": colours["delete"]},
                "prompt": {"title": f"{emojis['raidlock']} Purge Channel", "desc": f"How many messages in this channel should I clear? Max 100. Type `cancel` to cancel.", "col": colours["create"]},
                "default": 50
            },
            ctx
        )
        try: 
            try: out = int(out)
            except: return await m.edit(embed=createEmbed(f"{emojis['raidlock']} Purge Channel", f"Something went wrong, I couldn't delete that many messages.", colours["create"]))
            out += 2
            if out > 100: out = 100
            deleted = await ctx.channel.purge(limit=int(out))
            try: await m.edit(embed=createEmbed(f"{emojis['raidlock']} Purge Channel", f"I deleted {len(deleted)-2} messages.", colours["create"]), delete_after=10)
            except discord.ext.commands.errors.CommandInvokeError: await ctx.send(embed=createEmbed(f"{emojis['raidlock']} Purge Channel", f"I deleted {len(deleted)} messages.", colours["create"]), delete_after=10)
            except discord.errors.NotFound: await ctx.send(embed=createEmbed(f"{emojis['raidlock']} Purge Channel", f"I deleted {len(deleted)} messages.", colours["create"]), delete_after=10)
        except:
            try: await m.edit(embed=createEmbed(f"{emojis['raidlock']} Purge Channel", f"Something went wrong. I may not have permission to do that.", colours["delete"]), delete_after=10)
            except discord.ext.commands.errors.CommandInvokeError: await ctx.send(embed=createEmbed(f"{emojis['raidlock']} Purge Channel", f"Something went wrong. I may not have permission to do that.", colours["delete"]), delete_after=10)
            except discord.NotFound: await ctx.send(embed=createEmbed(f"{emojis['raidlock']} Purge Channel", f"Something went wrong. I may not have permission to do that.", colours["delete"]), delete_after=10)
        try: await m.clear_reactions() 
        except: pass
        return m

    
    async def toggleRaid(self, toggle, ctx):
        createEmbed = self.createEmbed
        if not (ctx.author.guild_permissions.administrator or (ctx.author.guild_permissions.manage_channels and ctx.author.guild_permissions.manage_server)): return await ctx.send(embed=self.createEmbed(f"{emojis['raidlock']} Looks like you don't have permissions", "You need the `administrator` or both `manage_server` and `manage_channels` permissions to toggle raid.", colours["delete"]), delete_after=10)
        m = await ctx.send(embed=createEmbed(f"{emojis['raidlock']} Raid", f"You are now {'entering' if toggle else 'leaving'} guild lockdown. {'We have to add a small delay between roles to ensure all roles are changed' if toggle else ''}", color=colours["delete"]))
        if toggle == True:
            logChannel = discord.utils.get(ctx.guild.text_channels, name="rsm-raid-logs")
            permsToStore = {}
            roles = ctx.guild.roles
            for role in roles:
                await asyncio.sleep(1)
                permsToStore[role.id] = role.permissions.value
                if not role.permissions.manage_messages:
                    roleperms = role.permissions
                    roleperms.send_messages = False
                    try: await role.edit(permissions=roleperms)
                    except: pass
                else:
                    roleperms = role.permissions
                    roleperms.send_messages = True
                    try: await role.edit(permissions=roleperms)
                    except: pass

            embed = createEmbed(f"{emojis['raidlock']} Raid in progress", f"This server is in guild lockdown.", color=colours["edit"])
            await m.edit(embed=embed)
            if logChannel == None:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                try: logChannel = await ctx.guild.create_text_channel('rsm-raid-logs', overwrites=overwrites)
                except: logChannel = ctx.channel
            url = await postbin.postAsync(json.dumps(permsToStore))
            await logChannel.send(f"`ROLE PERMISSIONS: {url}`\n> Raid: Every role in the server without `manage_messages` has lost permission to send messages. To end a raid, type `{ctx.prefix}raid off`. Role permissions have been stored, and can be restored when you run the raid off command. After 30 days, the logs will be deleted.\nPlease do not send any messages in this chat.")
            await self.raidUI(ctx)
            
        if toggle == False:
            logChannel = discord.utils.get(ctx.guild.channels, name="rsm-raid-logs")
            if logChannel == None: 
                try:
                    await m.edit(embed=createEmbed(f"{emojis['raidlock']} Raid", f"You are either not in a raid mode, or the log channel never got deleted. If you have a link that got sent in a different channel, please send just the link below. Otherwise, say `cancel`.", color=colours["create"]))
                    msg = await self.bot.wait_for('message', check=lambda message: message.author.id == ctx.author.id and message.channel.id == ctx.channel.id, timeout=60.0)
                    m2 = msg
                    match = re.match(r"^(?:https:\/\/)?(.+)\/(.*)$", msg.content)
                    if not match: return await ctx.send(emebed=createEmbed(f"{emojis['raidlock']} Raid", f"Got an invalid response. Please make sure to send only the link (can be without the `https://`, eg `https://hastebin.com/yazotefono` or `hastebin.com/yazotefono`)", color=colours["delete"]))
                except asyncio.TimeoutError:
                    return await m.edit(embed=createEmbed(f"{emojis['raidlock']} Raid", f"You are either not in a raid mode, or the log channel never got deleted. If you have a link that got sent in a different channel, please send just the link below. Otherwise, say `cancel`.", color=colours["delete"]))
            try:
                match
                matchExists = True
            except UnboundLocalError:
                matchExists = False
            if not matchExists: 
                m2 = await logChannel.fetch_message(logChannel.last_message_id)
                match = re.match(r"`ROLE PERMISSIONS: https:\/\/(.*)\/(.*)`(?:.|\n)*", m2.content)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://{match.group(1)}/raw/{match.group(2)}") as resp:
                    data = json.loads(await resp.text())
                    try: await logChannel.delete()
                    except: pass
                    for key in data:
                        await asyncio.sleep(1)
                        perms = discord.Permissions()
                        perms.value = data[key]
                        try: await ctx.guild.get_role(int(key)).edit(permissions=perms)
                        except: pass
            await m.edit(embed=createEmbed(f"{emojis['raidlock']} Raid", f"The server has ended its lockdown.", color=colours["create"]))
            
def setup(bot): bot.add_cog(Raid(bot))