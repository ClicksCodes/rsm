import io

import aiohttp
import datetime
import discord
import humanize
from discord.ext import commands
from dateutil.relativedelta import relativedelta
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

def mconvert(value):
    if value == 0:
        return hex_to_rgba("bbbbbb")
    return hex_to_rgba("68D49E")


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

        today = 0
        week = 0
        month = 0
        year = 0

        for member in ctx.guild.members:
            if member.joined_at + relativedelta(years=1) > datetime.datetime.now():
                year += 1
            if member.joined_at + relativedelta(months=1) > datetime.datetime.now():
                month += 1
            if member.joined_at + relativedelta(weeks=1) > datetime.datetime.now():
                week += 1
            if member.joined_at + relativedelta(days=1) > datetime.datetime.now():
                today += 1

        # Create blank image
        image = Image.new('RGBA', (1728, 972), (0, 0, 0, 255))

        # Generate server icon
        async with aiohttp.ClientSession() as session:
            async with session.get(str(ctx.guild.icon_url_as(format="png"))) as r:
                buf = io.BytesIO(await r.read())
                buf.seek(0)

        icon = Image.open(buf).resize((140, 140))
        mask = Image.new("L", icon.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, icon.size[0] - 0, icon.size[1] - 0), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(0))
        icon_round = Image.composite(icon, Image.new(icon.mode, icon.size, (0,0,0)), mask)

        # Paste icons
        image.paste(icon_round, (20, 20))

        draw = ImageDraw.Draw(image)
        titleFont = ImageFont.truetype("data/fonts/roboto/Roboto-Bold.ttf", 75)
        subFont = ImageFont.truetype("data/fonts/roboto/Roboto-Regular.ttf", 50)
        lightFont = ImageFont.truetype("data/fonts/roboto/Roboto-Light.ttf", 75)
        draw.text((180, 20), ctx.guild.name, (255, 255, 255, 255), font=titleFont)  # Server name
        draw.text((180, 110), f"Created {humanize.naturaldelta(created)} ago ({created.strftime('%Y-%M-%d at %H:%M:%S')})", hex_to_rgba("bbbbbb"), font=subFont)  # Date
        draw.arc([(20, 195), (320, 495)], start=-180, end=-180 * (bots / members), fill=hex_to_rgba("68D49E"), width=20)  # Humans
        draw.arc([(20, 195), (320, 495)], start=-180 * (bots / members), end=0, fill=hex_to_rgba("F27878"), width=20)  # Bots
        draw.text((170, 300), f"{round(humans/members * 100)}%", hex_to_rgba("68D49E"), font=subFont, anchor="mm")  # Percent

        draw.text((340, 195), f"{humanizeNumber(humans)} Humans", hex_to_rgba("68D49E"), font=subFont)  # Humans
        draw.text((340, 245), f"{humanizeNumber(bots)} Bots", hex_to_rgba("F27878"), font=subFont)  # Bots
        draw.text((340, 295), f"{humanizeNumber(members)} Total", hex_to_rgba("bbbbbb"), font=subFont)  # Total

        draw.line([(750, 195), (750, 345)], hex_to_rgba("bbbbbb"), width=5, joint="curve")

        draw.text((800, 195), f"{len(ctx.guild.roles)} Roles", hex_to_rgba("F2D478"), font=subFont)  # Roles
        draw.text((800, 245), f"{len([1 for c in ctx.guild.channels if hasattr(c, 'channels')])} Categories", hex_to_rgba("F27878"), font=subFont)  # Categories
        draw.text((800, 295), f"{len([1 for c in ctx.guild.channels if not hasattr(c, 'channels')])} Channels", hex_to_rgba("68D49E"), font=subFont)  # Channels


        x, y = 216, 400
        draw.text((864, y), "New members", hex_to_rgba("ffffff"), font=titleFont, anchor="mt")
        y += 100
        count = 0

        draw.rectangle([(0, 630), (1728, 670)], fill=hex_to_rgba("424242"))
        for period in [("Today", today, "F27878"), ("This week", week, "F2D478"), ("This month", month, "68D49E"), ("This year", year, "71AFE5")]:
            draw.text((x, y), period[0], hex_to_rgba("bbbbbb"), font=subFont, anchor="mt")
            draw.text((x, y + 55), ("+" if period [1]> 0 else "") + str(period[1]), mconvert(period[1]), font=lightFont, anchor="mt")
            draw.rectangle([(x - 216, y - 15), (x + 216, y - 25)], fill=hex_to_rgba(period[2]))
            end = (period[1] / members) * 1728
            draw.rectangle([(0, y + 125 + (count * 10)), ((end), y + 135 + (count * 10))], fill=hex_to_rgba(period[2]))
            x += 432
            count += 1

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
