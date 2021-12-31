import asyncio
import io
import secrets
import time
import typing

import aiohttp
import discord
from cogs.consts import *
from cogs.handlers import Failed, Handlers
from config import config
from discord.ext import commands


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
        async with aiohttp.ClientSession() as session:
            async with session.get("https://clicksminuteper.net") as r:
                resp = await r.status
        if resp != 200:
            return await m.edit(embed=discord.Embed(
                title=f"{self.emojis().icon.loading} Verify",
                description=f"Our servers appear to be down, please contact the moderators "
                            f"or try again later.",
                colour=self.colours.red
            ))
        def _gencode(length=5):
            return [random.choice(
                "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890-_"
            ) for _ in range(length)]
        code = _gencode(5)
        while code in self.bot.rsmv:
            code = _gencode(5)
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
        v = self.handlers.interactions.createUI(ctx, items=[
            self.handlers.interactions.Button(
                self.bot,
                title="Verify",
                style="url",
                url=f"https://clicksminuteper.net/rsmv?code={code}",
            )
        ])
        try:
            t = await ctx.author.send(embed=discord.Embed(
                title=f"{self.emojis().control.tick} Verify",
                description=f"To verify your account, click the button below "
                            f"or click [here](https://clicksminuteper.net/rsmv?code={code}) and"
                            f"complete the check.",
                colour=self.colours.green
            ), view=v)
        except discord.HTTPException:
            return await m.channel.send(ctx.author.mention,
                embed=discord.Embed(
                    title=f"{self.emojis().control.cross} Verify",
                    description=f"Your DMs are disabled - We need to DM your code in order to keep verification secure. Please enable them and try again.",
                    colour=self.colours.red,
                ), delete_after=10
            )
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().control.tick} Verify",
            description=f"All looks good, check your DMs for a link, or click here to [jump]({t.jump_url})",
            colour=self.colours.green
        ).set_footer(text="Sent"), delete_after=10)

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
