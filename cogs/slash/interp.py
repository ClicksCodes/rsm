import aiohttp
import asyncio
import regex
import pineaprint as pp
from cogs.consts import *


class Member:
    def __init__(self, member):
        user = member["user"]
        self.username = user["username"]
        self.public_flags = user["public_flags"]
        self.id = user["id"]
        self.discriminator = user["discriminator"]
        self.avatar = user["avatar"]
        self.username = user["username"]

        self.roles = member["roles"]
        self.premium_since = member["premium_since"]
        self.permissions = member["permissions"]
        self.pending = member["pending"]
        self.nick = member["nick"]
        self.mute = member["mute"]
        self.joined_at = member["joined_at"]
        self.is_pending = member["is_pending"]
        self.deaf = member["deaf"]

class User:
    def __init__(self, user):
        self.username = user["username"]
        self.public_flags = user["public_flags"]
        self.id = user["id"]
        self.discriminator = user["discriminator"]
        self.avatar = user["avatar"]
        self.username = user["username"]

class Role:
    def __init__(self, role):
        self.position = role["position"]
        self.permissions = role["permissions"]
        self.name = role["name"]
        self.mentionable = role["mentionable"]
        self.managed = role["managed"]
        self.id = role["id"]
        self.hoist = role["hoist"]
        self.color = role["color"]

class Channel:
    def __init__(self, channel):
        types = {
            0: "text",
            1: "dm",
            2: "voice",
            3: "group_dm",
            4: "category",
            5: "news",
            6: "store",
            10: "news_thread",
            11: "public_thread",
            12: "private_thread",
            13: "stage"
        }
        self.type = types[channel["type"]]
        self.permissions = channel["permissions"]
        self.name = channel["id"]

class Option:
    def __init__(self, data):
        types = {
            1: "sub_command",
            2: "sub_command_group",
            3: "string",
            4: "integer",
            5: "boolean",
            6: "user",
            7: "channel",
            8: "role",
            9: "mentionable",
        }
        self.name = data["name"]
        self.value = data["value"]
        self.type = types[data["type"]]

class Command:
    def __init__(self, data, bot):
        self.version = data["version"]
        self.token = data["token"]
        self.id = data["id"]
        self.guild_id = int(data["guild_id"])
        self.channel_id = int(data["channel_id"])
        self.application_id = data["application_id"]

        self.author = Member(data["member"])

        self.name = data["data"]["name"]
        self.command_id = data["data"]["id"]

        self.options = [Option(o) for o in data["data"]["options"]] if "options" in data["data"] else []
        self.bot = bot
        asyncio.create_task(self.create_initial_message())

    async def create_initial_message(self):
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"https://discord.com/api/v8/interactions/{self.id}/{self.token}/callback",
                json={"type": 4, "data": {"content": f"{emojis['online']} Running custom command", "flags": 64}},
                headers={'Authorization': f'Bot {self.bot.http.token}'}
            )
            await session.close()

    async def edit_initial_message(self, response):
        async with aiohttp.ClientSession() as session:
            await session.patch(
                f"https://discord.com/api/v8/webhooks/{self.application_id}/{self.token}/messages/@original",
                json={"content": response},
                headers={'Authorization': f'Bot {self.bot.http.token}'}
            )
            await session.close()

    async def followup(self, response, hidden=True):
        print(response)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://discord.com/api/v8/webhooks/{self.application_id}/{self.token}",
                json={"content": response, "flags": (64 if hidden else 0)},
                headers={'Authorization': f'Bot {self.bot.http.token}'}
            ) as r:
                pass

    async def run(self, instrs):
        if instrs == 404:
            return await self.edit_initial_message(f"{emojis['idle']} Command `{self.name}` not found")
        try:
            await self.followup(str(instrs))
        except Exception as e:
            print(e)
            await self.edit_initial_message(f"{emojis['dnd']} An error occurred when running the command")
        await self.edit_initial_message(f"{emojis['online']} Command finished successfully")

def fetchFunction(gid, name):
    try:
        with open(f"data/slash/{gid}/{name}.rsm") as f:
            lines = []
            for line in f.readlines():
                groups = re.search("")
            return [l.strip() for l in f.readlines() if len(l.strip()) > 0]
    except FileNotFoundError:
        return 404

