from quart import Quart
from discord.ext import commands
import discord
import asyncio
import bot as customBot

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
