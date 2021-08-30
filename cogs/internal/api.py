import datetime
import discord
import typing
import uvicorn
from cogs.handlers import Handlers
from cogs.consts import *
from config import config

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(docs_url=None, redoc_url=None)
colours = Cols()
emojis = Emojis

@app.get("/")
def root():
    from global_vars import bot
    return PlainTextResponse(str(bot.latency))


@app.get("/stage")
async def stage():
    return PlainTextResponse(str(config.stage.name))


@app.get("/role/gid/{guild}/rid/{role}/user/{user}/secret/{secret}/code/{code}")
async def role(guild: int, role: int, user: int, secret: str, code):
    from global_vars import bot
    try:
        if secret != config.urlsecret:
            return PlainTextResponse("403", 403)
        g = bot.get_guild(guild)
        mem = await g.fetch_member(user)

        await mem.add_roles(g.get_role(role))
        await mem.send(embed=discord.Embed(
            title=f"{emojis().control.tick} Verified",
            description=f"You are now verified in {g.name}. The `@{bot.get_guild(guild).get_role(role).name}` role has now been given.",
            colour=colours.green
        ))
        return PlainTextResponse("200", 200)
    except Exception as e:
        print(e)
        return PlainTextResponse("400", 400)


@app.get("/in/{guild}")
async def inGuild(guild: int):
    from global_vars import bot
    if guild in [g.id for g in bot.guilds]:
        return PlainTextResponse("True", 200)
    return PlainTextResponse("False", 404)


@app.get("/auth/{code}/user/{uid}")
async def mutuals(code, uid):
    from global_vars import bot
    if code != config.urlsecret:
        return PlainTextResponse("403", 403)
    guilds = []
    for guild in bot.guilds:
        for member in guild.members:
            if member.id == int(uid):
                guilds.append(guild.id)
    return JSONResponse(guilds, "200")


class Item(BaseModel):
    guild_id: int
    created_by: int
    questions: typing.Optional[int]
    name: str
    auth: str


@app.post("/clicksforms/create")
async def create(item: Item):
    from global_vars import bot
    data = dict(item)
    if data["auth"] != config.cfToken:
        return PlainTextResponse("403", 403)
    g = bot.apihandlers.fileManager(int(data["guild_id"]), create=False)
    if g is False:
        return PlainTextResponse("404", 404)
    await bot.apihandlers.sendLog(
        emoji=emojis().bots.clicksforms,
        type="Form created",
        server=int(data["guild_id"]),
        colour=colours.green,
        data={
            "Created by": f"{bot.get_user(data['created_by']).name} ({bot.get_user(data['created_by']).mention})",
            "Name": data['name'],
            "Questions": data['questions'],
            "Created": bot.apihandlers.strf(datetime.datetime.utcnow())
        }
    )
    return PlainTextResponse("200", 200)


@app.post("/clicksforms/import/googleforms")
async def create(item: Item):
    from global_vars import bot
    data = dict(item)
    if data["auth"] != config.cfToken:
        return PlainTextResponse("403", 403)
    g = bot.apihandlers.fileManager(int(data["guild_id"]), create=False)
    if g is False:
        return PlainTextResponse("404", 404)
    await bot.apihandlers.sendLog(
        emoji=emojis().bots.clicksforms,
        type="Form imported",
        server=int(data["guild_id"]),
        colour=colours.green,
        data={
            "Imported by": f"{bot.get_user(data['created_by']).name} ({bot.get_user(data['created_by']).mention})",
            "Service": "Google Forms",
            "Name": data['name'],
            "Questions": data['questions'],
            "Imported": bot.apihandlers.strf(datetime.datetime.utcnow())
        }
    )
    return PlainTextResponse("200", 200)


@app.post("/clicksforms/edit")
async def edit(item: Item):
    from global_vars import bot
    data = dict(item)
    if data["auth"] != config.cfToken:
        return PlainTextResponse("403", 403)
    g = bot.apihandlers.fileManager(int(data["guild_id"]), create=False)
    if g is False:
        return PlainTextResponse("404", 404)
    await bot.apihandlers.sendLog(
        emoji=emojis().bots.clicksforms,
        type="Form edited",
        server=int(data["guild_id"]),
        colour=colours.yellow,
        data={
            "Edited by": f"{bot.get_user(data['created_by']).name} ({bot.get_user(data['created_by']).mention})",
            "Name": data['name'],
            "Questions": data['questions'],
            "Edited": bot.apihandlers.strf(datetime.datetime.utcnow())
        }
    )
    return PlainTextResponse("200", 200)


@app.post("/clicksforms/delete")
async def delete(item: Item):
    from global_vars import bot
    data = dict(item)
    if data["auth"] != config.cfToken:
        return PlainTextResponse("403", 403)
    g = bot.apihandlers.fileManager(int(data["guild_id"]), create=False)
    if g is False:
        return PlainTextResponse("404", 404)
    await bot.apihandlers.sendLog(
        emoji=emojis().bots.clicksforms,
        type="Form deleted",
        server=int(data["guild_id"]),
        colour=colours.red,
        data={
            "Deleted by": f"{bot.get_user(data['created_by']).name} ({bot.get_user(data['created_by']).mention})",
            "Name": data['name'],
            "Deleted": bot.apihandlers.strf(datetime.datetime.utcnow())
        }
    )
    return PlainTextResponse("200", 200)


@app.post("/clicksforms/apply")
async def apply(item: Item):
    from global_vars import bot
    data = dict(item)
    if data["auth"] != config.cfToken:
        return PlainTextResponse("403", 403)
    g = bot.apihandlers.fileManager(int(data["guild_id"]), create=False)
    if g is False:
        return PlainTextResponse("404", 404)
    await bot.apihandlers.sendLog(
        emoji=emojis().bots.clicksforms,
        type="User applied",
        server=int(data["guild_id"]),
        colour=colours.green,
        data={
            "User": f"{bot.get_user(data['created_by']).name} ({bot.get_user(data['created_by']).mention})",
            "Form": data['name'],
            "Applied": bot.apihandlers.strf(datetime.datetime.utcnow())
        }
    )
    return PlainTextResponse("200", 200)


def setup(bot):
    start(bot)


def start(bot):
    bot.apihandlers = Handlers(bot)
    config = uvicorn.Config(app, host="0.0.0.0", port=10000, lifespan="on", access_log=False, log_level="critical")
    server = uvicorn.Server(config)
    server.config.setup_event_loop()
    if not hasattr(bot, "loop"):
        return
    loop = bot.loop
    loop.create_task(server.serve())
    return
