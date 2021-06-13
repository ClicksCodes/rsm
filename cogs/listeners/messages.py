import aiohttp
import discord
import datetime
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if len(message.mentions) >= 5:
            await self.handlers.sendLog(
                emoji=self.emojis().message.mass_ping,
                type="Mass mention",
                server=message.guild.id,
                colour=self.colours.red,
                data={
                    "Content": "```\n" + self.handlers.cleanMessageContent(message.content, max_length=1000) + "```",
                    "Mentions": len(message.mentions),
                    "Sent by": message.author.mention,
                    "Sent in": message.channel.mention,
                    "Sent": self.handlers.betterDelta(message.created_at)
                },
                jump_url=message.jump_url
            )
        elif len(message.role_mentions):
            await self.handlers.sendLog(
                emoji=self.emojis().message.role_ping,
                type="Role pinged",
                server=message.guild.id,
                colour=self.colours.yellow,
                data={
                    "Content": "```\n" + self.handlers.cleanMessageContent(message.content, max_length=1000) + "```",
                    "Mentions": len(message.mentions),
                    "Sent by": message.author.mention,
                    "Sent in": message.channel.mention,
                    "Sent": self.handlers.betterDelta(message.created_at)
                },
                jump_url=message.jump_url
            )
        elif message.mention_everyone:
            await self.handlers.sendLog(
                emoji=self.emojis().message.everyone_ping,
                type="Everyone pinged",
                server=message.guild.id,
                colour=self.colours.yellow,
                data={
                    "Content": "```\n" + self.handlers.cleanMessageContent(message.content, max_length=1000) + "```",
                    "Mentions": len(message.mentions),
                    "Sent by": message.author.mention,
                    "Sent in": message.channel.mention,
                    "Sent": self.handlers.betterDelta(message.created_at)
                },
                jump_url=message.jump_url
            )

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        await self.handlers.sendLog(
            emoji=self.emojis().message.delete,
            type="Message deleted",
            server=message.guild.id,
            colour=self.colours.red,
            data={
                "Content": "```\n" + self.handlers.cleanMessageContent(message.content, max_length=1000) + "```",
                "Mentions": len(message.mentions),
                "Sent by": message.author.mention,
                "Sent in": message.channel.mention,
                "Sent": self.handlers.betterDelta(message.created_at),
                "Edited": self.handlers.betterDelta(message.edited_at),
                "Deleted": self.handlers.strf(datetime.datetime.utcnow())
            },
            jump_url=message.jump_url
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if before.content == after.content:
            return
        change = len(after.mentions)-len(before.mentions)
        await self.handlers.sendLog(
            emoji=self.emojis().message.edit,
            type="Message edited",
            server=after.guild.id,
            colour=self.colours.yellow,
            data={
                "Before": "```\n" + self.handlers.cleanMessageContent(before.content, max_length=500) + "```",
                "After": "```\n" + self.handlers.cleanMessageContent(after.content, max_length=500) + "```",
                "Mentions": f"{len(before.mentions)} -> {len(after.mentions)} ({'+' if change >= 0 else ''}{change})",
                "Sent by": after.author.mention,
                "Sent in": after.channel.mention,
                "Sent": self.handlers.betterDelta(before.created_at),
                "Edited": self.handlers.strf(after.edited_at)
            },
            jump_url=after.jump_url
        )

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        audit = await self.handlers.getAuditLogEntry(messages[0].guild, type=discord.AuditLogAction.message_bulk_delete)
        if audit.user.bot:
            return
        mlist = "\n\n".join([self.handlers.convertMessage(message) for message in messages])
        async with aiohttp.ClientSession() as session:
            async with session.post('https://hastebin.com/documents', data=mlist) as r:
                s = '"'
                url = f'https://hastebin.com/{(await r.text()).split(s)[3]}'
        await self.handlers.sendLog(
            emoji=self.emojis().channel.purge,
            type="Messages purged",
            server=messages[0].guild.id,
            colour=self.colours.red,
            data={
                "Amount": len(messages),
                "Sent in": messages[0].channel.mention,
                "Purged": self.handlers.strf(datetime.datetime.utcnow()),
                "Messages": url
            }
        )

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, _):
        audit = await self.handlers.getAuditLogEntry(channel.guild, type=discord.AuditLogAction.message_pin, check=lambda l: l.extra.channel.id == channel.id)
        if not audit:
            return
        message = await channel.fetch_message(audit.extra.message_id)
        await self.handlers.sendLog(
            emoji=self.emojis().message.pin,
            type=f"Message {'un' if not message.pinned else ''}pinned",
            server=channel.guild.id,
            colour=self.colours.yellow,
            data={
                "Content": "```\n" + self.handlers.cleanMessageContent(message.content, max_length=1000) + "```",
                "Sent by": message.author.mention,
                "Pinned by": f"{audit.user.name} ({audit.user.mention})",
                "Sent in": message.channel.mention,
                ("Pinned" if message.pinned else 'Unpinned'): self.handlers.strf(datetime.datetime.utcnow())
            },
            jump_url=message.jump_url
        )

    @commands.Cog.listener()
    async def on_reaction_clear(self, message, reactions):
        if message.author.bot:
            return
        await self.handlers.sendLog(
            emoji=self.emojis().message.reaction_clear,
            type="Reactions cleared",
            server=message.guild.id,
            colour=self.colours.red,
            data={
                "Content": "```\n" + self.handlers.cleanMessageContent(message.content, max_length=1000) + "```",
                "Sent by": message.author.mention,
                "Sent in": message.channel.mention,
                "Cleared": self.handlers.strf(datetime.datetime.utcnow()),
                "Reactions": " ".join([f"<{'a' if emoji.emoji.animated else ''}:a:{emoji.emoji.id}>" for emoji in reactions])
            },
            jump_url=message.jump_url
        )


def setup(bot):
    bot.add_cog(Logs(bot))
