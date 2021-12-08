# Holy shit, that's a lot of imports
from urllib import parse, request
import aiohttp
import discord.ext
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
from decouple import config
from discord_slash import SlashCommand, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component
import requests
import discord
import json
from durations import Duration
import time
from discord.ext.commands import *
import sys
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
from discord import NotFound
from discord.ext import commands, tasks
from dpytools.menus import multichoice
from dpytools.parsers import to_timedelta, Trimmer
from database import db

# Setup the bot
intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix='$', intents=intents, case_insensitive=True)
bot.remove_command('help')
toe_ken = config('TOKEN')
slash = SlashCommand(bot, sync_commands=True)


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
    print(f"╔═══════════════════════════════════════════════════")
    print(f"╠Bot is ready")
    print(f"╠{bot_name}")
    print(f"╠Discord API Version: {discord.__version__}")
    print(f"╠═Guilds:")
    for guild in bot.guilds:  # Print list of current guilds
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
async def on_message(message):
    blacklist_channels = [907718985343197194]  # Don't listen to the message logger channel to avoid looping
    if message.channel.id in blacklist_channels:
        return
    else:  # Otherwise do the logging thing
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(config("LOG"), adapter=AsyncWebhookAdapter(session))
            await webhook.send(
                f"<#{message.channel.id}> {message.author.display_name} ({message.author.id}) sent: {message.content}",
                username=message.author.display_name, avatar_url=message.author.avatar_url)

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


@bot.command(name='buttontest', pass_context=True)
@check(has_perms)
async def buttontest(ctx):
    buttons = [
        create_button(style=ButtonStyle.green, label="A green button"),
        create_button(style=ButtonStyle.blue, label="A blue button")
    ]
    action_row = create_actionrow(*buttons)

    await ctx.send("Hello Friendo", components=[action_row])
    # note: this will only catch one button press, if you want more, put this in a loop
    button_ctx: ComponentContext = await wait_for_component(bot, components=action_row)
    await button_ctx.edit_origin(content="You pressed a button!, I am unsure how to detect which button though")


@bot.event
async def on_command_error(ctx, error):
    print(error)
    try:
        name = ctx.message.author.display_name
    except AttributeError:
        name = ctx.author.display_name
    try:
        icon = ctx.message.author.avatar_url
    except AttributeError:
        icon = ctx.author.avatar_url
    if isinstance(error, commands.errors.CheckFailure):
        embed = discord.Embed(title="We ran into an error", description="You are not staff", color=discord.Color.red())
        embed.set_footer(text=f"Caused by {name}", icon_url=icon)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="We ran into an error", description="You forgot to define something",
                              color=discord.Color.red())
        embed.set_footer(text=f"Caused by {name}", icon_url=icon)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.BotMissingPermissions):
        embed = discord.Embed(title="We ran into an error", description="I am missing permissions",
                              color=discord.Color.red())
        embed.set_footer(text=f"Caused by {name}", icon_url=icon)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.CommandNotFound):
        try:
            print("Doing nothing since this command doesn't exist")
        except:
            return
    else:
        embed = discord.Embed(title="We ran into an undefined error", description=error, color=discord.Color.red())
        embed.set_footer(text=f"Caused by {name}", icon_url=icon)
        await ctx.send(embed=embed)


@bot.event
async def on_member_join(member):
    if member.guild.id == 858547359804555264:  # Only detect if the user joined the Prism guild
        if member.bot:  # Bloody bots
            return
        else:
            # Send a message to the mods
            mod_log = bot.get_channel(897765157940396052)
            title = f"{member.display_name} joined the server"
            embed = discord.Embed(title=title, color=discord.Color.green())
            embed.set_footer(text=f"Discord name: {member.name}\nDiscord ID: {member.id}", icon_url=member.avatar_url)
            date_format = "%a, %d %b %Y %I:%M %p"
            embed.add_field(name="Joined Discord", value=member.created_at.strftime(date_format), inline=False)
            await mod_log.send(embed=embed)
            # Send the welcome message
            channel = bot.get_channel(858547359804555267)
            title = "Welcome to Prism SMP!"
            description = "Please look at the <#861317568807829535> when you have a minute.\n\n" \
                          "You can grab some self roles over in <#861288424640348160>.\n" \
                          "Join the server at least once (the IP is in <#858549386962272296>" \
                          " [You don't have to read the entirety of that])" \
                          " then ask in <#869280855657447445> to get yourself whitelisted."
            embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
            embed.set_footer(text=member.name, icon_url=member.avatar_url)
            await channel.send(embed=embed)
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


@bot.command(name='lp', pass_context=True)
@check(has_perms)
async def lp(ctx, *, message):
    await ctx.message.delete()
    changes = f"```diff\n{message} ```"
    embed = discord.Embed(title="Permission Changelog", description=changes, color=0x00ff40)
    embed.set_footer(text=f"Issued by {ctx.message.author.display_name}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='game', aliases=['gamecommands', 'gc'], pass_context=True)
async def game(ctx):
    help = "**Discord Commands:** (can only be run in #in-game-chat)\n`/inv` Shows the contents of your inventory\n" \
           "`/ender` Shows the contents of your enderchest\n\n**In-game Commands**\n" \
           "`[ec]` Broadcasts the contents of your enderchest\n`[inv]` Broadcasts the contents of your inventory\n" \
           "`[item]` Broadcasts your currently held item\n`[pos]` Broadcasts your position\n" \
           "`[ping]` Catching on yet?\n`/t <message>` Shortcut for team message"
    embed = discord.Embed(title="Game Command Help", description=help, color=ctx.message.author.color)
    embed.set_footer(text=f"Issued by {ctx.message.author.display_name}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name="help",
             guild_ids=bot.guild_ids,
             description="displays the help")
async def help(ctx):
    help = f"**Hello Friendo!**\nI am {bot_name}. I'm designed to make your life here easier.\n" \
           "If you run into any issues please ping <@324504908013240330>"
    embed = discord.Embed(title="Help", description=help, color=ctx.author.color)
    embed.set_footer(text=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/icons/858547359804555264/34eacdf2f8da259c1bf88ba6cbf087c7.jpg")
    await ctx.send(embed=embed)


@slash.slash(name="game-commands",
             guild_ids=bot.guild_ids,
             description="displays the list of game commands")
async def game(ctx):
    help = "**Discord Commands:** (can only be run in #in-game-chat)\n`/inv` Shows the contents of your inventory\n" \
           "`/ender` Shows the contents of your enderchest\n\n**In-game Commands**\n" \
           "`[ec]` Broadcasts the contents of your enderchest\n`[inv]` Broadcasts the contents of your inventory\n" \
           "`[item]` Broadcasts your currently held item\n`[pos]` Broadcasts your position\n" \
           "`[ping]` Catching on yet?\n`/t <message>` Shortcut for team message"
    embed = discord.Embed(title="Game Command Help", description=help, color=ctx.author.color)
    embed.set_footer(text=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='commands', aliases=['pc', 'bc'], pass_context=True)
async def commands(ctx):
    help = "**User Commands:**\n`/iam` Allows you to choose roles\n`/iamnot` Removes those roles\n" \
           "`/reminder create` Kinda self-explanatory\n`/reminder view` See above\n" \
           "`/suggestion create` Creates a suggestion for the staff to review\n" \
           "`/spotify` Easily share what you're currently listening to\n`$play <song>` Plays music in your VC\n" \
           "`$skip` Skips your song"
    embed = discord.Embed(title=f"{bot_name} Command Help", description=help, color=ctx.message.author.color)
    embed.set_footer(text=f"Issued by {ctx.message.author.display_name}", icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name="commands",
             guild_ids=bot.guild_ids,
             description=f"displays the list of {bot_name} commands")
async def commands(ctx):
    help = "**User Commands:**\n`/iam` Allows you to choose roles\n`/iamnot` Removes those roles\n" \
           "`/reminder create` Kinda self-explanatory\n`/reminder view` See above\n" \
           "`/suggestion create` Creates a suggestion for the staff to review\n" \
           "`/spotify` Easily share what you're currently listening to\n`$play <song>` Plays music in your VC\n" \
           "`$skip` Skips your song"
    embed = discord.Embed(title=f"{bot_name} Command Help", description=help, color=ctx.author.color)
    embed.set_footer(text=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name="staff-commands",
             guild_ids=bot.guild_ids,
             description="displays the list of staff commands")
@check(has_perms)
async def staff(ctx):
    help = "**Staff Commands**\n" \
           "`/self-roles add` Adds a role to the `/iam` command\n`/self-roles remove` Does the opposite\n" \
           "`/poll` Creates a poll for people to vote on\n" \
           "`/suggestion view` A nifty menu for viewing suggestions\n" \
           "`$warn <user> <reason>` Warns the mentioned user for the stated reason\n" \
           "`$ban <user> <reason>` Bans the mentioned user for the stated reason\n" \
           "`/whitelist <mention discord user>` Whitelists the user\n" \
           "'/arrest <user> <reason>` Arrests the user\n" \
           "`/release <user> <reason>` Releases the user from police custody"
    embed = discord.Embed(title=f"{bot_name} Command Help", description=help, color=ctx.author.color)
    embed.set_footer(text=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='staff', aliases=['staffcommands', 'sc'], pass_context=True)
@check(has_perms)
async def staff(ctx: SlashContext):
    help = "**Staff Commands**\n" \
           "`/self-roles add` Adds a role to the `/iam` command\n`/self-roles remove` Does the opposite\n" \
           "`/poll` Creates a poll for people to vote on\n" \
           "`/suggestion view` A nifty menu for viewing suggestions\n" \
           "`$warn <user> <reason>` Warns the mentioned user for the stated reason\n" \
           "`$ban <user> <reason>` Bans the mentioned user for the stated reason\n" \
           "`/whitelist <mention discord user>` Whitelists the user\n" \
           "'/arrest <user> <reason>` Arrests the user\n" \
           "`/release <user> <reason>` Releases the user from police custody"
    embed = discord.Embed(title=f"{bot_name} Command Help", description=help, color=ctx.message.author.color)
    embed.set_footer(text=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
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


@bot.command(name='whitelist', pass_context=True)
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


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
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


@bot.command(name="role-help")
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
             guild_ids=bot.guild_ids,
             description=f"Checks {bot_name}'s ping")
async def ping(ctx):
    await ctx.send(f'My ping is {round((bot.latency * 1000), 3)} ms!')


@bot.command()
async def ping(ctx):
    await ctx.send(f'My ping is {round((bot.latency * 1000), 3)} ms!')


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
    # We get an output of xxxxxxxx.xxx, this is an invalid epoch, so we strip everything after the "."
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


@bot.command()
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


@bot.command(name='load', pass_context=True)
async def load(ctx):
    await ctx.message.add_reaction('🔒')


@bot.command(name='auth', pass_context=True)
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


@bot.command()
@is_owner()
async def kill(ctx: Context):
    await ctx.send("https://c.tenor.com/huJuK_zUxSAAAAAM/im-dying-jake.gif")
    sys.exit()


bot.run(toe_ken)
