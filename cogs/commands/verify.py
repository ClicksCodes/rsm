import aiohttp
import asyncio
import discord
import typing
from discord.ext import commands
import io
# import mongoengine
# import pymongo
import time
import secrets

from cogs.consts import *
from config import config
from cogs.handlers import Handlers, Failed


# class User(mongoengine.Document):
#     code = mongoengine.StringField(required=True)
#     user = mongoengine.StringField(required=True)
#     role = mongoengine.StringField(required=True)
#     role_name = mongoengine.StringField(required=True)
#     guild = mongoengine.StringField(required=True)
#     guild_name = mongoengine.StringField(required=True)
#     guild_icon_url = mongoengine.StringField(required=True)
#     guild_size = mongoengine.StringField(required=True)
#     od = time.time()

#     meta = {'collection': 'rsmv-tokens'}


class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.command()
    @commands.guild_only()
    async def verify(self, ctx):
        m = await ctx.send(embed=loading_embed)
        await ctx.delete()
        data = self.handlers.fileManager(ctx.guild)
        roleid = data["verify_role"]
        if not roleid:
            return await m.edit(
                embed=discord.Embed(
                    title=f"{self.emojis().control.cross} Verify",
                    description=f"This server does not have a verify role set. You can `{ctx.prefix}setverify` to set this role.",
                    colour=self.colours.red
                ),
                delete_after=10
            )
        if roleid in [r.id for r in ctx.author.roles]:
            return await m.edit(
                embed=discord.Embed(
                    title=f"{self.emojis().control.cross} Verify",
                    description=f"You are already verified (You already have the {ctx.guild.get_role(roleid).mention} role)",
                    colour=self.colours.red,
                ),
                delete_after=10
            )
        if not data["images"]["nsfw"]:
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().icon.loading} Please wait",
                description="We are just checking that your profile picture is safe for work",
                colour=self.colours.yellow
            ).set_footer(text="Requesting"))
            try:
                nsfw, _, score, image = await self.handlers.is_pfp_nsfw(str(ctx.author.avatar.url))
                if nsfw or image:
                    buf = io.BytesIO()
                    image.save(buf, format="png")
                    buf.seek(0)
                    if data["log_info"]["staff"]:
                        await self.bot.get_channel(data["log_info"]["staff"]).send(
                            file=discord.File(buf, filename="SPOILER_image.png", spoiler=True),
                            embed=discord.Embed(
                                title=f"{self.emojis().control.cross} Verify - NSFW avatar detected",
                                description=f"**Member:** {ctx.author.name} ({ctx.author.mention})\n"
                                            f"**Confidence:** {round(score, 2)}%\nAbove is the list of detections found",
                                colour=self.colours.red
                            ).set_footer(text="No filter is 100% accurate and therefore no action was taken")
                        )
                    return await m.edit(
                        embed=discord.Embed(
                            title=f"{self.emojis().control.cross} Verify",
                            description=f"Your avatar was detected as NSFW. Please contact the moderators to verify manually",
                            colour=self.colours.red,
                        ).set_footer(text="No filter is 100% accurate and therefore no action was taken"),
                        delete_after=10
                    )
            except AttributeError:
                pass
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().icon.loading} Verify",
            description=f"All looks good, please wait",
            colour=self.colours.green
        ).set_footer(text="Connecting"))
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(f"https://clicksminuteper.net/") as r:
        #         if r.status != 200:
        #             return await m.edit(
        #                 embed=discord.Embed(
        #                     title=f"{self.emojis().control.cross} Verify",
        #                     description=f"We could not connect to the verification server. Please try again later",
        #                     colour=self.colours.red
        #                 ),
        #                 delete_after=10
        #             )
        a = 5
        code = secrets.token_urlsafe(a)
        while code in self.bot.rsmv:
            code = secrets.token_urlsafe(a)
            await asyncio.sleep(0)
        self.bot.rsmv[code] = {
            "user": str(ctx.author.id),
            "guild": str(ctx.guild.id),
            "guild_name": str(ctx.guild.name),
            "guild_icon_url": str(ctx.guild.icon.url),
            "guild_size": str(len(ctx.guild.members)),
            "role": str(roleid),
            "role_name": str(ctx.guild.get_role(roleid).name),
        }
        v = handlers.interactions.createUI(items=[
            handlers.interactions.button(
                label = "Verify",
                style = "url",
                url = f"https://clicksminuteper.net/rsmv?code={code}",
            )
        ])
        # try:
        #     mongoengine.connect(
        #         'rsm',
        #         host=config.mongoUrl
        #     )
        #     code = secrets.token_urlsafe(16)
        #     User(
        #         code=str(code),
        #         user=str(ctx.author.id),
        #         role=str(roleid),
        #         role_name=str(ctx.guild.get_role(roleid).name),
        #         guild=str(ctx.guild.id),
        #         guild_name=str(ctx.guild.name),
        #         guild_icon_url=str(ctx.guild.icon.url),
        #         guild_size=str(len(ctx.guild.members))
        #     ).save()
        # except (TypeError, pymongo.errors.ServerSelectionTimeoutError):
        #     return await m.edit(
        #         embed=discord.Embed(
        #             title=f"{self.emojis().control.cross} Verify",
        #             description=f"Our database appears to be down, and could not connect. Please contact the moderators in order to verify manually",
        #             colour=self.colours.red,
        #         ).set_footer(text="Connection failed"),
        #         delete_after=10
        #     )
        try:
            await ctx.author.send(embed=discord.Embed(
                title=f"{self.emojis().control.tick} Verify",
                description=f"Please click the link below to verify your account, "
                            f"or click [here](htts://clicksminuteper.net/rsmv?code={code})",
                colour=self.colours.green
            ), view=v)
        except discord.HTTPException:
            await m.channel.send(ctx.author.mention,
                embed=discord.Embed(
                    title=f"{self.emojis().control.cross} Verify",
                    description=f"Your DMs are disabled - We need to DM your code in order to keep verification secure. Please enable them and try again.",
                    colour=self.colours.red,
                ), delete_after=10
            )
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().icon.loading} Verify",
            description=f"All looks good, check your DMs for a link",
            colour=self.colours.green
        ).set_footer(text="Sent"))
        await asyncio.sleep(10)
        await m.delete()

    @commands.command()
    @commands.guild_only()
    async def setverify(self, ctx, role: typing.Optional[discord.Role]):
        m = await ctx.send(embed=loading_embed)
        if isinstance(await self.handlers.checkPerms(ctx, m, "manage_guild", emoji=self.emojis().control.tick, action="set the verify role", me=False), Failed):
            return
        if not role:
            role = await self.handlers.roleHandler(
                ctx,
                m,
                emoji=self.emojis().control.tick,
                title="Setverify",
                description="What role should be given when members verify?",
                optional=True,
                default=None
            )
            if isinstance(role, Failed):
                return
        await m.edit(
            embed=discord.Embed(
                title=f"{self.emojis().control.tick} Setverify",
                description=f"Setting role.",
                colour=self.colours.green,
            ).set_footer(text="Reading"), view=None
        )
        data = self.handlers.fileManager(ctx.guild)
        data["verify_role"] = role.id if role else None
        await m.edit(
            embed=discord.Embed(
                title=f"{self.emojis().control.tick} Setverify",
                description=f"Setting role.",
                colour=self.colours.green,
            ).set_footer(text="Writing"), view=None
        )
        self.handlers.fileManager(ctx.guild, action="w", data=data)
        await m.edit(
            embed=discord.Embed(
                title=f"{self.emojis().control.tick} Setverify",
                description=f"Set verify role successfully to {role.mention if role else 'None'}.",
                colour=self.colours.green,
            ), view=None
        )


def setup(bot):
    bot.add_cog(Verify(bot))
