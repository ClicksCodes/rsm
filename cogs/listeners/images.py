import copy, discord, json, humanize, aiohttp, traceback, typing, requests, cv2, pytesseract, os, random, re, time, shutil

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus
from colorthief import ColorThief as cf

from cogs.consts import *

class ImageDetect(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open("./data/core.json") as rfile: self.data = json.load(rfile)
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10.0))
    
    def cog_unload(self): 
        with open("./data/core.json", "w") as wfile: json.dump(self.data, wfile, indent=2)
        self.bot.loop.create_task(self.session.close())

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        att = [a.url for a in message.attachments]
        att += re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.content)
        
        if len(att):
            for attachment in att:
                page = requests.get(attachment)
                f_name = f'{random.randint(0,9999999999999999)}.png'
                with open(f_name, 'wb') as f: f.write(page.content)
                try:
                    # OCR
                    img = cv2.imread(f_name)
                    low_thresh = 16
                    up_thresh  = 4097
                    dimensions = [img.shape[0], img.shape[1]]
                    if min(dimensions) < low_thresh: await message.channel.send('Too small')
                    if max(dimensions) > up_thresh:  await message.channel.send('Too large')

                    if dimensions[1] > dimensions[0]:
                        w = 5000
                        h = (w//(dimensions[1] if dimensions[1] != 0 else 10)) * dimensions[0]
                    else:
                        h = 5000
                        w = (h//(dimensions[0] if dimensions[0] != 0 else 10)) * dimensions[1]
                    dim = (w, h)
                    img = cv2.resize(img, dim)
                    custom_config = r'--oem 3 --psm 6'

                    read_start = time.time()
                    try: 
                        text = pytesseract.image_to_string(img, config=custom_config).lower()
                    except:
                        text = 'No text found'

                    read_end = time.time()

                    cfimg = cf(f_name)
                    try: dc = cfimg.get_color(quality=2)
                    except: dc = (0,0,0)

                    try:
                        if dc == (52,60,60): blank = True
                        else: blank = False
                    except :
                        blank = True
                    
                    # NSFW
                    start = time.time()
                    async with self.session.post("https://api.deepai.org/api/nsfw-detector",data={'image': page.url},headers={'api-key': '5d6cca50-2441-44a8-9ab4-703fbd38ce5b'}) as r:
                        try:
                            resp = await r.json()
                            if len(resp['output']['detections']): nsfw = True
                            else: nsfw = False
                        except Exception as e: nsfw = False; print('1' + str(e))
                        conf = str(resp['output'])
                    end = time.time()
                    
                    e = discord.Embed(
                        title="Image sent",
                        description=f"**Size:** {dimensions[0]}x{dimensions[1]}\n"
                                    f"**Resized:** {w}x{h}\n"
                                    f"**NSFW:** {emojis['tick'] if nsfw else emojis['cross']}\n"
                                    f"**Text:** {text}\n"
                                    f"**RGB Colour:** {dc}\n"
                                    f"**Blank Image:** {emojis['tick'] if blank else emojis['cross']}\n"
                                    f"**Image Read Time Taken:** {round(read_end - read_start, 2)}s\n"
                                    f"**Web Request Time Taken:** {round(end - start, 2)}s",
                        color=discord.Color(0x00ff00)
                    )
                    #if message.author.bot == False: await message.channel.send(embed=e)
                except Exception as e: print(e)
                finally:
                    try: os.rename(f"{f_name}", f"cogs/{'nsfw' if nsfw else 'sfw'}/{f_name}")
                    except Exception as e: 
                        try: os.remove(f_name)
                        except: pass
        

def setup(bot):
    bot.add_cog(ImageDetect(bot))