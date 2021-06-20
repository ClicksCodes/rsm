import typing
import discord
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers


class Public(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)

    @commands.command()
    @commands.guild_only()
    async def avatar(self, ctx, member: typing.Optional[discord.Member]):
        m = await ctx.send(embed=loading_embed)
        if not member:
            member = ctx.author
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().member.join} Avatar",
            description=f"**URL:** [[Open]]({member.avatar_url})\n"
                        f"**Member:** {member.mention}",
            colour=self.colours.green
        ).set_image(url=member.avatar_url))

    @commands.command(aliases=["server", "serverinfo", "guildinfo"])
    @commands.guild_only()
    async def guild(self, ctx):
        m = await ctx.send(embed=loading_embed)
        g = ctx.guild
        match g.explicit_content_filter.name:
            case "disabled": ecf = "Disabled"
            case "no_role": ecf = "Everyone with no role"
            case "all_members": ecf = "Everyone"
            case _: ecf = "Failed to fetch"
        match g.region.name:
            case "amsterdam": region = ":flag_an: The Netherlands"
            case "brazil": region = ":flag_br: Brazil"
            case "dubai": region = ":flag_ae: United Arab Emirates"
            case "eu_central": region = ":flag_eu: Europe (Central)"
            case "eu_west": region = ":flag_eu: Europe (West)"
            case "europe": region = ":flag_eu: Europe"
            case "frankfurt": region = ":flag_de: Germany"
            case "hongkong": region = ":flag_hk: Hong Kong"
            case "india": region = ":flag_in: India"
            case "japan": region = ":flag_jp: Japan"
            case "russia": region = ":flag_ru: Russia"
            case "singapore": region = ":flag_sg: Singapore"
            case "southafrica": region = ":flag_za: South Africa"
            case "sydney": region = ":flag_au: Australia"
            case "us_central": region = ":flag_us: USA (Central)"
            case "us_east": region = ":flag_us: USA (East)"
            case "us_south": region = ":flag_us: USA (South"
            case "us_west": region = ":flag_us: USA (West)"
            case "vip_amsterdam": region = ":flag_an: The Netherlands (VIP)"
            case "vip_us_east": region = ":flag_us: USA (East, VIP)"
            case "vip_us_west": region = ":flag_us: USA (West, VIP)"
            case "_": region = "Failed to fetch"
        await m.edit(embed=discord.Embed(
            title="Server stats",
            description=f"**Name:** {g.name}\n"
                        f"**Created:** {self.handlers.betterDelta(g.created_at)}\n"
                        f"**Region:** {region}\n"
                        f"**Emojis:** {len(g.emojis)}\n> {' '.join([str(e) for e in g.emojis][:25])}{'...' if len(g.emojis) > 25 else ''}\n"
                        f"**Icon:** [[discord.com]]({g.icon_url})\n"
                        f"**ID:** `{g.id}`\n"
                        f"**Owner:** {g.owner.name} ({g.owner.mention})\n"
                        f"**2FA required:** {self.emojis().control.tick if g.mfa_level else self.emojis().control.cross}\n"
                        f"**Verification level:** {g.verification_level.name.capitalize()}\n"
                        f"**Explicit content filter:** {ecf}\n"
                        f"**Default notifications:** {g.default_notifications.name.replace('_', ' ').capitalize()}\n"
                        f"**Nitro boost level:** {g.premium_tier}\n"
                        f"**Channels:** {sum([1 if not c.type.name == 'category' else 0 for c in g.channels])}\n"
                        f"**Categories:** {len(g.categories)}\n"
                        f"**Roles:** {len(g.roles)}\n"
                        f"**Members:** {len(g.members)}\n",
            colour=self.colours.green
        ).set_thumbnail(url=g.icon_url).set_image(url=g.banner_url))


def setup(bot):
    bot.add_cog(Public(bot))
