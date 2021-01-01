import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, os

import datetime
from discord.ext import commands, tasks
from textwrap import shorten

from cogs.consts import *

class c:
    c = '\033[0m'

    RedDark = '\033[31m'
    GreenDark = '\033[32m'
    YellowDark = '\033[33m'
    BlueDark = '\033[34m'
    PinkDark = '\033[35m'
    CyanDark = '\033[36m'

    Red = '\033[91m'
    Green = '\033[92m'
    Yellow = '\033[93m'
    Blue = '\033[94m'
    Pink = '\033[95m'
    Cyan = '\033[96m'

class Mute(commands.Cog):
    """As soon as you mute someone
    1 -- You store information about the mute: what was the state before? when will the mute expire? when was it created? by who? for who? what's the reason?; You add the mute to the unmute list
    2 -- You mute the user by changing user-specific channel permissions. You do not change permission on channels that have a :white_check_mark: as a user-specific send-messages permission for that user, as those are normally only used on modmail threads and other channels that the user needs access to
    3 -- You send a DM telling the user they were muted
    --- end of part ---

    Meanwhile, every minute
    1 -- You go over all the mutes in the unmute list
    --- for any people that will be unmuted in the next 5 minutes ---
    2 -- You remove them from the unmute list
    3 -- You create a task to unmute them. Note: the task must not be awaited by this thread or it will block it
    please remember to try-except steps 2 and 3. If 3 fails (and it shouldn't), step 2 must be reverted
    --- end of part ---

    In the unmute tasks
    1 -- You asyncio.sleep until the person needs to be unmuted
    2 -- You revert to the stored state. Do not change permissions that have been changed by a user (for example ones that are not :x:, or ones that are :x: but were originally :white_check_mark:)
    3 -- You edit the data to reflect that they have been unmuted
    4 -- You send a DM telling the user they were unmuted
    --- end of part ---

    When the bot restarts. Note: Not in on_ready as that can be run multiple times. At the start before the bot even loads
    1 -- You recreate the unmute list from stored data
    """

    def __init__(self, bot):
        # TODO: reconstruct the mute list
        self.muted = {}  # guild_id:member_id: (unmute_time, {channel_id: before}})
        self.bot = bot
        self.check_mutes.start()

    def cog_unload(self): self.check_mutes.cancel()

    @tasks.loop(self, minutes=1)
    async def check_mutes(): # Loop over all mutes every minute
        now = datetime.datetime.utcnow()
        def mute_check(mute):
            try:
                if (unmute_time := datetime.datetime.utcfromtimestamp(self.muted[mute][0])) >= now + datetime.timedelta(minutes=5): self.unmute_after((unmute_time - now).total_seconds(), mute, self.muted[mute][1])
            except Exception as e: print(f"{c.RedDark}[C] {c.Red}FATAL:\n{e}{c.c}")
            else: return False
            return True

        filter(mute_check, self.muted)

    async def unmute_after(self, seconds, member, perms):
        """
        DONE: 1 -- You asyncio.sleep until the person needs to be unmuted
        """
        await asyncio.sleep(seconds)
        return await self.unmute(member, perms)

    async def mute(self, member, duration=None):
        """
        As soon as you mute someone
        DONE: 1 -- You store information about the mute: what was the state before? when will the mute expire for who?; You add the mute to the unmute list
        TODO:   -- Add saving
        DONE: 2 -- You mute the user by changing user-specific channel permissions. You do not change permission on channels that have a :white_check_mark: as a user-specific send-messages permission for that user, as those are normally only used on modmail threads and other channels that the user needs access to
        TODO: 3 -- You send a DM telling the user they were muted
        """
        mute_info = {
            "user": member.id,
            "guild": guild.id,
            "expiry": datetime.datetime.now() + datetime.timedelta(seconds=duration) if duration and duration > 0 else None,
            "completed": False,
        }
        channel_previous_perms = {}
        for channel in member.guild.channels:
            perms = channel.overwrites_for(member)
            channel_previous_perms[str(channel.id)] = perms.send_messages
        mute_info["permissions"] = channel_previous_perms
        this.save(mute_info)
        deny_send = discord.PermissionOverwrite()
        deny_send.send_messages = False
        for channel, permission in perms["permissions"].items():
            if not permission: guild.get_channel(channel).edit(overwrites=deny_send)
        mute_info["completed"] = True
        this.save(mute_info)
        await member.send(f"You were muted in {guild.name}")


    async def unmute(self, member, perms):
        guildid, memberid = member.split(":")
        guild = self.bot.get_guild(int(guildid))
        member = guild.get_member(int(memberid))
        for channel, (allow, deny) in perms.items(): await channel.edit(overwrites=splice_unmute_perms(discord.PermissionOverwrite.from_pair(allow, deny), channel.overwrites_for(member)))

    @staticmethod
    async def mute_perms(before_splice):
        if before_splice.send_messages == True: return before_splice
        before_splice.send_messages = False
        return before_splice

    @staticmethod
    async def splice_unmute_perms(before_mute, current):
        if current.send_messages != False or before_mute == True: return current
        current.send_messages = before_mute
        return current

    @commands.command(name="mute")
    @commands.guild_only()
    async def mute_command(self, ctx, user:typing.Optional[discord.Member], duration:typing.Optional[int]=None):
        try:
            if not ctx.author.guild_permissions.manage_messages and not ctx.author.guild_permissions.manage_roles:
                await ctx.send(embed=discord.Embed(
                    title=f"{emojis['PunMute']} Looks like you don't have permissions",
                    description="You need the `manage_messages` or `manage_roles` permission to mute someone.",
                    color=colours["delete"]))
                return await m.delete()
        except: return
        m = await ctx.send(self.loadingEmbed)
        if not user:
            await m.edit(embed=discord.Embed(
                title=f"{emojis['PunMute']} Which user would you like to mute?",
                description="Please enter the name or ID of the user you would like to mute. Type `cancel` to cancel.",
                color=colours['create']
            ))
            try: msg = await ctx.bot.wait_for('message', timeout=60, check=lambda r, user : r.message.id == m.id and user == ctx.author)
            except asyncio.TimeoutError: break

            r = None
            errored = False
            try: r = int(msg.content)
            except:
                try: user = msg.mentions[0]
                except errored = True
            if r:
                try: user = self.bot.get_member(r)
                except: errored = True
            if errored:
                return await m.edit(embed=discord.Embed(
                    title=f"{emojis['PunMute']} Which user would you like to mute?",
                    description="Please enter the name or ID of the user you would like to mute. Type `cancel` to cancel.",
                    color=colours['delete']
                ))
        self.mute(user, duration)

    @commands.command(name="unmute")
    @commands.guild_only)()
    async def unmute_command(self, ctx, user:typing.Optional[discord.Member]):
        try:
            if not ctx.author.guild_permissions.manage_messages and not ctx.author.guild_permissions.manage_roles:
                await ctx.send(embed=discord.Embed(
                    title=f"{emojis['PunMute']} Looks like you don't have permissions",
                    description="You need the `manage_messages` or `manage_roles` permission to unmute someone.",
                    color=colours["delete"]))
                return await m.delete()
        except: return
        m = await ctx.send(self.loadingEmbed)
        if not user:
            await m.edit(embed=discord.Embed(
                title=f"{emojis['PunMute']} Which user would you like to unmute?",
                description="Please enter the name or ID of the user you would like to unmute. Type `cancel` to cancel.",
                color=colours['create']
            ))
            try: msg = await ctx.bot.wait_for('message', timeout=60, check=lambda r, user : r.message.id == m.id and user == ctx.author)
            except asyncio.TimeoutError: break

            r = None
            errored = False
            try: r = int(msg.content)
            except:
                try: user = msg.mentions[0]
                except errored = True
            if r:
                try: user = self.bot.get_member(r)
                except: errored = True
            if errored:
                return await m.edit(embed=discord.Embed(
                    title=f"{emojis['PunMute']} Which user would you like to unmute?",
                    description="Please enter the name or ID of the user you would like to unmute. Type `cancel` to cancel.",
                    color=colours['delete']
                ))

def setup(bot): bot.add_cog(Mute(bot))
