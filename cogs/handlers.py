import asyncio
import datetime
from json.decoder import JSONDecodeError
import os
import re
import aiohttp

import discord
from cogs import interactions
from discord.ext import commands

from cogs.consts import *
from config import config
import io
from PIL import Image, ImageDraw, ImageFont


class Failed:
    pass


with open("data/template.json") as f:
    template = json.load(f)


class CustomCTX:
    def __init__(self, bot, author, guild, channel, message=None, interaction=None, m=None):
        self.me = bot
        self.author = author
        self.guild = guild
        self.message = message
        self.channel = channel
        self.interaction = interaction
        self.m = m

    async def delete(self):
        if self.message:
            await self.m.delete()
            return await self.message.delete()
        if self.interaction:
            return await self.m.edit(embed=discord.Embed(
                title="Closed",
                description="Dismiss this message to close it",
                color=Colours().red
            ).set_footer(text="Discord does not, in fact, let you delete messages only you can see :/"), view=None)


class Handlers:
    def __init__(self, bot):
        self.colours = Cols()
        self.emojis = Emojis
        self.bot = bot
        self.interactions = interactions

    def hex_to_rgba(self, value, alpha=255):
        lv = len(value)
        return tuple(int(value[i: i + lv // 3], 16) for i in range(0, lv, lv // 3)) + (alpha,)

    async def memberHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None, multiple=False):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\nYou can send the members name, ID or mention.\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.right} {skip}" if optional else "") + \
            (f"\nYou can select more than one member at a time" if multiple else "")
        v = self.interactions.createUI(ctx, [
            self.interactions.Button(self.bot, emojis=self.emojis, id="ca", emoji="control.cross", title="Cancel")
        ] + [self.interactions.Button(self.bot, emojis=self.emojis, id="sk", emoji="control.right", title="Skip", disabled=not optional)])
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Member"), view=v)
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    v.wait()
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except (asyncio.exceptions.TimeoutError, TimeoutError):
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request timed out"), view=None)
            return Failed()

        for future in done:
            future.exception()
        for future in pending:
            future.cancel()
        if v.selected:
            if v.selected == "sk" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"), view=None)
            return Failed()
        else:
            response = done.pop().result()
            if response.channel.permissions_for(response.channel.guild.me).manage_messages:
                await response.delete()
            if not multiple:
                try:
                    member = await commands.MemberConverter().convert(await self.bot.get_context(response), response.content)
                    return member
                except commands.MemberNotFound:
                    await m.edit(embed=discord.Embed(
                        title=f"{emoji} {title}",
                        description=description,
                        colour=self.colours.red
                    ).set_footer(text="Member could not be found"), view=None)
                    return Failed()

    async def roleHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None, multiple=False):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\nYou can send the roles name, ID or mention.\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "") + \
            (f"\nYou can enter more than one role at a time" if multiple else "")
        v = self.interactions.createUI(ctx, [
            self.interactions.Button(self.bot, emojis=self.emojis, id="ca", emoji="control.cross", title="Cancel")
        ] + [self.interactions.Button(self.bot, emojis=self.emojis, id="sk", emoji="control.right", title="Skip", disabled=not optional)])
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Role"), view=v)
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    v.wait()
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
        except (asyncio.exceptions.TimeoutError, TimeoutError):
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request timed out"), view=None)
            return Failed()

        for future in done:
            future.exception()
        for future in pending:
            future.cancel()
        if v.selected:
            if v.selected == "sk" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"), view=None)
            return Failed()
        else:
            response = done.pop().result()
            if response.channel.permissions_for(response.channel.guild.me).manage_messages:
                await response.delete()
            if not multiple:
                try:
                    role = await commands.RoleConverter().convert(await self.bot.get_context(response), response.content)
                    return role
                except commands.RoleNotFound:
                    await m.edit(embed=discord.Embed(
                        title=f"{emoji} {title}",
                        description=description,
                        colour=self.colours.red
                    ).set_footer(text="Role could not be found"), view=None)
                    return Failed()
            else:
                roles = []
                for role in response.content.split(" "):
                    try:
                        role = await commands.RoleConverter().convert(await self.bot.get_context(response), role)
                        roles.append(role)
                    except commands.RoleNotFound:
                        continue
                return roles

    async def channelHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None, accepted=["text", "voice", "announcement", "stage"], multiple=False):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\nYou can send the channel name, ID or mention.\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "") + \
            (f"\nYou can enter more than one channel at a time" if multiple else "")
        v = self.interactions.createUI(ctx, [
            self.interactions.Button(self.bot, emojis=self.emojis, id="ca", emoji="control.cross", title="Cancel")
        ] + [self.interactions.Button(self.bot, emojis=self.emojis, id="sk", emoji="control.right", title="Skip", disabled=not optional)])
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Channel"), view=v)
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    v.wait()
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
        if v.selected:
            if v.selected == "sk" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()
        else:
            response = done.pop().result()
            if response.channel.permissions_for(response.channel.guild.me).manage_messages:
                await response.delete()
            if not multiple:
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
                if channel.guild.id != ctx.guild.id:
                    await m.edit(embed=discord.Embed(
                        title=f"{emoji} {title}",
                        description=description,
                        colour=self.colours.red
                    ).set_footer(text="Channel was not in this server"))
                    return Failed()
                return channel
            else:
                channels = []
                for channel in response.content.split(" "):
                    if "text" in accepted or "announcement" in accepted:
                        try:
                            channel = await commands.TextChannelConverter().convert(await self.bot.get_context(response), channel)
                            if "announcement" not in accepted and channel.is_news():
                                channel = None
                            elif "text" not in accepted and not channel.is_news():
                                channel = None
                        except commands.ChannelNotFound:
                            pass
                    if "voice" in accepted:
                        try:
                            channel = await commands.VoiceChannelConverter().convert(await self.bot.get_context(response), channel)
                        except commands.ChannelNotFound:
                            pass
                    if "stage" in accepted:
                        try:
                            channel = await commands.StageChannelConverter().convert(await self.bot.get_context(response), channel)
                        except commands.ChannelNotFound:
                            pass
                    if not channel:
                        continue
                    if channel.guild.id != ctx.guild.id:
                        continue
                    channels.append(channel)
                return channels

    async def categoryHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None, returnNoneType=False):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\nYou can send the category name or ID.\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "")
        v = self.interactions.createUI(ctx, [
            self.interactions.Button(self.bot, emojis=self.emojis, id="ca", emoji="control.cross", title="Cancel")
        ] + [self.interactions.Button(self.bot, emojis=self.emojis, id="sk", emoji="control.right", title="Skip", disabled=not optional)])
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Category"), view=v)
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    v.wait()
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
        if v.selected:
            if v.selected == "sk" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()
        else:
            response = done.pop().result()
            if response.channel.permissions_for(response.channel.guild.me).manage_messages:
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

    async def intHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "")
        v = self.interactions.createUI(ctx, [
            self.interactions.Button(self.bot, emojis=self.emojis, id="ca", emoji="control.cross", title="Cancel")
        ] + [self.interactions.Button(self.bot, emojis=self.emojis, id="sk", emoji="control.right", title="Skip", disabled=not optional)])
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Number"), view=v)
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    v.wait()
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

        if v.selected:
            if v.selected == "sk" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()
        else:
            response = done.pop().result()
            if response.channel.permissions_for(response.channel.guild.me).manage_messages:
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

    async def strHandler(self, ctx, m, emoji=None, title="", description="", optional=False, default=None):
        if default:
            optional = True
        skip = f"Default: {default}" if default else "Skip"
        description = f"{description}\n{self.emojis().control.cross} Cancel" + \
            (f"\n{self.emojis().control.tick} {skip}" if optional else "")
        v = self.interactions.createUI(ctx, [
            self.interactions.Button(self.bot, emojis=self.emojis, id="ca", emoji="control.cross", title="Cancel")
        ] + [self.interactions.Button(self.bot, emojis=self.emojis, id="sk", emoji="control.right", title="Skip", disabled=not optional)])
        await m.edit(embed=discord.Embed(
            title=f"{emoji} {title}",
            description=description,
            colour=self.colours.green
        ).set_footer(text="Listening for your next message | Expected: Text"), view=v)
        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "message",
                        timeout=180,
                        check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id
                    ),
                    v.wait()
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

        if v.selected:
            if v.selected == "sk" and optional:
                return default
            await m.edit(embed=discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                colour=self.colours.red
            ).set_footer(text="The request was cancelled"))
            return Failed()
        else:
            response = done.pop().result()
            if response.channel.permissions_for(response.channel.guild.me).manage_messages:
                await response.delete()
            return str(response.content)

    async def checkPerms(self, ctx, m, permission, emoji, action, user=True, me=True, edit=True):
        if not getattr(ctx.channel.permissions_for(ctx.author), permission) and user:
            if edit:
                await m.edit(embed=discord.Embed(
                    title=f"{emoji} Missing permissions",
                    description=f"You need the `{permission}` permission to {action}.",
                    colour=self.colours.red
                ), view=None)
            return Failed()
        if not getattr(ctx.channel.permissions_for(ctx.me), permission) and me:
            if edit:
                await m.edit(embed=discord.Embed(
                    title=f"{emoji} Missing permissions",
                    description=f"I need the `{permission}` permission to {action}.",
                    colour=self.colours.red
                ), view=None)
            return Failed()
        return

    def fileManager(self, guild, action: str = "r", create=True, **kwargs):
        if not isinstance(guild, int):
            guild = guild.id

        match action:
            case "w":
                with open(f"data/guilds/{guild}.json", "w") as f:
                    json.dump(kwargs["data"], f, indent=2)
                with open(f"data/guilds/{guild}.json", "r") as f:
                    entry = json.load(f)
                    try:
                        with open(f"data/backup/{guild}.json", "w") as f:
                            json.dump(entry, f, indent=2)
                    except FileNotFoundError:
                        with open(f"data/backup/{guild}.json", "x") as f:
                            json.dump(entry, f, indent=2)
                return kwargs["data"]

            case "r":
                try:
                    with open(f"data/guilds/{guild}.json", "r") as f:
                        entry = json.load(f)
                    updated = self._update(entry.copy())
                    if updated != entry:
                        self.fileManager(guild, action="w", data=updated)
                    entry = self.defaultDict(updated, template)
                    return entry

                except FileNotFoundError:
                    if create:
                        t = template
                        t["guild_info"]["id"] = guild
                        t["guild_info"]["joined_at"] = str(self.bot.get_guild(guild).me.joined_at)

                        with open(f"data/guilds/{guild}.json", "x") as f:
                            json.dump(t, f, indent=2)
                        return t
                    else:
                        return False

                except (json.decoder.JSONDecodeError, AttributeError):
                    if os.path.exists(f"data/backup/{guild}.json"):
                        with open(f"data/backup/{guild}.json", "r") as f:
                            entry = json.load(f)
                        updated = self._update(entry.copy())
                        if updated != entry:
                            self.fileManager(guild, action="w", data=updated)
                        entry = self.defaultDict(updated, template)
                        self.fileManager(guild, "w", data=entry)
                        return entry
                    else:
                        self.fileManager(guild, action="RESET")
                        return self.fileManager(guild)

            case "RESET":
                if os.path.exists(f"data/guilds/{guild}.json"):
                    os.remove(f"data/guilds/{guild}.json")
                if os.path.exists(f"data/backup/{guild}.json"):
                    os.remove(f"data/backup/{guild}.json")

            case _:
                return None

    def _update(self, data):
        if "version" not in data:
            data["version"] = 1
        if data["version"] == 1:
            data["version"] = 2
            data["log_info"]["ignore"] = data.get("ignore_info", {"bots": True, "members": [], "roles": [], "channels": []})
            if "ignore_info" in data:
                del data["ignore_info"]
            replacements = {"roles": "role_mention", "webhook_create": "webhook_update"}
            data["log_info"]["to_log"] = [(replacements[p] if p in replacements else p) for p in data["log_info"]["to_log"]]
            data["log_info"]["to_log"] += ["guild_role_edit", "user_role_update"]
            data["images"] = {}
            data["images"]["nsfw"] = data.get("nsfw", True)
            if "nsfw" in data:
                del data["nsfw"]
            if "wordfilter" in data:
                data["wordfilter"]["strict"] = data.get("wordfilter", {"banned": []})["banned"]
            if "wordfilter" in data and "banned" in data["wordfilter"]:
                del data["wordfilter"]["banned"]
            if "wordfilter" not in data:
                data["wordfilter"] = {"ignore": {"roles": [], "channels": [], "members": [], "delta": None}, "strict": [], "soft": []}
            data["wordfilter"]["punishment"] = data.get("nameban", "change")
        if data["version"] == 2:
            data["version"] = 3
            data["mute"] = {"role": None}
        if data["version"] == 3:
            pass
        return data

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
        t = round(datetime.datetime.timestamp(o))
        return f"<t:{t}:R> (<t:{t}:D> at <t:{t}:T>)"

    def strf(self, o):
        if not o:
            return "Never"
        t = round(datetime.datetime.timestamp(o))
        return f"<t:{t}:D> at <t:{t}:T>"

    def getLogChannel(self, server):
        data = self.fileManager(server)
        if data["log_info"]["log_channel"]:
            return self.bot.get_channel(int(data["log_info"]["log_channel"]))
        else:
            return None

    def convertMessage(self, message, includeNames=True):
        if message.content:
            if includeNames:
                return f"{message.author.name} {self.strf(message.created_at.replace(tzinfo=None))}\n{message.content}"
            return message.content
        elif len(message.embeds) >= 1:
            strings = []
            if includeNames:
                strings.append(f"{message.author.name} {self.strf(message.created_at.replace(tzinfo=None))}\n")
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
            return None
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

    async def sendLog(self, emoji, type, server, colour, data, jump_url="", extra=""):
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
        ).set_footer(text=extra + (" • " if extra else "") + "All times are in your timezone • Updates on channel refresh"))

    async def is_pfp_nsfw(self, image_url):
        confidence = "80"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepai.org/api/nsfw-detector",
                data={"image": image_url},
                headers={"api-key": config.deepAIkey},
            ) as r:
                nsfw = False
                try:
                    resp = await r.json()
                    score = resp['output']['nsfw_score'] * 100
                    if len([1 for x in resp['output']['detections'] if float(x['confidence']) > 0.75]):
                        nsfw = True
                    if int(score) > int(confidence):
                        nsfw = True
                except KeyError:
                    return (False, {}, 100, None)
        image = None
        if nsfw:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as r:
                    buf = io.BytesIO(await r.read())
                    buf.seek(0)
            image = Image.open(buf)
            h, w = image.size
            scalex, scaley = round(1000/w), round(1000/h)
            image = image.resize((w * scalex, h * scaley))
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype("data/fonts/roboto/Roboto-Regular.ttf", 20)
            for detection in resp["output"]["detections"]:
                if float(detection["confidence"]) > 0.75:
                    bbox = detection["bounding_box"]
                    for i in range(len(bbox)):
                        bbox[i] = bbox[i] * (scaley if i % 2 else scalex)
                    detection["name"] = detection["name"].split(" - ")[0]
                    draw.rectangle([(bbox[0], bbox[1]), (bbox[2], bbox[3])], outline=(242, 120, 120, 255), width=10)
                    w, _ = font.getsize(detection["name"])
                    draw.rectangle([(bbox[0], bbox[1] - 40), (bbox[0] + w + 20, bbox[1])], fill=(242, 120, 120, 255))
                    draw.text((bbox[0] + 10, bbox[1] - 30), detection["name"], fill=(255, 255, 255, 255), font=font)
        return nsfw, resp['output']['detections'], score, image

    def is_text_banned(self, text, guild, member=None, channel=None):
        data = self.checkGuild(guild)
        if isinstance(data, Failed):
            return False
        data = data["filter"]
        if member:
            if member.id in data["ignore"]["members"]:
                return False
            for role in member.roles:
                if role.id in data["ignore"]["roles"]:
                    return False
        if channel:
            if channel.id in data["ignore"]["channels"]:
                return False
        for word in data["strict"]:
            if word in text:
                return True
        for word in [x.group().lower() for x in re.finditer(r'[a-zA-Z]+', text)]:
            if word.lower() in data["soft"]:
                return True
        return False

    def is_channel_locked(self, snowflake):
        symbol = ""
        if isinstance(snowflake, discord.TextChannel):
            symbol = "c"
        elif isinstance(snowflake, discord.Guild):
            symbol = "g"
        if os.path.exists(f"data/locks/{symbol}{snowflake.id}"):
            return True
        return False

    def lock_channel(self, snowflake, lock, info=""):
        symbol = ""
        if isinstance(snowflake, discord.TextChannel):
            symbol = "c"
        elif isinstance(snowflake, discord.Guild):
            symbol = "g"
        if lock:
            with open(f"data/locks/{symbol}{snowflake.id}", "x") as f:
                f.write(info)
        else:
            with open(f"data/locks/{symbol}{snowflake.id}", "r") as f:
                data = f.read()
            if os.path.exists(f"data/locks/{symbol}{snowflake.id}"):
                os.remove(f"data/locks/{symbol}{snowflake.id}")
            return data

    def genPerms(self, perms, permList):
        string = ""
        for perm in perms:
            name = ""
            if isinstance(perm, str):
                name = perm.replace('_', ' ').capitalize()
            else:
                name = perm[1]
                perm = perm[0]
            hasPerm = self.emojis().control.tick if permList[perm] else self.emojis().control.cross
            string += f"{hasPerm} {name}\n"
        return string

    def checkGuild(self, guild):
        if not guild:
            return Failed()
        if not isinstance(guild, int):
            guild = guild.id
        if guild in self.bot.mem:
            return self.bot.mem[guild]
        data = self.fileManager(guild)
        self.bot.mem[guild] = {"filter": data["wordfilter"], "invite": data["invite"], "images": data["images"], "prefix": data["prefix"]}
        return self.bot.mem[guild]

    def setMem(self, guild, data):
        if not isinstance(guild, int):
            guild = guild.id
        data = {"filter": data["wordfilter"], "invite": data["invite"], "images": data["images"], "prefix": data["prefix"]}
        self.bot.mem[guild] = data
