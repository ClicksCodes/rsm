import io

import aiohttp
import discord
import humanize
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from cogs.consts import *


def humanizeNumber(number):
    num = humanize.intword(number)
    if not num.split(" ")[-1].isdigit():
        num = str(round(int(float(" ".join(num.split(" ")[:-1]))))) + num.split(" ")[-1][:2].capitalize()
    return num

def hex_to_rgba(value, alpha=255):
    lv = len(value)
    return tuple(int(value[i: i + lv // 3], 16) for i in range(0, lv, lv // 3)) + (alpha,)


class GuildCommands(commands.Cog):
    def __init__(self, bot):
        self.loadingEmbed = loadingEmbed
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def breakdown(self, ctx):
        members = len(ctx.guild.members)
        bots = len([m for m in ctx.guild.members if m.bot])
        humans = members - bots
        created = ctx.guild.created_at

        # Create blank image
        image = Image.new('RGBA', (1728, 972), (0, 0, 0, 255))

        # Generate server icon
        async with aiohttp.ClientSession() as session:
            async with session.get(str(ctx.guild.icon_url)) as r:
                buf = io.BytesIO(await r.read())
                buf.seek(0)

        icon = Image.open(buf).resize((140, 140))
        mask = Image.new("L", icon.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, icon.size[0] - 0, icon.size[1] - 0), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(0))
        icon_round = Image.composite(icon, Image.new(icon.mode, icon.size, (0,0,0)), mask)

        # Generate owner icon
        async with aiohttp.ClientSession() as session:
            async with session.get(str(ctx.guild.owner.avatar_url)) as r:
                buf = io.BytesIO(await r.read())
                buf.seek(0)

        icon = Image.open(buf).resize((140, 140))
        mask = Image.new("L", icon.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, icon.size[0] - 0, icon.size[1] - 0), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(0))
        owner_icon = Image.composite(icon, Image.new(icon.mode, icon.size, (0,0,0)), mask)

        # Paste icons
        image.paste(icon_round, (20, 20))
        image.paste(owner_icon, (20, 375))

        draw = ImageDraw.Draw(image)
        titleFont = ImageFont.truetype("data/fonts/roboto/Roboto-Bold.ttf", 75)
        subFont = ImageFont.truetype("data/fonts/roboto/Roboto-Regular.ttf", 50)
        draw.text((180, 20), ctx.guild.name, (255, 255, 255, 255), font=titleFont)  # Server name
        draw.text((180, 110), f"Created {humanize.naturaldelta(created)} ago ({created.strftime('%Y-%M-%d at %H:%M:%S')})", hex_to_rgba("bbbbbb"), font=subFont)  # Date
        draw.text((180, 375), f"Owner: {ctx.guild.owner.display_name}", (255, 255, 255, 255), font=titleFont)  # Owner name
        draw.text((180, 465), f"{ctx.guild.owner.name}#{ctx.guild.owner.discriminator}", hex_to_rgba("bbbbbb"), font=subFont)  # Owner info
        draw.arc([(20, 195), (320, 495)], start=-180, end=-180 * (bots / members), fill=hex_to_rgba("68D49E"), width=20)  # Humans
        draw.arc([(20, 195), (320, 495)], start=-180 * (bots / members), end=0, fill=hex_to_rgba("F27878"), width=20)  # Bots
        draw.text((170, 300), f"{round(humans/members * 100)}%", hex_to_rgba("68D49E"), font=subFont, anchor="mm")  # Percent

        draw.text((340, 195), f"{humanizeNumber(humans)} Humans", hex_to_rgba("68D49E"), font=subFont)  # Humans
        draw.text((340, 245), f"{humanizeNumber(bots)} Bots", hex_to_rgba("F27878"), font=subFont)  # Bots
        draw.text((340, 295), f"{humanizeNumber(members)} Total", hex_to_rgba("bbbbbb"), font=subFont)  # Total

        draw.line([(750, 195), (750, 345)], hex_to_rgba("bbbbbb"), width=5, joint="curve")

        draw.text((800, 195), f"{len(ctx.guild.roles)} Roles", hex_to_rgba("F2D478"), font=subFont)  # Humans
        draw.text((800, 245), f"{len([1 for c in ctx.guild.channels if hasattr(c, 'channels')])} Categories", hex_to_rgba("F27878"), font=subFont)  # Bots
        draw.text((800, 295), f"{len([1 for c in ctx.guild.channels if not hasattr(c, 'channels')])} Channels", hex_to_rgba("68D49E"), font=subFont)  # Total

        # Save image
        buf = io.BytesIO()
        image.save(buf, format="png")
        buf.seek(0)

        e=discord.Embed(
            title="Server breakdown"
        )

        e.set_image(url="attachment://image.png")
        m = await ctx.send(
            embed=e,
            file=discord.File(buf, "image.png")
        )

def setup(bot):
    bot.add_cog(GuildCommands(bot))
