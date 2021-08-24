import typing
import discord
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed

reserved = [
    "new",
    "create",
    "remove",
    "delete",
    "edit",
    "update"
]


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.command()
    @commands.guild_only()
    async def tags(self, ctx):
        m = await ctx.send(embed=loading_embed)
        data = self.handlers.fileManager(ctx.guild)["tags"]
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().channel.store.create} Tags",
            description=f"Here are your servers tags:\n" + ("\n".join([f"`tag`" for tag in data.keys()])),
            colour=self.colours.green
        ))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def tag(self, ctx, *, name: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        data = self.handlers.fileManager(ctx.guild)["tags"]
        if name and name.lower() in data:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().channel.store.create} Tag",
                description=str(data[name.lower()]),
                colour=self.colours.green
            ))
        return await m.edit(embed=discord.Embed(
            title=f"{self.emojis().channel.store.create} Tag",
            description=f"Tag {name} could not be found",
            colour=self.colours.red
        ))

    @tag.command(name="new", aliases=["create"])
    @commands.guild_only()
    async def new(self, ctx, name: typing.Optional[str], desc: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        data = self.handlers.fileManager(ctx.guild)
        if not name:
            name = await self.handlers.strHandler(ctx, m, emoji=self.emojis().channel.store.create, title="Tag", description="What should the tag name be")
            if isinstance(name, Failed):
                return
            if name in data["tags"]:
                return await m.edit(embed=discord.Embed(
                    title=f"{self.emojis().channel.store.create} Tag",
                    description="This tag already exists",
                    colour=self.colours.red
                ), view=None)
            if name in reserved:
                return await m.edit(embed=discord.Embed(
                    title=f"{self.emojis().channel.store.create} Tag",
                    description="This tag contains a reserved phrase",
                    colour=self.colours.red
                ), view=None)
        if len(name) > 100:
            desc = desc[:100]
        if not desc:
            desc = await self.handlers.strHandler(ctx, m, emoji=self.emojis().channel.store.create, title="Tag", description="What should the tag content be")
            if isinstance(desc, Failed):
                return
        if len(desc) > 2000:
            desc = desc[:2000]
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().channel.store.create} Tag",
            description="Saving tag",
            colour=self.colours.green
        ).set_footer(text="Reading"), view=None)
        data = self.handlers.fileManager(ctx.guild)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().channel.store.create} Tag",
            description="Saving tag",
            colour=self.colours.green
        ).set_footer(text="Writing"), view=None)
        data["tags"][name.lower()] = desc
        data = self.handlers.fileManager(ctx.guild, action="w", data=data)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().channel.store.create} Tag",
            description="Tag created successfully",
            colour=self.colours.green
        ), view=None)

    @tag.command(name="remove", aliases=["delete"])
    @commands.guild_only()
    async def remove(self, ctx, name: typing.Optional[str]):
        m = await ctx.send(embed=loading_embed)
        data = self.handlers.fileManager(ctx.guild)
        if not name:
            name = await self.handlers.strHandler(ctx, m, emoji=self.emojis().channel.store.create, title="Tag", description="Which tag should be deleted")
            if isinstance(name, Failed):
                return
        if name.lower() not in data["tags"]:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().channel.store.create} Tag",
                description="Tag could not be found",
                colour=self.colours.red
            ), view=None)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().channel.store.create} Tag",
            description="Deleting tag",
            colour=self.colours.green
        ).set_footer(text="Reading"), view=None)
        data = self.handlers.fileManager(ctx.guild)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().channel.store.create} Tag",
            description="Deleting tag",
            colour=self.colours.green
        ).set_footer(text="Writing"), view=None)
        del data["tags"][name]
        data = self.handlers.fileManager(ctx.guild, action="w", data=data)
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().channel.store.create} Tag",
            description="Tag deleted successfully",
            colour=self.colours.green
        ), view=None)

    # @tag.command(name="edit", aliases=["update"])
    # @commands.guild_only()
    # async def edit(self, ctx):
    #     raise SystemExit(69)


def setup(bot):
    bot.add_cog(Tags(bot))
