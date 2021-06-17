import asyncio
import discord
import typing
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed


class RSM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        if not suggestion:
            suggestion = await self.handlers.strHandler(ctx, m, emoji=self.emojis().icon.add, title="Suggest", description="What would you like to suggest?")
            if isinstance(suggestion, Failed):
                return
        s = await self.bot.get_channel(853576297480716298).send(embed=discord.Embed(
            title=f"Suggestion",
            description=suggestion,
            colour=self.colours.yellow
        ))
        asyncio.create_task(self.handlers.reactionCollector(
            ctx,
            s,
            reactions=["control.tick", "control.cross"],
            collect=False
        ))
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().icon.add} Suggestion",
            description="Your suggestion has been sent to the develoeprs",
            colour=self.colours.green
        ))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = self.bot.get_user(payload.user_id)
        if payload.channel_id == 853576297480716298 and not user.bot:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if message.author.id == self.bot.user.id:
                await message.clear_reactions()
                match payload.emoji.name:
                    case "Tick":
                        embed = message.embeds[0]
                        embed.colour = self.colours.green
                        embed.title = f"{self.emojis().control.tick} Accepted"
                        await message.edit(embed=embed)
                        s = await self.bot.get_channel(777224376051040310).send(embed=discord.Embed(
                            title=f"{self.emojis().icon.add} Suggestion",
                            description=embed.description,
                            colour=self.colours.green
                        ))
                        asyncio.create_task(self.handlers.reactionCollector(
                            m=s,
                            reactions=["control.tick", "control.cross"],
                            collect=False
                        ))
                    case "Cross":
                        embed = message.embeds[0]
                        embed.colour = self.colours.red
                        embed.title = f"{self.emojis().control.cross} Rejected"
                        await message.edit(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        m = await ctx.send(embed=loading_embed)
        time = m.created_at - ctx.message.created_at
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().slowmode.on} Pong",
            description=f"Latency is: `{int(time.microseconds / 1000)}ms`",
            colour=self.colours.green
        ))

    @commands.command()
    async def stats(self, ctx):
        m = await ctx.send(embed=loading_embed)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().guild.graphs} Stats",
            description=f"**Servers:** {len(self.bot.guilds)}\n"
                        f"**Ping**: {self.bot.latency * 1000}ms",
            colour=self.colours.green
        ))

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx):
        m = await ctx.send(embed=loading_embed)
        data = self.handlers.fileManager(ctx.guild)
        one = True
        prefix = f"`{ctx.prefix}`"
        if data["prefix"]:
            if isinstance(data["prefix"], list):
                prefix = ", ".join(f"`{p}`" for p in data["prefix"])
                one = False
            else:
                prefix = f'`{data["prefix"]}`'
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().punish.mute} Prefix",
            description=f"Your server prefix{' is' if one else 'es are'}: {prefix}",
            colour=self.colours.green
        ))

    @commands.command()
    @commands.guild_only()
    async def setprefix(self, ctx, *, prefixes: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_guild", emoji=self.emojis().punish.mute, action="change the server prefix", me=False), Failed):
            return
        if not prefixes:
            prefixes = await self.handlers.strHandler(
                ctx,
                m,
                emoji=self.emojis().punish.mute,
                title="Prefix",
                description="What should the server prefix be?\nFor multiple, separate each with a space",
                optional=True,
                default="None"
            )
            if isinstance(prefixes, Failed):
                return
        if prefixes != "None":
            prefixes = prefixes.split(" ")
            if len(prefixes) == 1:
                prefixes = prefixes[0]
        else:
            prefixes = None
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().punish.mute} Prefix", description="Setting your prefix", colour=self.colours.green
        ).set_footer(text="Reading"))
        data = self.handlers.fileManager(ctx.guild)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().punish.mute} Prefix", description="Setting your prefix", colour=self.colours.green
        ).set_footer(text="Writing"))
        data["prefix"] = prefixes
        self.handlers.fileManager(ctx.guild, "w", data=data)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().punish.mute} Prefix", description="Prefix successfully set", colour=self.colours.green
        ))


def setup(bot):
    bot.add_cog(RSM(bot))
