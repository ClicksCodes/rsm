import discord
import asyncio
from discord.ext import commands
import datetime
import typing

from cogs.consts import *
from cogs.handlers import Handlers, Failed
from cogs import interactions


class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)
        self.interactions = interactions

    @commands.command()
    @commands.guild_only()
    async def modmail(self, ctx):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_guild", self.emojis().guild.modmail.open, "manage modmail", me=False), Failed):
            return
        while True:
            catName = "*No category set*"
            maxTickets = "*No limit set*"
            supportMention = "*No mention set*"
            active = "*Failed to fetch*"
            archived = "*Failed to fetch*"

            f = self.handlers.fileManager(ctx.guild)
            f = f["modmail"]
            if f["cat"] is not None:
                cat = ctx.guild.get_channel(f["cat"])
                catName = cat.name
                active = len([c for c in cat.channels if c.topic.split(" ")[1] == "Active"])
                archived = len([c for c in cat.channels if c.topic.split(" ")[1] == "Archived"])
            maxTickets = f["max"]
            if f["mention"]:
                supportMention = ctx.guild.get_role(f["mention"])
            v = self.interactions.createUI(ctx, [
                self.interactions.Button(self.bot, emojis=self.emojis, id="cr", emoji="control.cross"),
                self.interactions.Button(self.bot, emojis=self.emojis, id="cc", title="Category", emoji="channel.category.create"),
                self.interactions.Button(self.bot, emojis=self.emojis, id="tc", title="Max tickets", emoji="channel.text.create"),
                self.interactions.Button(self.bot, emojis=self.emojis, id="ep", title="Mention", emoji="message.everyone_ping"),
            ])
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().guild.modmail.open} Modmail",
                description=f"**Active tickets:** {active}\n"
                            f"**Archived tickets:** {archived}\n\n"
                            f"{self.emojis().channel.category.create} **Modmail category:** {catName}\n"
                            f"{self.emojis().channel.text.create} **Max tickets per user:** {maxTickets}\n"
                            f"{self.emojis().message.everyone_ping} **Support mention:** "
                            f"{supportMention.mention if isinstance(supportMention, discord.Role) else supportMention}\n",
                colour=self.colours.green
            ), view=v)
            await v.wait()
            match v.selected:
                case "cc":
                    category = await self.handlers.categoryHandler(
                        ctx,
                        m,
                        emoji=self.emojis().guild.modmail.open,
                        title="Modmail",
                        description="Which category should be used for modmail?",
                        optional=True,
                        default=None,
                        returnNoneType=True
                    )
                    if not isinstance(category, Failed):
                        m = await ctx.channel.fetch_message(m.id)
                        embed = m.embeds[0]
                        await m.edit(embed=embed.set_footer(text="Reading"))
                        data = self.handlers.fileManager(ctx.guild)
                        data["modmail"]["cat"] = category.id
                        m = await ctx.channel.fetch_message(m.id)
                        embed = m.embeds[0]
                        await m.edit(embed=embed.set_footer(text="Writing"))
                        self.handlers.fileManager(ctx.guild, "w", data=data)
                case "tc":
                    amount = await self.handlers.intHandler(
                        ctx,
                        m,
                        emoji=self.emojis().guild.modmail.open,
                        title="Modmail",
                        description="How many tickets should a user be able to have at once? 0 for infinite",
                        default=3
                    )
                    if not isinstance(amount, Failed):
                        m = await ctx.channel.fetch_message(m.id)
                        embed = m.embeds[0]
                        await m.edit(embed=embed.set_footer(text="Reading"))
                        data = self.handlers.fileManager(ctx.guild)
                        data["modmail"]["max"] = amount
                        m = await ctx.channel.fetch_message(m.id)
                        embed = m.embeds[0]
                        await m.edit(embed=embed.set_footer(text="Writing"))
                        self.handlers.fileManager(ctx.guild, "w", data=data)
                case "ep":
                    role = await self.handlers.roleHandler(
                        ctx,
                        m,
                        emoji=self.emojis().guild.modmail.open,
                        title="Modmail",
                        description="What role should be pinged when a new ticket is created?",
                        default=None,
                        optional=True
                    )
                    if not isinstance(role, Failed):
                        m = await ctx.channel.fetch_message(m.id)
                        embed = m.embeds[0]
                        await m.edit(embed=embed.set_footer(text="Reading"), view=None)
                        data = self.handlers.fileManager(ctx.guild)
                        data["modmail"]["mention"] = role.id
                        m = await ctx.channel.fetch_message(m.id)
                        embed = m.embeds[0]
                        await m.edit(embed=embed.set_footer(text="Writing"))
                        self.handlers.fileManager(ctx.guild, "w", data=data)
                case _: break
        m = await ctx.channel.fetch_message(m.id)
        embed = m.embeds[0]
        embed.colour = self.colours.red
        await m.edit(embed=embed, view=None)

    @commands.command(aliases=["ticket", "tickets"])
    @commands.guild_only()
    async def mail(self, ctx, *, message: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        data = self.handlers.fileManager(ctx.guild)
        if not data["modmail"]["cat"]:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().guild.modmail.open} Modmail",
                description=f"Modmail has not been set up in this server. Please contact the moderators if you believe this is a mistake.",
                colour=self.colours.red
            ))
        users = {}
        for channel in ctx.guild.get_channel(data["modmail"]["cat"]).channels:
            user = channel.topic.split(" ")[0]
            if channel.topic.split(" ")[1] == "Archived":
                continue
            if user not in users:
                users[user] = 1
            else:
                users[user] += 1
        if str(ctx.author.id) in users and data["modmail"]["max"] > 0:
            if users[str(ctx.author.id)] >= data["modmail"]["max"]:
                return await m.edit(embed=discord.Embed(
                    title=f"{self.emojis().guild.modmail.open} Modmail",
                    description=f"You have reached the ticket limit. Please close one of your current tickets.",
                    colour=self.colours.yellow
                ))

        c = await ctx.guild.create_text_channel(
            name=str(ctx.author.name),
            topic=f"{str(ctx.author.id)} Active",
            category=ctx.guild.get_channel(data["modmail"]["cat"])
        )
        await c.set_permissions(ctx.author, view_channel=True, send_messages=True)
        created = await c.send(embed=discord.Embed(
            title=f"{self.emojis().guild.modmail.open} {ctx.author.name} created a ticket",
            description=f"> Anyone can close this ticket with `{ctx.prefix}close`" + (f"\n\n> {message}" if message else '') +
                        f"\n\nTicket opened at {self.handlers.strf(datetime.datetime.utcnow())}",
            colour=self.colours.green
        ))
        if data["modmail"]["mention"] is not None:
            await c.set_permissions(self.bot.get_guild(ctx.guild.id).get_role(data['modmail']['mention']), view_channel=True, send_messages=True)
        await c.send(f"<@{ctx.author.id}>" + (f" • <@&{data['modmail']['mention']}>" if data['modmail']['mention'] else ''))
        await ctx.delete()
        await self.handlers.sendLog(
            emoji=self.emojis().guild.modmail.open,
            type=f"Ticket opened",
            server=ctx.guild.id,
            colour=self.colours.green,
            data={
                "Ticket by": f"{ctx.author.name} ({ctx.author.mention})",
                "Ticket channel": ctx.channel.mention,
            },
            jump_url=created.jump_url
        )
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().guild.modmail.open} Ticket created",
            description=f"You can jump to the channel [here]({created.jump_url})",
            colour=self.colours.green
        ))
        await asyncio.sleep(10)
        await m.delete()

    @commands.command()
    @commands.guild_only()
    async def close(self, ctx):
        data = self.handlers.fileManager(ctx.guild)
        if ctx.channel.category == None:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().guild.modmail.open} Modmail",
                description=f"This does not appear to be a modmail ticket. Please check the channel is correct or contact the [developers](https://discord.gg/bPaNnxe) if you expected this to work.",
                colour=self.colours.red
            ))
        if ctx.channel.category.id == data["modmail"]["cat"]:
            if ctx.channel.topic.split(" ")[1] == "Active":
                m = await ctx.send(embed=discord.Embed(
                    title=f"{self.emojis().guild.modmail.open} Modmail",
                    description=f"Closing your ticket",
                    colour=self.colours.red
                ))
                await ctx.channel.set_permissions(ctx.guild.get_member(int(ctx.channel.topic.split(" ")[0])), view_channel=False, send_messages=False)
                await ctx.channel.edit(topic=f"{ctx.channel.topic.split(' ')[0]} Archived", name=f"{ctx.channel.name}-archived")
                user = ctx.guild.get_member(int(ctx.channel.topic.split(' ')[0]))
                await self.handlers.sendLog(
                    emoji=self.emojis().guild.modmail.archive,
                    type=f"Ticket archived",
                    server=ctx.guild.id,
                    colour=self.colours.yellow,
                    data={
                        "Ticket by": f"{user.name} ({user.mention})",
                        "Archived by": f"{ctx.author.name} ({ctx.author.mention})",
                        "Ticket channel": ctx.channel.mention,
                    },
                    jump_url=ctx.message.jump_url
                )
                await m.edit(embed=discord.Embed(
                    title=f"{self.emojis().guild.modmail.open} Modmail",
                    description=f"The ticket is now archived. The original user cannot see it.\nUse `{ctx.prefix}close` to delete the channel",
                    colour=self.colours.green
                ))
            elif ctx.channel.topic.split(" ")[1] == "Archived":
                user = ctx.guild.get_member(int(ctx.channel.topic.split(' ')[0]))
                m = await ctx.send(embed=discord.Embed(
                    title=f"{self.emojis().guild.modmail.open} Modmail",
                    description=f"Deleting ticket",
                    colour=self.colours.red
                ))
                await ctx.channel.delete()
                await self.handlers.sendLog(
                    emoji=self.emojis().guild.modmail.close,
                    type=f"Ticket deleted",
                    server=ctx.guild.id,
                    colour=self.colours.red,
                    data={
                        "Ticket by": f"{user.name} ({user.mention})",
                        "Deleted by": f"{ctx.author.name} ({ctx.author.mention})",
                        "Ticket channel": ctx.channel.name,
                    }
                )


def setup(bot):
    bot.add_cog(Modmail(bot))
