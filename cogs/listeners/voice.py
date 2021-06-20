from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        if before.channel is None and after.channel is not None:  # Join
            await self.handlers.sendLog(
                emoji=self.emojis().voice.connect,
                type="Joined voice channel",
                server=member.guild.id,
                colour=self.colours.green,
                data={
                    "Member": f"{member.name} ({member.mention}",
                    "Channel": after.channel.name
                }
            )
        elif before.channel is not None and after.channel is None:  # Leave
            await self.handlers.sendLog(
                emoji=self.emojis().voice.leave,
                type="Left voice channel",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Member": f"{member.name} ({member.mention}",
                    "Channel": before.channel.name
                }
            )
        elif before.channel is not None and before.channel != after.channel:  # Move
            await self.handlers.sendLog(
                emoji=self.emojis().voice.change,
                type="Moved voice channel",
                server=member.guild.id,
                colour=self.colours.yellow,
                data={
                    "Member": f"{member.name} ({member.mention}",
                    "From": before.channel.name,
                    "To": after.channel.name
                }
            )
        elif not before.self_deaf and after.self_deaf:  # Deafen
            await self.handlers.sendLog(
                emoji=self.emojis().voice.deafen,
                type="Member deafened",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Member": f"{member.name} ({member.mention}"
                }
            )
        elif before.self_deaf and not after.self_deaf:  # Undeafen
            await self.handlers.sendLog(
                emoji=self.emojis().voice.undeafen,
                type="Member undeafened",
                server=member.guild.id,
                colour=self.colours.green,
                data={
                    "Member": f"{member.name} ({member.mention}"
                }
            )
        elif not before.self_mute and after.self_mute:  # Mute
            await self.handlers.sendLog(
                emoji=self.emojis().voice.mute,
                type="Member muted",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Member": f"{member.name} ({member.mention}"
                }
            )
        elif before.self_mute and not after.self_mute:  # Unmute
            await self.handlers.sendLog(
                emoji=self.emojis().voice.unmute,
                type="Member unmuted",
                server=member.guild.id,
                colour=self.colours.green,
                data={
                    "Member": f"{member.name} ({member.mention}"
                }
            )
        elif not before.deaf and after.deaf:  # Server Deafen
            await self.handlers.sendLog(
                emoji=self.emojis().voice.deafen,
                type="Member server deafened",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Member": f"{member.name} ({member.mention}"
                }
            )
        elif before.deaf and not after.deaf:  # Server Undeafen
            await self.handlers.sendLog(
                emoji=self.emojis().voice.undeafen,
                type="Member server undeafened",
                server=member.guild.id,
                colour=self.colours.green,
                data={
                    "Member": f"{member.name} ({member.mention}"
                }
            )
        elif not before.mute and after.mute:  # Server Mute
            await self.handlers.sendLog(
                emoji=self.emojis().voice.mute,
                type="Member server muted",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Member": f"{member.name} ({member.mention}"
                }
            )
        elif before.mute and not after.mute:  # Server Unmute
            await self.handlers.sendLog(
                emoji=self.emojis().voice.unmute,
                type="Member server unmuted",
                server=member.guild.id,
                colour=self.colours.green,
                data={
                    "Member": f"{member.name} ({member.mention}"
                }
            )
        elif not before.self_stream and after.self_stream:  # Started streaming
            await self.handlers.sendLog(
                emoji=self.emojis().voice.stream_start,
                type="Stream started",
                server=member.guild.id,
                colour=self.colours.green,
                data={
                    "Member": f"{member.name} ({member.mention}",
                    "Channel": after.channel.name
                }
            )
        elif before.self_stream and not after.self_stream:  # Ended stream
            await self.handlers.sendLog(
                emoji=self.emojis().voice.stream_end,
                type="Stream ended",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Member": f"{member.name} ({member.mention}",
                    "Channel": after.channel.name
                }
            )
        elif not before.self_video and after.self_video:  # Started video
            await self.handlers.sendLog(
                emoji=self.emojis().voice.video_start,
                type="Video started",
                server=member.guild.id,
                colour=self.colours.green,
                data={
                    "Member": f"{member.name} ({member.mention}",
                    "Channel": after.channel.name
                }
            )
        elif before.self_video and not after.self_video:  # Ended video
            await self.handlers.sendLog(
                emoji=self.emojis().voice.video_end,
                type="Video ended",
                server=member.guild.id,
                colour=self.colours.red,
                data={
                    "Member": f"{member.name} ({member.mention}",
                    "Channel": after.channel.name
                }
            )


def setup(bot):
    bot.add_cog(Logs(bot))
