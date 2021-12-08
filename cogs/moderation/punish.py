import discord
import typing
import datetime
from discord import interactions
import humanize
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed
from cogs import interactions


class Punish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)
        self.interactions = interactions

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if "type" not in interaction.data:
            return
        if interaction.data["type"] == 2 and interaction.guild:
            if interaction.data["name"] == "Punish":
                guild = self.bot.get_guild(interaction.guild.id)
                member = guild.get_member(int(interaction.data["target_id"]))
                await interaction.response.send_message(embed=loading_embed, ephemeral=True)
                m = await interaction.original_message()
                ctx = self.interactions.CustomCTX(self.bot, interaction.user, interaction.guild, interaction.channel, interaction=interaction, m=m)
                await self._punish(ctx, m, member, reason=None)
        elif interaction.type.name == "application_command" and interaction.guild:
            pass
            # if interaction.data["name"] == "apply":

    @commands.command()
    @commands.guild_only()
    async def warn(self, ctx, member: typing.Optional[discord.Member], *, reason: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        await self._warn(ctx, m, member, reason)

    @commands.command()
    @commands.guild_only()
    async def clear(self, ctx, member: typing.Optional[discord.Member], *, count: typing.Optional[int]):
        m = await ctx.send(embed=loading_embed)
        await self._clear(ctx, m, member, count)

    @commands.command()
    @commands.guild_only()
    async def kick(self, ctx, member: typing.Optional[discord.Member], *, reason: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        await self._kick(ctx, m, member, reason)

    @commands.command()
    @commands.guild_only()
    async def softban(self, ctx, member: typing.Optional[discord.Member], *, reason: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        await self._softban(ctx, m, member, reason)

    @commands.command()
    @commands.guild_only()
    async def ban(self, ctx, member: typing.Optional[discord.Member], *, count: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        await self._ban(ctx, m, member, count)

    @commands.command()
    @commands.guild_only()
    async def punish(self, ctx, member: typing.Optional[discord.Member], *, reason: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        ctx = self.interactions.CustomCTX(self.bot, ctx.author, ctx.guild, ctx.channel, m=m, message=ctx.message)
        await self._punish(ctx, m, member, reason)

    async def _punish(self, ctx, m, member: typing.Optional[discord.Member], reason: typing.Optional[str]):
        if not member:
            member = await self.handlers.memberHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.warn),
                title="Punish",
                description="Who would you like to punish?"
            )
            if isinstance(member, Failed):
                return

        v = self.interactions.createUI(ctx, [
            self.interactions.Button(self.bot, emojis=self.emojis, id="wa", title="Warn", emoji="punish.warn"),
            self.interactions.Button(self.bot, emojis=self.emojis, id="ch", title="Clear history", emoji="punish.clear_history"),
            self.interactions.Button(self.bot, emojis=self.emojis, id="ki", title="Kick", emoji="punish.kick"),
            self.interactions.Button(self.bot, emojis=self.emojis, id="sb", title="Softban", emoji="punish.soft_ban"),
            self.interactions.Button(self.bot, emojis=self.emojis, id="ba", title="Ban", emoji="punish.ban"),
            self.interactions.Button(self.bot, emojis=self.emojis, id="cr", emoji="control.cross"),
        ])
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().punish.warn} Punish",
            description=f"Punishing user {member.mention}\n\n"
                        f"{self.emojis().punish.warn} Warn\n"
                        f"{self.emojis().punish.clear_history} Clear history\n"
                        f"{self.emojis().punish.kick} Kick\n"
                        f"{self.emojis().punish.soft_ban} Softban\n"
                        f"{self.emojis().punish.ban} Ban\n"
                        f"{self.emojis().control.cross} Cancel",
            colour=self.colours.green
        ), view=v)
        await v.wait()
        match v.selected:
            case "wa": await self._warn(ctx, m, member, reason)
            case "ph": await self._clear(ctx, m, member, reason)
            case "ki": await self._kick(ctx, m, member, reason)
            case "sb": await self._softban(ctx, m, member, reason)
            case "ba": await self._ban(ctx, m, member, reason)
            case _:
                await m.edit(embed=discord.Embed(
                    title=f"{self.emojis().punish.warn} Punish",
                    description=f"Punishing user {member.mention}\n\n"
                                f"{self.emojis().punish.warn} Warn\n"
                                f"{self.emojis().punish.clear_history} Clear history\n"
                                f"{self.emojis().punish.kick} Kick\n"
                                f"{self.emojis().punish.soft_ban} Softban\n"
                                f"{self.emojis().punish.ban} Ban\n"
                                f"{self.emojis().control.cross} Cancel",
                    colour=self.colours.red
                ), view=None)

    async def _warn(self, ctx, m, member=None, reason=None):
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_messages", self.emojis().punish.warn, "warn someone", me=False), Failed):
            return

        if not member:
            member = await self.handlers.memberHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.warn),
                title="Warn",
                description="Who would you like to warn?"
            )
            if isinstance(member, Failed):
                return

        if not reason:
            reason = await self.handlers.strHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.warn),
                title="Warn",
                description="What is the warning for?",
                optional=True
            )
            if isinstance(reason, Failed):
                return

        try:
            await member.send(embed=discord.Embed(
                title=f"{self.emojis().punish.warn} Warn",
                description=f"You have been warned in {ctx.guild.name}" + (f" for:\n> {reason}" if reason else ""),
                colour=self.colours.yellow
            ))
            await self.handlers.sendLog(
                emoji=self.emojis().punish.warn,
                type="Member warned",
                server=ctx.guild.id,
                colour=self.colours.yellow,
                data={
                    "Warned": member.mention,
                    "Warned by": ctx.author.mention,
                    "Warned": self.handlers.strf(datetime.datetime.utcnow()),
                    "Reason": reason
                }
            )
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.warn} Warn",
                description=f"{member.mention} was successfully warned" + (f" for:\n> {reason}" if reason else ""),
                colour=self.colours.green
            ), view=None)
        except discord.errors.HTTPException:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.warn} Warn",
                description=f"An error occurred while warning {member.mention}",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"), view=None)

    async def _clear(self, ctx, m, member=None, count=None):
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_messages", self.emojis().punish.clear_history, "clear someones history"), Failed):
            return

        if not member:
            member = await self.handlers.memberHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.clear_history),
                title="Clear",
                description="Whose history would you like to clear?"
            )
            if isinstance(member, Failed):
                return

        try:
            count = int(count)
        except ValueError:
            count = None

        if not count:
            count = await self.handlers.intHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.clear_history),
                title="Clear",
                description="How many messages should be checked?",
                optional=True
            )
            if isinstance(count, Failed):
                return

        try:
            deleted = await ctx.channel.purge(limit=count, check=lambda message: message.author.id == member.id)
            await self.handlers.sendLog(
                emoji=self.emojis().punish.warn,
                type="History cleared",
                server=ctx.guild.id,
                colour=self.colours.red,
                data={
                    "User cleared": member.mention,
                    "Cleared by": ctx.author.mention,
                    "Cleared": self.handlers.strf(datetime.datetime.utcnow()),
                    "Amount checked": count,
                    "Amount deleted": len(deleted)
                }
            )
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.clear_history} Clear",
                description=f"Successfully cleared {len(deleted)} messages by {member.mention}",
                colour=self.colours.green
            ), view=None)
        except discord.errors.HTTPException:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.clear_history} Clear",
                description=f"An error occurred while clearing {member.mention}",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"), view=None)

    async def _kick(self, ctx, m, member=None, reason=None):
        if isinstance(await self.handlers.checkPerms(ctx, m, "kick_members", self.emojis().punish.kick, "kick someone"), Failed):
            return

        if not member:
            member = await self.handlers.memberHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.kick),
                title="Kick",
                description="Who would you like to kick?"
            )
            if isinstance(member, Failed):
                return

        if member.top_role.position >= ctx.author.top_role.position:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.kick} Kick",
                description=f"{member.mention} is higher or the same level as you and cannot be kicked",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"))

        if member.top_role.position >= ctx.me.top_role.position:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.kick} Kick",
                description=f"{member.mention} is higher or the same level as me and cannot be kicked",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"))

        if not reason:
            reason = await self.handlers.strHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.kick),
                title="Kick",
                description="What reason should be given?",
                optional=True
            )
            if isinstance(reason, Failed):
                return

        try:
            try:
                await member.send(embed=discord.Embed(
                    title=f"{self.emojis().punish.kick} Kick",
                    description=f"You have been kicked from {ctx.guild.name}" + (f" for:\n> {reason}" if reason else ""),
                    colour=self.colours.red
                ))
            except discord.errors.HTTPException:
                pass
            await ctx.guild.kick(member, reason=(reason if reason else "No reason provided"))
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.kick} Kick",
                description=f"{member.mention} was successfully kicked" + (f" for:\n> {reason}" if reason else ""),
                colour=self.colours.green
            ), view=None)
        except discord.errors.HTTPException:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.kick} Kick",
                description=f"An error occurred while kicking {member.mention}",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"), view=None)

    async def _softban(self, ctx, m, member=None, reason=None):
        if isinstance(await self.handlers.checkPerms(ctx, m, "kick_members", self.emojis().punish.soft_ban, "softban someone"), Failed):
            return

        if not member:
            member = await self.handlers.memberHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.soft_ban),
                title="Softban",
                description="Who would you like to softban?"
            )
            if isinstance(member, Failed):
                return

        if member.top_role.position >= ctx.author.top_role.position:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.soft_ban} Softban",
                description=f"{member.mention} is higher or the same level as you and cannot be softbanned",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"))

        if member.top_role.position >= ctx.me.top_role.position:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.soft_ban} Softban",
                description=f"{member.mention} is higher or the same level as me and cannot be softbanned",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"))

        if not reason:
            reason = await self.handlers.strHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.soft_ban),
                title="Softban",
                description="What reason should be given?",
                optional=True
            )
            if isinstance(reason, Failed):
                return

        try:
            try:
                await member.send(embed=discord.Embed(
                    title=f"{self.emojis().punish.soft_ban} Softban",
                    description=f"You have been softbanned from {ctx.guild.name}" + (f" for:\n> {reason}" if reason else ""),
                    colour=self.colours.yellow
                ))
            except discord.errors.HTTPException:
                pass
            await ctx.guild.ban(member, reason=(("RSM Softban | " + reason) if reason else "RSM Softban | No reason provided"), delete_message_days=7)
            await ctx.guild.unban(member, reason=(reason if reason else "RSM Softban"))
            await self.handlers.sendLog(
                emoji=self.emojis().punish.soft_ban,
                type="Member softbanned",
                server=ctx.guild.id,
                colour=self.colours.yellow,
                data={
                    "Name": f"{member.name} ({member.mention})",
                    "Joined": self.handlers.betterDelta(member.joined_at.replace(tzinfo=None)),
                    "Softbanned": self.handlers.strf(datetime.datetime.utcnow()),
                    "Softbanned by": f"{ctx.author.name} ({ctx.author.mention})",
                    "Reason": f"\n> {reason}",
                    "Time in server": humanize.naturaldelta(datetime.datetime.utcnow()-member.joined_at.replace(tzinfo=None)),
                    "Account created": self.handlers.betterDelta(member.created_at.replace(tzinfo=None)),
                    "ID": f"`{member.id}`",
                    "Server member count": len(member.guild.members)
                }
            )
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.soft_ban} Softban",
                description=f"{member.mention} was successfully softbanned" + (f" for:\n> {reason}" if reason else ""),
                colour=self.colours.green
            ), view=None)
        except discord.errors.HTTPException:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.soft_ban} Softban",
                description=f"An error occurred while softbanning {member.mention}",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"), view=None)

    async def _ban(self, ctx, m, member=None, reason=None):
        if isinstance(await self.handlers.checkPerms(ctx, m, "ban_members", self.emojis().punish.ban, "ban someone"), Failed):
            return

        if not member:
            member = await self.handlers.memberHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.ban),
                title="Ban",
                description="Who would you like to ban?"
            )
            if isinstance(member, Failed):
                return

        if member.top_role.position >= ctx.author.top_role.position:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.ban} Ban",
                description=f"{member.mention} is higher or the same level as you and cannot be banned",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"), view=None)

        if member.top_role.position >= ctx.me.top_role.position:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.ban} Ban",
                description=f"{member.mention} is higher or the same level as me and cannot be banned",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"), view=None)

        if not reason:
            reason = await self.handlers.strHandler(
                ctx=ctx,
                m=m,
                emoji=str(self.emojis().punish.ban),
                title="Ban",
                description="What reason should be given?",
                optional=True
            )
            if isinstance(reason, Failed):
                return

        try:
            try:
                await member.send(embed=discord.Embed(
                    title=f"{self.emojis().punish.ban} Ban",
                    description=f"You have been banned from {ctx.guild.name}" + (f" for:\n> {reason}" if reason else ""),
                    colour=self.colours.red
                ))
            except discord.HTTPException:
                pass
            await ctx.guild.ban(member, reason=(reason if reason else "No reason provided"))
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.ban} Ban",
                description=f"{member.mention} was successfully banned" + (f" for:\n> {reason}" if reason else ""),
                colour=self.colours.green
            ), view=None)
        except discord.HTTPException:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.ban} Ban",
                description=f"An error occurred while banning {member.mention}",
                colour=self.colours.red
            ).set_footer(text="403 Forbidden"), view=None)


def setup(bot):
    bot.add_cog(Punish(bot))
