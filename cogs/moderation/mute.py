import asyncio
import typing
import discord
import datetime
import humanize
from discord.ext import commands

from cogs.consts import *
from cogs.handlers import Handlers, Failed, CustomCTX
from cogs import interactions


import databases
import orm
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database = databases.Database("sqlite:///data/mutes.db")
metadata = sqlalchemy.MetaData()

sqlalchemy.Table(
    "mutes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("unmuteAt", sqlalchemy.Integer),
    sqlalchemy.Column("guild", sqlalchemy.Integer),
    sqlalchemy.Column("user", sqlalchemy.Integer),
    sqlalchemy.Column("mod", sqlalchemy.Integer),
    sqlalchemy.Column("reason", sqlalchemy.String),
    sqlalchemy.Column("type", sqlalchemy.String),
)


class Mutes(orm.Model):
    __tablename__ = "mutes"
    registry = orm.ModelRegistry(database=database)
    fields = {
        "id": orm.Integer(primary_key=True, allow_null=True, default=None),
        "unmuteAt": orm.Integer(),
        "guild": orm.Integer(),
        "user": orm.Integer(),
        "reason": orm.String(max_length=2000),
        "mod": orm.Integer(),
        "type": orm.String(max_length=20),
    }


class MuteEvent:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


engine = sqlalchemy.create_engine(str(database.url))
metadata.create_all(engine)


class Database:
    def __init__(self, engine, batchsize=60):
        self.db = Mutes
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.batchsize = batchsize

    async def getNext(self):
        upTo = datetime.datetime.utcnow().timestamp() + self.batchsize
        try:
            return list(filter(lambda entry: 0 < entry.unmuteAt <= upTo, await Mutes.objects.all()))
        except orm.NoMatch:
            return []

    async def removeAll(self, uid, gid):
        c = 0
        for entry in list(filter(lambda entry: str(entry.user) == str(uid) and str(entry.guild) == str(gid), await Mutes.objects.all())):
            c += 1
            await entry.delete()
        return c

    async def create(self, **kwargs):
        return await self.db.objects.create(**kwargs)


class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = Emojis
        self.colours = Cols()
        self.handlers = Handlers(self.bot)
        self.interactions = interactions
        self.batchsize = 60
        self.db = Database(engine=engine, batchsize=self.batchsize)
        self.batch = 0

        loop = bot.loop
        self.task = loop.create_task(self._periodic())

    async def _periodic(self):
        while True:
            self.batch = int(datetime.datetime.utcnow().timestamp()) + self.batchsize
            asyncio.create_task(self._fetch())
            await asyncio.sleep(self.batchsize)

    async def _fetch(self):
        nextUnmutes = await self.db.getNext()
        for unmute in nextUnmutes:
            asyncio.create_task(self._unmute(unmute))

    async def _unmute(self, unmute):
        time = unmute.unmuteAt - int(datetime.datetime.utcnow().timestamp())
        await asyncio.sleep(time if time > 0 else 0)
        entry = self.handlers.fileManager(unmute.guild)
        guild = self.bot.get_guild(int(unmute.guild))
        if guild is None:
            guild = await self.bot.fetch_guild(int(unmute.guild))
        if entry["mute"]["role"] is None:
            try:
                await(await Mutes.objects.get(pk=unmute.id)).delete()
            finally:
                return
        rid = guild.get_role(int(entry["mute"]["role"]))
        if rid is None:
            rid = await guild.fetch_role(int(entry["mute"]["role"]))
        member = guild.get_member(int(unmute.user))
        if member is None:
            member = await guild.fetch_member(int(unmute.user))
        await member.remove_roles(rid)
        try:
            await self.db.removeAll(uid=unmute.user, gid=unmute.guild)
        except orm.NoMatch:
            pass

    @commands.command()
    @commands.guild_only()
    async def mute(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="Mute",
            description="We're trying out slash commands - Please use `/mute` instead",
            colour=self.colours.red
        ))

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if "type" not in interaction.data:
            return
        if interaction.data["type"] == 1 and interaction.guild:
            if interaction.data["name"] == "mute":
                await self.mute(interaction)
            elif interaction.data["name"] == "unmute":
                await self.unmute(interaction)

    async def unmute(self, interaction):
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        m = await interaction.original_message()

        data = {}
        for prop in interaction.data["options"]:
            data[prop["name"]] = prop["value"]

        if isinstance(await self.handlers.checkPerms(
            CustomCTX(interaction.guild.get_member(self.bot.user.id), interaction.user, interaction.guild, interaction.channel), m, "manage_messages", "punish.mute", "mute members", me=False),
        Failed):
            return

        entry = self.handlers.fileManager(interaction.guild.id)
        if entry["mute"]["role"] is None:
            await m.edit(embed=discord.Embed(
                title="Mute",
                description="No mute role set",
                colour=self.colours.red
            ))
            return
        if entry["mute"]["role"] not in [r.id for r in interaction.guild.get_member(int(data["user"])).roles]:
            await interaction.response.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.mute} Unmute",
                description="Member was not muted",
                colour=self.colours.green
            ))
            return
        await interaction.guild.get_member(int(data["user"])).remove_roles(interaction.guild.get_role(int(entry["mute"]["role"])))
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().punish.mute} Unmute",
            description="Member unmuted",
            colour=self.colours.green
        ))
        user = interaction.guild.get_member(int(data["user"]))
        await self.handlers.sendLog(self.emojis().punish.mute, "Member unmuted", interaction.guild, self.colours.green, {
                "Name": f"{user.name} ({user.mention})",
                "Joined": self.handlers.betterDelta(user.joined_at.replace(tzinfo=None)),
                "Unmuted": self.handlers.strf(datetime.datetime.utcnow()),
                "Unmuted by": f"{interaction.user.name} ({interaction.user.mention})",
                "Time in server": humanize.naturaldelta(datetime.datetime.utcnow()-member.joined_at.replace(tzinfo=None)),
                "Account created": self.handlers.betterDelta(member.created_at.replace(tzinfo=None)),
                "ID": f"`{member.id}`",
        })
        try:
            await self.db.removeAll(uid=interaction.data["user"], gid=interaction.guild.id)
        except orm.NoMatch:
            pass

    async def mute(self, interaction):
        await interaction.response.send_message(embed=loading_embed, ephemeral=True)
        m = await interaction.original_message()

        if isinstance(await self.handlers.checkPerms(
            CustomCTX(interaction.guild.get_member(self.bot.user.id), interaction.user, interaction.guild, interaction.channel), m, "manage_messages", "Mute", "mute members", me=False),
        Failed):
            return

        if interaction.data["options"][0]["name"] == "role":
            if "options" not in interaction.data["options"][0]:
                entry = self.handlers.fileManager(interaction.guild.id)
                if entry["mute"]["role"] is None:
                    r = await self.newMuteRole(interaction, m)
                    if not r:
                        entry["mute"]["role"] = None
                        self.handlers.fileManager(interaction.guild.id, action="w", data=entry)
                        return await m.edit(embed=discord.Embed(
                            title=f"{self.emojis().punish.mute} Mute",
                            description="No mute role set",
                            colour=self.colours.red
                        ), view=None)
                    role = interaction.guild.get_role(int(r))
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().punish.mute} Mute",
                        description=f"Mute role has been to {role.mention}",
                        colour=self.colours.green
                    ), view=None)
                    return
                else:
                    return await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().punish.mute} Mute",
                        description=f"Mute role is {interaction.guild.get_role(int(entry['mute']['role'])).mention}",
                        colour=self.colours.green
                    ))
            elif interaction.data["options"][0]["options"][0]["value"]:
                entry = self.handlers.fileManager(interaction.guild.id)
                role = interaction.guild.get_role(int(interaction.data["options"][0]["options"][0]["value"]))
                if role.position >= interaction.guild.me.top_role.position:
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().punish.mute} Mute",
                        description="Mute role is above my highest role",
                        colour=self.colours.red
                    ))
                    return
                elif role.position >= interaction.user.top_role.position:
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().punish.mute} Mute",
                        description="Mute role must be below your highest",
                        colour=self.colours.red
                    ))
                    return
                else:
                    entry = self.handlers.fileManager(interaction.guild.id)
                    entry["mute"]["role"] = role.id
                    self.handlers.fileManager(interaction.guild.id, action="w", data=entry)
                    await m.edit(embed=discord.Embed(
                        title=f"{self.emojis().punish.mute} Mute",
                        description=f"Mute role has been changed to {role.mention}",
                        colour=self.colours.green
                    ))
                    return
            else:
                return

        entry = self.handlers.fileManager(interaction.guild.id)
        if not entry["mute"]["role"] or not interaction.guild.get_role(int(entry["mute"]["role"])):
            if not await self.newMuteRole(interaction, m):
                return

        data = {}
        for prop in interaction.data["options"][0]["options"]:
            data[prop["name"]] = prop["value"]

        if interaction.data["options"][0]["name"] == "permanently":
            timestamp = None
        else:
            time = 0
            units = [("days", 86400), ("hours", 3600), ("minutes", 60), ("seconds", 1)]
            for unit, value in units:
                if unit in data:
                    time += int(data[unit]) * value
            timestamp = int(datetime.datetime.utcnow().timestamp()) + time

        e = await self.db.create(
            guild=interaction.guild.id,
            user=data["user"],
            unmuteAt=round(timestamp) if timestamp else 0,
            reason=data["reason"] if "reason" in data else "No reason provided",
            mod=interaction.user.id,
            type="text"
        )

        if timestamp and timestamp < self.batch:
            asyncio.create_task(self._unmute(e))

        if timestamp:
            e = "T" if (datetime.datetime.fromtimestamp(timestamp).date() == datetime.datetime.utcnow().date()) else "F"
            e = f"<t:{timestamp}:{e}>"

        entry = self.handlers.fileManager(interaction.guild.id)
        await interaction.guild.get_member(int(data["user"])).add_roles(interaction.guild.get_role(int(entry["mute"]["role"])))

        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().punish.mute} Mute",
            description=f"{interaction.guild.get_member(int(data['user'])).mention} has been muted {'permanently' if not timestamp else {e}}",
            colour=self.colours.green
        ), view=None)

        try:
            await interaction.guild.get_member(int(data["user"])).send(embed=discord.Embed(
                title=f"{self.emojis().punish.mute} Mute",
                description=f"You have been muted in {interaction.guild.name} for {data['reason'] if 'reason' in data else 'No reason provided'}",
                colour=self.colours.red
            ))
        except discord.HTTPException:
            pass

        user = interaction.guild.get_member(int(data["user"]))
        await self.handlers.sendLog(self.emojis().punish.mute, "Member muted", interaction.guild, self.colours.yellow, {
                "Name": f"{user.name} ({user.mention})",
                "Joined": self.handlers.betterDelta(user.joined_at.replace(tzinfo=None)),
                "Muted": self.handlers.strf(datetime.datetime.utcnow()),
                "Muted by": f"{interaction.user.name} ({interaction.user.mention})",
                "Muted for": self.handlers.strf(datetime.datetime.fromtimestamp(timestamp)) if timestamp else "Permanently",
                "Reason": f"\n> {data['reason'] if 'reason' in data else 'No reason provided'}",
                "Time in server": humanize.naturaldelta(datetime.datetime.utcnow()-user.joined_at.replace(tzinfo=None)),
                "Account created": self.handlers.betterDelta(user.created_at.replace(tzinfo=None)),
                "ID": f"`{user.id}`",
        })

    async def newMuteRole(self, interaction, m):
        entry = self.handlers.fileManager(interaction.guild.id)
        v = self.interactions.createUI(CustomCTX(interaction.guild.get_member(self.bot.user.id), interaction.user, interaction.guild, interaction.channel), [
            self.interactions.Button(self.bot, emojis=self.emojis, id="ye", title="Yes", emoji="control.tick"),
            self.interactions.Button(self.bot, emojis=self.emojis, id="no", title="No", emoji="control.cross"),
        ])
        await m.edit(embed=discord.Embed(
            title=f"{self.emojis().punish.mute} Mute",
            description=f"You do not have a mute role set up. Would you like to create one?",
            colour=self.colours.yellow
        ), view=v)
        await v.wait()
        if v.selected == "ye":
            v = self.interactions.createUI(CustomCTX(interaction.guild.get_member(self.bot.user.id), interaction.user, interaction.guild, interaction.channel), [
                self.interactions.Select(id="role", placeholder="Let users...", options=[
                    self.interactions.Option(id="sm", title="Send messages", description="Users should be able to send messages"),
                    self.interactions.Option(id="rm", title="React to messages", description="Users should be able to react to messages"),
                    self.interactions.Option(id="vc", title="Talk in voice chats", description="Users should be able to talk in voice chats"),
                ], max_values=3, autoaccept=False),
                self.interactions.Button(self.bot, emojis=self.emojis, id="no", title="Confirm", emoji="control.tick"),
            ])
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.mute} Mute",
                description=f"Select what permissions muted users should have.",
                colour=self.colours.yellow
            ), view=v)
            await v.wait()
            embed = m.embeds[0]
            embed.title = f"{self.emojis().icon.loading} Mute"
            await m.edit(embed=embed, view=None)
            if "role" not in v.dropdowns:
                v.dropdowns["role"] = []
            r = await interaction.guild.create_role(name="Muted", permissions=discord.Permissions(
                send_messages="sm" in v.dropdowns["role"],
                add_reactions="rm" in v.dropdowns["role"],
                speak="vc" in v.dropdowns["role"]
            ), colour=0x000000)
            try:
                await r.edit(position=interaction.guild.me.top_role.position - 1)
            except discord.HTTPException:
                pass
            entry["mute"]["role"] = r.id
            self.handlers.fileManager(interaction.guild.id, action="w", data=entry)

        elif v.selected == "no":
            await m.edit(embed=discord.Embed(
                title=f"{self.emojis().punish.mute} Mute",
                description=f"You must have a mute role set up to use this command.",
                colour=self.colours.red
            ))
            return False
        return r.id

def setup(bot):
    bot.add_cog(Mute(bot))
