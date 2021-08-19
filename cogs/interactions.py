import discord
from cogs.consts import *


class Button(discord.ui.Button):
    def __init__(self, bot, title=None, style="secondary", disabled=False, url=None, emoji=None, id=None, emojis=None):
        super().__init__(
            label=title or " ",
            style=getattr(discord.ButtonStyle, style),
            disabled=disabled,
            url=url,
            emoji=bot.get_emoji(emojis(idOnly=True)(emoji)) if emoji else None
        )
        self.cb = id

    async def callback(self, _):
        self.view.selected = self.cb
        self.view.stop()


class Select(discord.ui.Select):
    def __init__(self, id, disabled=False, max_values=1, min_values=1, options=[], placeholder="", autoaccept=True):
        super().__init__(
            custom_id=id,
            disabled=disabled,
            max_values=max_values,
            min_values=min_values,
            options=options,
            placeholder=placeholder
        )
        self.autoAccept = autoaccept

    async def callback(self, _):
        self.view.dropdowns[self.custom_id] = self.values
        if self.autoAccept:
            self.view.stop()


class Option(discord.SelectOption):
    def __init__(self, id, title, description):
        super().__init__(
            value=id,
            title=title,
            description=description
        )
        self.cb = id


class View(discord.ui.View):
    def __init__(self, ctx, *args, alwaysAccept=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected = None
        self.dropdowns = {}
        self.ctx = ctx
        self.alwaysAccept = alwaysAccept

    def add_button(self, button):
        self.add_item(button)

    async def interaction_check(self, interaction):
        if interaction.user.id == self.ctx.author.id or self.alwaysAccept:
            return True
        if "type" in interaction.data and interaction.data["type"] == 1:
            await interaction.response.send_message(ephemeral=True, embed=discord.Embed(
                title="This message wasn't made by you",
                description="Only the person who ran the command can respond to it",
                color=Colours.red
            ))
            return False
        return False


def createUI(ctx, items, alwaysAccept=False):
    v = View(ctx=ctx, timeout=300, alwaysAccept=alwaysAccept)
    for item in items:
        v.add_item(item)
    return v


class CustomCTX:
    def __init__(self, bot, author, guild, channel, message=None, interaction=None, m=None):
        self.bot = bot
        self.author = author
        self.guild = guild
        self.message = message
        self.channel = channel
        self.interaction = interaction
        self.m = m
        self.me = guild.me

    async def delete(self):
        if self.message:
            await self.m.delete()
            return await self.message.delete()
        if self.interaction:
            return await self.m.edit(embed=discord.Embed(
                title="Closed",
                description="Dismiss this message to close it",
                color=Colours().red
            ).set_footer(text="Discord does not, in fact, let you delete messages only you can see :/"), view=None)
