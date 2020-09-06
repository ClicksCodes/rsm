import copy, discord, json, humanize, aiohttp, traceback, typing, time, cv2, pytesseract, os, random, re, time, shutil, requests

from datetime import datetime
from discord.ext import commands

with open("./data/emojis.json") as rfile: emojis = json.load(rfile)
with open("./data/template.json") as rfile: template = json.load(rfile)

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
    "Members":  emojis['join']
}

events = {
    "message_delete":       [colours["delete"], '`Deleted messages `', emojis['delete'],         'Messages'],
    "message_edit":         [colours[ "edit" ], '`Edited messages  `', emojis['edit'],           'Messages'],
    "bulk_message_delete":  [colours["delete"], '`Purged messages  `', emojis['purge'],          'Messages'],
    "channel_pins_update":  [colours[ "edit" ], '`Pinned messages  `', emojis['pinned'],         'Messages'],
    "reaction_clear":       [colours[ "edit" ], '`Cleared reactions`', emojis['reaction_clear'], 'Messages'], 
    "everyone_here":        [colours[ "edit" ], '`@Everyone & @Here`', emojis['everyone_ping'],  'Messages'],
    "mass_mention":         [colours[ "edit" ], '`Mass mentioning  `', emojis['mass_ping'],      'Messages'],
    "roles":                [colours[ "edit" ], '`Role mentions    `', emojis['role_ping'],      'Messages'],
    "channel_create":       [colours["create"], '`Created channel  `', emojis['channel_create'], 'Channels'],
    "channel_delete":       [colours["delete"], '`Deleted channel  `', emojis['channel_delete'], 'Channels'],
    "nsfw_update":          [colours[ "edit" ], '`Channel NSFW     `', emojis['nsfw_on'],        'Channels'],
    "channel_title_update": [colours[ "edit" ], '`Name changed     `', emojis['TitleUpdate'],    'Channels'],
    "channel_desc_update":  [colours[ "edit" ], '`Topic changed    `', emojis['TopicUpdate'],    'Channels'],
    "webhook_create":       [colours[ "edit" ], '`Webhook updated  `', emojis['webhook_create'], 'Channels'],
    "member_join":          [colours["create"], '`Member joins     `', emojis['join'],           'Members'],
    "member_leave":         [colours["delete"], '`Member leaves    `', emojis['leave'],          'Members'],
    "member_kick":          [colours["delete"], '`Member kicked    `', emojis['kick'],           'Members'],
    "member_ban":           [colours["delete"], '`Member banned    `', emojis['ban'],            'Members'],
    "member_unban":         [colours["create"], '`Member unbanned  `', emojis['unban'],          'Members'],
    "nickname_change":      [colours[ "edit" ], '`Nickname changed `', emojis['nickname_change'],'Members'],
    "guild_role_create":    [colours["create"], '`Role created     `', emojis['role_create'],    'Server'],
    "guild_role_delete":    [colours["delete"], '`Role deleted     `', emojis['role_delete'],    'Server'],
    "guild_emojis_update":  [colours[ "edit" ], '`Emojis updated   `', emojis['emoji'],          'Server'],
    "invite_create":        [colours["create"], '`Created invite   `', emojis['invite_create'],  'Server'],
    "invite_delete":        [colours["delete"], '`Deleted invite   `', emojis['invite_delete'],  'Server'],
    "icon_update":          [colours[ "edit" ], '`Icon changed     `', emojis['icon_update'],    'Server'],
    "mod_changed":          [colours[ "edit" ], '`Mod level changed`', emojis['mod_update'],     'Server'],
    "name_changed":         [colours[ "edit" ], '`Name changed     `', emojis['name_change'],    'Server']
}

