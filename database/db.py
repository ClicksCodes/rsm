from gino import Gino


db = Gino()

async def main(bot):
    from .models.guild import Guild
    await bot.wait_until_ready()
    print(f"Binding")
    try:
        await db.set_bind('postgres://pineapplefan:ehhhehehheheh@clicksminuteper.net:5432/tutorial')
    except: pass
    print(f"Set bind")
    await db.gino.create_all()
    print(f"Created models")
    for guild in bot.guilds:
        if not await Guild.get(guild.id):
            print(f"Creating guild entry {guild}")
            await Guild.create(guild.id)
        else:
            print(f"Guild entry {guild} exists")