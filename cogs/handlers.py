import asyncio
import datetime
import os
import aiohttp

import discord
import humanize
from discord.ext import commands

from cogs.consts import *
from config import config
import io
from PIL import Image, ImageDraw, ImageFilter, ImageFont


class Failed:
    pass


with open("data/template.json") as f:
    template = json.load(f)


class Handlers:
    def __init__(self, bot):
        self.colours = Cols()
        self.emojis = Emojis
        self.bot = bot

    def hex_to_rgba(self, value, alpha=255):
        lv = len(value)
        return tuple(int(value[i: i + lv // 3], 16) for i in range(0, lv, lv // 3)) + (alpha,)

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
            if channel.guild.id != ctx.guild.id:
                await m.edit(embed=discord.Embed(
                    title=f"{emoji} {title}",
                    description=description,
                    colour=self.colours.red
                ).set_footer(text="Channel was not in this server"))
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
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id and isinstance(reaction.emoji, discord.Emoji)
                    ),
                    ctx.bot.wait_for(
                        "reaction_remove",
                        timeout=180,
                        check=lambda reaction, user: user.id == ctx.author.id and reaction.message.id == m.id and isinstance(reaction.emoji, discord.Emoji)
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
                    if "version" not in entry:
                        entry["version"] = 1
                    if entry["version"] != 2:
                        self._update(entry)
                    entry = self.defaultDict(entry, template)
                    return entry

                except FileNotFoundError:
                    t = template
                    t["guild_info"]["id"] = guild
                    t["guild_info"]["joined_at"] = str(self.bot.get_guild(guild).me.joined_at)

                    with open(f"data/guilds/{guild}.json", "x") as f:
                        json.dump(t, f, indent=2)
                    return t

            case "RESET":
                if os.path.exists(f"data/guilds/{guild}.json"):
                    os.remove(f"data/guilds/{guild}.json")

            case _:
                return None

    def _update(self, data):
        if data["version"] == 2:
            return data
        if data["version"] == 1:
            data["version"] = 2
            data["log_info"]["ignore"] = data["ignore_info"]
            del data["ignore_info"]
            replacements = {"roles": "role_mention", "webhook_create": "webhook_update"}
            data["log_info"]["to_log"] = [(replacements[p] if p in replacements else p) for p in data["log_info"]["to_log"]]
            data["log_info"]["to_log"] += ["guild_role_edit", "user_role_update"]
            data["images"]["nsfw"] = data["nsfw"]
            del data["nsfw"]
            data["wordfilter"]["strict"] = data["wordfilter"]["banned"]
            del data["wordfilter"]["banned"]
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
        return f"{humanize.naturaltime(datetime.datetime.utcnow()-o)} ({o.strftime('%Y-%m-%d at %H:%M:%S')})"

    def strf(self, o):
        if not o:
            return "Never"
        return o.strftime('%Y-%m-%d at %H:%M:%S')

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
                except Exception as e:
                    print(e)
                    return (False, {}, 100, None)
        image = None
        if nsfw:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as r:
                    buf = io.BytesIO(await r.read())
                    buf.seek(0)
            image = Image.open(buf)
            h, w = image.size
            scalex, scaley = round(1000/h), round(1000/w)
            image = image.resize((h * scalex, w * scaley))
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
