import asyncio
import datetime
import json
import typing

import discord
from cogs.consts import *
from discord.ext import commands


class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def modmail(self, ctx):
        m = await ctx.send(embed=loadingEmbed)
        for r in [787987508465238026, 787987508507967488, 729066924943737033, 729763053352124529, 729064530310594601]:
            await m.add_reaction(self.bot.get_emoji(r))
            await asyncio.sleep(0.1)
        while True:
            active = 0
            archived = 0
            try:
                with open(f"data/guilds/{ctx.guild.id}.json") as f:
                    entry = json.load(f)
                    if "modmail" not in entry:
                        entry["modmail"] = {"cat": None, "max": 0, "mention": None}
                        with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                            json.dump(entry, f, indent=2)
                    try:
                        cname = entry["modmail"]
                        active = sum([1 if c.topic.split(" ")[1] == "Active" else 0 for c in ctx.guild.get_channel(cname["cat"]).channels]) if cname["cat"] else 0
                        archived = sum([1 if c.topic.split(" ")[1] == "Archived" else 0 for c in ctx.guild.get_channel(cname["cat"]).channels]) if cname["cat"] else 0
                        maxtickets = "*No limit set*" if not cname["max"] else cname["max"]
                        mention = "*No role*" if not cname["mention"] else f'<@&{cname["mention"]}>'
                        cname = "*No category set*" if not cname["cat"] else self.bot.get_channel(cname["cat"]).name
                    except KeyError:
                        cname = "*No category set*"
                        maxtickets = "*No limit set*"
            except FileNotFoundError:
                cname = "*Modmail not enabled*"
                maxtickets = "*Modmail not enabled*"
            await m.edit(embed=discord.Embed(
                title=f"{emojis['webhook_create']} Modmail Setup",
                description=f"**Active tickets:** {active}\n"
                            f"**Archived tickets:** {archived}\n\n"
                            f"**Maximum tickets per user:** {maxtickets}\n"
                            f"**Mention for new tickets:** {mention}\n"
                            f"**Modmail Category:** {cname}\n\n"
                            f"{emojis['catCreate']} Set category | {emojis['catDelete']} Clear channnel | {emojis['channel_create']} Maximum tickets per user | {emojis['mod_changed']} Support mention",
                color=colours["create"]
            ).set_footer(text="If you haven't already, it is recommended that you do not allow anyone permission to your modmail category. RSM will handle that automatically"))
            try:
                reaction = await ctx.bot.wait_for('reaction_add', timeout=120, check=lambda emoji, user: emoji.message.id == m.id and user == ctx.author)
            except asyncio.TimeoutError:
                break

            try:
                await m.remove_reaction(reaction[0].emoji, ctx.author)
            except Exception as e:
                pass
            reactionname = reaction[0].emoji.name
            if reactionname == "ChannelCreate":
                await m.edit(embed=discord.Embed(
                    title=f"{emojis['webhook_create']} Modmail Setup",
                    description=f"How many active tickets should a user be able to have? `0` is infinite, or type `none` to cancel",
                    color=colours["create"]
                ))

                try:
                    message = await ctx.bot.wait_for('message', timeout=120, check=lambda message: message.channel.id == m.channel.id and ctx.author.id == message.author.id)
                except asyncio.TimeoutError:
                    break
                await message.delete()

                a = 0
                if message.content.lower() != "none":
                    if message.content.isdigit():
                        a = int(message.content)

                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                    entry["modmail"]["max"] = a
                    json.dump(entry, f, indent=2)

            elif reactionname == "CatCreate":
                await m.edit(embed=discord.Embed(
                    title=f"{emojis['webhook_create']} Modmail Setup",
                    description=f"Send a category name or ID. Type `none` to disable modmail",
                    color=colours["create"]
                ))

                try:
                    message = await ctx.bot.wait_for('message', timeout=120, check=lambda message: message.channel.id == m.channel.id and ctx.author.id == message.author.id)
                except asyncio.TimeoutError:
                    break
                await message.delete()

                try:
                    if message.content.lower() != "none":
                        r = await commands.CategoryChannelConverter().convert(await self.bot.get_context(message), message.content.strip())
                        channel = r.id if r.guild.id == ctx.guild.id else None
                    else:
                        channel = None
                except commands.ChannelNotFound:
                    channel = None

                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                    entry["modmail"]["cat"] = channel
                    json.dump(entry, f, indent=2)

            elif reactionname == "ServerModerationUpdate":
                await m.edit(embed=discord.Embed(
                    title=f"{emojis['webhook_create']} Modmail Setup",
                    description=f"What role should be mentioned when a new ticket is created?\nSend a role name, mention or ID. Type `none` to select no role",
                    color=colours["create"]
                ))

                try:
                    message = await ctx.bot.wait_for('message', timeout=120, check=lambda message: message.channel.id == m.channel.id and ctx.author.id == message.author.id)
                except asyncio.TimeoutError:
                    break
                await message.delete()

                try:
                    if message.content.lower() != "none":
                        r = await commands.RoleConverter().convert(await self.bot.get_context(message), message.content.strip())
                        role = r.id if r.guild.id == ctx.guild.id else None
                    else:
                        role = None
                except commands.RoleNotFound:
                    role = None

                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                    entry["modmail"]["mention"] = role
                    json.dump(entry, f, indent=2)

            elif reactionname == "CatDelete":
                with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                    entry["modmail"]["cat"] = None
                    json.dump(entry, f, indent=2)
            elif reactionname == "Cross":
                break
        await m.clear_reactions()
        active = 0
        try:
            with open(f"data/guilds/{ctx.guild.id}.json") as f:
                entry = json.load(f)
                if "modmail" not in entry:
                    entry["modmail"] = {"cat": None, "max": 0, "mention": None}
                    with open(f"data/guilds/{ctx.guild.id}.json", "w") as f:
                        json.dump(entry, f, indent=2)
                try:
                    cname = entry["modmail"]
                    active = len(ctx.guild.get_channel(cname["cat"]).channels) if cname["cat"] else 0
                    maxtickets = "*No limit set*" if not cname["max"] else cname["max"]
                    mention = "*No role*" if not cname["mention"] else f'<@&{cname["mention"]}>'
                    cname = "*No category set*" if not cname["cat"] else self.bot.get_channel(cname["cat"]).name
                except KeyError:
                    cname = "*No category set*"
                    maxtickets = "*No limit set*"
        except FileNotFoundError:
            cname = "*Modmail not enabled*"
            maxtickets = "*Modmail not enabled*"
        await m.edit(embed=discord.Embed(
            title=f"{emojis['webhook_create']} Modmail Setup",
            description=f"**Active tickets:** {active}\n"
                        f"**Maximum tickets per user:** {maxtickets}\n"
                        f"**Mention for new tickets:** {mention}\n"
                        f"**Modmail Category:** {cname}\n\n"
                        f"{emojis['catCreate']} Set category | {emojis['catDelete']} Clear channnel | {emojis['channel_create']} Maximum tickets per user | {emojis['mod_changed']} Support mention",
            color=colours["delete"]
        ).set_footer(text="If you haven't already, it is recommended that you do not allow anyone permission to your modmail category. RSM will handle that automatically"))

    @commands.command(aliases=["ticket", "tickets"])
    @commands.guild_only()
    async def mail(self, ctx, *, message: typing.Optional[str]):
        m = await ctx.send(embed=loadingEmbed)
        try:
            with open(f"data/guilds/{ctx.guild.id}.json") as f:
                entry = json.load(f)
        except FileNotFoundError:
            return await m.edit(embed=discord.Embed(
                title=f"{emojis['webhook_delete']} Modmail",
                description=f"This server has not set up Modmail. Please contact the mods if you believe this is a mistake.",
                color=colours["delete"]
            ))
        if "modmail" not in entry:
            return await m.edit(embed=discord.Embed(
                title=f"{emojis['webhook_delete']} Modmail",
                description=f"This server has not set up Modmail. Please contact the mods if you believe this is a mistake.",
                color=colours["delete"]
            ))
        users = {}
        for channel in ctx.guild.get_channel(entry["modmail"]["cat"]).channels:
            user = channel.topic.split(" ")[0]
            if channel.topic.split(" ")[1] == "Archived":
                continue
            if user not in users:
                users[user] = 1
            else:
                users[user] += 1
        if str(ctx.author.id) in users and entry["modmail"]["max"] > 0:
            if users[str(ctx.author.id)] >= entry["modmail"]["max"]:
                return await m.edit(embed=discord.Embed(
                title=f"{emojis['webhook_delete']} Modmail",
                description=f"You have reached the ticket limit. Please close one of your current tickets.",
                color=colours["delete"]
            ))

        c = await ctx.guild.create_text_channel(
            name=str(ctx.author.name),
            topic=f"{str(ctx.author.id)} Active",
            category=ctx.guild.get_channel(entry["modmail"]["cat"])
        )
        await c.set_permissions(ctx.author, view_channel=True, send_messages=True)
        created = await c.send(embed=discord.Embed(
            title=f"{ctx.author.name} created a ticket",
            description=f"> Anyone can close this ticket with `{ctx.prefix}close`" + (f"\n\n> {message}" if message else ''),
            color=colours["edit"]
        ).set_footer(text=f"Ticket opened at {datetime.datetime.utcnow().strftime('%Y-%m-%d at %H:%M:%S')}"))
        await c.set_permissions(self.bot.get_guild(ctx.guild.id).get_role(entry['modmail']['mention']), view_channel=True, send_messages=True)
        await c.send(f"<@{ctx.author.id}>" + (f" • <@&{entry['modmail']['mention']}>" if entry['modmail']['mention'] else ''))

        await m.edit(embed=discord.Embed(
            title="Ticket created",
            description=f"You can jump to the channel [here]({created.jump_url})",
            color=colours["create"]
        ))

    @commands.command()
    @commands.guild_only()
    async def close(self, ctx):
        try:
            with open(f"data/guilds/{ctx.guild.id}.json") as f:
                entry = json.load(f)
        except FileNotFoundError:
            return await ctx.send(embed=discord.Embed(
                title=f"{emojis['webhook_delete']} Modmail",
                description=f"This server has not set up Modmail. Please contact the mods if you believe this is a mistake.",
                color=colours["delete"]
            ))

        if ctx.channel.category.id == entry["modmail"]["cat"]:
            if ctx.channel.topic.split(" ")[1] == "Active":
                m = await ctx.send(embed=discord.Embed(
                    title="Deleting",
                    description=f"The ticket will be closed in 5 seconds",
                    color=colours["delete"]
                ))
                await asyncio.sleep(5)
                await ctx.channel.set_permissions(ctx.guild.get_member(int(ctx.channel.topic.split(" ")[0])), view_channel=False, send_messages=False)
                await ctx.channel.edit(topic=f"{ctx.channel.topic.split(' ')[0]} Archived", name=f"{ctx.channel.name}-archived")
                await m.edit(embed=discord.Embed(
                    title="Deleted",
                    description=f"The ticket is now archived. The original user cannot see it.\nUse `{ctx.prefix}close` to delete the channel",
                    color=colours["create"]
                ))
            elif ctx.channel.topic.split(" ")[1] == "Archived":
                m = await ctx.send(embed=discord.Embed(
                    title="Deleting",
                    description=f"This channel will be deleted in 5 seconds",
                    color=colours["delete"]
                ))
                await asyncio.sleep(5)
                await ctx.channel.delete()


def setup(bot):
    bot.add_cog(Modmail(bot))
