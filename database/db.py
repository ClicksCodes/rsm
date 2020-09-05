from gino import Gino


db = Gino()

async def main(bot):
    from .models.guild import Guild
    await bot.wait_until_ready()
    print(f"Binding")
    await db.set_bind('postgres://pineapplefan:PG_Gruffalo16_N0010@clicksminuteper.net:5432/tutorial')
    print(f"Set bind")
    await db.gino.create_all()
    print(f"Created models")
    for guild in bot.guilds:
        if not await Guild.get(guild.id):
            print(f"Creating guild entry {guild}")
            await Guild.create(guild.id)
        else:
            print(f"Guild entry {guild} exists")