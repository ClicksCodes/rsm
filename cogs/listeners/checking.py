import discord
import cv2
import os
import re
import json
import requests
import datetime
import pytesseract
import colorthief as cf

from discord.ext import commands
from cogs.consts import *


class Checking(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if message.guild is None:
            return

        att = [a.url for a in message.attachments]
        att += re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.content)

        try:
            with open(f"data/guilds/{message.guild.id}.json") as entry:
                entry = json.load(entry)
        except FileNotFoundError:
            return

        if len(att):
            for attachment in att:
                page = requests.get(attachment)
                f_name = f'tmp/{message.channel.id}{message.id}.png'
                with open(f_name, 'wb') as f:
                    f.write(page.content)
                try:
                    # OCR
                    img = cv2.imread(f_name)
                    low_thresh = 16
                    up_thresh = 4097
                    try:
                        dimensions = [img.shape[0], img.shape[1]]
                    except AttributeError:
                        try:
                            os.remove(f_name)
                        except AttributeError:
                            pass
                        continue
                    if min(dimensions) < low_thresh:
                        await message.delete()
                        e = discord.Embed(
                            title=emojis["too_small"] + f" Image too small",
                            description=f"**Name:** {message.author.mention}\n"
                                        f"**Image size:** {dimensions[0]}x{dimensions[1]}px\n"
                                        f"**Channel:** {message.channel.mention}\n"
                                        f"**ID:** `{message.author.id}`",
                            color=colours["delete"],
                            timestamp=datetime.utcnow()
                        )
                        log = self.get_log(message.guild)
                        await log.send(embed=e)
                        try:
                            os.remove(f_name)
                        except Exception as e:
                            print(e)
                        return
                    # if max(dimensions) > up_thresh:
                    #     await message.channel.send('Too large')

                    # if dimensions[1] > dimensions[0]:
                    #     w = 5000
                    #     h = (w//(dimensions[1] if dimensions[1] != 0 else 10)) * dimensions[0]
                    # else:
                    #     h = 5000
                    #     w = (h//(dimensions[0] if dimensions[0] != 0 else 10)) * dimensions[1]

                    # dim = (w, h)
                    # img = cv2.resize(img, dim)
                    custom_config = r'--oem 3 --psm 6'

                    try:
                        text = pytesseract.image_to_string(img, config=custom_config).lower()
                    except Exception as e:
                        print(e)
                        text = 'No text found'
                    if "wordfilter" in entry:
                        if message.author.id not in entry["wordfilter"]["ignore"]["members"] and message.channel.id not in entry["wordfilter"]["ignore"]["channels"]:
                            for role in [r.id for r in message.author.roles]:
                                if role in entry["wordfilter"]["ignore"]["roles"]:
                                    break
                            passed = False
                            for role in message.author.roles:
                                if role.id in entry["wordfilter"]["ignore"]["roles"]:
                                    passed = True
                            if not passed:
                                for word in [x.group().lower() for x in re.finditer( r'[a-zA-Z]+', text)]:
                                    if word in [w.lower() for w in entry["wordfilter"]["soft"]]:
                                        await message.delete()
                                        return
                                for word in entry["wordfilter"]["banned"]:
                                    if word.lower() in message.content.lower():
                                        await message.delete()
                                        return

                    if "nsfw" not in entry:
                        try:
                            os.remove(f_name)
                        except Exception as e:
                            print(e)
                        continue
                    if entry["nsfw"]:
                        try:
                            os.remove(f_name)
                        except Exception as e:
                            print(e)
                        continue
                    if "invite" in entry:
                        if not entry["invite"]["enabled"]:
                            try:
                                os.remove(f_name)
                            except Exception as e:
                                print(e)
                            return
                        if message.channel.id in entry["invite"]["whitelist"]["channels"]:
                            try:
                                os.remove(f_name)
                            except Exception as e:
                                print(e)
                        if message.author.id in entry["invite"]["whitelist"]["members"]:
                            try:
                                os.remove(f_name)
                            except Exception as e:
                                print(e)
                        if re.search(r"(?:https?:\/\/)?discord(?:app)?\.(?:com\/invite|gg)\/[a-zA-Z0-9]+\/?", text, re.MULTILINE):
                            await message.delete()
                            if entry["log_info"]["log_channel"]:
                                await message.guild.get_channel(entry["log_info"]["log_channel"]).send(embed=discord.Embed(
                                    title=emojis['invite_delete'] + " Invite sent (image)",
                                    description=f"**Channel:** {message.channel.mention}\n"
                                                f"**Sent By:** {message.author.mention}",
                                    color=colours["delete"],
                                    timestamp=datetime.utcnow()
                                ))
                            try:
                                os.remove(f_name)
                            except Exception as e:
                                print(e)
                            return
                    cfimg = cf(f_name)
                    try:
                        dc = cfimg.get_color(quality=2)
                    except Exception as e:
                        print(e)
                        dc = (0, 0, 0)

                    try:
                        if dc == (52, 60, 60):
                            blank = True
                        else:
                            blank = False
                    except Exception as e:
                        print(e)
                        blank = True

                    # NSFW
                    if message.channel.nsfw:
                        try:
                            os.remove(f_name)
                        except Exception as e:
                            print(e)
                        continue
                    reason = None
                    confidence = "80"
                    async with self.session.post("https://api.deepai.org/api/nsfw-detector", data={'image': page.url}, headers={'api-key': deepAIkey}) as r:
                        try:
                            resp = await r.json()
                            if len(resp['output']['detections']):
                                nsfw = True
                            else:
                                nsfw = False
                            try:
                                score = resp['output']['nsfw_score'] * 100
                            except Exception as e:
                                print(e)
                            if "Exposed" in [x['name'] if float(x['confidence']) > 75 else "" for x in resp['output']['detections']]:
                                nsfw = True
                            if int(score) > int(confidence):
                                nsfw = True
                            else:
                                nsfw = False
                        except Exception as e:
                            pass
                        conf = str(resp['output'])
                    try:
                        os.remove(f_name)
                    except Exception as e:
                        print(e)
                    if nsfw:
                        backn = "\n"
                        nsfwInDepth = (
                            f"{backn.join([(r['name'] + '| Confidence: ' + str(round(float(r['confidence'])*100, 2)) + '%') for r in resp['output']['detections']])}\n\n"
                            f"Overall confidence: {round(float(resp['output']['nsfw_score'])*100)}%"
                        )
                        await message.delete()
                        e = discord.Embed(
                            title=emojis["nsfw_on"] + f" NSFW image sent",
                            description=f"**Name:** {message.author.mention}\n"
                                        f"**Channel:** {message.channel.mention}\n"
                                        f"**ID:** `{message.author.id}`\n\n{nsfwInDepth}",
                            color=colours["edit"],
                            timestamp=datetime.utcnow()
                        )
                        log = self.get_log(message.guild)
                        await log.send(embed=e)
                        try:
                            os.remove(f_name)
                        except Exception as e:
                            print(e)
                        return
                except Exception as e:
                    print(e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            with open(f"data/guilds/{member.guild.id}.json") as entry:
                entry = json.load(entry)
        except FileNotFoundError:
            return
        if "welcome" in entry:
            w = entry["welcome"]
            if w["role"]:
                await member.add_roles(member.guild.get_role(w["role"]))
            if w["message"]["channel"] and w["message"]["text"]:
                if w["message"]["channel"] == "dm":
                    await member.send(w["message"]["text"].replace("[@]", member.mention).replace("[mc]", str(len(member.guild.members))))
                else:
                    await member.guild.get_channel(w["message"]["channel"]).send(w["message"]["text"].replace("[@]", member.mention).replace("[mc]", str(len(member.guild.members))))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        try:
            with open(f"data/guilds/{message.guild.id}.json") as entry:
                entry = json.load(entry)
        except FileNotFoundError:
            return
        if "invite" in entry:
            if not entry["invite"]["enabled"]:
                return
            if message.channel.id in entry["invite"]["whitelist"]["channels"]:
                return
            if message.author.id in entry["invite"]["whitelist"]["members"]:
                return
            if "roles" in entry["invite"]["whitelist"]:
                for role in entry["invite"]["whitelist"]["roles"]:
                    if role in [r.id for r in message.author.roles]:
                        return
            if re.search(r"(?:https?:\/\/)?discord(?:app)?\.(?:com\/invite|gg)\/[a-zA-Z0-9]+\/?", message.content, re.MULTILINE):
                await message.delete()
                if entry["log_info"]["log_channel"]:
                    await message.guild.get_channel(entry["log_info"]["log_channel"]).send(embed=discord.Embed(
                        title=emojis['invite_delete'] + " Invite sent",
                        description=(
                            (f"```{message.clean_content[:2042].replace('```', '***')}```\n" if message.content else "") +
                            f"**Channel:** {message.channel.mention}\n"
                            f"**Sent By:** {message.author.mention}"
                        ),
                        color=colours["delete"],
                        timestamp=datetime.datetime.utcnow()
                    ))

def setup(bot):
    bot.add_cog(Checking(bot))
