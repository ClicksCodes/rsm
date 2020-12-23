import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio

from datetime import datetime
from discord.ext import commands, tasks
from textwrap import shorten

from cogs.consts import *

class Tags(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def createEmbed(self, title, description, color=0x000000):
        return discord.Embed(
            title=title,
            description=description,
            color=color
        )
    
    @commands.command(aliases=["tags"])
    @commands.guild_only()
    async def tag(self, ctx, *, s: str = None): 
        with open(f"data/guilds/{ctx.guild.id}.json", 'r') as entry:
            entry = json.load(entry)
            try: entry["tags"]
            except KeyError: entry["tags"] = {}
        with open(f"data/guilds/{ctx.guild.id}.json", 'w') as f:
            json.dump(entry, f, indent=2)
        if not s:
            with open(f"data/guilds/{ctx.guild.id}.json", 'r') as entry:
                entry = json.load(entry)
                return await ctx.send(embed=self.createEmbed(
                    f"{emojis['store_create']} Here are your server's tags:",
                    ", ".join([t for t in entry["tags"]]) if len(entry["tags"]) else "*Your server has no tags.*",
                    color=colours["create"]
                ))
        s = s.split(" ")
        if s[0] in ["create", "add", "new"]:
            m = await ctx.send(embed=loadingEmbed)
            try:
                if not ctx.author.guild_permissions.manage_messages: return await m.edit(embed=self.createEmbed(f"{emojis['store_delete']} Looks like you don't have permissions", "You need the `manage_messages` permission to edit tags.", colours["delete"]))
                else: print("fine")
            except: return
            with open(f"data/guilds/{ctx.guild.id}.json", 'r') as e:
                entry = json.load(e)
            try: title = s[1]
            except:
                await m.edit(embed=self.createEmbed(
                    f"{emojis['store_create']} Please enter a tag mention:",
                    f"This is what you type, for example `{ctx.prefix}tag welcome`.",
                    color=colours["create"]
                ))
                try: mess = await ctx.bot.wait_for('message', timeout=120, check=lambda message : message.author == ctx.author and message.channel.id == ctx.channel.id)
                except: return await m.edit(embed=self.createEmbed(
                        f"{emojis['store_create']} Please enter a tag mention:",
                        f"This is what you type, for example: 'welcome' for `{ctx.prefix}tag welcome`.",
                        color=colours["delete"]
                    ))
                title = mess.content.split(" ")[0]
            if title in entry["tags"]:
                await m.edit(embed=self.createEmbed(
                    f"{emojis['store_create']} That tag already exists.",
                    f"You can either <:Tick:729064531107774534> overwrite it, or <:Cross:729064530310594601> cancel.",
                    color=colours["create"]
                ))
                for emoji in [729064531107774534, 729064530310594601]: await m.add_reaction(ctx.bot.get_emoji(emoji))

                reaction = None
                try: reaction = await ctx.bot.wait_for('reaction_add', timeout=120, check=lambda emoji, user : emoji.message.id == m.id and user == ctx.author)
                except asyncio.TimeoutError: await m.edit(embed=self.createEmbed(
                    f"{emojis['store_create']} That tag already exists.",
                    f"You can either <:Tick:729064531107774534> overwrite it, or <:Cross:729064530310594601> cancel.",
                    color=colours["delete"]
                ))

                try: await m.clear_reactions()
                except: pass

                if reaction[0].emoji.name != "Tick": return await m.edit(embed=self.createEmbed("<:NicknameChange:729064531019694090> Tags", "No changes were made.", color=colours["delete"]))
            try: 
                text = " ".join(s[2:])
                if not len(text): raise Exception
            except:
                await m.edit(embed=self.createEmbed(
                    f"{emojis['store_create']} Please enter a tag content:",
                    f"This is the text that appears when you do `{ctx.prefix}tag {title}`.",
                    color=colours["create"]
                ))
                try: mess = await ctx.bot.wait_for('message', timeout=120, check=lambda message : message.author == ctx.author and message.channel.id == ctx.channel.id)
                except: return await m.edit(embed=self.createEmbed(
                        f"{emojis['store_create']} Please enter a tag content:",
                        f"This is the text that appears when you do `{ctx.prefix}tag {title}`.",
                        color=colours["create"]
                    ))
                text = mess.content
            await m.edit(embed=self.createEmbed(
                f"{emojis['store_create']} Creating tag",
                f"Please wait.",
                color=colours["delete"]
            ))

            entry["tags"][title] = " ".join([text])
            with open(f"data/guilds/{ctx.guild.id}.json", 'w') as f:
                json.dump(entry, f, indent=2)
            return await m.edit(embed=self.createEmbed(
                f"{emojis['store_create']} Tag created",
                f"Tag {title} created.",
                color=colours["create"]
            ))
        elif s[0] in ["delete", "remove", "del"]:
            m = await ctx.send(embed=loadingEmbed)
            try:
                if not ctx.author.guild_permissions.manage_messages: 
                    return await m.edit(embed=self.createEmbed(f"{emojis['store_delete']} Looks like you don't have permissions", "You need the `manage_messages` permission to edit tags.", colours["delete"]))
            except: return
            try: title = s[1]
            except: 
                await m.edit(embed=self.createEmbed(
                    f"{emojis['store_create']} Please enter a tag to delete",
                    f"Enter the name of the tag you want to delete.",
                    color=colours["create"]
                ))
                try: mess = await ctx.bot.wait_for('message', timeout=120, check=lambda message : message.author == ctx.author and message.channel.id == ctx.channel.id)
                except: return await m.edit(embed=self.createEmbed(
                    f"{emojis['store_create']} Please enter a tag to delete",
                    f"Enter the name of the tag you want to delete.",
                    color=colours["create"]
                ))
                title = mess.content.split(" ")[0]
            with open(f"data/guilds/{ctx.guild.id}.json", 'r') as e:
                entry = json.load(e)
            if title in entry["tags"]:
                del entry["tags"][title]
                with open(f"data/guilds/{ctx.guild.id}.json", 'w') as f:
                    json.dump(entry, f, indent=2)
                return await m.edit(embed=self.createEmbed(
                    f"{emojis['store_create']} Tag deleted",
                    f"Tag with name {title} deleted.",
                    color=colours["create"]
                ))
            else:
                return await m.edit(embed=self.createEmbed(
                    f"{emojis['store_create']} Tag not found",
                    f"No tag with name `{title}` found.",
                    color=colours["create"]
                ))
        else:
            with open(f"data/guilds/{ctx.guild.id}.json", 'r') as e: entry = json.load(e)
            if s[0] in entry["tags"]: return await ctx.send(embed=discord.Embed(description=entry["tags"][s[0]], color=colours['create']))
            else: return await ctx.send(embed=self.createEmbed(
                "<:StoreDelete:729064530768035922> Tag not found",
                f"No tag with the name {s[0]}.",
                color=colours["delete"]
            ))

def setup(bot):
    bot.add_cog(Tags(bot))
