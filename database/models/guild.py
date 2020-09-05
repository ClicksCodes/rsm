from ..db import db
import enum

type = {
    1: "user",
    2: "channel",
    3: "role"
}

class Ignored(db.Model):
    __tablename__ = 'ignored'
    
    id = db.Column(db.BigInteger(), primary_key=True)
    snowflake = db.Column(db.BigInteger(), nullable=False)
    type = db.Column(db.Integer())
    # guild = db.Column(db.ForeignKey('guilds.id'))
    guild = db.Column(db.BigInteger())

class Guild(db.Model):
    __tablename__ = 'guilds'

    id = db.Column(db.BigInteger(), primary_key=True)
    nickname = db.Column(db.String(), default='noname')
    message_delete = db.Column(db.Boolean(), default=True)
    message_edit = db.Column(db.Boolean(), default=True)
    bulk_message_delete = db.Column(db.Boolean(), default=True)
    channel_pins_update = db.Column(db.Boolean(), default=True)
    reaction_clear = db.Column(db.Boolean(), default=True)
    everyone_here = db.Column(db.Boolean(), default=True)
    mass_mention = db.Column(db.Boolean(), default=True)
    roles = db.Column(db.Boolean(), default=True)
    channel_create = db.Column(db.Boolean(), default=True)
    channel_delete = db.Column(db.Boolean(), default=True)
    nsfw_update = db.Column(db.Boolean(), default=True)
    channel_title_update = db.Column(db.Boolean(), default=True)
    channel_desc_update = db.Column(db.Boolean(), default=True)
    member_join = db.Column(db.Boolean(), default=True)
    member_leave = db.Column(db.Boolean(), default=True)
    member_kick = db.Column(db.Boolean(), default=True)
    member_ban = db.Column(db.Boolean(), default=True)
    member_unban = db.Column(db.Boolean(), default=True)
    nickname_change = db.Column(db.Boolean(), default=True)
    guild_role_create = db.Column(db.Boolean(), default=True)
    guild_role_delete = db.Column(db.Boolean(), default=True)
    guild_emojis_update = db.Column(db.Boolean(), default=True)
    invite_create = db.Column(db.Boolean(), default=True)
    invite_delete = db.Column(db.Boolean(), default=True)
    icon_update = db.Column(db.Boolean(), default=True)
    mod_changed = db.Column(db.Boolean(), default=True)
    name_change = db.Column(db.Boolean(), default=True)
    ignore_bots = db.Column(db.Boolean(), default=True)
    log_channel = db.Column(db.Integer(), default=None, nullable=True)
    enabled = db.Column(db.Boolean(), default=True)
