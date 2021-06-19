import discord
import uvicorn
from cogs.consts import *
from cogs.handlers import Handlers
from config import config
from discord.ext import commands

from fastapi import FastAPI, APIRouter
from fastapi.responses import PlainTextResponse
from uvicorn import Config, Server


app = FastAPI()
colours = Cols()
emojis = Emojis


@app.get("/")
def root():
    from global_vars import bot
    return PlainTextResponse(str(bot.latency))


@app.get("/stage")
async def root():
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


def setup(bot):
    start(bot)


def start(bot):
    config = uvicorn.Config(app, host="0.0.0.0", port=10000, lifespan="on", access_log=False, log_level="critical")
    server = uvicorn.Server(config)
    server.config.setup_event_loop()
    if not hasattr(bot, "loop"):
        return
    loop = bot.loop
    loop.create_task(server.serve())
    return
