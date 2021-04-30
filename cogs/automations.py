import discord
import json
import re
import datetime
import asyncio

from discord.ext import commands

from cogs.consts import *


class Automations(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loadingEmbed = loadingEmbed

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            with open(f"data/guilds/{member.guild.id}.json") as entry:
                entry = json.load(entry)
        except FileNotFoundError:
            return
        if "welcome" in entry:
            w = entry["welcome"]
            if w["role"]:
                await member.add_roles(member.guild.get_role(w["role"]))
            if w["message"]["channel"] and w["message"]["text"]:
                if w["message"]["channel"] == "dm":
                    await member.send(w["message"]["text"].replace("[@]", member.mention).replace("[mc]", str(len(member.guild.members))))
                else:
                    await member.guild.get_channel(w["message"]["channel"]).send(w["message"]["text"].replace("[@]", member.mention).replace("[mc]", str(len(member.guild.members))))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        try:
            with open(f"data/guilds/{message.guild.id}.json") as entry:
                entry = json.load(entry)
        except FileNotFoundError:
            return
        if "invite" in entry:
            if not entry["invite"]["enabled"]:
                return
            if message.channel.id in entry["invite"]["whitelist"]["channels"]:
                return
            if message.author.id in entry["invite"]["whitelist"]["members"]:
                return
            if "roles" in entry["invite"]["whitelist"]:
                for role in entry["invite"]["whitelist"]["roles"]:
                    if role in [r.id for r in message.author.roles]:
                        return
            if re.search(r"(?:https?:\/\/)?discord(?:app)?\.(?:com\/invite|gg)\/[a-zA-Z0-9]+\/?", message.content, re.MULTILINE):
                await message.delete()
                if entry["log_info"]["log_channel"]:
                    await message.guild.get_channel(entry["log_info"]["log_channel"]).send(embed=discord.Embed(
                        title=emojis['invite_delete'] + " Invite sent",
                        description=(
                            (f"```{message.clean_content[:2042].replace('```', '***')}```\n" if message.content else "") +
                            f"**Channel:** {message.channel.mention}\n"
                            f"**Sent By:** {message.author.mention}"
                        ),
                        color=colours["delete"],
                        timestamp=datetime.datetime.utcnow()
                    ))

    @commands.command(aliases=["auto", "automation"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def automations(self, ctx):
        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
            entry = json.load(entry)
            write = False
            if "welcome" not in entry:
                write = True
                entry["welcome"] = {"message": {"channel": None, "text": None}, "role": None}
            if "invite" not in entry:
                write = True
                entry["invite"] = {"enabled": False, "whitelist": {"servers": [], "members": [], "roles": [], "channels": []}}
            if "images" not in entry:
                write = True
                entry["images"] = {"toosmall": False}
            if "nsfw" not in entry:
                write = True
                entry["nsfw"] = True
            if "wordfilter" not in entry:
                write = True
                entry["wordfilter"] = {"ignore": {"roles": [], "channels": [], "members": [], "delta": None}, "banned": [], "soft": []}
            if "soft" not in entry["wordfilter"]:
                write = True
                entry["wordfilter"]["soft"] = []
            if "roles" not in entry["invite"]['whitelist']:
                write = True
                entry["invite"]["whitelist"]['roles'] = []
            if write:
                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                    json.dump(entry, f, indent=2)
        m = await ctx.send(embed=loadingEmbed)
        pages = ["filter", "nsfw", "welcome", "invite", "images"]
        page = 0
        skip = False
        while True:
            page = max(0, min(page, len(pages)-1))
            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
            if not skip:
                await m.add_reaction(self.bot.get_emoji(729064530310594601))
                await m.add_reaction(self.bot.get_emoji(729762938411548694))
                await m.add_reaction(self.bot.get_emoji(729762938843430952))
                await m.add_reaction(self.bot.get_emoji(752570111063228507))
            else:
                skip = False
            if pages[page] == "filter":
                wf = entry['wordfilter']
                await m.edit(embed=discord.Embed(
                    title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                    description=f"**Exempt users:** {', '.join([ctx.guild.get_member(u).mention for u in wf['ignore']['members']]) or 'None'}\n"
                                f"**Exempt roles:** {', '.join([ctx.guild.get_role(u).mention for u in wf['ignore']['roles']]) or 'None'}\n"
                                f"**Exempt channels:** {', '.join([ctx.guild.get_channel(u).mention for u in wf['ignore']['channels']]) or 'None'}\n\n"
                                f"**Banned words (strict):**\n> {', '.join(['||' + w + '||' for w in wf['banned']]) or 'None'}\n"
                                f"**Banned words (soft):**\n> {', '.join(['||' + w + '||' for w in wf['soft']]) or 'None'}\n",
                    color=colours["create"]
                ))
                try:
                    reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                except asyncio.TimeoutError:
                    break

                try:
                    await asyncio.sleep(0.1)
                    await m.remove_reaction(reaction[0].emoji, ctx.author)
                except Exception as e:
                    print(e)

                if reaction is None:
                    break
                elif reaction[0].emoji.name == "Right":
                    page += 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "Left":
                    page -= 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "ServerRole":
                    await asyncio.sleep(0.1)
                    await m.clear_reactions()
                    for r in [
                        729064531107774534, 752570111281594509, 729763053352124529,
                        729066924943737033, 837355918831124500, 826823515268186152,
                        826823514904330251, 837355918420869162
                    ]:
                        await asyncio.sleep(0.1)
                        await m.add_reaction(self.bot.get_emoji(r))
                    while True:
                        with open(f"data/guilds/{ctx.guild.id}.json", "r") as e:
                            entry = json.load(e)
                        wf = entry['wordfilter']
                        await m.edit(embed=discord.Embed(
                            title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                            description=f"<:a:752570111281594509> **Exempt users:** {', '.join([ctx.guild.get_member(u).mention for u in wf['ignore']['members']]) or 'None'}\n"
                                        f"<:a:729763053352124529> **Exempt roles:** {', '.join([ctx.guild.get_role(u).mention for u in wf['ignore']['roles']]) or 'None'}\n"
                                        f"<:a:729066924943737033> **Exempt channels:** {', '.join([ctx.guild.get_channel(u).mention for u in wf['ignore']['channels']]) or 'None'}\n\n"
                                        f"<:a:837355918831124500> **Banned words (strict):** Appearances anywhere in a message\n> {', '.join(['||' + w + '||' for w in wf['banned']]) or 'None'}\n"
                                        f"<:a:826823514904330251> **Banned words (soft):** Appearences surrounded by spaces or punctuation\n> {', '.join(['||' + w + '||' for w in wf['soft']]) or 'None'}\n",
                            color=colours["create"]
                        ))
                        try:
                            reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                        except asyncio.TimeoutError:
                            break

                        try:
                            await m.remove_reaction(reaction[0].emoji, ctx.author)
                        except Exception as e:
                            print(e)

                        if reaction is None:
                            break
                        elif reaction[0].emoji.name == "MembersRole":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which members should be allowed to use banned words - Allows mentions, names or IDs",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                break

                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "cancel":
                                continue
                            if message.content.lower() == "none":
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["wordfilter"]["ignore"]["members"] = []
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                                continue
                            members = []
                            for s in message.content.split(" "):
                                try:
                                    r = await commands.MemberConverter().convert(await self.bot.get_context(message), s)
                                    members.append(r.id)
                                except commands.MemberNotFound:
                                    pass
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                                entry["wordfilter"]["ignore"]["members"] = members
                                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                    json.dump(entry, f, indent=2)
                        elif reaction[0].emoji.name == "ServerModerationUpdate":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which roles should be allowed to use banned words - Allows mentions, names or IDs",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                break
                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "cancel":
                                continue
                            if message.content.lower() == "none":
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["wordfilter"]["ignore"]["roles"] = []
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                                continue
                            roles = []
                            for s in message.content.split(" "):
                                try:
                                    r = await commands.RoleConverter().convert(await self.bot.get_context(message), s)
                                    roles.append(r.id)
                                except commands.RoleNotFound:
                                    pass
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                                entry["wordfilter"]["ignore"]["roles"] = roles
                                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                    json.dump(entry, f, indent=2)
                        elif reaction[0].emoji.name == "ChannelCreate":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which channels should be allowed to use banned words - Allows mentions, names or IDs",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                break
                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "cancel":
                                continue
                            if message.content.lower() == "none":
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["wordfilter"]["ignore"]["channels"] = []
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                                continue
                            channels = []
                            for s in message.content.split(" "):
                                try:
                                    r = await commands.TextChannelConverter().convert(await self.bot.get_context(message), s)
                                    channels.append(r.id)
                                except commands.ChannelNotFound:
                                    pass
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                                entry["wordfilter"]["ignore"]["channels"] = channels
                                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                    json.dump(entry, f, indent=2)
                        elif reaction[0].emoji.name == "addopp":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which words should be added to the strict banned word list - Separated by spaces",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                break
                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "cancel":
                                continue
                            if message.content.lower() == "none":
                                continue
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                            for s in message.content.split(" "):
                                entry["wordfilter"]["banned"].append(s)
                            with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                json.dump(entry, f, indent=2)
                        elif reaction[0].emoji.name == "add":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which words should be added to the soft banned word list - Separated by spaces",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                break
                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "cancel":
                                continue
                            if message.content.lower() == "none":
                                continue
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                            for s in message.content.split(" "):
                                entry["wordfilter"]["soft"].append(s)
                            with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                json.dump(entry, f, indent=2)
                        elif reaction[0].emoji.name == "remove":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which words should be removed from the strict banned word list - Separated by spaces",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                break

                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "cancel":
                                continue
                            if message.content.lower() == "none":
                                continue
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                            for s in message.content.split(" "):
                                try:
                                    entry["wordfilter"]["banned"].remove(s)
                                except ValueError:
                                    pass
                            with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                json.dump(entry, f, indent=2)
                        elif reaction[0].emoji.name == "removeopp":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which words should be removed from the soft banned word list - Separated by spaces",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                break

                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "cancel":
                                continue
                            if message.content.lower() == "none":
                                continue
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                            for s in message.content.split(" "):
                                try:
                                    entry["wordfilter"]["soft"].remove(s)
                                except ValueError:
                                    pass
                            with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                json.dump(entry, f, indent=2)
                        else:
                            await asyncio.sleep(0.1)
                            await m.clear_reactions()
                            await asyncio.sleep(0.1)
                            break
                else:
                    break
            elif pages[page] == "welcome":
                role = entry['welcome']['role']
                if isinstance(role, int):
                    role = ctx.guild.get_role(role).mention
                welcome = ""
                w = entry['welcome']['message']['text']
                c = entry['welcome']['message']['channel']
                if w is not None:
                    welcome = f"  **Text:**\n> {w}\n"
                    welcome += f"  **Channel**: {self.bot.get_channel(c).mention if isinstance(c, int) else 'DMs' if c is not None else '*None*'}"
                await m.edit(embed=discord.Embed(
                    title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                    description=f"**Welcome role:** {role} (Given to users on join)\n"
                                f"**Welcome message:** {'*Disabled*' if entry['welcome']['message']['channel'] is None else '*Enabled*'}\n"
                                f"{welcome}",
                    color=colours["create"]
                ))
                try:
                    reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                except asyncio.TimeoutError:
                    break

                try:
                    await asyncio.sleep(0.1)
                    await m.remove_reaction(reaction[0].emoji, ctx.author)
                except Exception as e:
                    print(e)

                if reaction is None:
                    break
                elif reaction[0].emoji.name == "Right":
                    page += 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "Left":
                    page -= 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "ServerRole":
                    await asyncio.sleep(0.1)
                    await m.clear_reactions()
                    for r in [729064531107774534, 753259025990418515, 753259024409034896, 753259024358703205]:
                        await asyncio.sleep(0.1)
                        await m.add_reaction(self.bot.get_emoji(r))
                    while True:
                        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                            entry = json.load(entry)
                        welcome = ""
                        role = entry['welcome']['role']
                        if isinstance(role, int):
                            role = ctx.guild.get_role(role).mention
                        w = entry['welcome']['message']['text']
                        c = entry['welcome']['message']['channel']
                        welcome = f"{emojis['2']}  **Text:**\n> {w or '*None*'}\n"
                        welcome += f"{emojis['3']}  **Channel**: {self.bot.get_channel(c).mention if isinstance(c, int) else 'DMs' if c is not None else '*None*'}"
                        await m.edit(embed=discord.Embed(
                            title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                            description=f"{emojis['1']} **Welcome role:** {role} (Given to users on join)\n"
                                        f"**Welcome message:** {'*Disabled*' if entry['welcome']['message']['channel'] is None else '*Enabled*'}\n"
                                        f"{welcome}",
                            color=colours["create"]
                        ))
                        try:
                            reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                        except asyncio.TimeoutError:
                            break

                        try:
                            await m.remove_reaction(reaction[0].emoji, ctx.author)
                        except Exception as e:
                            print(e)

                        if reaction is None:
                            break
                        elif reaction[0].emoji.name == "1_":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"What role should be given to users when they join - Type `cancel` to cancel or `none` if you don't want to give a role",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                break

                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "cancel":
                                continue
                            if message.content.lower() == "none":
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["welcome"]["role"] = None
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                                continue
                            try:
                                r = await commands.RoleConverter().convert(await self.bot.get_context(message), message.content)
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["welcome"]["role"] = r.id
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                            except commands.RoleNotFound:
                                pass
                        elif reaction[0].emoji.name == "2_":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"What text should be sent when someone joins the server? Type `none` for no message or `cancel` to cancel. You can use `[@]` and `[mc]` for the user's mention and server member count",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                await m.clear_reactions()
                                break

                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "none":
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["welcome"]["message"]["text"] = None
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                                continue
                            if message.content.lower() == "cancel":
                                continue
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                                entry["welcome"]["message"]["text"] = message.content
                                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                    json.dump(entry, f, indent=2)
                        elif reaction[0].emoji.name == "3_":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"What channel should the message be sent in? Type `dm` for DMs, `cancel` to cancel or `none` to not send a message",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                await m.clear_reactions()
                                break

                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "none":
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["welcome"]["message"]["channel"] = None
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                                continue
                            if message.content.lower() == "cancel":
                                continue
                            try:
                                r = await commands.TextChannelConverter().convert(await self.bot.get_context(message), message.content)
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["welcome"]["message"]["channel"] = r.id
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                            except commands.ChannelNotFound:
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["welcome"]["message"]["channel"] = "dm"
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                        else:
                            await asyncio.sleep(0.1)
                            await m.clear_reactions()
                            await asyncio.sleep(0.1)
                            break
                else:
                    break
            elif pages[page] == "invite":
                exclude = ""
                w = entry['invite']['whitelist']
                if entry['invite']['enabled']:
                    exclude += f"  **Members:** {', '.join([ctx.guild.get_member(mem).mention for mem in w['members']])}\n"
                    exclude += f"  **Channels**: {', '.join([self.bot.get_channel(cha).mention for cha in w['channels']])}\n"
                    exclude += f"  **Roles**: {', '.join([ctx.guild.get_role(cha).mention for cha in w['roles']])}"
                await m.edit(embed=discord.Embed(
                    title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                    description=f"**Invite deletion:** {'Enabled' if entry['invite']['enabled'] else 'Disabled'}\n"
                                f"{exclude}",
                    color=colours["create"]
                ))
                try:
                    reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                except asyncio.TimeoutError:
                    break

                try:
                    await asyncio.sleep(0.1)
                    await m.remove_reaction(reaction[0].emoji, ctx.author)
                except Exception as e:
                    print(e)

                if reaction is None:
                    break
                elif reaction[0].emoji.name == "Right":
                    page += 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "Left":
                    page -= 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "ServerRole":
                    await asyncio.sleep(0.1)
                    await m.clear_reactions()
                    for r in [729064531107774534, 753259025990418515, 753259024409034896, 753259024358703205, 753259024555835513]:
                        await asyncio.sleep(0.1)
                        await m.add_reaction(self.bot.get_emoji(r))
                    while True:
                        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                            entry = json.load(entry)
                        welcome = ""
                        role = entry['welcome']['role']
                        if isinstance(role, int):
                            role = ctx.guild.get_role(role).mention
                        exclude = ""
                        w = entry['invite']['whitelist']
                        exclude += f"{emojis['2']}   **Members:** {', '.join([ctx.guild.get_member(mem).mention for mem in w['members']])}\n"
                        exclude += f"{emojis['3']}   **Channels**: {', '.join([self.bot.get_channel(cha).mention for cha in w['channels']])}\n"
                        exclude += f"{emojis['4']}   **Roles**: {', '.join([ctx.guild.get_role(cha).mention for cha in w['roles']])}"
                        await m.edit(embed=discord.Embed(
                            title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                            description=f"{emojis['1']} **Invite deletion:** {'Enabled' if entry['invite']['enabled'] else 'Disabled'}\n"
                                        f"{exclude}",
                            color=colours["create"]
                        ))
                        try:
                            reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                        except asyncio.TimeoutError:
                            break

                        try:
                            await m.remove_reaction(reaction[0].emoji, ctx.author)
                        except Exception as e:
                            print(e)

                        if reaction is None:
                            break
                        elif reaction[0].emoji.name == "1_":
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                                entry["invite"]["enabled"] = not entry["invite"]["enabled"]
                                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                    json.dump(entry, f, indent=2)
                            continue
                        elif reaction[0].emoji.name == "2_":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which members should be allowed to send invites? Use their mention, ID or name. Type `none` for no exemptions or `cancel` to cancel",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                await m.clear_reactions()
                                break

                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "none":
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["invite"]["whitelist"]["members"] = []
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                                continue
                            if message.content.lower() == "cancel":
                                continue
                            members = []
                            for s in message.content.split(" "):
                                try:
                                    r = await commands.MemberConverter().convert(await self.bot.get_context(message), s)
                                    members.append(r.id)
                                except commands.MemberNotFound:
                                    pass
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                                entry["invite"]["whitelist"]["members"] = members
                                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                    json.dump(entry, f, indent=2)
                        elif reaction[0].emoji.name == "3_":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which members should allow invites? Use their mention, ID or name. Type `none` for no exemptions or `cancel` to cancel",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                await m.clear_reactions()
                                break

                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "none":
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["invite"]["whitelist"]["channels#"] = []
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                                continue
                            if message.content.lower() == "cancel":
                                continue
                            channels = []
                            for s in message.content.split(" "):
                                try:
                                    r = await commands.TextChannelConverter().convert(await self.bot.get_context(message), s)
                                    channels.append(r.id)
                                except commands.ChannelNotFound:
                                    pass
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                                entry["invite"]["whitelist"]["channels"] = channels
                                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                    json.dump(entry, f, indent=2)
                        elif reaction[0].emoji.name == "4_":
                            await m.edit(embed=discord.Embed(
                                title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                                description=f"Which roles should allow invites? Use its mention, ID or name. Type `none` for no exemptions or `cancel` to cancel",
                                color=colours["create"]
                            ))
                            try:
                                message = await ctx.bot.wait_for("message", timeout=60, check=lambda message: message.channel.id == ctx.channel.id)
                            except asyncio.TimeoutError:
                                await m.clear_reactions()
                                break

                            try:
                                await message.delete()
                            except Exception as e:
                                print(e)
                            if message.content.lower() == "none":
                                with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                    entry = json.load(entry)
                                    entry["invite"]["whitelist"]["roles"] = []
                                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                        json.dump(entry, f, indent=2)
                                continue
                            if message.content.lower() == "cancel":
                                continue
                            roles = []
                            for s in message.content.split(" "):
                                try:
                                    r = await commands.RoleConverter().convert(await self.bot.get_context(message), s)
                                    roles.append(r.id)
                                except commands.RoleNotFound:
                                    pass
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                                entry["invite"]["whitelist"]["roles"] = roles
                                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                    json.dump(entry, f, indent=2)
                        else:
                            await asyncio.sleep(0.1)
                            await m.clear_reactions()
                            await asyncio.sleep(0.1)
                            break
            elif pages[page] == "nsfw":
                await m.edit(embed=discord.Embed(
                    title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                    description=f"**You are {'not ' if entry['nsfw'] else ''}currently moderating NSFW content** like profile pictures and images in chat\n"
                                f"When a user changes their profile picture to something NSFW, you will recieve a message in your stafflog channel\n"
                                f"NSFW images are automatically deleted and logged with normal server logs",
                    color=colours["create"]
                ).set_footer(text="No NSFW filter is 100% accurate, however we try our best to ensure only NSFW content triggers our checks", icon_url=""))
                try:
                    reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                except asyncio.TimeoutError:
                    break

                try:
                    await asyncio.sleep(0.1)
                    await m.remove_reaction(reaction[0].emoji, ctx.author)
                except Exception as e:
                    print(e)

                if reaction is None:
                    break
                elif reaction[0].emoji.name == "Right":
                    page += 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "Left":
                    page -= 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "ServerRole":
                    await asyncio.sleep(0.1)
                    await m.clear_reactions()
                    for r in [729064531107774534, 729064531208175736]:
                        await asyncio.sleep(0.1)
                        await m.add_reaction(self.bot.get_emoji(r))
                    while True:
                        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                            entry = json.load(entry)
                        await m.edit(embed=discord.Embed(
                            title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                            description=f"**You are {'not ' if entry['nsfw'] else ''}currently moderating NSFW content** like profile pictures and images in chat\n"
                                        f"When a user changes their profile picture to something NSFW, you will recieve a message in your stafflog channel\n"
                                        f"NSFW images are automatically deleted and logged with normal server logs",
                            color=colours["create"]
                        ).set_footer(text="No NSFW filter is 100% accurate, however we try our best to ensure only NSFW content triggers our checks", icon_url=""))
                        try:
                            reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                        except asyncio.TimeoutError:
                            break

                        try:
                            await m.remove_reaction(reaction[0].emoji, ctx.author)
                        except Exception as e:
                            print(e)

                        if reaction is None:
                            break
                        elif reaction[0].emoji.name == "NsfwOn":
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                            entry["nsfw"] = not entry["nsfw"]
                            with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                json.dump(entry, f, indent=2)
                            continue
                        else:
                            await asyncio.sleep(0.1)
                            await m.clear_reactions()
                            await asyncio.sleep(0.1)
                            break
            elif pages[page] == "images":
                role = entry['welcome']['role']
                if isinstance(role, int):
                    role = ctx.guild.get_role(role).mention
                await m.edit(embed=discord.Embed(
                    title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                    description=f"**Image too small:** {'Enabled' if entry['images']['toosmall'] else 'Disabled'} (*Deletes small, annoying images*)\n",
                    color=colours["create"]
                ))
                try:
                    reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                except asyncio.TimeoutError:
                    break

                try:
                    await asyncio.sleep(0.1)
                    await m.remove_reaction(reaction[0].emoji, ctx.author)
                except Exception as e:
                    print(e)

                if reaction is None:
                    break
                elif reaction[0].emoji.name == "Right":
                    page += 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "Left":
                    page -= 1
                    skip = True
                    await asyncio.sleep(0.1)
                elif reaction[0].emoji.name == "ServerRole":
                    await asyncio.sleep(0.1)
                    await m.clear_reactions()
                    for r in [729064531107774534, 753259025990418515]:
                        await asyncio.sleep(0.1)
                        await m.add_reaction(self.bot.get_emoji(r))
                    while True:
                        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                            entry = json.load(entry)
                        await m.edit(embed=discord.Embed(
                            title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                            description=f"{emojis['1']} **Image too small:** {'Enabled' if entry['images']['toosmall'] else 'Disabled'} (*Deletes small, annoying images*)\n",
                            color=colours["create"]
                        ))
                        try:
                            reaction = await ctx.bot.wait_for("reaction_add", timeout=60, check=lambda _, user: user == ctx.author)
                        except asyncio.TimeoutError:
                            break

                        try:
                            await m.remove_reaction(reaction[0].emoji, ctx.author)
                        except Exception as e:
                            print(e)

                        if reaction is None:
                            break
                        elif reaction[0].emoji.name == "1_":
                            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                                entry = json.load(entry)
                                entry["images"]["toosmall"] = not entry["images"]["toosmall"]
                                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                                    json.dump(entry, f, indent=2)
                            continue
                        else:
                            await asyncio.sleep(0.1)
                            await m.clear_reactions()
                            await asyncio.sleep(0.1)
                            break
        await m.clear_reactions()


def setup(bot):
    bot.add_cog(Automations(bot))
