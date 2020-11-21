import copy, discord, json, humanize, aiohttp, traceback, typing, time, asyncio, os

from datetime import datetime
from discord.ext import commands
from textwrap import shorten
from discord.ext import menus

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
        page = 0
        n = '\n'
        noLog = ":warning: Your server has not got a log channel. Use `m!setup` to make a log file and `m!setlog #channel` to set it.\n\n" if not os.path.exists(f"data/guilds/{ctx.guild.id}.json") else ""
        descriptions = [
            f"**Commands** - {emojis['PunWarn']} - {emojis['lock']} - {emojis['about']} - {emojis['support']}\n\n"
            f"{noLog}"
            f"{emojis['rsm']           } `m!info    [*T]  {'' if mob else '|'} ` {n if mob else ''}Shows all commands and info. Give [T] for mobile.\n"
            f"{emokis['graphs']        } `m!stats         {'' if mob else '|'} ` {n if mob else ''}Shows the bot statistics\n"
            f"{emojis['settings']      } `m!settings      {'' if mob else '|'} ` {n if mob else ''}Shows your servers log settings.\n"
            f"{emojis['join']          } `m!user    [*@]  {'' if mob else '|'} ` {n if mob else ''}Shows information about a user.\n"
            f"{emojis['support']       } `m!contact [ T]  {'' if mob else '|'} ` {n if mob else ''}Sends [T] to the staff for support.\n"
            f"{emojis['commands']      } `m!suggest [ T]  {'' if mob else '|'} ` {n if mob else ''}Sends [T] to the staff to add to the bot for voting.\n"
            f"{emojis['role_edit']     } `m!setlog  [ C]  {'' if mob else '|'} ` {n if mob else ''}Sets the servers log channel to [C].\n"
            f"{emojis['slowmodeOn']    } `m!ping          {'' if mob else '|'} ` {n if mob else ''}Checks the bots ping time.\n"
            f"{emojis['ignore']        } `m!ignore [*CR@] {'' if mob else '|'} ` {n if mob else ''}Stops logging the users, roles and channels privided.\n"
            f"{emojis['PunWarn']       } `m!punish   [*@] {'' if mob else '|'} ` {n if mob else ''}Punishes a user.\n"
            f"{emojis['mod_update']    } `m!server        {'' if mob else '|'} ` {n if mob else ''}Shows all information about your server.\n"
            f"{emojis['role_create']   } `m!role     [ R] {'' if mob else '|'} ` {n if mob else ''}With `Role`: Shows information about a role.\n"
            f"{emojis['role_create']   } `m!role     [ @] {'' if mob else '|'} ` {n if mob else ''}With `Mention`: Lets you edit or view a users roles.\n"
            f"{emojis['channel_create']} `m!viewas   [ @] {'' if mob else '|'} ` {n if mob else ''}Shows the channels that [@] can see.\n",

            f"{emojis['commands']} - **Moderation** - {emojis['lock']} - {emojis['about']} - {emojis['support']}\n\n"
            f"{emojis['PunWarn']   } `m!warn    [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Warns [@] for reason [T].\n"
            f"{emojis['PunHistory']} `m!clear   [*@] [*N] {'' if mob else '|'} ` {n if mob else ''}Clears [N] messages from [@].\n"
            f"{emojis['PunKick']   } `m!kick    [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Kicks [@] for reason [T].\n"
            f"{emojis['PunSoftBan']} `m!softban [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Soft bans [@] for reason [T].\n"
            f"{emojis['PunBan']    } `m!ban     [*@] [*T] {'' if mob else '|'} ` {n if mob else ''}Bans [@] for reason [T].\n"
            f"{emojis['purge']     } `m!purge        [*N] {'' if mob else '|'} ` {n if mob else ''}Deletes [N] messages in the channel.\n", 

            f"{emojis['commands']} - {emojis['PunWarn']} - **Raid** - {emojis['about']} - {emojis['support']}\n\n"
            f"{emojis['slowmodeOn']} `m!slowmode [*N]`\nSets the channel slowmode to [N]. Toggles if [N] is not provided.\n\n"
            f"{emojis['lock']      } `m!lock     [*T]`\nLocks the channel. All roles are denied `send_messages` unless they have `manage_messages`. `m!lock off` unlocks the channel.\n\n"
            f"{emojis['lock']      } `m!unlock       `\nUnlocks the channel. All roles are given `send_messages` if they did before.\n\n"
            f"{emojis['raidlock']  } `m!raid     [*T]`\nLocks down the entire server. All roles are denied `send_messages` if they do not have `manage_messages`. You can type `m!raid off` to end a raid, and type `m!raid` during a raid to view options like ban members.\n\n",

            f"{emojis['commands']} - {emojis['PunWarn']} - {emojis['lock']} - **About** - {emojis['support']}\n\n"
            f"RSM by ClicksMinutePer\n"
            f"Designed to make moderation easier.\n",

            f"{emojis['commands']} - {emojis['PunWarn']} - {emojis['about']} - **Support**\n\n"
            f"For support, use `m!contact`.\n"
        ]

        m = await ctx.send(embed=self.loadingEmbed)

        for _ in range(0,25):
            emb = discord.Embed (
                title=emojis["rsm"] + " RSM",
                description=descriptions[page] + "[Trello](https://trello.com/b/pBvhvzbY/rsm) | [Invite](https://discord.com/api/oauth2/authorize?client_id=715989276382462053&permissions=499510486&scope=bot) | [Support](https://discord.gg/bPaNnxe)",
                color=colours["create"]
            )
            emb.set_footer(text="[@] = Mention | [T] = Text | [N] = Number | [R] = Role | [C] = Channel | [* ] = Optional")
            await m.edit(embed=emb)

            for emoji in [729762938411548694, 729762938843430952, 729064530310594601]: await m.add_reaction(ctx.bot.get_emoji(emoji))

            reaction = None
            try: reaction = await ctx.bot.wait_for('reaction_add', timeout=120, check=lambda emoji, user : emoji.message.id == m.id and user == ctx.author)
            except asyncio.TimeoutError: break

            try: await m.remove_reaction(reaction[0].emoji, ctx.author)
            except: pass

            if reaction == None: break
            elif reaction[0].emoji.name == "Left":  page -= 1
            elif reaction[0].emoji.name == "Right": page += 1
            else: break

            page = min(len(descriptions)-1, max(0, page))

        emb = discord.Embed (
            title=emojis["rsm"] + " RSM",
            description=descriptions[page] + "[Trello](https://trello.com/b/pBvhvzbY/rsm) | [Invite](https://discord.com/api/oauth2/authorize?client_id=715989276382462053&permissions=499510486&scope=bot) | [Support](https://discord.gg/bPaNnxe)",
            color=colours["delete"]
        )
        emb.set_footer(text="[@] = Mention | [T] = Text | [N] = Number | [R] = Role | [C] = Channel | [* ] = Optional")
        await m.clear_reactions()
        await m.edit(embed=emb)
    
    @commands.command()
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def suggest(self, ctx, *, msg):
        await ctx.message.delete()
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
    async def contact(self, ctx, *, msg):
        await ctx.message.delete()
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
