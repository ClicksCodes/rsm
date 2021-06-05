import enum
import json

import discord

with open("./data/emojis.json") as rfile:
    emojis = json.load(rfile)


class C(enum.Enum):
    c = '\033[0m'

    RedDark = '\033[31m'
    GreenDark = '\033[32m'
    YellowDark = '\033[33m'
    BlueDark = '\033[34m'
    PinkDark = '\033[35m'
    CyanDark = '\033[36m'

    Red = '\033[91m'
    Green = '\033[92m'
    Yellow = '\033[93m'
    Blue = '\033[94m'
    Pink = '\033[95m'
    Cyan = '\033[96m'


colours = {
    "delete": 0xF27878,
    "create": 0x68D49E,
    "edit":   0xF2D478,
    "update": 0xF2D478
}

categories = {
    "Messages": emojis['edit'],
    "Channels": emojis['channel_create'],
    "Server":   emojis['settings'],
    "Members":  emojis['join'],
    "Voice":    emojis['Connect']
}

events = {
    "message_delete":       [colours["delete"], '`Deleted messages `', emojis['delete'],         'Messages'],
    "message_edit":         [colours["edit"], '`Edited messages  `', emojis['edit'],           'Messages'],
    "bulk_message_delete":  [colours["delete"], '`Purged messages  `', emojis['purge'],          'Messages'],
    "channel_pins_update":  [colours["edit"], '`Pinned messages  `', emojis['pinned'],         'Messages'],
    "reaction_clear":       [colours["delete"], '`Cleared reactions`', emojis['reaction_clear'], 'Messages'],
    "everyone_here":        [colours["edit"], '`@Everyone & @Here`', emojis['everyone_ping'],  'Messages'],
    "mass_mention":         [colours["edit"], '`Mass mentioning  `', emojis['mass_ping'],      'Messages'],
    "roles":                [colours["edit"], '`Role mentions    `', emojis['role_ping'],      'Messages'],
    "channel_create":       [colours["create"], '`Created channel  `', emojis['channel_create'], 'Channels'],
    "channel_delete":       [colours["delete"], '`Deleted channel  `', emojis['channel_delete'], 'Channels'],
    "nsfw_update":          [colours["edit"], '`Channel NSFW     `', emojis['nsfw_on'],        'Channels'],
    "channel_title_update": [colours["edit"], '`Name changed     `', emojis['TitleUpdate'],    'Channels'],
    "channel_desc_update":  [colours["edit"], '`Topic changed    `', emojis['TopicUpdate'],    'Channels'],
    "webhook_create":       [colours["edit"], '`Webhook updated  `', emojis['webhook_create'], 'Channels'],
    "member_join":          [colours["create"], '`Member joins     `', emojis['join'],           'Members'],
    "member_leave":         [colours["delete"], '`Member leaves    `', emojis['leave'],          'Members'],
    "member_kick":          [colours["delete"], '`Member kicked    `', emojis['kick'],           'Members'],
    "member_ban":           [colours["delete"], '`Member banned    `', emojis['ban'],            'Members'],
    "member_unban":         [colours["create"], '`Member unbanned  `', emojis['unban'],          'Members'],
    "nickname_change":      [colours["edit"], '`Nickname changed `', emojis['nickname_change'], 'Members'],
    "guild_role_create":    [colours["create"], '`Role created     `', emojis['role_create'],    'Server'],
    "guild_role_delete":    [colours["delete"], '`Role deleted     `', emojis['role_delete'],    'Server'],
    "guild_emojis_update":  [colours["edit"], '`Emojis updated   `', emojis['emoji'],          'Server'],
    "invite_create":        [colours["create"], '`Created invite   `', emojis['invite_create'],  'Server'],
    "invite_delete":        [colours["delete"], '`Deleted invite   `', emojis['invite_delete'],  'Server'],
    "icon_update":          [colours["edit"], '`Icon changed     `', emojis['icon_update'],    'Server'],
    "mod_changed":          [colours["edit"], '`Mod level changed`', emojis['mod_changed'],    'Server'],
    "name_changed":         [colours["edit"], '`Name changed     `', emojis['name_changed'],   'Server'],
    "connect":              [colours["create"], '`Voice join       `', emojis['Connect'],        'Voice'],
    "disconnect":           [colours["delete"], '`Voice leave      `', emojis['Leave'],          'Voice'],
    "mute":                 [colours["delete"], '`User mute        `', emojis['Mute'],           'Voice'],
    "deafen":               [colours["delete"], '`User deafen      `', emojis['Deafen'],         'Voice'],
    "unmute":               [colours["create"], '`User unmute      `', emojis['Unmute'],         'Voice'],
    "undeafen":             [colours["create"], '`User undeafen    `', emojis['Undeafen'],       'Voice'],
    "server_mute":          [colours["delete"], '`Server mute      `', emojis['Mute'],           'Voice'],
    "server_deafen":        [colours["delete"], '`Server deafen    `', emojis['Deafen'],         'Voice'],
    "server_unmute":        [colours["create"], '`Server unmute    `', emojis['Unmute'],         'Voice'],
    "server_undeafen":      [colours["create"], '`Server undeafen  `', emojis['Undeafen'],       'Voice'],
    "move":                 [colours["edit"], '`Moved voice chat `', emojis['Change'],         'Voice']
}

loadingEmbed = discord.Embed(
    title=f"{emojis['loading']} Loading"
)
