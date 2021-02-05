import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, os

from datetime import datetime
from discord.ext import commands
from textwrap import shorten

from cogs.consts import *

class InfoCommands(commands.Cog):
    def __init__(self, bot):
        self.loadingEmbed = loadingEmbed
        self.bot = bot

    def createEmbed(self, title, description, color=0x000000):
        return discord.Embed(
            title=title,
            description=description,
            color=color
        )

    @commands.command()
    async def ping(self, ctx):
        m = await ctx.send(embed=self.loadingEmbed)
        time = m.created_at - ctx.message.created_at
        await m.edit(content=None, embed=self.createEmbed(f"<:SlowmodeOn:777138171301068831> Ping", f"Latency is: `{int(time.microseconds / 1000)}ms`", colours['create']))

    @commands.command(aliases=["help"])
    async def info(self, ctx: commands.Context, mob:typing.Optional[str]):
        prefix = ctx.prefix

        n = '\n'
        noLog = ""
        try: noLog = f":warning: Your server has not got a log channel. Use `{prefix}setup` to make a log file and `{prefix}setlog #channel` to set it.\n\n" if not os.path.exists(f"data/guilds/{ctx.guild.id}.json") else ""
        except: pass
        headers = {
            "Commands": [emojis['commands'], "Basic commands for your server"],
            "Moderation": [emojis['PunWarn'], "Commands to moderate your server"],
            "Raid": [emojis['lock'], "Emergency commands to use during a raid"]
        }
        descriptions = {
            "Commands": [
                f"{noLog}",
                f"{emojis['rsm']           } `{prefix}info     [*T] {'' if mob else '|'} ` {n if mob else ''}Shows all commands and info. Give [T] for mobile.",
                f"{emojis['graphs']        } `{prefix}stats         {'' if mob else '|'} ` {n if mob else ''}Shows the bot statistics",
                f"{emojis['settings']      } `{prefix}settings      {'' if mob else '|'} ` {n if mob else ''}Shows your servers log settings.",
                f"{emojis['join']          } `{prefix}user     [*@] {'' if mob else '|'} ` {n if mob else ''}Shows information about a user.",
                f"{emojis['role_edit']     } `{prefix}roleall  [*T] {'' if mob else '|'} ` {n if mob else ''}Role all humans or bots in the server. [T] to search",
                f"{emojis['support']       } `{prefix}contact   [T] {'' if mob else '|'} ` {n if mob else ''}Sends [T] to the staff for support.",
                f"{emojis['commands']      } `{prefix}suggest   [T] {'' if mob else '|'} ` {n if mob else ''}Sends [T] to the staff to add to the bot for voting.",
                f"{emojis['support']       } `{prefix}report    [T] {'' if mob else '|'} ` {n if mob else ''}Messages the staff team of the server it was ran in.",
                f"{emojis['slowmodeOn']    } `{prefix}ping          {'' if mob else '|'} ` {n if mob else ''}Checks the bots ping time.",
                f"{emojis['mod_update']    } `{prefix}server        {'' if mob else '|'} ` {n if mob else ''}Shows all information about your server.",
                f"{emojis['store_create']  } `{prefix}tag      [*T] {'' if mob else '|'} ` {n if mob else ''}`{prefix}tag create/delete` `title text`, or `{prefix}tag title`",
                f"{emojis['role_create']   } `{prefix}role      [R] {'' if mob else '|'} ` {n if mob else ''}With `Role`: Shows information about a role.",
                f"{emojis['role_create']   } `{prefix}role      [@] {'' if mob else '|'} ` {n if mob else ''}With `Mention`: Lets you edit or view a users roles.",
                f"{emojis['channel_create']} `{prefix}viewas    [@] {'' if mob else '|'} ` {n if mob else ''}Shows the channels that [@] can see.",
                f"{emojis['join']          } `{prefix}verify    [@] {'' if mob else '|'} ` {n if mob else ''}Lets users verify in your server.",
                f"{emojis['join']          } `{prefix}setverify [R] {'' if mob else '|'} ` {n if mob else ''}Sets the role given when you `{prefix}verify`. Name or ID."
            ],
            "Moderation": [
                f"{emojis['PunMute']   } `{prefix}prefix            {'' if mob else '|'} ` {n if mob else ''}Shows the bots prefix. Use @ if unknown.",
                f"{emojis['PunMute']   } `{prefix}setprefix     [T] {'' if mob else '|'} ` {n if mob else ''}Sets the bots prefix. You can always @ the bot.",
                f"{emojis['PunWarn']   } `{prefix}warn    [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Warns [@] for reason [T].",
                f"{emojis['PunHistory']} `{prefix}clear   [*@] [*N] {'' if mob else '|'} ` {n if mob else ''}Clears [N] messages from [@].",
                f"{emojis['PunKick']   } `{prefix}kick    [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Kicks [@] for reason [T].",
                f"{emojis['PunSoftBan']} `{prefix}softban [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Soft bans [@] for reason [T].",
                f"{emojis['PunBan']    } `{prefix}ban     [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Bans [@] for reason [T].",
                f"{emojis['purge']     } `{prefix}purge        [*N] {'' if mob else '|'} ` {n if mob else ''}Deletes [N] messages in the channel.",
                f"{emojis['PunWarn']   } `{prefix}punish       [*@] {'' if mob else '|'} ` {n if mob else ''}Punishes a user.",
                f"{emojis['role_edit'] } `{prefix}setlog       [ C] {'' if mob else '|'} ` {n if mob else ''}Sets the servers log channel to [C].",
                f"{emojis['ignore']    } `{prefix}ignore     [*CR@] {'' if mob else '|'} ` {n if mob else ''}Stops logging users, roles and channels privided.",
                f"{emojis['ignore']    } `{prefix}ignored           {'' if mob else '|'} ` {n if mob else ''}Shows the ignored users, roles and channels.",
                f"{emojis['rgeneral']  } `{prefix}stafflog     [*C] {'' if mob else '|'} ` {n if mob else ''}Sets the staff log channel for reports and messages."
            ],
            "Raid": [
                f"{emojis['slowmodeOn']} `{prefix}slowmode [*N]{'' if mob else '|'} ` {n if mob else ''}Sets the channel slowmode to [N]. Toggles if [N] is not provided.",
                f"{emojis['lock']      } `{prefix}lock     [*T]{'' if mob else '|'} ` {n if mob else ''}Locks the channel. All roles are denied `send_messages` unless they have `manage_messages`. `{prefix}lock off` unlocks the channel.",
                f"{emojis['lock']      } `{prefix}unlock       {'' if mob else '|'} ` {n if mob else ''}Unlocks the channel. All roles are given `send_messages` if they did before.",
                f"{emojis['raidlock']  } `{prefix}raid     [*T]{'' if mob else '|'} ` {n if mob else ''}Locks down the entire server. All roles are denied `send_messages` if they do not have `manage_messages`. You can type `{prefix}raid off` to end a raid, and type `{prefix}raid` during a raid to view options like ban members."
            ]
        }
        nn = "\n\n"

        paginated = []
        indeces = {0: "Commands", 1: "Moderation", 2: "Raid"}
        for key in descriptions.keys():
            indeces[key] = len(paginated)
            itt, thisitt = "", ""
            thispaginated = []
            for x in range(len(descriptions[key])):
                thisitt += descriptions[key][x] + "\n"
                if len(thisitt) > 1750:
                    thispaginated.append(thisitt)
                    thisitt = "\n"
                    continue
            thispaginated.append(thisitt)
            for page in thispaginated: paginated.append(f"{headers[key][0]} **{key}** - {headers[key][1]}\n{(noLog + nn + nn) if noLog else ''}{page}\n")

        m = await ctx.send(embed=self.loadingEmbed)

        page = 0

        for _ in range(0,25):
            emb = discord.Embed (
                title=emojis["rsm"] + " RSM",
                description=paginated[page] + "[Detailed](http://bit.do/fLQkz) | [Invite](http://bit.do/fLQkB) | [Support](https://discord.gg/bPaNnxe)",
                color=colours["create"]
            )
            emb.set_footer(text="[@] = Mention | [T] = Text | [N] = Number | [R] = Role | [C] = Channel | [* ] = Optional")
            await m.edit(embed=emb)

            for emoji in [729762938411548694, 729762938843430952, 729064530310594601, 751762088229339136, 729764054897524768, 776848800995868682]: await m.add_reaction(ctx.bot.get_emoji(emoji))

            reaction = None
            done, pending = await asyncio.wait([
                    self.bot.wait_for('reaction_add',    timeout=120, check=lambda emoji, user : emoji.message.id == m.id and user == ctx.author),
                    self.bot.wait_for('reaction_remove', timeout=120, check=lambda emoji, user : emoji.message.id == m.id and user == ctx.author)
                ], return_when=asyncio.FIRST_COMPLETED)

            try: reaction, _ = done.pop().result()
            except: break

            for future in done: future.exception()
            for future in pending: future.cancel()

            try: await m.remove_reaction(reaction.emoji, ctx.author)
            except: pass

            if reaction == None: break
            elif reaction.emoji.name == "Left":  page -= 1
            elif reaction.emoji.name == "Right": page += 1
            elif reaction.emoji.name == "Commands": page = indeces["Commands"]
            elif reaction.emoji.name == "PunishWarn": page = indeces["Moderation"]
            elif reaction.emoji.name == "Lock": page = indeces["Raid"]
            else: break

            page = min(len(paginated)-1, max(0, page))

        emb = discord.Embed (
            title=emojis["rsm"] + " RSM",
            description=paginated[page] + "[Detailed](https://docs.google.com/spreadsheets/d/1AiuGLtrnwy-Xe6ZMAAj4BfEl9o6MC5H-1uH-8jWh6Us/edit?usp=sharing) | [Invite](https://discord.com/api/oauth2/authorize?client_id=715989276382462053&permissions=499510486&scope=bot) | [Support](https://discord.gg/bPaNnxe)",
            color=colours["delete"]
        )
        emb.set_footer(text="[@] = Mention | [T] = Text | [N] = Number | [R] = Role | [C] = Channel | [* ] = Optional")
        try: await m.clear_reactions()
        except: pass
        await m.edit(embed=emb)

    @commands.command()
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def suggest(self, ctx, *, msg: typing.Optional[str]):
        try: await ctx.message.delete()
        except: pass
        if not msg:
            return await ctx.send(embed=discord.Embed(
            title=f"{emojis['cross']} No suggestion",
            description=f"Please enter a suggestion after `{ctx.prefix}suggest`.",
            color=colours["delete"]
        ), delete_after=10)
        r = await self.bot.get_channel(777214577187487744).send(embed=discord.Embed(
            title="Suggestion",
            description=f"Ticket: `{ctx.author.id}`\nName: `{ctx.author.name}`\n\n" + str(msg),
            color=colours["create"]
        ))
        await r.add_reaction(self.bot.get_emoji(729064531107774534))
        await r.add_reaction(self.bot.get_emoji(729064530310594601))
        await ctx.send(embed=discord.Embed(
            title=f"{emojis['tick']} Success",
            description="Your suggestion was sent to the dev team.",
            color=colours["create"]
        ), delete_after=10)

    @commands.command(aliases=["support"])
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def contact(self, ctx, *, msg: typing.Optional[str]):
        try: await ctx.message.delete()
        except: pass
        if not msg:
            return await ctx.send(embed=discord.Embed(
            title=f"{emojis['cross']} No message",
            description=f"Please enter a message after `{ctx.prefix}contact`.",
            color=colours["delete"]
        ), delete_after=10)
        await self.bot.get_channel(777220967315406929).send(embed=discord.Embed(
            title="Support",
            description=f"Ticket: `{ctx.author.id}`\nName: `{ctx.author.name}`\n\n" + str(msg),
            color=colours["delete"]
        ))
        await ctx.send(embed=discord.Embed(
            title=f"{emojis['tick']} Success",
            description="Your ticket was sent to the mod team.",
            color=colours["create"]
        ), delete_after=10)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id != 715989276382462053 and reaction.message.channel.id == 777214577187487744 and reaction.emoji.name == 'Tick':
            await reaction.message.delete()
            r = await self.bot.get_channel(777224376051040310).send(embed=discord.Embed(
                title="Suggestion",
                description='\n'.join(reaction.message.embeds[0].description.split("\n")[2:]),
                color=colours["create"]
            ))
            await r.add_reaction(self.bot.get_emoji(729064531107774534))
            await r.add_reaction(self.bot.get_emoji(729064530310594601))
        elif user.id != 715989276382462053 and reaction.message.channel.id == 777214577187487744 and reaction.emoji.name == 'Cross': await reaction.message.delete()

def setup(bot):
    bot.add_cog(InfoCommands(bot))
