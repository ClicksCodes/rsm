import aiohttp
import asyncio
import re
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

        self.vars = {}
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
        setup = instrs[0]
        instrs = instrs[1:]

        variables = setup.split(" ")[1:]
        for variable in variables:
            self.vars[str(variable)] = None
        for option in self.options:
            if option.type == 3:
                self.vars[str(option.name)] = str(option.value)
            elif option.type == 3:
                self.vars[str(option.name)] = int(option.value)
            elif option.type == 3:
                self.vars[str(option.name)] = bool(option.value)
            else:
                self.vars[str(option.name)] = option.value

        for instr in instrs:
            instruction = instr.split(" ")[0]
            params = instr.split(" ")[1:]
            if instruction == "SEND":
                await self.bot.get_channel(self.channel_id).send(" ".join(params))
                await asyncio.sleep(0.1)
            elif instruction == "REPLY":
                await self.followup(" ".join(params))
                await asyncio.sleep(0.1)
            elif instruction in self.vars:
                if params[0] == "=":
                    self.vars[str(instruction)] = self.parse(params[1:])
                elif params[0] == "+=":
                    self.vars[str(instruction)] = self.vars[str(instruction)] + self.parse(params[1:])
                elif params[0] == "-=":
                    self.vars[str(instruction)] = self.vars[str(instruction)] - self.parse(params[1:])
                elif params[0] == "*=":
                    self.vars[str(instruction)] = self.vars[str(instruction)] * self.parse(params[1:])
                elif params[0] == "/=":
                    self.vars[str(instruction)] = self.vars[str(instruction)] / self.parse(params[1:])
            else:
                return await self.edit_initial_message(f"{emojis['dnd']} Could not decode instruction into a variable or function")
            print(self.vars)
        await self.edit_initial_message(f"{emojis['online']} Command finished successfully")

    def parse(self, params):
        parsed = []
        for param in params:
            parsed.append([param, 0])
        for x in range(len(parsed)):
            if parsed[x].isdigit():
                parsed[x] = [int(parsed[x][0]), 1]

def fetchFunction(gid, name):
    try:
        with open(f"data/slash/{gid}/{name}.rsm") as f:
            lines = []
            for line in f.readlines():
                groups = re.search(r"^(((?![#\\]).)+(\\\\)*(\\#)?)+(?=#)?", line)
                if groups:
                    lines.append(groups.group(0))
            return lines
    except FileNotFoundError:
        return 404

