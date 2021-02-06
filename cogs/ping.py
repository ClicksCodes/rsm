from quart import Quart
from discord.ext import commands
import discord
import asyncio
import bot as customBot
from config import config

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shutdown_event = asyncio.Event()

    def _signal_handler(self, *_) -> None:
        shutdown_event.set()

    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.runningPing:
            return
        self.bot.runningPing = True

        app = Quart(__name__)

        @app.route("/")
        async def ping():
            return str(self.bot.latency)

        @app.route("/stage")
        async def stage():
            return str(config.stage.name)

        @app.route("/role/gid/<string:guild>/rid/<string:role>/user/<string:user>/secret/<string:secret>")
        async def role(guild, role, user, secret):
            try:
                if secret != "slwu0rZV5W6WdmGtgI16du8Ar2tQGMr3Q9dE6u3poKiVODNV9SweaA3buawgkTmTuITXDWOUpBcTFA0qWrUvoshi1JB180WOFwA7"
                g = self.bot.get_guild(int(guild))
                mem = await g.fetch_member(int(user))
                await mem.add_roles(g.get_role(int(role)))
                return "200"
            except:
                return "400"

        self.bot.server_teardown = self._signal_handler
        task = await app.run_task(
            "0.0.0.0",
            10000,
            None,
            True,
            None,
            None,
            None,
            shutdown_trigger=self.shutdown_event.wait
        )

def setup(bot):
    bot.add_cog(Ping(bot))

def teardown(bot):
    bot.server_teardown()
