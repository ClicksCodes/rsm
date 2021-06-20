import asyncio
import discord
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed


class Auto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.command()
    @commands.guild_only()
    async def auto(self, ctx):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_guild", self.emojis().webhook.create, "change server automations", me=False), Failed):
            return
        page = 0
        noAdd = False
        while True:
            data = self.handlers.fileManager(ctx.guild)
            match page:
                case 0:
                    punName = {'none': 'No action', 'change': 'Change nickname', 'kick': 'Kick member', 'ban': 'Ban member'}
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().webhook.create} Filters",
                        description=f"**Exempt users:**\n> {' '.join([ctx.guild.get_member(u).mention for u in data['wordfilter']['ignore']['members']])}\n"
                                    f"**Exempt roles:**\n> {' '.join([ctx.guild.get_role(r).mention for r in data['wordfilter']['ignore']['roles']])}\n"
                                    f"**Exempt Channels:**\n> {' '.join([ctx.guild.get_channel(c).mention for c in data['wordfilter']['ignore']['channels']])}\n"
                                    f"**Banned words: (Strict)**\n> {', '.join([f'||{w}||' for w in data['wordfilter']['strict']])}\n"
                                    f"**Banned words: (Soft)**\n> {', '.join([f'||{w}||' for w in data['wordfilter']['soft']])}\n\n"
                                    f"**Punishments:**\n> Nickname contained banned words: {punName[data['wordfilter']['punishment']]}",
                        colour=self.colours.green
                    ))
                case 1:
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().webhook.create} NSFW",
                        description=f"**You are{' not' if data['images']['nsfw'] else ''} currently moderating NSFW content like profile pictures and images in chat**\n"
                                    f"When a user verifies, joins etc. their profile picture will be checked\n"
                                    f"You will recieve a message in your stafflog channel if a user has a NSFW profile picture\n",
                        colour=self.colours.green
                    ).set_footer(text="No NSFW filter is 100% accurate, however we try our best to ensure only NSFW content triggers our checks"))
                case 2:
                    if data['welcome']['role']:
                        r = f"{ctx.guild.get_role(data['welcome']['role']).name} ({ctx.guild.get_role(data['welcome']['role']).mention})"
                    else:
                        r = "None"
                    if data['welcome']['message']['text']:
                        t = data['welcome']['message']['text'].replace("[@]", ctx.author.mention).replace("[mc]", str(len(ctx.guild.members)))
                    else:
                        t = "None"
                    if data['welcome']['message']['channel'] == "dm":
                        c = "DMs"
                    elif isinstance(data['welcome']['message']['channel'], int):
                        c = self.bot.get_channel(int(data['welcome']['message']['channel'])).mention
                    else:
                        c = "None"
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().webhook.create} Welcome",
                        description=f"**Welcome role:** {r}\n"
                                    f"**Welcome message:**\n> {t}\n"
                                    f"**Sent:** {c}\n",
                        colour=self.colours.green
                    ))
                case 3:
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().webhook.create} Invites",
                        description=f"**Invite deletion:** {'Enabled' if data['invite']['enabled'] else 'Disabled'}\n"
                                    f"**Exempt users:**\n> {' '.join([ctx.guild.get_member(u).mention for u in data['invite']['whitelist']['members']])}\n"
                                    f"**Exempt roles:**\n> {' '.join([ctx.guild.get_role(r).mention for r in data['invite']['whitelist']['roles']])}\n"
                                    f"**Exempt Channels:**\n> {' '.join([ctx.guild.get_channel(c).mention for c in data['invite']['whitelist']['channels']])}\n_ _",
                        colour=self.colours.green
                    ))
            r = ["control.cross", "control.left", "control.right", "guild.settings"]
            if noAdd:
                r = []
            reaction = await self.handlers.reactionCollector(ctx, m, reactions=r)
            if isinstance(reaction, Failed):
                break
            await asyncio.sleep(0.1)
            match reaction.emoji.name:
                case "Cross": break
                case "Left":
                    page -= 1
                    noAdd = True
                case "Right":
                    page += 1
                    noAdd = True
                case "ServerRole":
                    match page:
                        case 0:
                            await m.clear_reactions()
                            await self.filters(ctx, m)
                            noAdd = False
                            await m.clear_reactions()
                        case 1:
                            await m.clear_reactions()
                            await self.nsfw(ctx, m)
                            noAdd = False
                            await m.clear_reactions()
                        case 2:
                            await m.clear_reactions()
                            await self.welcome(ctx, m)
                            noAdd = False
                            await m.clear_reactions()
                        case 3:
                            await m.clear_reactions()
                            await self.invite(ctx, m)
                            noAdd = False
                            await m.clear_reactions()
            page = max(0, min(page, 3))
        await asyncio.sleep(0.1)

    async def filters(self, ctx, m):
        await asyncio.sleep(0.1)
        while True:
            await asyncio.sleep(0.1)
            data = self.handlers.fileManager(ctx.guild.id)
            self.handlers.setMem(ctx.guild.id, data)
            punName = {'none': 'No action', 'change': 'Change nickname', 'kick': 'Kick member', 'ban': 'Ban member'}
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().webhook.create} Filters",
                description=f"{self.emojis()('numbers.1.normal')} **Exempt users:**\n> "
                            f"{' '.join([ctx.guild.get_member(u).mention for u in data['wordfilter']['ignore']['members']])}\n"
                            f"{self.emojis()('numbers.2.normal')} **Exempt roles:**\n> {' '.join([ctx.guild.get_role(r).mention for r in data['wordfilter']['ignore']['roles']])}\n"
                            f"{self.emojis()('numbers.3.normal')} **Exempt Channels:**\n> "
                            f"{' '.join([ctx.guild.get_channel(c).mention for c in data['wordfilter']['ignore']['channels']])}\n"
                            f"{self.emojis()('icon.opp.add')} **Banned words: (Strict)**\n> {', '.join([f'||{w}||' for w in data['wordfilter']['strict']])}\n"
                            f"{self.emojis()('icon.add')} **Banned words: (Soft)**\n> {', '.join([f'||{w}||' for w in data['wordfilter']['soft']])}\n\n"
                            f"{self.emojis()('numbers.4.normal')} **Punishments:**\n> Nickname contained banned words: {punName[data['wordfilter']['punishment']]}",
                colour=self.colours.green
            ))
            reaction = await self.handlers.reactionCollector(ctx, m, [
                "control.cross",
                "numbers.1.normal",
                "numbers.2.normal",
                "numbers.3.normal",
                "icon.opp.add",
                "icon.remove",
                "icon.add",
                "icon.opp.remove",
                "numbers.4.normal"
            ])
            if isinstance(reaction, Failed):
                return
            await m.clear_reactions()
            match reaction.emoji.name:
                case "1_":
                    members = await self.handlers.memberHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="Who should be exempt from the filter?",
                        optional=True,
                        multiple=True
                    )
                    if isinstance(members, Failed):
                        continue
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["wordfilter"]["ignore"]["members"] = [m.id for m in members]
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "2_":
                    roles = await self.handlers.roleHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="Which roles should be exempt from the filter?",
                        optional=True,
                        multiple=True
                    )
                    if isinstance(roles, Failed):
                        continue
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["wordfilter"]["ignore"]["roles"] = [r.id for r in roles]
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "3_":
                    channels = await self.handlers.channelHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="Which channels should be exempt from the filter?",
                        optional=True,
                        multiple=True
                    )
                    if isinstance(channels, Failed):
                        continue
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["wordfilter"]["ignore"]["channels"] = [c.id for c in channels]
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "addopp":
                    words = await self.handlers.strHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="What words should be added to the strict list? Separate each word by a space\nStrict words apply anywhere in the message"
                    )
                    if isinstance(words, Failed):
                        continue
                    words = words.split(" ")
                    data = self.handlers.fileManager(ctx.guild.id)
                    for word in words:
                        if word.lower() not in data["wordfilter"]["strict"]:
                            data["wordfilter"]["strict"].append(word.lower())
                    self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "remove":
                    words = await self.handlers.strHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="What words should be removed from the strict list? Separate each word by a space\nStrict words apply anywhere in the message"
                    )
                    if isinstance(words, Failed):
                        continue
                    words = words.split(" ")
                    data = self.handlers.fileManager(ctx.guild.id)
                    w = []
                    for word in data["wordfilter"]["strict"]:
                        if word.lower() not in words:
                            w.append(word.lower())
                    data["wordfilter"]["strict"] = w
                    self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "add":
                    words = await self.handlers.strHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="What words should be added to the soft list? Separate each word by a space\nSoft words apply surrounded by spaces or punctuation"
                    )
                    if isinstance(words, Failed):
                        continue
                    words = words.split(" ")
                    data = self.handlers.fileManager(ctx.guild.id)
                    for word in words:
                        if word.lower() not in data["wordfilter"]["soft"]:
                            data["wordfilter"]["soft"].append(word.lower())
                    self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "removeopp":
                    words = await self.handlers.strHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="What words should be removed from the soft list? Separate each word by a space\nSoft words apply surrounded by spaces or punctuation"
                    )
                    if isinstance(words, Failed):
                        continue
                    words = words.split(" ")
                    data = self.handlers.fileManager(ctx.guild.id)
                    w = []
                    for word in data["wordfilter"]["soft"]:
                        if word.lower() not in words:
                            w.append(word.lower())
                    data["wordfilter"]["soft"] = w
                    self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "4_":
                    val = await self.handlers.intHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="What should happen if a new members username breaks the rules?\n`1` Nothing | `2` Change nickname | `3` Kick | `4` Ban"
                    )
                    if isinstance(words, Failed):
                        continue
                    data = self.handlers.fileManager(ctx.guild.id)
                    match val:
                        case "1": data["wordfilter"]["punishment"] = "none"
                        case "2": data["wordfilter"]["punishment"] = "change"
                        case "3": data["wordfilter"]["punishment"] = "kick"
                        case "4": data["wordfilter"]["punishment"] = "ban"
                        case _: break
                    self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case _: break

    async def nsfw(self, ctx, m):
        await asyncio.sleep(0.1)
        task = asyncio.create_task(self.handlers.reactionCollector(ctx, m, ["control.cross", "numbers.1.normal"], collect=False))
        while True:
            await asyncio.sleep(0.1)
            data = self.handlers.fileManager(ctx.guild.id)
            self.handlers.setMem(ctx.guild.id, data)
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().webhook.create} NSFW",
                description=f"**You are{' not' if data['images']['nsfw'] else ''} currently moderating NSFW content like profile pictures and images in chat**\n"
                            f"When a user verifies, joins etc. their profile picture will be checked\n"
                            f"You will recieve a message in your stafflog channel if a user has a NSFW profile picture\n",
                colour=self.colours.green
            ).set_footer(text="No NSFW filter is 100% accurate, however we try our best to ensure only NSFW content triggers our checks"))
            reaction = await self.handlers.reactionCollector(ctx, m, [], task=task)
            if isinstance(reaction, Failed):
                break
            match reaction.emoji.name:
                case "Cross": break
                case "1_":
                    data = self.handlers.fileManager(ctx.guild.id)
                    data["images"]["nsfw"] = not data["images"]["nsfw"]
                    self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case _: break
        await asyncio.sleep(0.1)

    async def welcome(self, ctx, m):
        await asyncio.sleep(0.1)
        while True:
            await asyncio.sleep(0.1)
            data = self.handlers.fileManager(ctx.guild.id)
            if data['welcome']['role']:
                r = f"{ctx.guild.get_role(data['welcome']['role']).name} ({ctx.guild.get_role(data['welcome']['role']).mention})"
            else:
                r = "None"
            if data['welcome']['message']['text']:
                t = data['welcome']['message']['text'].replace("[@]", ctx.author.mention).replace("[mc]", str(len(ctx.guild.members)))
            else:
                t = "None"
            if data['welcome']['message']['channel'] == "dm":
                c = "DMs"
            elif isinstance(data['welcome']['message']['channel'], int):
                c = self.bot.get_channel(int(data['welcome']['message']['channel'])).mention
            else:
                c = "None"
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().webhook.create} Welcome",
                description=f"{self.emojis()('numbers.1.normal')} **Welcome role:** {r}\n"
                            f"{self.emojis()('numbers.2.normal')} **Welcome message:**\n> {t}\n"
                            f"{self.emojis()('numbers.3.normal')} **Sent:** {c}\n",
                colour=self.colours.green
            ))
            reaction = await self.handlers.reactionCollector(ctx, m, [
                "control.cross",
                "numbers.1.normal",
                "numbers.2.normal",
                "numbers.3.normal",
            ])
            if isinstance(reaction, Failed):
                return
            await asyncio.sleep(0.1)
            await m.clear_reactions()
            match reaction.emoji.name:
                case "1_":
                    role = await self.handlers.roleHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Welcome",
                        description="What role should be given when someone joins?",
                        optional=True
                    )
                    if isinstance(role, Failed):
                        continue
                    if not role:
                        role = None
                    else:
                        role = role.id
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["welcome"]["role"] = role
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "2_":
                    message = await self.handlers.strHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Welcome",
                        description="What message should be sent?\nUse [@] to mention the user and [mc] for tthe server member count",
                        optional=True
                    )
                    if isinstance(message, Failed):
                        continue
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["welcome"]["message"]["text"] = message
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "3_":
                    channel = await self.handlers.channelHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Welcome",
                        description="Where should the message be sent?",
                        optional=True,
                        default="DMs",
                        accepted=["text"]
                    )
                    if isinstance(channel, Failed):
                        channel = None
                    if not channel:
                        channel = None
                    elif channel == "DMs":
                        channel = "dm"
                    else:
                        channel = channel.id
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["welcome"]["message"]["channel"] = channel
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case _: break

    async def invite(self, ctx, m):
        await asyncio.sleep(0.1)
        while True:
            await asyncio.sleep(0.1)
            data = self.handlers.fileManager(ctx.guild.id)
            self.handlers.setMem(ctx.guild.id, data)
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().webhook.create} Invites",
                description=f"{self.emojis()('numbers.1.normal')} **Invite deletion:** {'Enabled' if data['invite']['enabled'] else 'Disabled'}\n"
                            f"{self.emojis()('numbers.2.normal')} **Exempt users:**\n> "
                            f"{' '.join([ctx.guild.get_member(u).mention for u in data['invite']['whitelist']['members']])}\n"
                            f"{self.emojis()('numbers.3.normal')} **Exempt roles:**\n> {' '.join([ctx.guild.get_role(r).mention for r in data['invite']['whitelist']['roles']])}\n"
                            f"{self.emojis()('numbers.4.normal')} **Exempt Channels:**\n> "
                            f"{' '.join([ctx.guild.get_channel(c).mention for c in data['invite']['whitelist']['channels']])}\n_ _",
                colour=self.colours.green
            ))
            reaction = await self.handlers.reactionCollector(ctx, m, [
                "control.cross",
                "numbers.1.normal",
                "numbers.2.normal",
                "numbers.3.normal",
                "numbers.4.normal"
            ])
            if isinstance(reaction, Failed):
                return
            await asyncio.sleep(0.1)
            await m.clear_reactions()
            await asyncio.sleep(0.1)
            match reaction.emoji.name:
                case "1_":
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["invite"]["enabled"] = not data["invite"]["enabled"]
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "2_":
                    members = await self.handlers.memberHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="Which members should be exempt from the filter?",
                        optional=True,
                        multiple=True
                    )
                    if isinstance(members, Failed):
                        continue
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["invite"]["whitelist"]["members"] = [r.id for r in members]
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "3_":
                    roles = await self.handlers.roleHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="Which roles should be exempt from the filter?",
                        optional=True,
                        multiple=True
                    )
                    if isinstance(roles, Failed):
                        continue
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["invite"]["whitelist"]["roles"] = [r.id for r in roles]
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case "4_":
                    channels = await self.handlers.channelHandler(
                        ctx,
                        m,
                        emoji=self.emojis().webhook.create,
                        title="Filters",
                        description="Which channels should be exempt from the filter?",
                        optional=True,
                        multiple=True,
                        accepted=["text"]
                    )
                    if isinstance(channels, Failed):
                        continue
                    embed = m.embeds[0].set_footer(text="Reading")
                    await m.edit(embed=embed)
                    data = self.handlers.fileManager(ctx.guild.id)
                    embed = embed.set_footer(text="Writing")
                    await m.edit(embed=embed)
                    data["invite"]["whitelist"]["channels"] = [r.id for r in channels]
                    data = self.handlers.fileManager(ctx.guild.id, action="w", data=data)
                case _: break


def setup(bot):
    bot.add_cog(Auto(bot))
