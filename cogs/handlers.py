import asyncio
import datetime
from typing import DefaultDict

import discord
import humanize
from discord.ext import commands

from cogs.consts import *


class Failed:
    pass


with open("data/template.json") as f:
    template = json.load(f)


class Handlers:
    def __init__(self, bot):
        self.colours = Cols()
        self.emojis = Emojis
        self.bot = bot

    async def memberHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\nYou can send the members name, ID or mention.\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "")
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Member"))
        await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.cross))
        if optional:
            await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.tick))
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    ctx.bot.wait_for(
                        "reaction_add",
                        timeout=180,
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except (asyncio.exceptions.TimeoutError, TimeoutError):
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request timed out"))
            return Failed()

        for future in done:
            future.exception()
        for future in pending:
            future.cancel()

        await m.clear_reactions()
        response = done.pop().result()
        if isinstance(response, discord.message.Message):
            await response.delete()
            try:
                member = await commands.MemberConverter().convert(await self.bot.get_context(response), response.content)
                return member
            except commands.MemberNotFound:
                await m.edit(embed=discord.Embed(
                    title=f"{emoji} {title}",
                    description=description,
                    colour=self.colours.red
                ).set_footer(text="Member could not be found"))
                return Failed()
        else:
            if response[0].emoji.name == "Tick" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()

    async def roleHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\nYou can send the roles name, ID or mention.\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "")
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Role"))
        await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.cross))
        if optional:
            await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.tick))
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    ctx.bot.wait_for(
                        "reaction_add",
                        timeout=180,
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except (asyncio.exceptions.TimeoutError, TimeoutError):
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request timed out"))
            return Failed()

        for future in done:
            future.exception()
        for future in pending:
            future.cancel()

        await m.clear_reactions()
        response = done.pop().result()
        if isinstance(response, discord.message.Message):
            await response.delete()
            try:
                role = await commands.RoleConverter().convert(await self.bot.get_context(response), response.content)
                return role
            except commands.RoleNotFound:
                await m.edit(embed=discord.Embed(
                    title=f"{emoji} {title}",
                    description=description,
                    colour=self.colours.red
                ).set_footer(text="Role could not be found"))
                return Failed()
        else:
            if response[0].emoji.name == "Tick" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()

    async def channelHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None, accepted=["text", "voice", "announcement", "news"]):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\nYou can send the channel name, ID or mention.\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "")
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Channel"))
        await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.cross))
        if optional:
            await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.tick))
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    ctx.bot.wait_for(
                        "reaction_add",
                        timeout=180,
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except (asyncio.exceptions.TimeoutError, TimeoutError):
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request timed out"))
            return Failed()

        for future in done:
            future.exception()
        for future in pending:
            future.cancel()

        await m.clear_reactions()
        response = done.pop().result()
        if isinstance(response, discord.message.Message):
            await response.delete()
            channel = None
            if "text" in accepted or "announcement" in accepted:
                try:
                    channel = await commands.TextChannelConverter().convert(await self.bot.get_context(response), response.content)
                    if "announcement" not in accepted and channel.is_news():
                        channel = None
                    elif "text" not in accepted and not channel.is_news():
                        channel = None
                except commands.ChannelNotFound:
                    pass
            if "voice" in accepted:
                try:
                    channel = await commands.VoiceChannelConverter().convert(await self.bot.get_context(response), response.content)
                except commands.ChannelNotFound:
                    pass
            if "stage" in accepted:
                try:
                    channel = await commands.StageChannelConverter().convert(await self.bot.get_context(response), response.content)
                except commands.ChannelNotFound:
                    pass
            if not channel:
                await m.edit(embed=discord.Embed(
                    title=f"{emoji} {title}",
                    description=description,
                    colour=self.colours.red
                ).set_footer(text="Channel could not be found"))
                return Failed()
            return channel
        else:
            if response[0].emoji.name == "Tick" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()

    async def categoryHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None, returnNoneType=False):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\nYou can send the category name or ID.\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "")
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Category"))
        await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.cross))
        if optional:
            await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.tick))
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    ctx.bot.wait_for(
                        "reaction_add",
                        timeout=180,
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except (asyncio.exceptions.TimeoutError, TimeoutError):
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request timed out"))
            return Failed()

        for future in done:
            future.exception()
        for future in pending:
            future.cancel()

        await m.clear_reactions()
        response = done.pop().result()
        if isinstance(response, discord.message.Message):
            await response.delete()
            try:
                category = await commands.CategoryChannelConverter().convert(await self.bot.get_context(response), response.content)
                return category
            except commands.ChannelNotFound:
                if returnNoneType:
                    return None
                await m.edit(embed=discord.Embed(
                    title=f"{emoji} {title}",
                    description=description,
                    colour=self.colours.red
                ).set_footer(text="Category could not be found"))
                return Failed()
        else:
            if response[0].emoji.name == "Tick" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()

    async def intHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "")
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Number"))
        await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.cross))
        if optional:
            await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.tick))
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    ctx.bot.wait_for(
                        "reaction_add",
                        timeout=180,
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except (asyncio.exceptions.TimeoutError, TimeoutError):
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request timed out"))
            return Failed()

        for future in done:
            future.exception()
        for future in pending:
            future.cancel()

        await m.clear_reactions()
        response = done.pop().result()
        if isinstance(response, discord.message.Message):
            await response.delete()
            try:
                return int(response.content)
            except ValueError:
                await m.edit(embed=discord.Embed(
                    title=f"{emoji} {title}",
                    description=description,
                    colour=self.colours.red
                ).set_footer(text="An invalid number was provided"))
                return Failed()
        else:
            if response[0].emoji.name == "Tick" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()

    async def strHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "")
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Text"))
        await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.cross))
        if optional:
            await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True).control.tick))
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    ctx.bot.wait_for(
                        "reaction_add",
                        timeout=180,
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except (asyncio.exceptions.TimeoutError, TimeoutError):
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request timed out"))
            return Failed()

        for future in done:
            future.exception()
        for future in pending:
            future.cancel()

        await m.clear_reactions()
        response = done.pop().result()
        if isinstance(response, discord.message.Message):
            await response.delete()
            return str(response.content)
        else:
            if response[0].emoji.name == "Tick" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()

    async def reactionCollector(self, ctx=None, m=None, reactions=[], collect=True, task=None):
        for r in reactions:
            await asyncio.sleep(0.1)
            await m.add_reaction(self.bot.get_emoji(self.emojis(idOnly=True)(r)))

        if not collect:
            return

        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "reaction_add",
                        timeout=180,
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id
                    ),
                    ctx.bot.wait_for(
                        "reaction_remove",
                        timeout=180,
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except (asyncio.exceptions.TimeoutError, TimeoutError, asyncio.exceptions.CancelledError):
            return Failed()

        for future in done:
            future.exception()
        for future in pending:
            future.cancel()

        if task:
            await asyncio.wait_for(task, timeout=10)
            await asyncio.sleep(0.1)
        try:
            reaction = done.pop().result()[0]
        except asyncio.TimeoutError:
            return Failed()
        await m.remove_reaction(reaction, ctx.author)
        return reaction

    async def checkPerms(self, ctx, m, permission, emoji, action, user=True, me=True):
        if not getattr(ctx.author.guild_permissions, permission) and user:
            await m.edit(embed=discord.Embed(
                title=f"{emoji} Missing permissions",
                description=f"You need the `{permission}` permission to {action}.",
                colour=self.colours.red
            ))
            return Failed()
        if not getattr(ctx.guild.me.guild_permissions, permission) and me:
            await m.edit(embed=discord.Embed(
                title=f"{emoji} Missing permissions",
                description=f"I need the `{permission}` permission to {action}.",
                colour=self.colours.red
            ))
            return Failed()
        return

    def fileManager(self, guild, action: str = "r", **kwargs):
        if not isinstance(guild, int):
            guild = guild.id

        match action:
            case "w":
                with open(f"data/guilds/{guild}.json", "w") as f:
                    json.dump(kwargs["data"], f, indent=2)
                return kwargs["data"]

            case "r":
                try:
                    with open(f"data/guilds/{guild}.json", "r") as f:
                        entry = json.load(f)

                    entry = self.defaultDict(entry, template)
                    return entry

                except FileNotFoundError:
                    t = template
                    t["guild_info"]["id"] = guild
                    t["guild_info"]["joined_at"] = str(self.bot.get_guild(guild).me.joined_at)

                    with open(f"data/guilds/{guild}.json", "x") as f:
                        json.dump(t, f, indent=2)
                    return t

            case _:
                return None

    def defaultDict(self, data, ref):
        for key in ref.keys():
            if key not in data:
                data[key] = ref[key]
        for k, v in data.items():
            if isinstance(v, dict) and k in ref:
                data[k] = self.defaultDict(data[k], ref[k])
        return data

    def cleanMessageContent(self, content, max_length=1000):
        if content:
            replace = r'\`'
            if len(content) > max_length:
                cut = round(max_length / 2) - 2
                content = (content[:cut] + "\n...\n" + content[-cut:])
            return content.replace("`", replace)
        else:
            return " "

    def betterDelta(self, o):
        if not o:
            return "Never"
        return f"{humanize.naturaltime(datetime.datetime.utcnow()-o)} ({o.strftime('%Y-%M-%d at %H:%m:%S')})"

    def strf(self, o):
        if not o:
            return "Never"
        return o.strftime('%Y-%M-%d at %H:%m:%S')

    def getLogChannel(self, server):
        data = self.fileManager(server)
        if data["log_info"]["log_channel"]:
            return self.bot.get_channel(int(data["log_info"]["log_channel"]))
        else:
            return None

    def convertMessage(self, message, includeNames=True):
        if message.content:
            if includeNames:
                return f"{message.author.name} {self.strf(message.created_at)}\n{message.content}"
            return message.content
        elif len(message.embeds) >= 1:
            strings = []
            if includeNames:
                strings.append(f"{message.author.name} {self.strf(message.created_at)}\n")
            for embed in message.embeds:
                string = ""
                string += "| " + embed.title
                if hasattr(embed, "description"):
                    string += "\n| ".join(embed.description.split("\n"))
                for field in embed.fields:
                    string += f"\n| {field.name}: {field.value}"
                strings.append(string)
            return "\n".join(strings)

    async def getAuditLogEntry(self, guild, type: discord.AuditLogAction, check=None):
        if not guild.me.guild_permissions.view_audit_log:
            raise commands.BotMissingPermissions(["view_audit_log"])
        async for log in guild.audit_logs(action=type):
            if check:
                if check(log):
                    return log
                else:
                    continue
            else:
                return log
        else:
            return None

    async def sendLog(self, emoji, type, server, colour, data, jump_url=""):
        channel = self.getLogChannel(server)
        if channel is None:
            return
        if jump_url:
            jump_url = f"\n[[Jump to message]]({jump_url})"
        await channel.send(embed=discord.Embed(
            title=f"{emoji} {type}",
            description="\n".join([f"**{k}:** {v}" for k, v in data.items()]) + jump_url,
            colour=colour,
            timestamp=datetime.datetime.utcnow()
        ).set_footer(text="All times are in UTC"))
