import discord
import json
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

    @commands.command(aliases=["auto", "automation"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def automations(self, ctx):
        with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
            entry = json.load(entry)
            if "welcome" not in entry:
                entry["welcome"] = {"message": {"channel": None, "text": None}, "role": None}
                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                    json.dump(entry, f, indent=2)
        m = await ctx.send(embed=loadingEmbed)
        pages = ["welcome"]
        page = 0
        while True:
            with open(f"data/guilds/{ctx.guild.id}.json", "r") as entry:
                entry = json.load(entry)
            await m.add_reaction(self.bot.get_emoji(729064530310594601))
            await m.add_reaction(self.bot.get_emoji(729762938411548694))
            await m.add_reaction(self.bot.get_emoji(729762938843430952))
            await m.add_reaction(self.bot.get_emoji(752570111063228507))
            if pages[page] == "welcome":
                role = entry['welcome']['role']
                if isinstance(role, int):
                    role = ctx.guild.get_role(role).mention
                welcome = ""
                w = entry['welcome']['message']['text']
                c = entry['welcome']['message']['channel']
                if w is not None:
                    welcome = f"  **Text:**\n> {w}\n"
                    welcome += f"  **Channel**: {self.bot.get_channel(c).mention if isinstance(c, int) else 'DMs'}"
                await m.edit(embed=discord.Embed(
                    title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                    description=f"**Welcome role:** {role} (Given to users on join)\n"
                                f"**Welcome message:** {'None' if entry['welcome']['message']['channel'] is None else ''}\n"
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
                elif reaction[0].emoji.name == "Right":
                    page += 1
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
                        if w is not None:
                            welcome = f"{emojis['2']}  **Text:**\n> {w}\n"
                            welcome += f"{emojis['3']}  **Channel**: {self.bot.get_channel(c).mention if isinstance(c, int) else 'DMs'}"
                        await m.edit(embed=discord.Embed(
                            title=f"{emojis['webhook_create']} Automations: {pages[page].capitalize()}",
                            description=f"{emojis['1']} **Welcome role:** {role} (Given to users on join)\n"
                                        f"**Welcome message:** {'None' if entry['welcome']['message']['channel'] is None else ''}\n"
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
                            if message.content.lower() == "none":
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


def setup(bot):
    bot.add_cog(Automations(bot))
