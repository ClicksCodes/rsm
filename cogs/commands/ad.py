import asyncio
import io
import aiohttp
import webcolors
import typing
import discord
import numpy as np
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed
from cogs import interactions

from PIL import Image, ImageFilter, ImageDraw, ImageFont


def palette(img):
    arr = np.asarray(img)
    palette, index = np.unique(asvoid(arr).ravel(), return_inverse=True)
    palette = palette.view(arr.dtype).reshape(-1, arr.shape[-1])
    count = np.bincount(index)
    order = np.argsort(count)
    return palette[order[::-1]]

def asvoid(arr):
    arr = np.ascontiguousarray(arr)
    return arr.view(np.dtype((np.void, arr.dtype.itemsize * arr.shape[-1])))


def get_colour_name(rgb_triplet):
    min_colours = {}
    for key, name in webcolors.CSS21_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - rgb_triplet[0]) ** 2
        gd = (g_c - rgb_triplet[1]) ** 2
        bd = (b_c - rgb_triplet[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


class Ad(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)
        self.images = {}

    def circle(self, image):
        width, height = image.size
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, width, height), fill=255)
        image = image.convert("RGBA")
        image.putalpha(mask)
        return image

    async def downloadTo(self, downloads):
        out = []
        async with aiohttp.ClientSession() as session:
            for download in downloads:
                async with session.get(download) as r:
                    im = Image.open(io.BytesIO(await r.read()))
                    im = im.resize((150, 150), Image.ANTIALIAS)  # Resize image
                    im = self.circle(im)  # Circle image
                    out.append(im)
        return out

    @commands.command()
    async def ad(self, ctx):
        BACKGROUND = (255, 255, 255, 255)
        FOREGROUND = (0, 0, 0, 255)

        bots = [u for u in ctx.guild.members if u.bot]
        bots = sorted(bots, key=lambda bot: (bot.status.name == "offline", 1000 - bot.top_role.position, bot.display_name))
        urls = [bot.avatar.url for bot in bots][:5]

        async def download():
            self.images[f"{ctx.guild.id}{ctx.channel.id}{ctx.message.id}"] = await self.downloadTo(urls)
        task = asyncio.create_task(download())

        async with aiohttp.ClientSession() as session:
            async with session.get(ctx.guild.icon.url) as r:
                buf = io.BytesIO(await r.read())
                buf.seek(0)

        icon = Image.open(buf)
        rgbToUse = {}
        for colour in palette(icon):
            name = get_colour_name(colour[:3])
            if name not in rgbToUse.keys():
                rgbToUse[name] = [colour]
            else:
                rgbToUse[name].append(colour)
        rgbToUse = {k: np.mean(v, axis=0) for k, v in rgbToUse.items() if k not in ["gray", "black", "white"]}
        for k, v in rgbToUse.items():
            rgbToUse[k] = tuple(v)
        if "teal" and "navy" in rgbToUse:
            teal = (rgbToUse["teal"][0], rgbToUse["teal"][1], rgbToUse["teal"][2])
            navy = (rgbToUse["navy"][0], rgbToUse["navy"][1], rgbToUse["navy"][2])
            rgbToUse["teal"] = ((teal[0] + navy[0]) / 2, (teal[1] + navy[1]) / 2, (teal[2] + navy[2]) / 2, 255)
            del rgbToUse["navy"]
        if "red" and "maroon" in rgbToUse:
            red = (rgbToUse["red"][0], rgbToUse["red"][1], rgbToUse["red"][2])
            maroon = (rgbToUse["maroon"][0], rgbToUse["maroon"][1], rgbToUse["maroon"][2])
            rgbToUse["red"] = ((red[0] + maroon[0]) / 2, (red[1] + maroon[1]) / 2, (red[2] + maroon[2]) / 2, 255)
            del rgbToUse["maroon"]
        if "black" in rgbToUse and len(rgbToUse) > 2:
            del rgbToUse["black"]
        if "white" in rgbToUse and len(rgbToUse) > 2:
            del rgbToUse["white"]
        if "gray" in rgbToUse and len(rgbToUse) > 2:
            del rgbToUse["gray"]
        if not len(rgbToUse):
            rgbToUse = {"white": (255, 255, 255, 255), "black": (0, 0, 0, 255)}
        if len(rgbToUse) == 1:
            rgbToUse["second"] = (255, 255, 255, 255)
        for k, v in rgbToUse.items():
            rgbToUse[k] = [round(i) for i in v]
        BACKGROUND = list(rgbToUse.values())[0]
        FOREGROUND = list(rgbToUse.values())[1]
        cover = Image.new("RGBA", (1500, 750), color=(255, 255, 255, 0))  # Generate blank image

        card = Image.open("data/images/Card.png")  # Get card
        cover.paste(card, (0, 0), card)  # Paste card onto cover

        icon = icon.resize((150, 150), Image.ANTIALIAS)  # Resize icon
        icon = self.circle(icon)  # Circle icon
        cover.paste(icon, ((cover.size[0] - icon.size[0]) // 2, 80), icon)  # Paste icon onto cover

        font = ImageFont.truetype("data/fonts/roboto/Roboto-Light.ttf", size=100)  # Get font
        draw = ImageDraw.Draw(cover)
        text = ctx.guild.name
        draw.text(((cover.size[0] - font.getsize(text)[0]) // 2, 225), text=text, font=font, fill=(66, 66, 66, 255))  # Write name onto cover

        font = ImageFont.truetype("data/fonts/roboto/Roboto-Regular.ttf", size=44)  # Get font
        invite = await ctx.guild.invites()
        url = ""
        if invite:
            url = invite[0].url
        text = f"{len(ctx.guild.members)} members" + (f"   •   {url}" if url else "")
        size = font.getsize(text)[0]
        offset = (cover.size[0] - size) // 2, 325
        text = f"{len(ctx.guild.members)} members" + (f"   •   " if url else "")
        draw.text(offset, text, font=font, fill=(66, 66, 66, 255))  # Write member onto cover
        if url:
            draw.text(((offset[0] + size + font.getsize("   •    ")[0]) // 2, 325), url, font=font, fill=(101, 118, 204))  # Write url onto cover
        created = ctx.guild.created_at
        text = f"Created on {created.strftime('%A %d %B %Y')}"
        size = font.getsize(text)[0]
        offset = (cover.size[0] - size) // 2, 600
        draw.text(offset, text, font=font, fill=(66, 66, 66, 255))  # Write created date onto cover

        await asyncio.wait_for(task, timeout=10)
        images = self.images[f"{ctx.guild.id}{ctx.channel.id}{ctx.message.id}"]
        x = ((cover.size[0] - (200 * len(images))) // 2) + 25
        for image in images:
            cover.paste(image, (x, 410), image)  # Paste image onto cover
            x += 200

        while True:
            main = Image.new("RGBA", (1500, 750), color=tuple(BACKGROUND))  # Generate blank image
            wave = Image.open("data/images/Wave.png")  # Get wave
            wave.convert("RGBA")
            data = np.array(wave)
            r, g, b, a = data.T
            red = (r == 255) & (g == 0) & (b == 0)
            data[..., :-1][red.T] = FOREGROUND[:3]  # Replace red with secondary colour
            wave = Image.fromarray(data)
            main.paste(wave, (0, cover.size[1] - wave.size[1]), wave)  # Paste wave onto main

            box = (50, 47, 1450, 703)  # Get box
            temp = main.crop(box)
            temp = temp.filter(ImageFilter.GaussianBlur(radius=15))  # Blur area
            main.paste(temp, box)  # Paste box onto cover


            main.paste(cover, (0, 0), cover)  # Paste cover onto main
            rad = 75
            circle = Image.new('L', (rad * 2, rad * 2), 0)
            draw = ImageDraw.Draw(circle)
            draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
            alpha = Image.new('L', main.size, 255)
            w, h = main.size
            alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
            alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
            alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
            alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
            main.putalpha(alpha)  # Round corners

            buf = io.BytesIO()
            main.save(buf, format="PNG")
            buf.seek(0)
            await ctx.send(file=discord.File(buf, filename="ad.png"))
            break

def setup(bot):
    bot.add_cog(Ad(bot))
