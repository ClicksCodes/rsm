import typing
import discord
from discord import interactions
import datetime
from discord.ext import commands
from discord.ext.commands.converter import T

from cogs.consts import *
from cogs.handlers import Handlers
from cogs import interactions


class Public(commands.Cog):
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
        if interaction.data["type"] == 2:
            if interaction.data["name"] == "Flag for moderators":
                data = self.handlers.fileManager(interaction.guild)
                if data["log_info"]["staff"]:
                    await interaction.guild.get_channel(data["log_info"]["channel"]).send(embed=discord.Embed(
                        title=f"Member flagged",
                        description=f"**Flagged by:** {interaction.user.mention}\n"
                                    f"**Member flagged:** {interaction.guild.get_member(interaction.data['target_id']).mention}\n"
                                    f"**Flagged at:** {self.handlers.strf(datetime.datetime.now())}\n",
                        colour=self.colours.red
                    ))
                    await interaction.response.send_message(embed=discord.Embed(
                        title=f"Member flagged",
                        description=f"Member flagged successfully",
                        colour=self.colours.green
                    ), ephemeral=True)
                else:
                    await interaction.response.send_message(embed=discord.Embed(
                        title=f"Not accepting flags",
                        description=f"This server is not accepting member flags",
                        colour=self.colours.red
                    ), ephemeral=True)
        elif interaction.data["type"] == 3:
            if interaction.data["name"] == "Show message data":
                await interaction.response.send_message(embed=loading_embed, ephemeral=True)
                m = await interaction.original_message()
                await self._showdata(m, interaction.data, interaction.channel)
            elif interaction.data["name"] == "Flag for moderators":
                await interaction.response.send_message(embed=loading_embed, ephemeral=True)
                m = await interaction.original_message()
                return await m.edit(embed=discord.Embed(
                    title=f"Coming soon",
                    description=f"Sadly, this feature is not yet added. It is, however, being actively developed",
                    colour=self.colours.red
                ))
        elif interaction.type.name == "application_command" and interaction.guild:
            pass
            # if interaction.data["name"] == "apply":

    async def _showdata(self, m, data, channel):
        mes = await channel.fetch_message(data["target_id"])
        await m.edit(embed=discord.Embed(
            title=f"Message data",
            description=(
                f"Authour: {mes.author.mention}\n"
                f"Attachments: \n" + "".join([
                    f"> [[URL]]({n.url}) | Type: `{n.content_type}` | File: `{n.filename}`" +
                    (f" | Size: `{n.width}x{n.height}`" if hasattr(n, "height") else "") + "\n" for n in mes.attachments
                ]) +
                f"Sent: {self.handlers.betterDelta(mes.created_at)}\n"
                f"Jump URL:\n> {mes.jump_url}\n"
                f"Edited: {self.handlers.betterDelta(mes.edited_at) if mes.edited_at else 'Never'}\n"
                f"Mentioned everyone: {'Yes' if mes.mention_everyone else 'No'}\n"
                f"Nonce: `{mes.nonce}`\n"
                f"ID: `{mes.id}`"
            ),
            colour=self.colours.green
        ))

    @commands.command()
    @commands.guild_only()
    async def avatar(self, ctx, member: typing.Optional[discord.Member]):
        m = await ctx.send(embed=loading_embed)
        if not member:
            member = ctx.author
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().member.join} Avatar",
            description=f"**URL:** [[Open]]({member.avatar.url})\n"
                        f"**Member:** {member.mention}",
            colour=self.colours.green
        ).set_image(url=member.avatar.url))

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
                        f"**Icon:** [[discord.com]]({g.icon.url})\n"
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
        ).set_thumbnail(url=g.icon.url).set_image(url=(g.banner.url if g.banner else "")))


def setup(bot):
    bot.add_cog(Public(bot))
