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


@app.get("/verify/{guild}/{role}/{user}/{secret}/{code}")
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
        del bot.rsmv[code]
        return PlainTextResponse("200", 200)
    except Exception as e:
        print(e)
        return PlainTextResponse("400", 400)


@app.get("/verify/code")
async def verify(code):
    from global_vars import bot
    if code in bot.rsmv:
        return JSONResponse(bot.rsmv[code], "200")
    return JSONResponse({"error": "404"}, "404")


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
    service: typing.Optional[str]
    service_url: typing.Optional[str]
    verified: typing.Optional[bool]
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


@app.post("/clicksforms/import")
async def service(item: Item):
    try:
        from global_vars import bot
        data = dict(item)
        if data["auth"] != config.cfToken:
            return PlainTextResponse("403", 403)
        g = bot.apihandlers.fileManager(int(data["guild_id"]), create=False)
        if g is False:
            return PlainTextResponse("404", 404)
        await bot.apihandlers.sendLog(
            emoji=f"{emojis()['verified' if data['verified'] else 'unverified']} {emojis().bots.clicksforms}",
            type="Form imported",
            server=int(data["guild_id"]),
            colour=colours.green,
            data={
                "Imported by": f"{bot.get_user(data['created_by']).name} ({bot.get_user(data['created_by']).mention})",
                "Service": f"[{data['service']}]({data['service_url']})",
                "Name": data['name'],
                "Questions": data['questions'],
                "Imported": bot.apihandlers.strf(datetime.datetime.utcnow())
            },
            extra=(
                f"This service has been verified as {data['service']}" if data["verified"] else
                f"This service has not been verified. If this is your service and you would like to be verified, message us at https://discord.gg/bPaNnx"
            )
        )
        return PlainTextResponse("200", 200)
    except Exception as e:
        print(e)


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
