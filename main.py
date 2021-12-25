# Holy shit, that's a lot of imports
import contextlib
import io
import ipaddress
import os
import re
import subprocess
import sys
from urllib import parse, request
from urllib.parse import parse_qsl
from requests import PreparedRequest
from decouple import config
import aiohttp
import discord.ext
import discord
from discord import Webhook, AsyncWebhookAdapter, http
from discord.ext.commands import CommandNotFound
from discord.ext.commands import *
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext, ComponentContext, MenuContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow,\
    create_select_option, create_select, wait_for_component
from discord_slash.model import ButtonStyle, ContextMenuType
from slash_help import SlashHelp
import requests
import json
from durations import Duration
import time
from datetime import datetime
import logging


# Setup the logger
class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


# Setup the bot
intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix=['$', 'pls', 'prism'],
                   intents=intents,
                   case_insensitive=True,
                   help_command=None,
                   strip_after_prefix=True
                   )
toe_ken = config('TOKEN')
slash = SlashCommand(bot, sync_commands=True)
help_slash = SlashHelp(bot,
                       slash,
                       toe_ken,
                       dpy_command=True,
                       no_category_name="All commands",
                       no_category_description=" ",
                       extended_buttons=True,
                       prefix='$'
                       )


# Much easier than remembering numbers
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

bot_name = "Prism Bot"
filename = "roles.json"
status = ""

#
# # Returns a string if the timedelta is shorter than the minimum
# def bad_time(delta: timedelta) -> Optional[str]:
#     if delta.total_seconds() <= 0:
#         return 'I cannot work backwards... maybe one day.'
#     elif delta.total_seconds() < (60 * 5):
#         return 'Minimum reminder time is 5 minutes, please try again.'
#
#
# # The $remind command
# @bot.command(name='remind')
# async def remind(ctx, time: to_timedelta, *, what):
#     if bad_time_string := bad_time(time):  # ensure user isn't dumb
#         return await ctx.send(bad_time_string)
#
#     now = ctx.message.created_at
#     when = now + time
#
#     await db.all_reminders.insert_one({  # add reminder to db
#         'user_id': ctx.author.id,
#         'channel_id': ctx.channel.id,
#         'next_time': when,
#         'content': what,
#         'recurrent_time': False,
#         'done': False,
#     })
#
#     await ctx.send(f"I'll remind you on {when.strftime('%x %X')} (utc)")
#
#
# # Remind every x
# @bot.command()
# async def every(ctx, time: str, *, what):
#
#     delta = to_timedelta(time)
#
#     if bad_time_string := bad_time(delta):  # ensure user isn't dumb
#         return await ctx.send(bad_time_string)
#
#     now = ctx.message.created_at
#     when = now + delta
#     await db.all_reminders.insert_one({
#         'user_id': ctx.author.id,
#         'channel_id': ctx.channel.id,
#         'next_time': when,
#         'content': what,
#         'recurrent_time': time,
#         'done': False,
#     })
#     await ctx.send(f"I'll remind you every {delta}.\n"
#                    f"Next reminder on {when.strftime('%x %X')} (utc)")
#
#
# # Delete recurring reminders
# @bot.command()
# async def delete(self, ctx):
#     trimmer = Trimmer(max_length=140)
#     reminders = await db.all_reminders.find({'user_id': ctx.author.id, 'done': False}).to_list(length=None)
#     options = {}
#     for i, reminder in enumerate(reminders, start=1):
#         channel = self.bot.get_channel(reminder['channel_id'])
#         options[
#
#             (f"**{i})** Every: __{reminder['recurrent_time']}__ "
#              if reminder['recurrent_time']
#              else f"On: __{reminder['next_time'].strftime('%x %X')}__ ") +
#             (f"In: {channel.mention}" if channel else "") +
#             f"| {trimmer(reminder['content'])}\n\n"
#             ] = reminder
#     if options:
#         choice = await multichoice(ctx, list(options))
#         if choice:
#             reminder = options[choice]
#             reminder['done'] = True
#             await db.all_reminders.replace_one({'_id': ObjectId(reminder['_id'])}, reminder)
#             await ctx.send('Done!')
#         else:
#             await ctx.send('Cancelled!')
#     else:
#         await ctx.send("You don't have any active reminders")
#
#
# @tasks.loop(seconds=5)  # every 5 seconds check if a reminder is due
# async def remind(self):
#     now = datetime.utcnow()
#     reminders = db.all_reminders.find({'done': False, 'next_time': {'$lte': now}})
#     async for reminder in reminders:
#         channel = self.bot.get_channel(reminder['channel_id'])
#         guild = getattr(channel, 'guild', None)
#         try:
#             if guild:
#                 author = await guild.fetch_member(reminder['user_id'])
#             else:
#                 author = await self.bot.fetch_user(reminder['user_id'])
#         except NotFound:
#             if reminder['next_time'] <= (now - timedelta(days=2)):
#                 reminder['done'] = True
#                 await db.all_reminders.replace_one({'_id': reminder['_id']}, reminder)
#             continue
#         else:
#             if author and channel:
#                 await channel.send(f"{author.mention}! Here's your reminder:\n"
#                                    f">>> {reminder['content']}")
#
#                 if (time := reminder['recurrent_time']) is not False:
#                     reminder['next_time'] = now + to_timedelta(time)
#                 else:
#                     reminder['done'] = True
#
#                 await db.all_reminders.replace_one({'_id': reminder['_id']}, reminder)
#


async def has_perms(ctx):  # Check that a user has one of the roles to manage the bot
    for b in ctx.author.roles:
        if b.id in RJD["perms"]:
            return True

# Slash commands don't have a message object
    try:
        name = ctx.message.author.display_name
    except:
        name = ctx.author.display_name
    try:
        icon = ctx.message.author.avatar_url
    except:
        icon = ctx.author.avatar_url
    embed = discord.Embed(title="We ran into an error",
                          description="You don't have permissions to manage this bot's functions",
                          color=discord.Color.red())
    embed.set_footer(text=f"Caused by {name}", icon_url=icon)
    await ctx.send(embed=embed)
    return False

bot.guild_ids = []  # Bypass stupid hour+ waiting time for global commands


@bot.event
async def on_ready():
    if config("DEBUG") == "False":
        await discord.utils.get(bot.get_all_members(), id=bot.user.id).edit(nick="prism bot peace be upon him")
        debugStatus = "normal"
    else:
        await discord.utils.get(bot.get_all_members(), id=bot.user.id).edit(nick="prism bot testing be his job")
        debugStatus = "debug"
    print(f"╔═══════════════════════════════════════════════════")
    print(f"╠Bot is ready")
    print(f"╠{bot.user.name} running in {debugStatus} mode")
    print(f"╠Discord API Version: {discord.__version__}")
    print(f"╠═Guilds:")
    for guild in bot.guilds:  # Print list of current guildsPreparedRequest
        bot.guild_ids.append(guild.id)
        print(f"╠════{guild.name} ({guild.id})")
    print(f"╚═══════════════════════════════════════════════════")
    global RJD, RolesJson
    TestingZone = bot.get_guild(int(config('guild_id')))
    try:
        RolesJson = open(filename, "r+")
    except:
        RolesJson = open(filename, "w+")
        json.dump({"perms": [], "roles": []}, RolesJson)
        RolesJson.seek(0)
    RJD = json.load(RolesJson)
    RolesJson.seek(0)
    for role in RJD["roles"]:
        for member in RJD[role[0]]:
            if member[1] <= time.time():
                try:
                    await TestingZone.get_member(member[0]).remove_roles(TestingZone.get_role(int(role[0])),
                                                                         reason="expired")
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


@bot.event
async def on_component(ctx: ComponentContext):
    if ctx.custom_id == "gimme-roles":
        for role in ctx.selected_options:
            roles = discord.utils.get(ctx.guild.roles, id=int(role))
            await ctx.author.add_roles(roles)
        # This definitely looks like shit, but it works really goodly
        rolestr = str(ctx.selected_options).replace(" '", "<@&").replace("',", "> ").replace("']", "> ").replace("['", "<@&")
        await ctx.edit_origin(content=f"Added you to {rolestr}", hidden=True, components=None)
    if ctx.custom_id == "take-me-roles":
        for role in ctx.selected_options:
            roles = discord.utils.get(ctx.guild.roles, id=int(role))
            await ctx.author.remove_roles(roles)
        # This definitely looks like shit, but it works really goodly
        rolestr = str(ctx.selected_options).replace(" '", "<@&").replace("',", "> ").replace("']", "> ").replace(
            "['", "<@&")
        await ctx.edit_origin(content=f"Removed you from {rolestr}", hidden=True, components=None)


@bot.event
async def on_member_update(before, after):
    if before.guild.id == 858547359804555264:
        if before.display_name != after.display_name:
            embed = discord.Embed(title=f"Changed Name")
            embed.add_field(name='User', value=before.mention)
            embed.add_field(name='Before', value=before.display_name)
            embed.add_field(name='After', value=after.display_name)
            embed.set_thumbnail(url=after.avatar_url)
            channel = bot.get_channel(897765157940396052)
            await channel.send(embed=embed)


@bot.command(description="Allows Bored to evaluate code", category="Owner Only")
@is_owner()
async def eval(ctx, *, code):
    async with ctx.typing():
        str_obj = io.StringIO()  # Retrieves a stream of data
        try:
            with contextlib.redirect_stdout(str_obj):
                exec(code)
        except Exception as e:
            return await ctx.send(f"```{e.__class__.__name__}: {e}```")
        output = str_obj.getvalue()
        if len(output) < 1:
            output = "There was no output"
        await ctx.send(f'```py\n{output}```')


@slash.slash(name="ip",
             guild_ids=bot.guild_ids,
             description="Displays information on the given IP",
             options=[
                 create_option(
                     name="address",
                     description="The IP address you want to check",
                     option_type=option_type['string'],
                     required=True
                 )
             ])
async def ip(ctx: SlashContext, address=None):
    if address is None:
        embed = discord.Embed(title="We ran into an error", description="You forgot to add an IP",
                              color=discord.Color.red())
        embed.set_footer(text=f"Caused by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        return

    try:
        ip_address = ipaddress.ip_address(address)  # This will return an error if it's not a valid IP. Saves me doing input validation
        message = await ctx.send("https://cdn.discordapp.com/emojis/783447587940073522.gif")
        os.system(f"nmap  {address} -oG nmap.grep")
        process = subprocess.Popen(['./nmap.sh'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        three = stdout.decode('utf-8').replace('///', '')
        two = three.replace('//', ' ')
        one = two.replace('/', ' ').replace('      1 ', '')
        url = 'https://neutrinoapi.net/ip-info'
        params = {
            'user-id': config("NaughtyBoy_user"),
            'api-key': config("NaughtyBoy_key"),
            'ip': address,
            'reverse-lookup': True
        }
        postdata = parse.urlencode(params).encode()
        req = request.Request(url, data=postdata)
        response = request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))
        url = 'https://neutrinoapi.net/ip-probe'
        params = {
            'user-id': config("NaughtyBoy_user"),
            'api-key': config("NaughtyBoy_key"),
            'ip': address,
            'reverse-lookup': True
        }
        postdata = parse.urlencode(params).encode()
        req = request.Request(url, data=postdata)
        response = request.urlopen(req)
        probe = json.loads(response.read().decode("utf-8"))
        embed = discord.Embed(title="IP lookup", description=f"Lookup details for {address}",
                              color=discord.Color.green())
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        state = ""
        embed.add_field(name="Location", value=f"{result['city']}, {state[1]}\n{result['region']}, {result['country']}", inline=True)
        if not result['hostname'] == '':
            embed.add_field(name="Hostname", value=str(result['hostname']), inline=True)
        if not result['host-domain'] == '':
            embed.add_field(name="Host Domain", value=str(result['host-domain']), inline=True)
        embed.add_field(name="Maps Link", value=f"https://maps.google.com/?q={result['latitude']},{result['longitude']}", inline=True)
        embed.add_field(name="Provider", value=f"{probe['provider-description']}", inline=True)
        if probe['is-vpn']:
            embed.add_field(name="Is VPN?", value=f"Yes {probe['vpn-domain']}", inline=True)
        elif not probe['is-vpn']:
            embed.add_field(name="Is VPN?", value=f"No", inline=True)
        if probe['is-hosting']:
            embed.add_field(name="Is Hosting?", value=f"Yes {probe['vpn-domain']}", inline=True)
        elif not probe['is-hosting']:
            embed.add_field(name="Is Hosting?", value=f"No", inline=True)
        if len(one) < 3:
            one = None
        embed.add_field(name="Nmap Results", value=f"```py\n{one}\n```", inline=False)
        await message.edit(embed=embed, content="")
        print(probe)
    except ValueError:
        embed = discord.Embed(title="We ran into an error", description="That isn't a valid IP",
                              color=discord.Color.red())
        embed.set_footer(text=f"Caused by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


@bot.command(description="Displays information on the given IP", category="Utility")
async def ip(ctx, ip=None):
    if ip is None:
        embed = discord.Embed(title="We ran into an error", description="You forgot to add an IP",
                              color=discord.Color.red())
        embed.set_footer(text=f"Caused by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        return

    try:
        ip_address = ipaddress.ip_address(ip)
        message = await ctx.send("https://cdn.discordapp.com/emojis/783447587940073522.gif")
        os.system(f"nmap  {ip} -oG nmap.grep")
        process = subprocess.Popen(['./nmap.sh'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        three = stdout.decode('utf-8').replace('///', '')
        two = three.replace('//', ' ')
        one = two.replace('/', ' ').replace('      1 ', '')
        url = 'https://neutrinoapi.net/ip-info'
        params = {
            'user-id': config("NaughtyBoy_user"),
            'api-key': config("NaughtyBoy_key"),
            'ip': ip,
            'reverse-lookup': True
        }
        postdata = parse.urlencode(params).encode()
        req = request.Request(url, data=postdata)
        response = request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))
        url = 'https://neutrinoapi.net/ip-probe'
        params = {
            'user-id': config("NaughtyBoy_user"),
            'api-key': config("NaughtyBoy_key"),
            'ip': ip,
            'reverse-lookup': True
        }
        postdata = parse.urlencode(params).encode()
        req = request.Request(url, data=postdata)
        response = request.urlopen(req)
        probe = json.loads(response.read().decode("utf-8"))
        embed = discord.Embed(title="IP lookup", description=f"Lookup details for {ip}",
                              color=discord.Color.green())
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        state = ""
        embed.add_field(name="Location", value=f"{result['city']}, {state[1]}\n{result['region']}, {result['country']}", inline=True)
        if not result['hostname'] == '':
            embed.add_field(name="Hostname", value=str(result['hostname']), inline=True)
        if not result['host-domain'] == '':
            embed.add_field(name="Host Domain", value=str(result['host-domain']), inline=True)
        embed.add_field(name="Maps Link", value=f"https://maps.google.com/?q={result['latitude']},{result['longitude']}", inline=True)
        embed.add_field(name="Provider", value=f"{probe['provider-description']}", inline=True)
        if probe['is-vpn']:
            embed.add_field(name="Is VPN?", value=f"Yes {probe['vpn-domain']}", inline=True)
        elif not probe['is-vpn']:
            embed.add_field(name="Is VPN?", value=f"No", inline=True)
        if probe['is-hosting']:
            embed.add_field(name="Is Hosting?", value=f"Yes {probe['vpn-domain']}", inline=True)
        elif not probe['is-hosting']:
            embed.add_field(name="Is Hosting?", value=f"No", inline=True)
        if len(one) < 3:
            one = None
        embed.add_field(name="Nmap Results", value=f"```py\n{one}\n```", inline=False)
        await message.edit(embed=embed, content="")
        print(probe)
    except ValueError:
        embed = discord.Embed(title="We ran into an error", description="That isn't a valid IP",
                              color=discord.Color.red())
        embed.set_footer(text=f"Caused by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


@slash.slash(name="gimme-roles",
             guild_ids=bot.guild_ids,
             description="Give yourself some roles",
)
async def roles(ctx: SlashContext):
    select = create_select(
    options=[
    create_select_option("Random Gang", value="893284269798068305"),
    create_select_option("Other pronouns/ask me", value="866455940958126091"),
    create_select_option("One/ones", value="866460688583229492"),
    create_select_option("He/Him", value="866455665357881364"),
    create_select_option("She/Her", value="866455537234477095"),
    create_select_option("They/Them", value="866455786988765194"),
    create_select_option("It/its", value="866460549680332810"),
    create_select_option("Among us gang", value="891046340996530256"),
    create_select_option("Jackbox gang", value="863916385268400158"),
    create_select_option("There be dungeons and dragons", value="861365982803132456"),
    create_select_option("Movie gang", value="860624643449946153"),
    create_select_option("Announcement gang", value="866471817450356737"),
    create_select_option("Shush the bot pings", value="920459523947364373")

    ],
    custom_id="gimme-roles",
    placeholder="Choose your roles",
    min_values=1,
    max_values=13
    )
    await ctx.send("Role selection", components=[create_actionrow(select)], hidden=True)


@slash.slash(name="take-me-roles",
             guild_ids=bot.guild_ids,
             description="Remove roles from yourself",
)
async def roles(ctx: SlashContext):
    select = create_select(
    options=[
    create_select_option("Random Gang", value="893284269798068305"),
    create_select_option("Other pronouns/ask me", value="866455940958126091"),
    create_select_option("One/ones", value="866460688583229492"),
    create_select_option("He/Him", value="866455665357881364"),
    create_select_option("She/Her", value="866455537234477095"),
    create_select_option("They/Them", value="866455786988765194"),
    create_select_option("It/its", value="866460549680332810"),
    create_select_option("Among us gang", value="891046340996530256"),
    create_select_option("Jackbox gang", value="863916385268400158"),
    create_select_option("There be dungeons and dragons", value="861365982803132456"),
    create_select_option("Movie gang", value="860624643449946153"),
    create_select_option("Announcement gang", value="866471817450356737"),
    create_select_option("Shush the bot pings", value="920459523947364373")

    ],
    custom_id="take-me-roles",
    placeholder="Choose the roles you no longer want",
    min_values=1,
    max_values=13
    )
    await ctx.send("Role selection", components=[create_actionrow(select)], hidden=True)


@bot.command(description="Sends some info on what the self roles are", category="Utility")
async def rolehelp(ctx):
    embed = discord.Embed(title="How to assign your roles",
                          description="Simply type /gimme-roles in any text channel to grab some roles, you can select more than one and can also choose your preferred pronouns")
    embed.set_thumbnail(url='https://discordtemplates.me/icon.png')
    embed.add_field(name="D&D gang", value="We will ping you when we're going to play D&D", inline=True)
    embed.add_field(name="Movie gang", value="Like to watch movies? We will ping you when it's movie time",
                    inline=True)
    embed.add_field(name="Announcement gang", value="Want to be pinged for non essential announcements?", inline=True)
    embed.add_field(name="Jackbox gang", value="Do you play Jackbox?", inline=True)
    embed.add_field(name="Among us gang", value="Feeling sus? Grab this role", inline=True)
    embed.add_field(name="Random gang",
                    value="Sometimes random events happen. Grab this role to be notified of them", inline=True)
    embed.add_field(name="Shush the bot pings",
                    value="Don't want to be pinged when you level up? Grab this role", inline=True)
    await ctx.send(embed=embed)


@bot.command(description="Sends the User's banner", category="Testing")
async def banner(ctx, member: discord.Member = None):
    await ctx.message.delete()
    if member is None:
        member = ctx.message.author
    req = PreparedRequest()
    users = await bot.http.request(discord.http.Route("GET", f"/users/{member.id}"))
    banner_id = users["banner"]
    # If statement because the user may not have a banner
    if not str(banner_id) == "None":
        banner_url = f"https://cdn.discordapp.com/banners/{member.id}/{banner_id}?size=1024"
        req.prepare_url(
        url='https://api.xzusfin.repl.co/card?',
        params={
            'avatar': str(member.avatar_url_as(format='png')),
            'middle': ' ',
            'name': str(member.name),
            'bottom': ' ',
            'text': member.color,
            'avatarborder': member.color,
            'avatarbackground': member.color,
            'background': banner_url
        }
        )
        await ctx.send(req.url)
    else:
        req.prepare_url(
        url='https://api.xzusfin.repl.co/card?',
        params={
            'avatar': str(member.avatar_url_as(format='png')),
            'middle': ' ',
            'name': str(member.name),
            'bottom': ' ',
            'text': '#CCCCCC',
            'avatarborder': '#CCCCCC',
            'avatarbackground': '#CCCCCC',
            'background': "https://cdnb.artstation.com/p/assets/images/images/013/535/601/large/supawit-oat-fin1.jpg"
        }
        )
        await ctx.send(req.url)


@bot.event
async def on_message(message):
    if "discord.com/channels" in message.content:
        try:
            message.delete()
            link = message.content.split('/')
            server_id = int(link[4])
            channel_id = int(link[5])
            msg_id = int(link[6])

            print(server_id, channel_id, msg_id)
            server = bot.get_guild(server_id)
            channel = server.get_channel(channel_id)
            quoted = await channel.fetch_message(msg_id)
            embed = discord.Embed(description=f"{quoted.content}", color=quoted.author.color)
            embed.set_author(name=f"{quoted.author.display_name} in #{quoted.channel.name}",
                             icon_url=quoted.author.avatar_url,
                             url=quoted.jump_url)
            embed.set_footer(text=f"Quoted by {message.author.display_name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        except:
            print("Not doing anything")

    # blacklist_channels = [907718985343197194]  # Don't listen to the message logger channel to avoid looping
    # if len(message.content) > 1500:
    #     if not message.channel.id in blacklist_channels:
    #         step = 1000
    #         for i in range(0, len(message.content), 1000):
    #             slice = message.content[i:step]
    #             step += 1000
    #             async with aiohttp.ClientSession() as session:
    #                 webhook = Webhook.from_url(config("LOG"), adapter=AsyncWebhookAdapter(session))
    #                 await webhook.send(
    #                     f"<#{message.channel.id}> {message.author.display_name} ({message.author.id}) sent: {slice}",
    #                     username=message.author.display_name, avatar_url=message.author.avatar_url)
    #
    # if message.channel.id in blacklist_channels:
    #     return
    # else:  # Otherwise do the logging thing
    #     async with aiohttp.ClientSession() as session:
    #         webhook = Webhook.from_url(config("LOG"), adapter=AsyncWebhookAdapter(session))
    #         await webhook.send(
    #             f"<#{message.channel.id}> {message.author.display_name} ({message.author.id}) sent: {message.content}",
    #             username=message.author.display_name, avatar_url=message.author.avatar_url)

    if message.author == bot.user:  # Don't listen to yourself
        return
    if "https://discord.gift/" in message.content.lower():  # Some dumbass sent free nitro
        await message.channel.send(":warning: FREE NITRO! :warning:\nThis link appears to be legitimate :D")
        return
    if not message.guild:  # If message not in a guild it must be a DM
        if not message.author == bot.user:  # Don't listen to yourself
            message_filtered = str(message.content).replace('www', '').replace('http', '')  # No links pls
            url = 'https://neutrinoapi.net/bad-word-filter'  # Filter out bad boy words
            params = {
                'user-id': config("NaughtyBoy_user"),
                'api-key': config("NaughtyBoy_key"),
                'content': message_filtered,
                'censor-character': '•',
                'catalog': 'strict'
            }
            postdata = parse.urlencode(params).encode()
            req = request.Request(url, data=postdata)
            response = request.urlopen(req)
            result = json.loads(response.read().decode("utf-8"))
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(config("MOD"), adapter=AsyncWebhookAdapter(session))
                await webhook.send(
                    f"{result['censored-content']}",
                    username=f"{message.author.display_name} in DM", avatar_url=message.author.avatar_url)
    if str(bot.user.id) in message.content:
        reactions = ["<:iseeyou:876201272972304425>", "🇨", "🇦", "🇳", "▪️", "🇮", "◼️", "🇭", "🇪", "🇱", "🇵", "⬛", "🇾", "🇴", "🇺", "❓"]
        for reaction in reactions:
            await message.add_reaction(reaction)
    await bot.process_commands(message)  # Continue processing bot.commands


@slash.slash(name="list-members",
             guild_ids=bot.guild_ids,
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
    usernames = [m.display_name for m in role.members]
    count = 0
    for m in role.members:
        count += 1
    check_len = str(sorted(usernames,
                             key=str.lower)).replace(',', '\n').replace('[', '').replace(']', '').replace('\'', '')
    if len(check_len) > 2000:  # Ensure we don't go over the Discord embed limit
        title = f"**{count} members with the {role.name} role**"
        description = str(sorted(usernames,
                                 key=str.lower)).replace(',', '\n').replace('[', '').replace(']', '').replace('\'', '')
        await ctx.send(f"{title}\n{description}\n\n`List too long to be sent as an embed`")
    else:
        usernames = [m.mention for m in role.members]
        title = f"**{count} members with the {role.mention} role**"
        description = str(sorted(usernames,
                                 key=str.lower)).replace(',', '\n').replace('[', '').replace(']', '').replace('\'', '')
        embed = discord.Embed(description=f"{title}\n{description}", color=role.color)
        embed.set_footer(text=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


@bot.command(pass_context=True)
@check(has_perms)
async def purge(ctx, limit: int=None):
    if limit is None:
        await ctx.send("You didn't tell me how many messages to purge", delete_after=20)
        return
    await ctx.channel.purge(limit=limit)
    await ctx.send(f'Purged {limit} messages')
    mod_log = bot.get_channel(897765157940396052)
    title = f"Messages Purged"
    embed = discord.Embed(title=title,
                          color=ctx.message.author.color,
                          description=f"Purged {limit} messages from <#{ctx.channel.id}>")
    embed.set_footer(text=f"Discord name: {ctx.message.author.display_name}\nDiscord ID: {ctx.message.author.id}",
                     icon_url=ctx.message.author.avatar_url)
    await mod_log.send(embed=embed)


@purge.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You cant do that!")


@bot.command(description="Sends the welcome message in-case users need it again", category="Utility")
async def welcomemsg(ctx):
    # Send the welcome message
    title = "Welcome to Prism SMP!"
    description = """__General information__
                    "If you need anything or have a question of any sort, contact a <@&858547638719086613>. Your issue will then go as far as necessary up the ladder.
                    
                    You can grab some self roles over in <#861288424640348160>.
                    
                    The IP is in <#858549386962272296>: you don't have to read the entirety of that as it is a tad outdated and due a complete rewrite... it still can give you a rough idea of where we are coming from and can give you an idea of your rights as a Prismian.
                    
                    Ask in <#869280855657447445> to get yourself whitelisted.
                    
                    Have fun!
                    
                    __Rules__
                    ```Note: 
                    Use common sense and don't be a douche. There is more to "rules" than those written here. This is not meant as an exhaustive list. Listen to the staff```
                    
                    **1) Social**
                    1.1 Follow the [Discord ToS](https://discord.com/terms).
                    
                    1.2 No hate speech or harassment.
                    
                    1.3 Keep the server PG-13. Keep in mind some of our members might be younger than you. Set an example.
                    
                    1.4 Unwanted PvP (don't go around murdering people), stealing and griefing are severely punished.
                    
                    1.5 Don't spam in the discord or on the server.
                    
                    1.6 Respect player's claims and boundaries. Do not use farms without explicit permission. It is generally accepted to harvest crops for food and replant it unless the owner decides otherwise. If a sign says "keep out", keep out.
                    
                    **2) Technical**
                    2.1 Any unofficial application/mod/client giving you an advantage over other players are considered cheating and are strictly prohibited. In case of doubt, contact the staff.
                    
                    **3) Building**
                    3.1 Ask for permission from the players you want to settle nearby. 
                    
                    3.2 No building at less than 500 blocks from spawn (~x280 z230). The area around spawn is dedicated to community builds such as the Shopping District and the Mini-games District. Anything built there prior to this rule is safe to stay as long as their owners are Prism members.
                    
                    3.3 For Shopping District rules, see the pinned message in 🎙︱survival-adverts 
                    
                    3.4 Mega-projects are to be validated by staff: if you plan a build spanning more than 50 chunks please contact staff for approval prior to start building.
                    
                    3.5 Spawnproof anything you build on the Nether Roof.
                    
                    3.6 Consider lag when building farms. Examples: 
                    3.6.1 Put your villagers in minecart or on double carpets to disable their pathfinding AI
                    
                    3.6.2 Put composters on top of your unlocked hoppers to disable their "sucking" action and reduce their impact on the server. """

    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/890176674237399040/5716879890391b6204a71b05a77b2258.webp?size=1024")
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    embed = discord.Embed(title=f"**Error in command: {ctx.command}**", description=f"```\n{error}\n```", colour=discord.Color.red())
    await ctx.send(embed=embed)
    raise error


@bot.event
async def on_member_join(member):
    if member.guild.id == 858547359804555264:  # Only detect if the user joined the Prism guild
        if member.bot:  # Bloody bots
            return
        else:
            if time.time() - member.created_at.timestamp() < 2592000:
                # Send a message to the mods
                mod_log = bot.get_channel(897765157940396052)
                title = f"{member.display_name} is potentially suspicious"
                embed = discord.Embed(title=title, color=discord.Color.red())
                embed.set_footer(text=f"Discord name: {member.name}\nDiscord ID: {member.id}",
                                 icon_url=member.avatar_url)
                date_format = "%a, %d %b %Y %I:%M %p"
                embed.set_thumbnail(
                    url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/1200px-Warning.svg.png")
                embed.add_field(name="Joined Discord", value=member.created_at.strftime(date_format), inline=False)
                await mod_log.send(embed=embed)
            else:
                # Send a message to the mods
                mod_log = bot.get_channel(897765157940396052)
                title = f"{member.display_name} joined the server"
                embed = discord.Embed(title=title, color=discord.Color.green())
                embed.set_footer(text=f"Discord name: {member.name}\nDiscord ID: {member.id}", icon_url=member.avatar_url)
                date_format = "%a, %d %b %Y %I:%M %p"
                embed.add_field(name="Joined Discord", value=member.created_at.strftime(date_format), inline=False)
                await mod_log.send(embed=embed)
            # Send the welcome banner
            channel = bot.get_channel(858547359804555267)
            await channel.send("If you need anything from staff or simply have questions, ping a <@&858547638719086613>")
            req = PreparedRequest()
            users = await bot.http.request(discord.http.Route("GET", f"/users/{member.id}"))
            banner_id = users["banner"]
            # If statement because the user may not have a banner
            if not str(banner_id) == "None":
                banner_url = f"https://cdn.discordapp.com/banners/{member.id}/{banner_id}?size=1024"
                req.prepare_url(
                    url='https://api.xzusfin.repl.co/card?',
                    params={
                        'avatar': str(member.avatar_url_as(format='png')),
                        'middle': 'Everyone welcome',
                        'name': str(member.name),
                        'bottom': f'To {member.guild.name}',
                        'text': member.color,
                        'avatarborder': member.color,
                        'avatarbackground': member.color,
                        'background': banner_url
                    }
                )
                body = dict(parse_qsl(req.body))
                if 'code' in body:
                    print("Not sending a banner due to invalid response")
                    print(body)
                    print(req.url)
                else:
                    await channel.send(req.url)

            else:
                req.prepare_url(
                    url='https://api.xzusfin.repl.co/card?',
                    params={
                        'avatar': str(member.avatar_url_as(format='png')),
                        'middle': 'Everybody welcome',
                        'name': str(member.name),
                        'bottom': f'To {member.guild.name}',
                        'text': '#CCCCCC',
                        'avatarborder': '#CCCCCC',
                        'avatarbackground': '#CCCCCC',
                        'background': "https://cdnb.artstation.com/p/assets/images/images/013/535/601/large/supawit-oat-fin1.jpg"
                    }
                )
                body = dict(parse_qsl(req.body))
                if 'code' in body:
                    print("Not sending a banner due to invalid response")
                    print(body)
                    print(req.url)
                else:
                    await channel.send(req.url)

            # Give the user the New Member role
            role = discord.utils.get(member.guild.roles, name='New Member')
            await member.add_roles(role)


@bot.event
async def on_member_remove(member):
    if member.guild.id == 858547359804555264:  # Only detect if the user left the Prism guild
        if member.bot:
            return
        else:
            channel = bot.get_channel(897765157940396052)
            title = f"{member.display_name} left the server"
            embed = discord.Embed(title=title, color=discord.Color.red())
            embed.set_footer(text=f"Discord name: {member.name}\nDiscord ID: {member.id}", icon_url=member.avatar_url)
            date_format = "%a, %d %b %Y %I:%M %p"
            embed.set_author(name=str(member), icon_url=member.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="Joined Server", value=member.joined_at.strftime(date_format), inline=False)
            embed.add_field(name="Joined Discord", value=member.created_at.strftime(date_format), inline=False)
            embed.set_footer(text='ID: ' + str(member.id))
            await channel.send(embed=embed)


@bot.command(name='lp', pass_context=True, description="Adds to the permission changelog", category="Moderation")
@check(has_perms)
async def lp(ctx, *, message):
    await ctx.message.delete()
    changes = f"```diff\n{message} ```"
    embed = discord.Embed(title="Permission Changelog", description=changes, color=0x00ff40)
    embed.set_footer(text=f"Issued by {ctx.message.author.display_name}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name="embed",
             guild_ids=bot.guild_ids,
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
        embed.set_footer(text=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    await ctx.send("Embed sent", hidden=True)
    await channel.send(embed=embed)


@slash.slash(name="whitelist",
             guild_ids=bot.guild_ids,
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
    message = f"Added {member.mention} to the whitelist"
    embed = discord.Embed(description=message, color=ctx.author.color)
    embed.set_footer(text=f"Whitelisted by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    embed.set_author(name="📋 User added to whitelist")
    await channel.send(embed=embed)
    await ctx.send(embed=embed, hidden=True)


@bot.command(name='whitelist', pass_context=True, description="Adds a user to the whitelisted role", category="Moderation")
@check(has_perms)
async def whitelist(ctx, member: discord.Member):
    await ctx.message.delete()
    channel = bot.get_channel(869280855657447445)
    role = discord.utils.get(member.guild.roles, id=899568696593367070)
    await member.add_roles(role)
    message = f"Added {member.mention} to the whitelist"
    embed = discord.Embed(description=message, color=ctx.author.color)
    embed.set_footer(text=f"Whitelisted by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    embed.set_author(name="📋 User added to whitelist")
    await channel.send(embed=embed)


@slash.slash(name="edit-embed",
             guild_ids=bot.guild_ids,
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
        embed.set_footer(text=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    await ctx.send("Embed edited", hidden=True)
    editembed = embedlink.split('/')
    message = await bot.get_guild(int(editembed[-3])).get_channel(int(editembed[-2])).fetch_message(int(editembed[-1]))
    await message.edit(embed=newembed)


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
    years = int(secs // dyears)
    month = int((secs - years * dyears) // dmonth)
    weeks = int((secs - years * dyears - month * dmonth) // dweeks)
    days = int((secs - years * dyears - month * dmonth - weeks * dweeks) // ddays)
    hours = int((secs - years * dyears - month * dmonth - weeks * dweeks - days * ddays) // dhours)
    minutes = int((secs - years * dyears - month * dmonth - weeks * dweeks - days * ddays - hours * dhours) // dmins)
    seconds = int((secs - years * dyears - month * dmonth - weeks *
                   dweeks - days * ddays - hours * dhours - minutes * dmins) // 1)
    milliseconds = float(round(((
                                        secs - years * dyears - month * dmonth - weeks *
                                        dweeks - days * ddays - hours * dhours - minutes * dmins - seconds) * 1000),
                               3))
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



# Command to set a role to expire
@slash.slash(name="role-expire",
             guild_ids=bot.guild_ids,
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
    await ctx.send(
        f"✓ set {role.name} to expire {str(Duration(time)).replace('<Duration ', 'after ').replace('>', '')}")


@bot.command(description="Sets a role to expire", category="Moderation")
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
    await ctx.message.add_reaction("✓")


@slash.slash(name="role-unexpire",
             guild_ids=bot.guild_ids,
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
    await ctx.send(f"✓ set {role.name} to not expire")


@bot.command(description="Removes a role from expiration", category="Moderation")
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
    await ctx.message.add_reaction("✓")


@slash.slash(name="role-help",
             guild_ids=bot.guild_ids,
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
        value=f"_Sets a role to expire after a certain amount of time_\n\n"
              f"`/role-expire <role> <time>`\n(eg, /role-expire @examplerole 1m 12s)",
        inline=False
    )
    help_embed.add_field(
        name="role-unexpire",
        value=f"_Removes a role from the list of expiring roles_\n\n"
              f"`/role-unexpire <role>`\n(eg, /role-unexpire @examplerole2)",
        inline=False
    )
    help_embed.add_field(
        name="AddPerm",
        value=f"_Gives a role permissions to use this bot."
              f" You need to have `Manage Roles` Permissions to use this command._\n\n`/addperm <role>`",
        inline=False
    )
    help_embed.add_field(
        name="DelPerm",
        value=f"_Removes a role's permission to use this bot."
              f" You need to have `Manage Roles` Permissions to use this command._\n\n`/delperm <role>`",
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


@bot.command(name="role-help", description="Shows the role expiry settings help", category="Moderation")
async def _help(ctx: discord.ext.commands.Context):
    help_embed = discord.Embed(
        title=f"{bot_name} >> Help",
        description="Commands",
        colour=discord.Colour.blue()
    )
    help_embed.add_field(
        name="Expire",
        value=f"_Sets a role to expire after a certain amount of time_\n\n"
              f"`$expire <role> <time>`\n(eg, $expire @examplerole 1m 12s)",
        inline=False
    )
    help_embed.add_field(
        name="Unexpire",
        value=f"_Removes a role from the list of expiring roles_\n\n"
              f"`$unexpire <role>`\n(eg, $unexpire @examplerole2)",
        inline=False
    )
    help_embed.add_field(
        name="AddPerm",
        value=f"_Gives a role permissions to use this bot."
              f" You need to have `Manage Roles` Permissions to use this command._\n\n`$addperm <role>`",
        inline=False
    )
    help_embed.add_field(
        name="DelPerm",
        value=f"_Removes a role's permission to use this bot."
              f" You need to have `Manage Roles` Permissions to use this command._\n\n`$delperm <role>`",
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
             guild_ids=bot.guild_ids,
             description=f"Adds a role to manage {bot_name}",
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
        await ctx.send(f"✓ added {role.name} to the management team")
    else:
        await ctx.send("That role already has permissions!")


@bot.command(description="Adds a role to be allowed to manage the bot", category="Moderation")
@has_permissions(manage_roles=True)
async def addperm(ctx: Context, role: discord.Role):
    r = role.id
    if r not in RJD["perms"]:
        RJD["perms"].append(r)
        y = json.load(RolesJson)
        RolesJson.seek(0)
        y["perms"].append(r)
        jsondump(y)
        await ctx.send(f"✓ added {role.name} to the management team")
    else:
        await ctx.send("That role already has permissions!")


@slash.slash(name="delperm",
             guild_ids=bot.guild_ids,
             description=f"Removes a role from managing {bot_name}",
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
        await ctx.send(f"✓ removed {role.name} from the management role")
    else:
        await ctx.send("I don't think that role had permissions :confused:")


@bot.command(description="Removes a role from managing the bot", category="Moderation")
@has_permissions(manage_roles=True)
async def delperm(ctx: Context, role: discord.Role):
    r = role.id
    if r in RJD["perms"]:
        RJD["perms"].remove(r)
        y = json.load(RolesJson)
        RolesJson.seek(0)
        y["perms"].remove(r)
        jsondump(y)
        await ctx.send(f"✓ removed {role.name} from the management role")
    else:
        await ctx.send("I don't think that role had permissions :confused:")


@slash.slash(name="viewroles",
             guild_ids=bot.guild_ids,
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


@bot.command(description="Lists the roles that are set to expire", category="Moderation")
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
             guild_ids=bot.guild_ids,
             description=f"Views the roles allowed to manage {bot_name}")
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


@bot.command(description="Views the roles that are allowed to manage the bot", category="Moderation")
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
             guild_ids=bot.guild_ids,
             description=f"Checks {bot_name}'s ping")
async def ping(ctx):
    await ctx.send(f'My ping is {round((bot.latency * 1000), 3)} ms!')


@bot.command(description=f"Checks {bot_name}'s ping", category="")
async def ping(ctx):
    await ctx.send(f'My ping is {round((bot.latency * 1000), 3)} ms!')


@slash.context_menu(target=ContextMenuType.USER,
                    name="Who is this?",
                    guild_ids=bot.guild_ids)
async def my_new_command(ctx: MenuContext, user: discord.Member = None):
    user = ctx.target_author
    if user.activities:  # check if the user has an activity
        if str(user.activities[0].type) == "ActivityType.playing":
            activity = "Playing:"
        elif str(user.activities[0].type) == "ActivityType.streaming":
            activity = "Streaming:"
        elif str(user.activities[0].type) == "ActivityType.listening":
            activity = "Listening to:"
        elif str(user.activities[0].type) == "ActivityType.watching":
            activity = "Watching"
        elif str(user.activities[0].type) == "ActivityType.custom":
            activity = ""
        elif str(user.activities[0].type) == "ActivityType.competing":
            activity = "Competing in:"
        else:
            activity = "Funkiness"
        has_activity = True
    else:  # if they don't we can't reference it
        has_activity = False

    top_role = user.roles[-1]  # first element in roles is `@everyone` and last is top role
    embed = discord.Embed(color=top_role.color, description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar_url)
    if str(user.id) == "709089341007200288":  # FT :POGGERS:
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/861289278374150164/917731281503150090/"
                                "3ee9a6c54e15a2929d276cd9ba366442.gif")
    elif str(user.id) == "510748531926106113":  # Orang
        embed.set_thumbnail(url="https://c.tenor.com/aw-QZPYpGmkAAAAM/carrot-garden.gif")
    elif str(user.id) == "103523893834166272":  # Apo
        embed.set_thumbnail(url="https://thumbs.gfycat.com/FrayedUncommonGrosbeak-size_restricted.gif")
    elif str(user.id) == "690864077861421066":  # Alina
        embed.set_thumbnail(url="https://media4.giphy.com/media/QsTGfN7bYXUm4/200.gif")
    elif str(user.id) == "324504908013240330":  # ME!!!!!!!!111!!
        embed.set_thumbnail(url="https://64.media.tumblr.com/e12f4de9050b40e88d76d396bd848c08/"
                                "tumblr_oi94oaK9Wl1rcqnnxo1_r1_400.gifv")
    else:
        embed.set_thumbnail(url=user.avatar_url)
    if has_activity:
        try:
            if str(user.activities[0].details) == "None":
                embed.add_field(name="Current Activity",
                                value=f"{activity} {user.activities[0].name}", inline=False)
            else:
                embed.add_field(name="Current Activity",
                                value=f"{activity} {user.activities[0].name} | {user.activities[0].details}",
                                inline=False)
        except:
            embed.add_field(name="Current Activity",
                            value=f"{activity} {user.activities[0].name}", inline=False)
    joined_time = str((user.joined_at - datetime(1970, 1, 1)).total_seconds()).split('.')
    discord_joined_time = str((user.created_at - datetime(1970, 1, 1)).total_seconds()).split('.')

    embed.add_field(name="Joined Server", value=f"<t:{joined_time[0]}:R>", inline=False)
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(name="Join Position", value=str(members.index(user) + 1), inline=False)
    embed.add_field(name="Joined Discord", value=f"<t:{discord_joined_time[0]}:R>", inline=False)
    if len(user.roles) > 1:
        role_string = ' '.join([r.mention for r in user.roles][1:])
        embed.add_field(name="Roles [{}]".format(len(user.roles) - 1), value=role_string, inline=False)
    embed.set_footer(text='ID: ' + str(user.id))
    return await ctx.send(embed=embed, hidden=True)


@slash.slash(name="whois",
             guild_ids=bot.guild_ids,
             description="Shows some info on users",
             options=[
                 create_option(
                     name="user",
                     description="The user to lookup",
                     option_type=option_type["user"],
                     required=False
                 )]
             )
async def whois(ctx: Context, *, user: discord.Member = None):
    if user is None:
        user = ctx.guild.get_member(ctx.author.id)
    if user.activities:  # check if the user has an activity
        if str(user.activities[0].type) == "ActivityType.playing":
            activity = "Playing:"
        elif str(user.activities[0].type) == "ActivityType.streaming":
            activity = "Streaming:"
        elif str(user.activities[0].type) == "ActivityType.listening":
            activity = "Listening to:"
        elif str(user.activities[0].type) == "ActivityType.watching":
            activity = "Watching"
        elif str(user.activities[0].type) == "ActivityType.custom":
            activity = ""
        elif str(user.activities[0].type) == "ActivityType.competing":
            activity = "Competing in:"
        else:
            activity = "Funkiness"
        has_activity = True
    else:  # if they don't we can't reference it
        has_activity = False
    if user.status.name == "online":
        statusemoji = "\N{LARGE GREEN CIRCLE}"
        status = "Online"
    elif user.status.name == "offline":
        statusemoji = "\N{MEDIUM WHITE CIRCLE}\N{VARIATION SELECTOR-16}"
        status = "Offline"
    elif user.status.name == "dnd":
        statusemoji = "\N{LARGE RED CIRCLE}"
        status = "Do not disturb"
    elif user.status.name == "idle":
        statusemoji = "\N{LARGE ORANGE CIRCLE}"
        status = "Idling"
    else:  # just in case some funky shit is going on
        statusemoji = "\N{LARGE PURPLE CIRCLE}"
        status = ""
    top_role = user.roles[-1]  # first element in roles is `@everyone` and last is top role
    embed = discord.Embed(color=top_role.color, description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar_url)
    if str(user.id) == "709089341007200288":  # FT :POGGERS:
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/861289278374150164/917731281503150090/"
                                "3ee9a6c54e15a2929d276cd9ba366442.gif")
    elif str(user.id) == "510748531926106113":  # Orang
        embed.set_thumbnail(url="https://c.tenor.com/aw-QZPYpGmkAAAAM/carrot-garden.gif")
    elif str(user.id) == "103523893834166272":  # Apo
        embed.set_thumbnail(url="https://thumbs.gfycat.com/FrayedUncommonGrosbeak-size_restricted.gif")
    elif str(user.id) == "690864077861421066":  # Alina
        embed.set_thumbnail(url="https://media4.giphy.com/media/QsTGfN7bYXUm4/200.gif")
    elif str(user.id) == "324504908013240330":  # ME!!!!!!!!111!!
        embed.set_thumbnail(url="https://64.media.tumblr.com/e12f4de9050b40e88d76d396bd848c08/"
                                "tumblr_oi94oaK9Wl1rcqnnxo1_r1_400.gifv")
    else:
        embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="Current Status", value=f"{statusemoji} | {status}", inline=False)
    if has_activity:
        try:
            if str(user.activities[0].details) == "None":
                embed.add_field(name="Current Activity",
                                value=f"{activity} {user.activities[0].name}", inline=False)
            else:
                embed.add_field(name="Current Activity",
                                value=f"{activity} {user.activities[0].name} | {user.activities[0].details}",
                                inline=False)
        except:
            embed.add_field(name="Current Activity",
                            value=f"{activity} {user.activities[0].name}", inline=False)
    joined_time = str((user.joined_at - datetime(1970, 1, 1)).total_seconds()).split('.')
    discord_joined_time = str((user.created_at - datetime(1970, 1, 1)).total_seconds()).split('.')

    embed.add_field(name="Joined Server", value=f"<t:{joined_time[0]}:R>", inline=False)
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(name="Join Position", value=str(members.index(user) + 1), inline=False)
    embed.add_field(name="Joined Discord", value=f"<t:{discord_joined_time[0]}:R>", inline=False)
    if len(user.roles) > 1:
        role_string = ' '.join([r.mention for r in user.roles][1:])
        embed.add_field(name="Roles [{}]".format(len(user.roles) - 1), value=role_string, inline=False)
    embed.set_footer(text='ID: ' + str(user.id))
    return await ctx.send(embed=embed)


@bot.command(description="Shows some info on users", category="Utility")
async def whois(ctx, *, user: discord.Member = None):
    if user is None:
        user = ctx.guild.get_member(ctx.author.id)
    if user.activities:  # check if the user has an activity
        if str(user.activities[0].type) == "ActivityType.playing":
            activity = "Playing:"
        elif str(user.activities[0].type) == "ActivityType.streaming":
            activity = "Streaming:"
        elif str(user.activities[0].type) == "ActivityType.listening":
            activity = "Listening to:"
        elif str(user.activities[0].type) == "ActivityType.watching":
            activity = "Watching"
        elif str(user.activities[0].type) == "ActivityType.custom":
            activity = ""
        elif str(user.activities[0].type) == "ActivityType.competing":
            activity = "Competing in:"
        else:
            activity = "Funkiness"
        has_activity = True
    else:  # if they don't we can't reference it
        has_activity = False
    if user.status.name == "online":
        statusemoji = "\N{LARGE GREEN CIRCLE}"
        status = "Online"
    elif user.status.name == "offline":
        statusemoji = "\N{MEDIUM WHITE CIRCLE}\N{VARIATION SELECTOR-16}"
        status = "Offline"
    elif user.status.name == "dnd":
        statusemoji = "\N{LARGE RED CIRCLE}"
        status = "Do not disturb"
    elif user.status.name == "idle":
        statusemoji = "\N{LARGE ORANGE CIRCLE}"
        status = "Idling"
    else:  # just in case some funky shit is going on
        statusemoji = "\N{LARGE PURPLE CIRCLE}"
        status = ""
    top_role = user.roles[-1]  # first element in roles is `@everyone` and last is top role
    embed = discord.Embed(color=top_role.color, description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar_url)
    if str(user.id) == "709089341007200288":  # FT :POGGERS:
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/861289278374150164/917731281503150090/"
                                "3ee9a6c54e15a2929d276cd9ba366442.gif")
    elif str(user.id) == "510748531926106113":  # Orang
        embed.set_thumbnail(url="https://c.tenor.com/aw-QZPYpGmkAAAAM/carrot-garden.gif")
    elif str(user.id) == "103523893834166272":  # Apo
        embed.set_thumbnail(url="https://thumbs.gfycat.com/FrayedUncommonGrosbeak-size_restricted.gif")
    elif str(user.id) == "690864077861421066":  # Alina
        embed.set_thumbnail(url="https://media4.giphy.com/media/QsTGfN7bYXUm4/200.gif")
    elif str(user.id) == "324504908013240330":  # ME!!!!!!!!111!!
        embed.set_thumbnail(url="https://64.media.tumblr.com/e12f4de9050b40e88d76d396bd848c08/"
                                "tumblr_oi94oaK9Wl1rcqnnxo1_r1_400.gifv")
    else:
        embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="Current Status", value=f"{statusemoji} | {status}", inline=False)
    if has_activity:
        try:
            if str(user.activities[0].details) == "None":
                embed.add_field(name="Current Activity",
                                value=f"{activity} {user.activities[0].name}", inline=False)
            else:
                embed.add_field(name="Current Activity",
                                value=f"{activity} {user.activities[0].name} | {user.activities[0].details}",
                                inline=False)
        except:
            embed.add_field(name="Current Activity",
                            value=f"{activity} {user.activities[0].name}", inline=False)
    joined_time = str((user.joined_at - datetime(1970, 1, 1)).total_seconds()).split('.')
    discord_joined_time = str((user.created_at - datetime(1970, 1, 1)).total_seconds()).split('.')

    embed.add_field(name="Joined Server", value=f"<t:{joined_time[0]}:R>", inline=False)
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(name="Join Position", value=str(members.index(user) + 1), inline=False)
    embed.add_field(name="Joined Discord", value=f"<t:{discord_joined_time[0]}:R>", inline=False)
    if len(user.roles) > 1:
        role_string = ' '.join([r.mention for r in user.roles][1:])
        embed.add_field(name="Roles [{}]".format(len(user.roles) - 1), value=role_string, inline=False)
    embed.set_footer(text='ID: ' + str(user.id))
    return await ctx.send(embed=embed)


@slash.slash(name="doggo",
             guild_ids=bot.guild_ids,
             description="Sends a photo of a doggo")
async def doggo(ctx: Context):
    f = r"https://random.dog/woof.json"
    page = requests.get(f)
    data = json.loads(page.text)
    await ctx.send(data["url"])


@slash.slash(name="catto",
             guild_ids=bot.guild_ids,
             description="Sends a photo of a catto")
async def catto(ctx: Context):
    f = r"https://aws.random.cat/meow"
    page = requests.get(f)
    data = json.loads(page.text)
    await ctx.send(data["file"])


@bot.command(name='auth', pass_context=True, description="Checks the validity of a token", category="Utility")
async def auth(ctx, message):
    nonce = "SuperSecretNonce"
    f = f"https://api2.yubico.com/wsapi/2.0/verify?id=1&otp={message}&nonce={nonce}"
    page = requests.get(f)
    if config('yubi_key') in message:
        if nonce in page.text:
            if "status=OK" in page.text:
                await ctx.message.add_reaction('🔓')
                log = f"<p class=\"white\">Authenticated"

                with open("messages.log", "a", encoding="utf8") as text_file:
                    print(log, file=text_file)
            elif "status=REPLAYED_REQUEST" in page.text:
                await ctx.message.add_reaction('❌')
                log = f"<p class=\"white\">Replayed OTP"
                with open("messages.log", "a", encoding="utf8") as text_file:
                    print(log, file=text_file)
            elif "status=BAD_OTP" in page.text:
                await ctx.message.add_reaction('❌')
                log = f"<p class=\"white\">OTP was invalid"
                with open("messages.log", "a", encoding="utf8") as text_file:
                    print(log, file=text_file)
            else:
                log = f"<p class=\"white\">Recieved an invalid nonce"
                with open("messages.log", "a", encoding="utf8") as text_file:
                    print(log, file=text_file)
                return
        else:
            await ctx.send("Something funky is going on")
    else:
        await ctx.send("Something funky is going on")


@slash.slash(name="arrest",
             guild_ids=bot.guild_ids,
             description="Arrests a member",
             options=[
                 create_option(
                     name="user",
                     description="The user to arrest",
                     option_type=option_type["user"],
                     required=True
                 ), create_option(
                     name="reason",
                     description="The reason for the arrest",
                     option_type=option_type["string"],
                     required=True
                 )]
             )
@check(has_perms)
async def arrest(ctx: SlashContext, user, reason):
    await ctx.send(f"{user.mention} has been arrested. Please wait for the permissions to be changed\n"
                   f" This shouldn't be more than a minute", hidden=True)
    mod_log = bot.get_channel(897765157940396052)
    police_station = bot.get_channel(866304038524813352)
    whitelist = discord.utils.get(ctx.guild.roles, name='Whitelisted')
    await user.remove_roles(whitelist)
    arrestee = discord.utils.get(ctx.guild.roles, name='Arrestee')
    for member in ctx.guild.members:
        if arrestee in member.roles:
            member.remove_roles(arrestee)
    await user.add_roles(arrestee)
    await police_station.purge(limit=int(10000))
    await police_station.set_permissions(discord.utils.get(ctx.guild.roles, name="Arrestee"), send_messages=True,
                                         read_messages=True, reason=reason)
    await police_station.set_permissions(discord.utils.get(ctx.guild.roles, name="Moderator"), send_messages=True,
                                         read_messages=True, reason=reason)
    await police_station.set_permissions(discord.utils.get(ctx.guild.roles, name="Administrator"), send_messages=True,
                                         read_messages=True, reason=reason)
    await police_station.set_permissions(discord.utils.get(ctx.guild.roles, name="Adjudicator"), send_messages=True,
                                         read_messages=True, reason=reason)

    await mod_log.send(f'{ctx.author.display_name} cleared the <#866304038524813352> chat and arrested '
                       f'{user.display_name} for {reason}')
    await police_station.send(f"{user.mention} you have been arrested by {ctx.author.mention} for "
                              f"{reason}. Please stand-by")


@slash.slash(name="release",
             guild_ids=bot.guild_ids,
             description="Releases a member from police custody",
             options=[
                 create_option(
                     name="user",
                     description="The user to release",
                     option_type=option_type["user"],
                     required=True
                 ), create_option(
                     name="reason",
                     description="The reason for releasing",
                     option_type=option_type["string"],
                     required=True
                 )]
             )
@check(has_perms)
async def release(ctx: SlashContext, user, reason):
    await ctx.send(f"{user.mention} has been released")
    sentences_log = bot.get_channel(875356199174938644)
    police_station = bot.get_channel(866304038524813352)
    await sentences_log.send(f'{ctx.author.display_name} released {user.display_name} from police custody for {reason}'
                             f'\n{ctx.author.mention} please don\'t forget to fill out the sentence here')
    arrestee = discord.utils.get(ctx.guild.roles, name='Arrestee')
    await user.remove_roles(arrestee)
    await police_station.set_permissions(discord.utils.get(ctx.guild.roles, name="Arrestee"), send_messages=False,
                                         read_messages=False, reason=reason)
    await police_station.set_permissions(discord.utils.get(ctx.guild.roles, name="Moderator"), send_messages=True,
                                         read_messages=True, reason=reason)
    await police_station.set_permissions(discord.utils.get(ctx.guild.roles, name="Administrator"), send_messages=True,
                                         read_messages=True, reason=reason)
    await police_station.set_permissions(discord.utils.get(ctx.guild.roles, name="Adjudicator"), send_messages=True,
                                         read_messages=True, reason=reason)


@slash.slash(name="kill",
             guild_ids=bot.guild_ids,
             description=f"Kills {bot_name}")
@is_owner()
async def kill(ctx: Context):
    await ctx.send("https://c.tenor.com/huJuK_zUxSAAAAAM/im-dying-jake.gif")
    sys.exit()


@bot.command(description="Kills any instance of the bot", category="Owner Only")
@is_owner()
async def kill(ctx: Context):
    await ctx.send("https://c.tenor.com/huJuK_zUxSAAAAAM/im-dying-jake.gif")
    sys.exit()


@bot.command(description="Lists all the guilds emojis", category="Owner Only")
@is_owner()
async def emojilist(ctx):
    await ctx.message.delete()
    for emoji in ctx.guild.emojis:
        creation = str((emoji.created_at - datetime(1970, 1, 1)).total_seconds()).split('.')
        await ctx.send(f"{emoji} {emoji.name} ({emoji.id}) Created: <t:{creation[0]}:R>")


bot.run(toe_ken)
