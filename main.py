import discord.ext
from discord.ext import commands
from decouple import config
from discord_slash import SlashCommand, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component
import requests
from numpy import genfromtxt
import discord
from discord.ext import tasks
import json
from durations import Duration
import time
from discord.ext.commands import *
import sys


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents, case_insensitive=True)
bot.remove_command('help')
toe_ken = config('TOKEN')
slash = SlashCommand(bot, sync_commands=True)
guilds = [858547359804555264]
option_type = {
    "sub_command": 1,
    "sub_command_group": 2,
    "string": 3,
    "integer": 4,
    "boolean": 5,
    "user": 6,
    "channel": 7,
    "role": 8,
    "mentionable": 9,
    "float": 10
}

# Download scam domains
scamlist_url = "https://api.hyperphish.com/gimme-domains"
req = requests.get(scamlist_url)
url_content = req.content
bot.json_file = open('scamlist.json', 'wb')
bot.json_file.write(url_content)
bot.json_file.close()

async def has_perms(ctx):
    for b in ctx.author.roles:
        if b.id in RJD["perms"]:
            return True
    embed = discord.Embed(title="We ran into an error", description="You don't have permissions to manage this bot's functions",
                          color=discord.Color.red())
    embed.set_footer(text="Caused by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)
    return False


@slash.slash(name="scamlist",
             guild_ids=guilds,
             description="refreshes the scamlist and counts domains")
async def scamlist(ctx):
    scamlist_url = "https://api.hyperphish.com/gimme-domains"
    req = requests.get(scamlist_url)
    url_content = req.content
    bot.json_file = open('scamlist.json', 'wb')
    bot.json_file.write(url_content)
    bot.json_file.close()
    links = genfromtxt('scamlist.json', delimiter=',', skip_header=False, dtype=None, encoding="utf8")
    count = 0
    for link in links:
        count += 1
    await ctx.send(f"Updated scam list\nCurrently scanning for {count} scam links\n\nList is generated from: https://api.hyperphish.com/gimme-domains")


@bot.command(name='scamlist', pass_context=True)
async def scamlist(ctx):
    scamlist_url = "https://api.hyperphish.com/gimme-domains"
    req = requests.get(scamlist_url)
    url_content = req.content
    bot.json_file = open('scamlist.json', 'wb')
    bot.json_file.write(url_content)
    bot.json_file.close()
    links = genfromtxt('scamlist.json', delimiter=',', skip_header=False, dtype=None, encoding="utf8")
    count = 0
    for link in links:
        count += 1
    await ctx.send(f"Updated scam list\nCurrently scanning for {count} scam links\n\nList is generated from: https://api.hyperphish.com/gimme-domains")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "https://discord.gift/" in message.content:
        await message.channel.send(":warning: FREE NITRO! :warning:\nThis link appears to be legitimate :D")
        return
    links = genfromtxt('scamlist.json', delimiter=',', skip_header=False, dtype=None, encoding="utf8")
    filtered_links = []
    for link in links:
        filtered_link = link.replace('"', '')
        filtered_links.append(filtered_link)
    if any(keyword in message.content.lower() for keyword in filtered_links):
        await message.delete()
        role = discord.utils.get(message.guild.roles, name='Muted')
        await message.author.add_roles(role)
        warn = ":warning::mute:" + message.author.mention + " you have been muted for sending a scam link. Knock it off"
        await message.channel.send(warn)
        modlog = bot.get_channel(897765157940396052)
        description = message.author.display_name + " [" + str(message.author.id) + "] " "sent a scam link." + "\nLink: " + message.content + "\n" + ":mute: They have been muted :mute:"
        embed = discord.Embed(title="Scam Detected", description=str(description).replace(',', '').replace('(', '').replace(')', '').replace('\'', ''))
        embed.set_author(name=message.author.display_name,
                         icon_url=message.author.avatar_url)
        embed.set_thumbnail(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Warning_icon.svg/1153px-Warning_icon.svg.png")
        await modlog.send(embed=embed)

    await bot.process_commands(message)


# @bot.event
# async def on_message_edit(message_before, message_after):
#     if message_before.author == bot.user:
#         return
#
#     links = genfromtxt('scamlist.json', delimiter=',', skip_header=False, dtype=None, encoding="utf8")
#     filtered_links = []
#     for link in links:
#         filtered_link = link.replace('"', '')
#         filtered_links.append(filtered_link)
#     if any(keyword in message_after.content.lower() for keyword in filtered_links):
#         await message_after.delete()
#         await message_after.channel.send(":warning: Scam detected :warning:")
#         modlog = bot.get_channel(897765157940396052)
#         description = message_after.author.display_name + " (" + str(message_after.author.id) + ") " "sent a scam link." + "\nLink: " + message_after.content + "\n" + "Be careful if you click this link"
#         embed = discord.Embed(title="Scam Detected", description=str(description).replace(',', '').replace('(', '').replace(')', '').replace('\'', ''))
#         embed.set_author(name=message_after.author.display_name,
#                          icon_url=message_after.author.avatar_url)
#         embed.set_thumbnail(
#             url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Warning_icon.svg/1153px-Warning_icon.svg.png")
#         await modlog.send(embed=embed)


# @bot.event
# async def on_ready():
#     print(f'Logged in as {bot.user} (ID: {bot.user.id})')
#     print('------')


@slash.slash(name="list-members",
             guild_ids=guilds,
             description="Lists all members with a certain role",
             options=[
                 create_option(
                     name="role",
                     description="The role you want to list",
                     option_type=option_type['role'],
                     required=True
                 )
             ])
async def list(ctx: SlashContext, role: discord.Role):
    usernames = [m.mention for m in role.members]
    count = 0
    for m in role.members:
        count += 1
    title_text = "**", count, "members with the", role.mention, "role**"
    title = str(title_text).replace(',', '').replace('(', '').replace(')', '').replace('\'', '')
    description = str(sorted(usernames, key=str.lower)).replace(',', '\n').replace('[', '').replace(']', '').replace('\'', '')
    embed = discord.Embed(description=title + "\n" + description, color=role.color)
    embed.set_footer(text="Issued by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='buttontest', pass_context=True)
@check(has_perms)
async def buttontest(ctx, *, message):
    buttons = [
        create_button(style=ButtonStyle.green, label="A green button"),
        create_button(style=ButtonStyle.blue, label="A blue button")
    ]
    action_row = create_actionrow(*buttons)

    await ctx.send("Hello Friendo", components=[action_row])
    # note: this will only catch one button press, if you want more, put this in a loop
    button_ctx: ComponentContext = await wait_for_component(bot, components=action_row)
    await button_ctx.edit_origin(content="You pressed a button!, I am unsure how to detect which button though")


# @bot.event
# async def on_component(ctx: ComponentContext):
#     # you may want to filter or change behaviour based on custom_id or message
#     await ctx.edit_origin(content="This is a event handler for all interactions, this is pretty much useless to me")


@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.errors.CheckFailure):
        embed = discord.Embed(title="We ran into an error", description="You are not staff", color=discord.Color.red())
        embed.set_footer(text="Caused by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="We ran into an error", description="You forgot to define something", color=discord.Color.red())
        embed.set_footer(text="Caused by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.BotMissingPermissions):
        embed = discord.Embed(title="We ran into an error", description="I am missing permissions", color=discord.Color.red())
        embed.set_footer(text="Caused by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.CommandNotFound):
        try:
            print("Doing nothing since this command doesn't exist")
        except:
            crash = True
    else:
        embed = discord.Embed(title="We ran into an undefined error", description=error, color=discord.Color.red())
        embed.set_footer(text="Issued by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@bot.event
async def on_member_join(ctx):
    if ctx.guild.id == 858547359804555264:
        if ctx.bot:
            return
        else:
            channel = bot.get_channel(858547359804555267)
            title = "Welcome to Prism SMP!"
            description = "Please look at the <#861317568807829535> when you have a minute.\n\n" \
                   "You can grab some self roles over in <#861288424640348160>.\n" \
                   "Join the server at least once (the IP is in <#858549386962272296> [You don't have to read the entirety of that])" \
                   " then ask in <#869280855657447445> to get yourself whitelisted."
            embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
            embed.set_footer(text=ctx.name, icon_url=ctx.avatar_url)
            await channel.send(embed=embed)
            role = discord.utils.get(ctx.guild.roles, name='New Member')
            await ctx.add_roles(role)


@bot.command(name='lp', pass_context=True)
@check(has_perms)
async def lp(ctx, *, message):
    await ctx.message.delete()
    changes = "```diff\n" + message + "```"
    embed = discord.Embed(title="Permission Changelog", description=changes, color=0x00ff40)
    embed.set_footer(text="Issued by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='game', aliases=['gamecommands', 'gc'], pass_context=True)
async def game(ctx):

    help = "**Discord Commands:** (can only be run in #in-game-chat)\n`/inv` Shows the contents of your inventory\n"\
           "`/ender` Shows the contents of your enderchest\n\n**In-game Commands**\n"\
           "`[ec]` Broadcasts the contents of your enderchest\n`[inv]` Broadcasts the contents of your inventory\n"\
           "`[item]` Broadcasts your currently held item\n`[pos]` Broadcasts your position\n"\
           "`[ping]` Catching on yet?\n`/t <message>` Shortcut for team message"
    embed = discord.Embed(title="Game Command Help", description=help, color=ctx.message.author.color)
    embed.set_footer(text="Issued by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name="help",
             guild_ids=guilds,
             description="displays the help")
async def help(ctx):
    help = "**Hello Friendo!**\nI am Prism Bot. I'm designed to make your life on Prism easier.\nIf you run into any issues please ping <@324504908013240330>"
    embed = discord.Embed(title="Help", description=help, color=ctx.author.color)
    embed.set_footer(text="Issued by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/icons/858547359804555264/34eacdf2f8da259c1bf88ba6cbf087c7.jpg")
    await ctx.send(embed=embed)


@slash.slash(name="game-commands",
             guild_ids=guilds,
             description="displays the list of game commands")
async def game(ctx):

    help = "**Discord Commands:** (can only be run in #in-game-chat)\n`/inv` Shows the contents of your inventory\n"\
           "`/ender` Shows the contents of your enderchest\n\n**In-game Commands**\n"\
           "`[ec]` Broadcasts the contents of your enderchest\n`[inv]` Broadcasts the contents of your inventory\n"\
           "`[item]` Broadcasts your currently held item\n`[pos]` Broadcasts your position\n"\
           "`[ping]` Catching on yet?\n`/t <message>` Shortcut for team message"
    embed = discord.Embed(title="Game Command Help", description=help, color=ctx.author.color)
    embed.set_footer(text="Issued by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='bolte', aliases=['boltecommands', 'bc'], pass_context=True)
async def bolte(ctx):

    help = "**Prismian Commands:**\n`/iam` Allows you to choose roles\n`/iamnot` Removes those roles\n"\
           "`/reminder create` Kinda self-explanatory\n`/reminder view` See above\n"\
           "`/suggestion create` Creates a suggestion for the staff to review\n"\
           "`/spotify` Easily share what you're currently listening to\n`$play <song>` Plays music in your VC\n`$skip` Skips your song"
    embed = discord.Embed(title="Prism Bot Command Help", description=help, color=ctx.message.author.color)
    embed.set_footer(text="Issued by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name="bolte-commands",
             guild_ids=guilds,
             description="displays the list of bolte commands")
async def bolte(ctx):

    help = "**Prismian Commands:**\n`/iam` Allows you to choose roles\n`/iamnot` Removes those roles\n"\
           "`/reminder create` Kinda self-explanatory\n`/reminder view` See above\n"\
           "`/suggestion create` Creates a suggestion for the staff to review\n"\
           "`/spotify` Easily share what you're currently listening to\n`$play <song>` Plays music in your VC\n`$skip` Skips your song"
    embed = discord.Embed(title="Bolte:tm: Command Help", description=help, color=ctx.author.color)
    embed.set_footer(text="Issued by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name="staff-commands",
             guild_ids=guilds,
             description="displays the list of staff commands")
@check(has_perms)
async def staff(ctx):

    help = "**Staff Commands**\n"\
           "`/self-roles add` Adds a role to the `/iam` command\n`/self-roles remove` Does the opposite\n"\
           "`/poll` Creates a poll for people to vote on\n"\
           "`/suggestion view` A nifty menu for viewing suggestions\n"\
           "`$warn <user> <reason>` Warns the mentioned user for the stated reason\n"\
           "`$ban <user> <reason>` Bans the mentioned user for the stated reason\n`/whitelist <user>` Whitelists the user"
    embed = discord.Embed(title="Bolte:tm: Command Help", description=help, color=ctx.author.color)
    embed.set_footer(text="Issued by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='staff', aliases=['staffcommands', 'sc'], pass_context=True)
@check(has_perms)
async def staff(ctx: SlashContext):

    help = "**Staff Commands**\n"\
           "`/self-roles add` Adds a role to the `/iam` command\n`/self-roles remove` Does the opposite\n"\
           "`/poll` Creates a poll for people to vote on\n"\
           "`/suggestion view` A nifty menu for viewing suggestions\n"\
           "`$warn <user> <reason>` Warns the mentioned user for the stated reason\n"\
           "`$ban <user> <reason>` Bans the mentioned user for the stated reason\n`$whitelist <mention discord user>` Whitelists the user"
    embed = discord.Embed(title="Prism Bot Command Help", description=help, color=ctx.message.author.color)
    embed.set_footer(text="Issued by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name="embed",
             guild_ids=guilds,
             description="creates an embed",
             options=[
                 create_option(
                     name="title",
                     description="The title of the embed",
                     option_type=option_type["string"],
                     required=True
                 ), create_option(
                     name="description",
                     description="The description of the embed",
                     option_type=option_type["string"],
                     required=True
                 ), create_option(
                     name="channel",
                     description="The channel to send to",
                     option_type=option_type["channel"],
                     required=True
                 ), create_option(
                     name="silent",
                     description="Whether to show the creator",
                     option_type=option_type["boolean"],
                     required=True
                 )
             ])
@check(has_perms)
async def embed(ctx: SlashContext, *, title, description, channel: discord.TextChannel, silent):
    embed = discord.Embed(title=title, description=description, color=ctx.author.color)
    if not silent:
        embed.set_footer(text="Issued by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    await ctx.send("Embed sent", hidden=True)
    await channel.send(embed=embed)


@slash.slash(name="whitelist",
             guild_ids=guilds,
             description="Adds a user to the whitelist",
             options=[
                 create_option(
                     name="member",
                     description="The user you want to whitelist",
                     option_type=option_type["user"],
                     required=True
                 )
             ])
@check(has_perms)
async def whitelist(ctx: SlashContext, member: discord.Member):
    channel = bot.get_channel(869280855657447445)
    role = discord.utils.get(member.guild.roles, name='Whitelisted')
    await member.add_roles(role)
    message = "Added " + member.mention + " to the whitelist"
    embed = discord.Embed(title="Whitelisted", description=message, color=ctx.author.color)
    embed.set_footer(text="Whitelisted by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    await channel.send(embed=embed)
    await ctx.send(embed=embed, hidden=True)


@bot.command(name='whitelist', pass_context=True)
@check(has_perms)
async def whitelist(ctx, member: discord.Member):
    await ctx.message.delete()
    channel = bot.get_channel(869280855657447445)
    role = discord.utils.get(member.guild.roles, id=899568696593367070)
    await member.add_roles(role)
    message = "Added " + member.display_name + " to the whitelist"
    embed = discord.Embed(title="Whitelisted", description=message, color=ctx.message.author.color)
    embed.set_footer(text="Whitelisted by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    await channel.send(embed=embed)


@slash.slash(name="edit-embed",
             guild_ids=guilds,
             description="edits an embed",
             options=[
                 create_option(
                     name="embedlink",
                     description="The message link to edit",
                     option_type=option_type["string"],
                     required=True
                 ), create_option(
                     name="title",
                     description="The title of the embed",
                     option_type=option_type["string"],
                     required=True
                 ), create_option(
                     name="description",
                     description="The description of the embed",
                     option_type=option_type["string"],
                     required=True
                 ), create_option(
                     name="silent",
                     description="Whether to show the creator",
                     option_type=option_type["boolean"],
                     required=True
                 )
             ])
@check(has_perms)
async def embed(ctx: SlashContext, *, embedlink, title, description, silent):
    newembed = discord.Embed(title=title, description=description, color=ctx.author.color)
    if not silent:
        embed.set_footer(text="Issued by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    await ctx.send("Embed edited", hidden=True)
    editembed = embedlink.split('/')
    message = await bot.get_guild(int(editembed[-3])).get_channel(int(editembed[-2])).fetch_message(int(editembed[-1]))
    await message.edit(embed=newembed)

# Ping logger, currently disabled but working
#@bot.event
#async def on_message(message):
#    blacklist_guilds = [858547359804555264]
#    blacklist_channels = [900307948969025576]
#    if message.guild.id in blacklist_guilds or message.channel.id in blacklist_channels:
#        return
#    else:
#        if message.mentions:
#            if not message.author.bot:
#                for i in message.mentions:
#                    mention = str(i)
#                    no_ping = str(message.content).replace('<@', '\<@')
#                    if '\<@' in no_ping:
#                        content = str("Mentioning: " + mention + "\nMessage: " + no_ping)
#                    else:
#                        content = str("Replying to: " + mention + "\nMessage: " + no_ping)
#                    async with aiohttp.ClientSession() as session:
#                        webhook = Webhook.from_url('https://canary.discord.com/api/webhooks/907719076007276584/3q9vN9bsEDGP99jjsX_26NvIyCVas5G246ylXvIoV015cdPCxKTJ-o8zsSXZjG6pdFYk', adapter=AsyncWebhookAdapter(session))
#                        await webhook.send(content, username=message.author.display_name, avatar_url=message.author.avatar_url)
#        else:
#            return

bot_name = "Prism Bot"
filename = "roles.json"
status = ""



def jsondump(v: dict):
    RolesJson.seek(0)
    json.dump(v, RolesJson)
    RolesJson.truncate()
    RolesJson.seek(0)




def timeformat(secs):
    dyears = 31622400
    dmonth = 2635200
    dweeks = 604800
    ddays = 86400
    dhours = 3600
    dmins = 60
    years = int(secs//dyears)
    month = int((secs - years*dyears)//dmonth)
    weeks = int((secs - years*dyears - month*dmonth)//dweeks)
    days = int((secs - years*dyears - month*dmonth - weeks*dweeks)//ddays)
    hours = int((secs - years*dyears - month*dmonth - weeks*dweeks - days*ddays)//dhours)
    minutes = int((secs - years*dyears - month*dmonth - weeks*dweeks - days*ddays - hours*dhours)//dmins)
    seconds = int((secs - years*dyears - month*dmonth - weeks*dweeks - days*ddays - hours*dhours - minutes*dmins)//1)
    milliseconds = float(round(((secs - years*dyears - month*dmonth - weeks*dweeks - days*ddays - hours*dhours - minutes*dmins - seconds)*1000), 3))
    if milliseconds.is_integer():
        int(milliseconds)
    result = []
    if years != 0:
        if years == 1:
            s = ""
        else:
            s = "s"
        result.append(f"{years} year{s}")
    if month != 0:
        result.append(f"{month} month")
    if weeks != 0:
        if weeks == 1:
            s = ""
        else:
            s = "s"
        result.append(f"{weeks} week{s}")
    if days != 0:
        if days == 1:
            s = ""
        else:
            s = "s"
        result.append(f"{days} day{s}")
    if hours != 0:
        if hours == 1:
            s = ""
        else:
            s = "s"
        result.append(f"{hours} hour{s}")
    if minutes != 0:
        if minutes == 1:
            s = ""
        else:
            s = "s"
        result.append(f"{minutes} minute{s}")
    if seconds != 0:
        if seconds == 1:
            s = ""
        else:
            s = "s"
        result.append(f"{seconds} second{s}")
    if milliseconds != 0:
        if years == 1:
            s = ""
        else:
            s = "s"
        result.append(f"{milliseconds} millisecond{s}")
    result = ", ".join(result)
    return result


# EVENTS
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    print(f'{message.author.display_name} sent: {message.content}')


@bot.event
async def on_ready():
    global RJD, RolesJson
    TestingZone = bot.get_guild(int(config('guild_id')))
    try:
        RolesJson = open(filename, "r+")
    except:
        RolesJson = open(filename, "w+")
        json.dump({"perms": [], "roles": []}, RolesJson)
        RolesJson.seek(0)
    # Setup
    RJD = json.load(RolesJson)
    RolesJson.seek(0)
    for role in RJD["roles"]:
        for member in RJD[role[0]]:
            if member[1] <= time.time():
                try:
                    await TestingZone.get_member(member[0]).remove_roles(TestingZone.get_role(int(role[0])), reason="expired")
                except:
                    pass
                RJD[role[0]].remove(member)
            else:
                break
    jsondump(RJD)
    current_time = time.time()
    for role in RJD["roles"]:
        for member in RJD[role[0]]:
            member[1] -= current_time
    print("Bot is ready")
    print(f"Prism Bot")
    print(f"Discord API Version: {discord.__version__}")

    async def pushList(n: str):
        try:
            RJD[n][0][1] = RJD[n][0][1]
        except IndexError:
            return False
        if RJD[n][0][1] <= 0:
            try:
                await TestingZone.get_member(RJD[n][0][0]).remove_roles(TestingZone.get_role(int(n)), reason="expired")
            except:
                pass
            del RJD[n][0]
            RolesJson.seek(0)
            r = json.load(RolesJson)
            del r[n][0]
            jsondump(r)
            for memberlist in RJD[n]:
                memberlist[1] -= 0.5
            await pushList(n)
        else:
            return True

    @tasks.loop(seconds=0.5)
    async def dec():
        for role in RJD["roles"]:
            n = role[0]
            if not await pushList(n):
                continue
            for memberlist in RJD[n]:
                memberlist[1] -= 0.5
    dec.start()


@bot.event
async def on_member_update(before:discord.Member, after:discord.Member):
    RolesJson.seek(0)
    a = json.load(RolesJson)
    RolesJson.seek(0)
    for role in after.roles:
        if role in before.roles:
            continue
        h = str(role.id)
        for roleTup in a["roles"]:
            if h == roleTup[0]:
                RJD[h].append([after.id, roleTup[1]])
                a[h].append([after.id, roleTup[1] + round(time.time())])
    jsondump(a)


# Command to set a role to expire
@slash.slash(name="role-expire",
             guild_ids=guilds,
             description="Sets when a role will expire",
             options=[
                 create_option(
                     name="role",
                     description="the role you want to expire",
                     option_type=option_type["role"],
                     required=True
                 ), create_option(
                     name="time",
                     description="how long you want people to have the role",
                     option_type=option_type["string"],
                     required=True
                 )
             ])
@check(has_perms)
async def expire(ctx: Context, role: discord.Role, *, time: str):
    print(role.permissions)
    ExpireDuration = Duration(time)
    ExpireDuration = ExpireDuration.to_seconds()
    if int(ExpireDuration) == 0:
        await ctx.send(f"Check your syntax, /role-help")
        return
    RolesJsonData = json.load(RolesJson)
    RolesJson.seek(0)
    found = False
    t = str(role.id)
    for ExpiringRole in RolesJsonData["roles"]:
        if ExpiringRole[0] == t:
            for memberlist in RJD[t]:
                memberlist[1] -= (ExpiringRole[1] - ExpireDuration)
            for memberlist2 in RolesJsonData[t]:
                memberlist2[1] -= (ExpiringRole[1] - ExpireDuration)
            ExpiringRole[1] = ExpireDuration
            RJD["roles"][RolesJsonData["roles"].index(ExpiringRole)][1] = ExpireDuration
            print(RolesJsonData)
            found = True
            break
    if not found:
        RJD["roles"].append([t, ExpireDuration])
        RJD[t] = []
        RolesJsonData["roles"].append([t, ExpireDuration])
        RolesJsonData[t] = []
    jsondump(RolesJsonData)
    await ctx.send(f"✅ set {role.name} to expire {str(Duration(time)).replace('<Duration ', 'after ').replace('>', '')}")


@bot.command()
@check(has_perms)
async def expire(ctx: Context, role: discord.Role, *, time: str):
    print(role.permissions)
    ExpireDuration = Duration(time)
    ExpireDuration = ExpireDuration.to_seconds()
    if int(ExpireDuration) == 0:
        await ctx.send(f"Check your syntax, $role-help")
        return
    RolesJsonData = json.load(RolesJson)
    RolesJson.seek(0)
    found = False
    t = str(role.id)
    for ExpiringRole in RolesJsonData["roles"]:
        if ExpiringRole[0] == t:
            for memberlist in RJD[t]:
                memberlist[1] -= (ExpiringRole[1] - ExpireDuration)
            for memberlist2 in RolesJsonData[t]:
                memberlist2[1] -= (ExpiringRole[1] - ExpireDuration)
            ExpiringRole[1] = ExpireDuration
            RJD["roles"][RolesJsonData["roles"].index(ExpiringRole)][1] = ExpireDuration
            print(RolesJsonData)
            found = True
            break
    if not found:
        RJD["roles"].append([t, ExpireDuration])
        RJD[t] = []
        RolesJsonData["roles"].append([t, ExpireDuration])
        RolesJsonData[t] = []
    jsondump(RolesJsonData)
    await ctx.message.add_reaction("✅")


@slash.slash(name="role-unexpire",
             guild_ids=guilds,
             description="Sets a role to not expire",
             options=[
                 create_option(
                     name="role",
                     description="the role you don't want to expire",
                     option_type=option_type["role"],
                     required=True
                 )
             ])
@check(has_perms)
async def unexpire(ctx, role: discord.Role):
    RolesJson.seek(0)
    RolesJsonData = json.load(RolesJson)
    RolesJson.seek(0)
    for ExpiringRole in RolesJsonData["roles"]:
        if ExpiringRole[0] == str(role.id):
            RolesJsonData["roles"].remove(ExpiringRole)
            RJD["roles"].remove(ExpiringRole)
            del RolesJsonData[str(role.id)]
            del RJD[str(role.id)]
    jsondump(RolesJsonData)
    await ctx.send(f"✅ set {role.name} to not expire")


@bot.command()
@check(has_perms)
async def unexpire(ctx, role: discord.Role):
    RolesJson.seek(0)
    RolesJsonData = json.load(RolesJson)
    RolesJson.seek(0)
    for ExpiringRole in RolesJsonData["roles"]:
        if ExpiringRole[0] == str(role.id):
            RolesJsonData["roles"].remove(ExpiringRole)
            RJD["roles"].remove(ExpiringRole)
            del RolesJsonData[str(role.id)]
            del RJD[str(role.id)]
    jsondump(RolesJsonData)
    await ctx.message.add_reaction("✅")

@slash.slash(name="role-help",
             guild_ids=guilds,
             description="Displays the role help embed"
             )
async def _help(ctx: discord.ext.commands.Context):
    help_embed = discord.Embed(
        title=f"Role Help",
        description="slash commands",
        colour=discord.Colour.blue()
    )
    help_embed.add_field(
        name="role-expire",
        value=f"_Sets a role to expire after a certain amount of time_\n\n`/role-expire <role> <time>`\n(eg, /role-expire @examplerole 1m 12s)",
        inline=False
    )
    help_embed.add_field(
        name="role-unexpire",
        value=f"_Removes a role from the list of expiring roles_\n\n`/role-unexpire <role>`\n(eg, /role-unexpire @examplerole2)",
        inline=False
    )
    help_embed.add_field(
        name="AddPerm",
        value=f"_Gives a role permissions to use this bot. You need to have `Manage Roles` Permissions to use this command._\n\n`/addperm <role>`",
        inline=False
    )
    help_embed.add_field(
        name="DelPerm",
        value=f"_Removes a role's permission to use this bot. You need to have `Manage Roles` Permissions to use this command._\n\n`/delperm <role>`",
        inline=False
    )
    help_embed.add_field(
        name="ViewRoles",
        value=f"_Displays the current settings._\n\n`/viewroles`",
        inline=False
    )
    help_embed.add_field(
        name="ViewPerms",
        value=f"_Displays which Roles have permissions to configure the Bot._\n\n`/viewperms`",
        inline=False
    )
    help_embed.add_field(
        name="Ping",
        value=f"_Displays the bots latency._\n\n`/ping`",
        inline=False
    )
    await ctx.send(embed=help_embed)


@bot.command(name="role-help")
async def _help(ctx: discord.ext.commands.Context):
    help_embed = discord.Embed(
        title=f"{bot_name} >> Help",
        description="Commands",
        colour=discord.Colour.blue()
    )
    help_embed.add_field(
        name="Expire",
        value=f"_Sets a role to expire after a certain amount of time_\n\n`$expire <role> <time>`\n(eg, $expire @examplerole 1m 12s)",
        inline=False
    )
    help_embed.add_field(
        name="Unexpire",
        value=f"_Removes a role from the list of expiring roles_\n\n`$unexpire <role>`\n(eg, $unexpire @examplerole2)",
        inline=False
    )
    help_embed.add_field(
        name="AddPerm",
        value=f"_Gives a role permissions to use this bot. You need to have `Manage Roles` Permissions to use this command._\n\n`$addperm <role>`",
        inline=False
    )
    help_embed.add_field(
        name="DelPerm",
        value=f"_Removes a role's permission to use this bot. You need to have `Manage Roles` Permissions to use this command._\n\n`$delperm <role>`",
        inline=False
    )
    help_embed.add_field(
        name="ViewRoles",
        value=f"_Displays the current settings_\n\n`$viewroles`",
        inline=False
    )
    help_embed.add_field(
        name="ViewPerms",
        value=f"_Displays which Roles have permissions to configure the Bot_\n\n`$viewperms`",
        inline=False
    )
    help_embed.add_field(
        name="Ping",
        value=f"_Displays the bots latency.\n\n`$ping`",
        inline=False
    )
    await ctx.send(embed=help_embed)


@slash.slash(name="addperm",
             guild_ids=guilds,
             description="Adds a role to manage Prism Bot",
             options=[
                 create_option(
                     name="role",
                     description="the role",
                     option_type=option_type["role"],
                     required=True
                 )
             ])
@has_permissions(manage_roles=True)
async def addperm(ctx: Context, role: discord.Role):
    r = role.id
    if r not in RJD["perms"]:
        RJD["perms"].append(r)
        y = json.load(RolesJson)
        RolesJson.seek(0)
        y["perms"].append(r)
        jsondump(y)
        await ctx.send(f"✅ added {role.name} to the management team")
    else:
        await ctx.send("That role already has permissions!")


@bot.command()
@has_permissions(manage_roles=True)
async def addperm(ctx: Context, role: discord.Role):
    r = role.id
    if r not in RJD["perms"]:
        RJD["perms"].append(r)
        y = json.load(RolesJson)
        RolesJson.seek(0)
        y["perms"].append(r)
        jsondump(y)
        await ctx.send(f"✅ added {role.name} to the management team")
    else:
        await ctx.send("That role already has permissions!")


@slash.slash(name="delperm",
             guild_ids=guilds,
             description="Removes a role from managing Prism Bot",
             options=[
                 create_option(
                     name="role",
                     description="the role",
                     option_type=option_type["role"],
                     required=True
                 )
             ])
@has_permissions(manage_roles=True)
async def delperm(ctx: Context, role: discord.Role):
    r = role.id
    if r in RJD["perms"]:
        RJD["perms"].remove(r)
        y = json.load(RolesJson)
        RolesJson.seek(0)
        y["perms"].remove(r)
        jsondump(y)
        await ctx.send(f"✅ removed {role.name} from the management role")
    else:
        await ctx.send("I don't think that role had permissions :confused:")


@bot.command()
@has_permissions(manage_roles=True)
async def delperm(ctx: Context, role: discord.Role):
    r = role.id
    if r in RJD["perms"]:
        RJD["perms"].remove(r)
        y = json.load(RolesJson)
        RolesJson.seek(0)
        y["perms"].remove(r)
        jsondump(y)
        await ctx.send(f"✅ removed {role.name} from the management role")
    else:
        await ctx.send("I don't think that role had permissions :confused:")


@slash.slash(name="viewroles",
             guild_ids=guilds,
             description="View the roles that are set to expire"
             )
async def viewroles(ctx: Context):
    Roles = []
    for role in RJD["roles"]:
        Roles.append(f"<@&{role[0]}>")
    expires = []
    for role in RJD["roles"]:
        expires.append(timeformat(role[1]))
    roles_embed = discord.Embed(
        title=f"{bot_name} >> Roles",
        description=f"Displays all Roles you added using /expire",
        colour=discord.Colour.blue()
    )
    roles_embed.add_field(
        name="Role",
        value="\n".join(Roles),
        inline=True
    )
    roles_embed.add_field(
        name="Expires After",
        value="\n".join(expires),
        inline=True
    )
    await ctx.send(embed=roles_embed)


@bot.command()
async def viewroles(ctx: Context):
    Roles = []
    for role in RJD["roles"]:
        Roles.append(f"<@&{role[0]}>")
    expires = []
    for role in RJD["roles"]:
        expires.append(timeformat(role[1]))
    roles_embed = discord.Embed(
        title=f"{bot_name} >> Roles",
        description=f"Displays all Roles you added using $expire",
        colour=discord.Colour.blue()
    )
    roles_embed.add_field(
        name="Role",
        value="\n".join(Roles),
        inline=True
    )
    roles_embed.add_field(
        name="Expires After",
        value="\n".join(expires),
        inline=True
    )
    await ctx.send(embed=roles_embed)


@slash.slash(name="viewperms",
             guild_ids=guilds,
             description="Views the roles allowed to manage Prism Bot")
async def viewperms(ctx: Context):
    perms = []
    for role in RJD["perms"]:
        perms.append(f"<@&{role}>")
    perms_embed = discord.Embed(
        title=f"{bot_name} >> Permissions",
        description=f"Displays all Roles (you added using /addperm) that have permissions.",
        colour=discord.Colour.blue()
    )
    perms_embed.add_field(
        name="Role(s) with Permissions",
        value="\n".join(perms),
        inline=False
    )
    await ctx.send(embed=perms_embed)


@bot.command()
async def viewperms(ctx: Context):
    perms = []
    for role in RJD["perms"]:
        perms.append(f"<@&{role}>")
    perms_embed = discord.Embed(
        title=f"{bot_name} >> Permissions",
        description=f"Displays all Roles (you added using $addperm) that have permissions.",
        colour=discord.Colour.blue()
    )
    perms_embed.add_field(
        name="Role(s) with Permissions",
        value="\n".join(perms),
        inline=False
    )
    await ctx.send(embed=perms_embed)


@slash.slash(name="ping",
             guild_ids=guilds,
             description="Checks Prism Bot's ping")
async def ping(ctx):
    await ctx.send(f'My ping is {round((bot.latency * 1000), 3)} ms!')


@bot.command()
async def ping(ctx):
    await ctx.send(f'My ping is {round((bot.latency * 1000), 3)} ms!')


@slash.slash(name="stop",
             guild_ids=guilds,
             description="Kills Prism Bot")
@is_owner()
async def stop(ctx: Context):
    await ctx.send("https://c.tenor.com/huJuK_zUxSAAAAAM/im-dying-jake.gif")
    sys.exit()


@bot.command()
@is_owner()
async def stop(ctx: Context):
    await ctx.send("https://c.tenor.com/huJuK_zUxSAAAAAM/im-dying-jake.gif")
    sys.exit()


@bot.event
async def on_command_error(ctx: Context, err):
    await ctx.send(err)


bot.run(toe_ken)



