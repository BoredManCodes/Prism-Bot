# Holy shit, that's a lot of imports
import contextlib
import io
import ipaddress
import os
import subprocess
import sys
import difflib
import textwrap
import traceback
import re
from base64 import urlsafe_b64encode
import uuid
from urllib import parse, request
from urllib.parse import parse_qsl
from millify import prettify
import uuid as uuid
from PIL import Image
from requests import PreparedRequest
from decouple import config
import aiohttp
import discord.ext
import discord
from discord import Webhook, AsyncWebhookAdapter, http, DMChannel
from discord.ext.commands import (
    CommandNotFound,
    is_owner,
    check,
    Context,
    has_permissions,
)
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext, ComponentContext, MenuContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import (
    create_button,
    create_actionrow,
    create_select_option,
    create_select,
    wait_for_component,
)
from discord_slash.model import ButtonStyle, ContextMenuType
from slash_help import SlashHelp
import requests
import json
from durations import Duration
import time
from datetime import datetime
import logging
import random
import sentry_sdk

if config("DEBUG"):
    environment = "development"
else:
    environment = "production"
sentry_sdk.init(config("SENTRY"), environment=environment, traces_sample_rate=1.0)


# Setup the logger
class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
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
bot = commands.Bot(
    command_prefix=["$", "pls", "prism"],
    intents=intents,
    case_insensitive=True,
    help_command=None,
    strip_after_prefix=True,
)
toe_ken = config("TOKEN")
slash = SlashCommand(bot, sync_commands=True)
help_slash = SlashHelp(
    bot,
    slash,
    toe_ken,
    dpy_command=True,
    no_category_name="All commands",
    no_category_description=" ",
    extended_buttons=True,
    prefix="$",
)
bot.completion_date = "soon"
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
    "float": 10,
}

bot_name = "Prism Bot"
filename = "roles.json"
status = ""


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
    embed = discord.Embed(
        title="We ran into an error",
        description="You don't have permissions to manage this bot's functions",
        color=discord.Color.red(),
    )
    embed.set_footer(text=f"Caused by {name}", icon_url=icon)
    await ctx.send(embed=embed)
    return False


bot.guild_ids = [
    858547359804555264
]  # Bypass stupid hour+ waiting time for global commands


@bot.event
async def on_ready():
    channel = bot.get_channel(897765157940396052)
    message = await channel.fetch_message(920460790354567258)
    with open("old.txt", "w", encoding="utf8") as text_file:
        print(message.content, file=text_file)
    if config("DEBUG") == "False":
        await discord.utils.get(bot.get_all_members(), id=bot.user.id).edit(
            nick="prism bot peace be upon him"
        )
        bot.debug_status = "normal"
    else:
        await discord.utils.get(bot.get_all_members(), id=bot.user.id).edit(
            nick="prism bot testing be his job"
        )
        bot.debug_status = "debug"
    print(f"╔═══════════════════════════════════════════════════")
    print(f"╠Bot is ready")
    print(f"╠{bot.user.name} running in {bot.debug_status} mode")
    print(f"╠Discord API Version: {discord.__version__}")
    print(f"╠═Guilds:")
    for guild in bot.guilds:  # Print list of current guildsPreparedRequest
        print(f"╠════{guild.name} ({guild.id})")
    print(f"╚═══════════════════════════════════════════════════")
    prismian.start()
    changelog.start()
    # updating_embed.start()
    global RJD, roles_json
    testing_zone = bot.get_guild(int(config("guild_id")))
    try:
        roles_json = open(filename, "r+")
    except:
        roles_json = open(filename, "w+")
        json.dump({"perms": [], "roles": []}, roles_json)
        roles_json.seek(0)
    RJD = json.load(roles_json)
    roles_json.seek(0)
    for role in RJD["roles"]:
        for member in RJD[role[0]]:
            if member[1] <= time.time():
                try:
                    await testing_zone.get_member(member[0]).remove_roles(
                        testing_zone.get_role(int(role[0])), reason="expired"
                    )
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


@bot.command
async def dm(ctx):
    for member in ctx.guild.members:
        await member.send(
            "Hey there! This is just a reminder to vote in the current Prismian Presidential Election if you haven't already! You can do so in the election-votes."
        )
        print(f"Sent a DM to {member.display_name}")


@bot.command()
async def prismian(ctx):
    for member in bot.get_guild(858547359804555264).members:
        prismian_role = discord.utils.get(ctx.guild.roles, name="Prismian")
        new_role = discord.utils.get(ctx.guild.roles, name="New Member")
        general = bot.get_channel(858547359804555267)
        if prismian_role not in member.roles and new_role in member.roles:
            duration = datetime.now() - member.joined_at
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            days, hours = divmod(hours, 24)
            if days >= 14:
                mod_log = bot.get_channel(897765157940396052)
                await mod_log.send(
                    f"{member.display_name} has been a new member for {days} days and upgraded to Prismian today!"
                )
                await member.remove_roles(new_role)
                await member.add_roles(prismian_role)
                await general.send(
                    "https://cdn.discordapp.com/attachments/861289278374150164/934758089075355708/party-popper-joypixels.gif"
                )
                await general.send(
                    f"{member.mention} congrats on upgrading from New Member to Prismian today!"
                )
                logger.info(f"{member.display_name} has been upgraded to Prismian")


@tasks.loop(hours=2)
async def prismian():
    logger.info("Checking for Prismian upgrades")
    guild = bot.get_guild(858547359804555264)
    for member in bot.get_guild(858547359804555264).members:
        prismian_role = discord.utils.get(guild.roles, name="Prismian")
        new_role = discord.utils.get(guild.roles, name="New Member")
        general = bot.get_channel(858547359804555267)
        if prismian_role not in member.roles and new_role in member.roles:
            duration = datetime.now() - member.joined_at
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            days, hours = divmod(hours, 24)
            if days >= 14:
                mod_log = bot.get_channel(897765157940396052)
                await mod_log.send(
                    f"{member.display_name} has been a new member for {days} days and upgraded to Prismian today!"
                )
                await member.remove_roles(new_role)
                await member.add_roles(prismian_role)
                await general.send(
                    "https://cdn.discordapp.com/attachments/861289278374150164/934758089075355708/party-popper-joypixels.gif"
                )
                await general.send(
                    f"{member.mention} congrats on upgrading from New Member to Prismian today!"
                )
                logger.info(f"{member.display_name} has been upgraded to Prismian")
    logger.info("Done checking for Prismian upgrades")


@tasks.loop(minutes=2)
async def changelog():
    channel = bot.get_channel(897765157940396052)
    message = await channel.fetch_message(920460790354567258)
    with open("old.txt", "w", encoding="utf8") as text_file:
        print(message.content, file=text_file)


@tasks.loop(seconds=10)
async def updating_embed():
    channel = bot.get_channel(861289278374150164)
    message = await channel.fetch_message(932900240019828756)
    user = bot.get_user(324504908013240330)
    IP = config("GAME_IP")
    url = f"http://{IP}/players/{user.display_name}/stats"
    # print(f"http://{IP}/players/{user.display_name}/stats")
    page = requests.get(url)
    stats = json.loads(page.text)
    try:
        if stats["error"]:
            embed = discord.Embed(
                color=discord.colour.Color.red(),
                title=f"No one is currently in game",
                description=f"Last updated at {datetime.now()}",
            )
            await message.edit(embed=embed)
            return
    except:
        # Game time
        sec = int(stats["time"])
        sec_value = sec % (24 * 3600)
        hour_value = sec_value // 3600
        sec_value %= 3600
        min_value = sec_value // 60
        sec_value %= 60
        if hour_value != 0:
            game_time = f"{hour_value} hours, {min_value} minutes"
        else:
            game_time = f"{min_value} minutes"
        # Death time
        sec = int(stats["death"])
        sec_value = sec % (24 * 3600)
        hour_value = sec_value // 3600
        sec_value %= 3600
        min_value = sec_value // 60
        sec_value %= 60
        time = stats["lastJoined"]
        time = int(str(time)[:-3])
        if hour_value != 0:
            death_time = f"{hour_value} hours, {min_value} minutes"
        else:
            death_time = f"{min_value} minutes"
        embed = discord.Embed(
            color=discord.colour.Color.red(),
            title=f"{user.display_name}'s current game stats",
        )
        embed.add_field(name="Time spent in game:", value=game_time, inline=True)
        embed.add_field(name="Time since last death:", value=death_time, inline=True)
        embed.add_field(name="Last quit:", value=f"<t:{time}:R>", inline=True)
        embed.add_field(name="Kills:", value=stats["kills"], inline=True)
        embed.add_field(name="Deaths:", value=stats["deaths"], inline=True)
        embed.add_field(name="XP level:", value=stats["level"], inline=True)
        embed.add_field(name="Health:", value=stats["health"], inline=True)
        embed.add_field(name="Hunger:", value=stats["food"], inline=True)
        embed.add_field(name="Times jumped:", value=stats["jumps"], inline=True)
        embed.add_field(name="World:", value=stats["world"], inline=True)
        embed.set_thumbnail(
            url=f"https://heads.discordsrv.com/head.png?name={user.display_name}&overlay#{random.randint(1, 2000)}"
        )
        await message.edit(embed=embed)


@bot.event
async def on_component(ctx: ComponentContext):
    if "release" in ctx.custom_id:
        await ctx.edit_origin(content="Released.", components=None)
        css = """
            body {
            background-color: #36393e;
            color: #dcddde;
            }
            a {
                color: #0096cf;
            }
            .info {
                display: flex;
                max-width: 100%;
                margin: 0 5px 10px;
            }
            .guild-icon-container {
                flex: 0;
            }
            .guild-icon {
                max-width: 88px;
                max-height: 88px;
            }
            .metadata {
                flex: 1;
                margin-left: 10px;
            }
            .guild-name {
                font-size: 1.4em;
            }
            .channel-name {
                font-size: 1.2em;
            }
            .channel-topic {
                margin-top: 2px;
            }
            .channel-message-count {
                margin-top: 2px;
            }
            .chatlog {
                max-width: 100%;
                margin-bottom: 24px;
            }
            .message-group {
                display: flex;
                margin: 0 10px;
                padding: 15px 0;
                border-top: 1px solid;
            }
            .author-avatar-container {
                flex: 0;
                width: 40px;
                height: 40px;
            }
            .author-avatar {
                border-radius: 50%;
                height: 40px;
                width: 40px;
            }
            .messages {
                flex: 1;
                min-width: 50%;
                margin-left: 20px;
            }
            .author-name {
                font-size: 1em;
                font-weight: 500;
            }
            .timestamp {
                margin-left: 5px;
                font-size: 0.75em;
            }
            .message {
                padding: 2px 5px;
                margin-right: -5px;
                margin-left: -5px;
                background-color: transparent;
                transition: background-color 1s ease;
            }
            .content {
                font-size: 0.9375em;
                word-wrap: break-word;
            }
            .mention {
                color: #7289da;
            }
            .botTag {
                height: 0.9375rem;
                padding: 0px 0.275rem;
                margin-top: 0.075em;
                border-radius: 0.1875rem;
                background: #5961ec;
                font-size: 0.625rem;
                text-transform: uppercase;
                vertical-align: top;
                display: inline-flex;
                align-items: center;
                flex-shrink: 0;
                text-indent: 0px;
                position: relative;
                top: 0.1rem;
                margin-left: 0.25rem;
                line-height: 1.375rem;
                white-space: break-spaces;
                overflow-wrap: break-word;
            }

            .botText {
                position: relative;
                font-size: 10px;
                line-height: 15px;
                text-transform: uppercase;
                text-indent: 0px;
                color: rgb(255, 255, 255);
                font-weight: 500;
            }

        """

        def check_message_mention(msgs: discord.Message):
            user_mentions: list = msgs.mentions
            role_mentions: list = msgs.role_mentions
            channel_mentions: list = msgs.channel_mentions
            total_mentions: list = user_mentions + role_mentions + channel_mentions
            m: str = msgs.content
            for mentions in total_mentions:
                if mentions in user_mentions:
                    for mention in user_mentions:
                        m = m.replace(
                            str(f"<@{mention.id}>"),
                            f'<span class="mention">@{mention.name}</span>',
                        )
                        m = m.replace(
                            str(f"<@!{mention.id}>"),
                            f'<span class="mention">@{mention.name}</span>',
                        )
                elif mentions in role_mentions:
                    for mention in role_mentions:
                        m = m.replace(
                            str(f"<@&{mention.id}>"),
                            f'<span class="mention">@{mention.name}</span>',
                        )
                elif mentions in channel_mentions:
                    for mention in channel_mentions:
                        m = m.replace(
                            str(f"<#{mention.id}>"),
                            f'<span class="mention">#{mention.name}</span>',
                        )
                else:
                    pass
            return m

        messages: discord.TextChannel.history = await ctx.channel.history(
            limit=None, oldest_first=True
        ).flatten()
        title = str(
            f"Transcript of {str(ctx.channel.name).encode('ascii', 'ignore')}'s arrest"
        )
        description = str(f"Saved by {ctx.author.display_name}")
        f = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                <meta charset=utf-8>
                <meta name=viewport content="width=device-width">
                <meta content="Transcript saved" property="og:title" />
                <meta content="{str(title).replace("b'", "").replace("'", "")}
                {description}" property="og:description"/>
                <meta content="https://transcripts.boredman.net" property="og:url" />
                <meta content="https://paste.boredman.net/transcripts.png" property="og:image" />
                <meta content="#14adc4" data-react-helmet="true" name="theme-color" />

                <style>
                    {css}
                </style>
            </head>
            <body>
                <div class=info>
                    <div class=guild-icon-container><img class=guild-icon src={ctx.guild.icon_url}></div>
                    <div class=metadata>
                        <div class=guild-name>{ctx.guild.name}</div>
                        <div class=channel-name>{ctx.channel.name}'s arrest</div>
                        <div class=channel-message-count>{len(messages)} messages</div>
                    </div>
                </div>
            """

        for message in messages:
            if message.embeds:
                content = f"""Embed:
                Title: {message.embeds[0].title}

                Description: {message.embeds[0].description}

                """

            elif message.attachments:
                # IS AN IMAGE:
                if message.attachments[0].url.endswith(("jpg", "png", "gif", "bmp")):
                    if message.content:
                        content = (
                            check_message_mention(message)
                            + "<br>"
                            + f'<a href="{message.attachments[0].url}" target="_blank"><img src="{message.attachments[0].url}" width="200" alt="Attachment" \\></a>'
                        )
                    else:
                        content = f'<a href="{message.attachments[0].url}" target="_blank"><img src="{message.attachments[0].url}" width="200" alt="Attachment" \\></a>'

                # IS A VIDEO
                elif message.attachments[0].url.endswith(
                    ("mp4", "ogg", "flv", "mov", "avi")
                ):
                    if message.content:
                        content = (
                            check_message_mention(message)
                            + "<br>"
                            + f"""
                        <video width="320" height="240" controls>
                          <source src="{message.attachments[0].url}" type="video/{message.attachments[0].url[-3:]}">
                        Your browser does not support the video.
                        </video>
                        """
                        )
                    else:
                        content = f"""
                        <video width="320" height="240" controls>
                          <source src="{message.attachments[0].url}" type="video/{message.attachments[0].url[-3:]}">
                        Your browser does not support the video.
                        </video>
                        """
                elif message.attachments[0].url.endswith(("mp3", "boh")):
                    if message.content:
                        content = (
                            check_message_mention(message)
                            + "<br>"
                            + f"""
                        <audio controls>
                          <source src="{message.attachments[0].url}" type="audio/{message.attachments[0].url[-3:]}">
                        Your browser does not support the audio element.
                        </audio>
                        """
                        )
                    else:
                        content = f"""
                        <audio controls>
                          <source src="{message.attachments[0].url}" type="audio/{message.attachments[0].url[-3:]}">
                        Your browser does not support the audio element.
                        </audio>
                        """
                # OTHER TYPE OF FILES
                else:
                    # add things
                    pass
            else:
                content = check_message_mention(message)
            if message.author.bot:
                isBot = """<span class="botTag">
                                    <svg aria-label="Verified bot" class="botTagVerified" aria-hidden="false" width="16" height="16" viewBox="0 0 16 15.2">
                                        <path d="M7.4,11.17,4,8.62,5,7.26l2,1.53L10.64,4l1.36,1Z" fill="currentColor"></path>
                                     </svg>                                 
                                    <span class="botText">BOT</span>
                                </span>"""
            else:
                isBot = ""
            f += f"""
            <div class="message-group">
                <div class="author-avatar-container"><img class=author-avatar src={message.author.avatar_url}></div>
                <div class="messages">
                    <span class="author-name" >{message.author.name}</span>{isBot}<span class="timestamp">{message.created_at.strftime("%b %d, %Y %H:%M")}</span>
                    <div class="message">
                        <div class="content"><span class="markdown">{content}</span></div>
                    </div>
                </div>
            </div>
            """
        f += """
                </div>
            </body>
        </html>
        """
        id = uuid.uuid4()
        with open(f"transcripts/{str(id)}.html", mode="w+", encoding="utf-8") as file:
            print(io.StringIO(f).read(), file=file)

        sentences_log = bot.get_channel(875356199174938644)
        user_from_string = int(ctx.custom_id.split("release")[1])
        user = discord.utils.get(ctx.guild.members, id=user_from_string)
        user: discord.Member
        embed = discord.Embed(title=user.name, colour=discord.colour.Color.green())
        embed.add_field(name="Moderator", value=ctx.author, inline=True)
        embed.add_field(
            name="Discord account:", value=f"{user} ({user.id})", inline=True
        )
        embed.add_field(
            name="Minecraft account:", value=user.display_name, inline=False
        )
        embed.add_field(
            name="Sentence:",
            value=str(ctx.selected_options)
            .replace("[", "")
            .replace("'", "")
            .replace(",", "\n")
            .replace("]", ""),
            inline=True,
        )
        embed.add_field(
            name="Transcript:",
            value=f"[Click here](http://transcripts.boredman.net/{str(id)}.html)",
        )
        await sentences_log.send(embed=embed)
        staff = discord.utils.get(ctx.guild.roles, name="Staff")
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            user: discord.PermissionOverwrite(read_messages=False),
            staff: discord.PermissionOverwrite(read_messages=True),
        }
        await ctx.channel.edit(overwrites=overwrites)
        muted = discord.utils.get(ctx.guild.roles, name="Muted")
        await user.remove_roles(muted)
        try:
            await user.send(
                f"Hi there, I've taken the liberty of sending you a copy of your arrest transcript\n"
                f"http://transcripts.boredman.net/{str(id)}.html"
            )
        except Exception:
            print("user has DM's closed")

    if ctx.custom_id == "gimme-roles":
        for role in ctx.selected_options:
            roles = discord.utils.get(ctx.guild.roles, id=int(role))
            await ctx.author.add_roles(roles)
        # This definitely looks like shit, but it works really goodly
        rolestr = (
            str(ctx.selected_options)
            .replace(" '", "<@&")
            .replace("',", "> ")
            .replace("']", "> ")
            .replace("['", "<@&")
        )
        await ctx.edit_origin(
            content=f"Added you to {rolestr}", hidden=True, components=None
        )
    if ctx.custom_id == "take-me-roles":
        for role in ctx.selected_options:
            roles = discord.utils.get(ctx.guild.roles, id=int(role))
            await ctx.author.remove_roles(roles)
        # This definitely looks like shit, but it works really goodly
        rolestr = (
            str(ctx.selected_options)
            .replace(" '", "<@&")
            .replace("',", "> ")
            .replace("']", "> ")
            .replace("['", "<@&")
        )
        await ctx.edit_origin(
            content=f"Removed you from {rolestr}", hidden=True, components=None
        )


@bot.event
async def on_member_update(before, after):
    if (
        before.guild.id == 858547359804555264
        and before.display_name != after.display_name
    ):
        embed = discord.Embed(title=f"Changed Name")
        embed.add_field(name="User", value=before.mention)
        embed.add_field(name="Before", value=before.display_name)
        embed.add_field(name="After", value=after.display_name)
        embed.set_thumbnail(url=after.avatar_url)
        channel = bot.get_channel(897765157940396052)
        await channel.send(embed=embed)


@bot.command()
@is_owner()
async def msg(ctx, *, member=None):
    if member is None:
        await ctx.send("No members to message")
        return
    member = member.replace("<", "").replace("@", "").replace(">", "").replace("!", "")
    members = member.split(" ")
    mod_log = bot.get_channel(897765157940396052)
    members_messaged = []
    for i in members:
        member = await ctx.guild.fetch_member(i)
        await member.send(
            "Hi there,\n"
            "I have noticed you haven't joined the Minecraft server in over two months "
            "and haven't sent any messages in that time period in our Discord.\n"
            "If you don't indicate your intention to stay a member of Prism SMP "
            "within 2 weeks you will be automatically removed to make way for new members"
        )
        members_messaged.append(member.display_name)
    members_messaged = (
        str(members_messaged)
        .replace("[", "")
        .replace("]", "")
        .replace(",", "\n")
        .replace("'", "")
    )
    await mod_log.send(
        f"The following members have been messaged about their inactivity\n{members_messaged}"
    )


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
        await ctx.send(f"```py\n{output}```")


@slash.slash(
    name="ip",
    guild_ids=bot.guild_ids,
    description="Displays information on the given IP",
    options=[
        create_option(
            name="address",
            description="The IP address you want to check",
            option_type=option_type["string"],
            required=True,
        )
    ],
)
async def ip(ctx: SlashContext, address=None):
    if address is None:
        embed = discord.Embed(
            title="We ran into an error",
            description="You forgot to add an IP",
            color=discord.Color.red(),
        )
        embed.set_footer(
            text=f"Caused by {ctx.author.display_name}", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)
        return

    try:
        # This will return an error if it's not a valid IP. Saves me doing input validation
        ipaddress.ip_address(address)
        message = await ctx.send(
            "https://cdn.discordapp.com/emojis/783447587940073522.gif"
        )
        # os.system(f"ping -c 1  {address}")
        try:
            ping = subprocess.check_output(["ping", "-c", "1", address]).decode("utf-8")
        except subprocess.CalledProcessError:
            ping = "Host appears down, or not answering ping requests"
        os.system(f"nmap  {address} -oG nmap.grep")
        process = subprocess.Popen(
            ["./nmap.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        three = stdout.decode("utf-8").replace("///", "")
        two = three.replace("//", " ")
        one = two.replace("/", " ").replace("      1 ", "")
        url = "https://neutrinoapi.net/ip-info"
        params = {
            "user-id": config("NaughtyBoy_user"),
            "api-key": config("NaughtyBoy_key"),
            "ip": address,
            "reverse-lookup": True,
        }
        postdata = parse.urlencode(params).encode()
        req = request.Request(url, data=postdata)
        response = request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))
        url = "https://neutrinoapi.net/ip-probe"
        params = {
            "user-id": config("NaughtyBoy_user"),
            "api-key": config("NaughtyBoy_key"),
            "ip": address,
            "reverse-lookup": True,
        }
        postdata = parse.urlencode(params).encode()
        req = request.Request(url, data=postdata)
        response = request.urlopen(req)
        probe = json.loads(response.read().decode("utf-8"))
        embed = discord.Embed(
            title="IP lookup",
            description=f"Lookup details for {address}",
            color=discord.Color.green(),
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url,
        )
        try:
            embed.add_field(
                name="Location",
                value=f"{result['city']}\n{result['region']}, {result['country']}",
                inline=True,
            )
        except:
            print(probe)
        if not result["hostname"] == "":
            embed.add_field(name="Hostname", value=str(result["hostname"]), inline=True)
        if not result["host-domain"] == "":
            embed.add_field(
                name="Host Domain", value=str(result["host-domain"]), inline=True
            )
        embed.add_field(
            name="Maps Link",
            value=f"https://maps.google.com/?q={result['latitude']},{result['longitude']}",
            inline=True,
        )
        embed.add_field(
            name="Provider", value=f"{probe['provider-description']}", inline=True
        )
        if probe["is-vpn"]:
            embed.add_field(
                name="Is VPN?", value=f"Yes {probe['vpn-domain']}", inline=True
            )
        elif not probe["is-vpn"]:
            embed.add_field(name="Is VPN?", value=f"No", inline=True)
        if probe["is-hosting"]:
            embed.add_field(
                name="Is Hosting?", value=f"Yes {probe['vpn-domain']}", inline=True
            )
        elif not probe["is-hosting"]:
            embed.add_field(name="Is Hosting?", value=f"No", inline=True)
        if len(one) < 3:
            one = None
        embed.add_field(name="Nmap Results", value=f"```py\n{one}\n```", inline=False)
        embed.add_field(name="Ping Results", value=f"```\n{ping}\n```", inline=True)
        await message.edit(embed=embed, content="")
    except ValueError:
        embed = discord.Embed(
            title="We ran into an error",
            description="That isn't a valid IP",
            color=discord.Color.red(),
        )
        embed.set_footer(
            text=f"Caused by {ctx.author.display_name}", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)


@bot.command(description="Displays information on the given IP", category="Utility")
async def ip(ctx, address=None):
    if ip is None:
        embed = discord.Embed(
            title="We ran into an error",
            description="You forgot to add an IP",
            color=discord.Color.red(),
        )
        embed.set_footer(
            text=f"Caused by {ctx.author.display_name}", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)
        return

    try:
        ipaddress.ip_address(
            address
        )  # This will return an error if it's not a valid IP. Saves me doing input validation
        message = await ctx.reply(
            "https://cdn.discordapp.com/emojis/783447587940073522.gif"
        )
        # os.system(f"ping -c 1  {address}")
        try:
            ping = subprocess.check_output(["ping", "-c", "1", address]).decode("utf-8")
        except subprocess.CalledProcessError:
            ping = "Host appears down, or not answering ping requests"
        os.system(f"nmap  {address} -oG nmap.grep")
        process = subprocess.Popen(
            ["./nmap.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        three = stdout.decode("utf-8").replace("///", "")
        two = three.replace("//", " ")
        one = two.replace("/", " ").replace("      1 ", "")
        url = "https://neutrinoapi.net/ip-info"
        params = {
            "user-id": config("NaughtyBoy_user"),
            "api-key": config("NaughtyBoy_key"),
            "ip": address,
            "reverse-lookup": True,
        }
        postdata = parse.urlencode(params).encode()
        req = request.Request(url, data=postdata)
        response = request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))
        url = "https://neutrinoapi.net/ip-probe"
        params = {
            "user-id": config("NaughtyBoy_user"),
            "api-key": config("NaughtyBoy_key"),
            "ip": address,
            "reverse-lookup": True,
        }
        postdata = parse.urlencode(params).encode()
        req = request.Request(url, data=postdata)
        response = request.urlopen(req)
        probe = json.loads(response.read().decode("utf-8"))
        embed = discord.Embed(
            title="IP lookup",
            description=f"Lookup details for {address}",
            color=discord.Color.green(),
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url,
        )
        try:
            embed.add_field(
                name="Location",
                value=f"{result['city']}\n{result['region']}, {result['country']}",
                inline=True,
            )
        except:
            print(probe)
        if not result["hostname"] == "":
            embed.add_field(name="Hostname", value=str(result["hostname"]), inline=True)
        if not result["host-domain"] == "":
            embed.add_field(
                name="Host Domain", value=str(result["host-domain"]), inline=True
            )
        embed.add_field(
            name="Maps Link",
            value=f"https://maps.google.com/?q={result['latitude']},{result['longitude']}",
            inline=True,
        )
        embed.add_field(
            name="Provider", value=f"{probe['provider-description']}", inline=True
        )
        if probe["is-vpn"]:
            embed.add_field(
                name="Is VPN?", value=f"Yes {probe['vpn-domain']}", inline=True
            )
        elif not probe["is-vpn"]:
            embed.add_field(name="Is VPN?", value=f"No", inline=True)
        if probe["is-hosting"]:
            embed.add_field(
                name="Is Hosting?", value=f"Yes {probe['vpn-domain']}", inline=True
            )
        elif not probe["is-hosting"]:
            embed.add_field(name="Is Hosting?", value=f"No", inline=True)
        if len(one) < 3:
            one = None
        embed.add_field(name="Nmap Results", value=f"```py\n{one}\n```", inline=False)
        embed.add_field(name="Ping Results", value=f"```\n{ping}\n```", inline=True)
        await message.edit(embed=embed, content="")
    except ValueError:
        embed = discord.Embed(
            title="We ran into an error",
            description="That isn't a valid IP",
            color=discord.Color.red(),
        )
        embed.set_footer(
            text=f"Caused by {ctx.author.display_name}", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)


@slash.slash(
    name="gimme-roles",
    guild_ids=bot.guild_ids,
    description="Give yourself some roles",
)
async def roles(ctx: SlashContext):
    select = create_select(
        options=[
            create_select_option("Random Gang", value="893284269798068305"),
            create_select_option("Other pronouns/ask me", value="866455940958126091"),
            create_select_option("He/Him", value="866455665357881364"),
            create_select_option("She/Her", value="866455537234477095"),
            create_select_option("They/Them", value="866455786988765194"),
            create_select_option("It/its", value="866460549680332810"),
            create_select_option("Announcement gang", value="866471817450356737"),
            create_select_option("Shush the bot pings", value="920459523947364373"),
        ],
        custom_id="gimme-roles",
        placeholder="Choose your roles",
        min_values=1,
        max_values=8,
    )
    await ctx.send(
        "Role selection", components=[create_actionrow(select)], hidden=False
    )


@slash.slash(
    name="take-me-roles",
    guild_ids=bot.guild_ids,
    description="Remove roles from yourself",
)
async def roles(ctx: SlashContext):
    select = create_select(
        options=[
            create_select_option("Random Gang", value="893284269798068305"),
            create_select_option("Other pronouns/ask me", value="866455940958126091"),
            create_select_option("He/Him", value="866455665357881364"),
            create_select_option("She/Her", value="866455537234477095"),
            create_select_option("They/Them", value="866455786988765194"),
            create_select_option("It/its", value="866460549680332810"),
            create_select_option("Announcement gang", value="866471817450356737"),
            create_select_option("Shush the bot pings", value="920459523947364373"),
        ],
        custom_id="take-me-roles",
        placeholder="Choose the roles you no longer want",
        min_values=1,
        max_values=9,
    )
    await ctx.send("Role selection", components=[create_actionrow(select)], hidden=True)


@bot.command()
async def transcript(ctx):
    css = """
        body {
        background-color: #36393e;
        color: #dcddde;
        }
        a {
            color: #0096cf;
        }
        .info {
            display: flex;
            max-width: 100%;
            margin: 0 5px 10px;
        }
        .guild-icon-container {
            flex: 0;
        }
        .guild-icon {
            max-width: 88px;
            max-height: 88px;
        }
        .metadata {
            flex: 1;
            margin-left: 10px;
        }
        .guild-name {
            font-size: 1.4em;
        }
        .channel-name {
            font-size: 1.2em;
        }
        .channel-topic {
            margin-top: 2px;
        }
        .channel-message-count {
            margin-top: 2px;
        }
        .chatlog {
            max-width: 100%;
            margin-bottom: 24px;
        }
        .message-group {
            display: flex;
            margin: 0 10px;
            padding: 15px 0;
            border-top: 1px solid;
        }
        .author-avatar-container {
            flex: 0;
            width: 40px;
            height: 40px;
        }
        .author-avatar {
            border-radius: 50%;
            height: 40px;
            width: 40px;
        }
        .messages {
            flex: 1;
            min-width: 50%;
            margin-left: 20px;
        }
        .author-name {
            font-size: 1em;
            font-weight: 500;
        }
        .timestamp {
            margin-left: 5px;
            font-size: 0.75em;
        }
        .message {
            padding: 2px 5px;
            margin-right: -5px;
            margin-left: -5px;
            background-color: transparent;
            transition: background-color 1s ease;
        }
        .content {
            font-size: 0.9375em;
            word-wrap: break-word;
        }
        .mention {
            color: #7289da;
        }
        .botTag {
            height: 0.9375rem;
            padding: 0px 0.275rem;
            margin-top: 0.075em;
            border-radius: 0.1875rem;
            background: #5961ec;
            font-size: 0.625rem;
            text-transform: uppercase;
            vertical-align: top;
            display: inline-flex;
            align-items: center;
            flex-shrink: 0;
            text-indent: 0px;
            position: relative;
            top: 0.1rem;
            margin-left: 0.25rem;
            line-height: 1.375rem;
            white-space: break-spaces;
            overflow-wrap: break-word;
        }

        .botText {
            position: relative;
            font-size: 10px;
            line-height: 15px;
            text-transform: uppercase;
            text-indent: 0px;
            color: rgb(255, 255, 255);
            font-weight: 500;
        }

    """

    def check_message_mention(msgs: discord.Message):
        user_mentions: list = msgs.mentions
        role_mentions: list = msgs.role_mentions
        channel_mentions: list = msgs.channel_mentions
        total_mentions: list = user_mentions + role_mentions + channel_mentions
        m: str = msgs.content
        for mentions in total_mentions:
            if mentions in user_mentions:
                for mention in user_mentions:
                    m = m.replace(
                        str(f"<@{mention.id}>"),
                        f'<span class="mention">@{mention.name}</span>',
                    )
                    m = m.replace(
                        str(f"<@!{mention.id}>"),
                        f'<span class="mention">@{mention.name}</span>',
                    )
            elif mentions in role_mentions:
                for mention in role_mentions:
                    m = m.replace(
                        str(f"<@&{mention.id}>"),
                        f'<span class="mention">@{mention.name}</span>',
                    )
            elif mentions in channel_mentions:
                for mention in channel_mentions:
                    m = m.replace(
                        str(f"<#{mention.id}>"),
                        f'<span class="mention">#{mention.name}</span>',
                    )
            else:
                pass
        return m

    messages: discord.TextChannel.history = await ctx.channel.history(
        limit=None, oldest_first=True
    ).flatten()
    title = str(f"Transcript of #{str(ctx.channel.name).encode('ascii', 'ignore')}")
    description = str(f"Saved by {ctx.author.display_name}")
    f = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            <meta charset=utf-8>
            <meta name=viewport content="width=device-width">
            <meta content="Transcript saved" property="og:title" />
            <meta content="{str(title).replace("b'", "").replace("'", "")}
            {description}" property="og:description"/>
            <meta content="https://transcripts.boredman.net" property="og:url" />
            <meta content="https://paste.boredman.net/transcripts.png" property="og:image" />
            <meta content="#14adc4" data-react-helmet="true" name="theme-color" />

            <style>
                {css}
            </style>
        </head>
        <body>
            <div class=info>
                <div class=guild-icon-container><img class=guild-icon src={ctx.guild.icon_url}></div>
                <div class=metadata>
                    <div class=guild-name>{ctx.guild.name}</div>
                    <div class=channel-name>{ctx.channel.name}</div>
                    <div class=channel-message-count>{len(messages)} messages</div>
                </div>
            </div>
        """

    for message in messages:
        if message.embeds:
            content = f"""Embed:
            Title: {message.embeds[0].title}

            Description: {message.embeds[0].description}

            """

        elif message.attachments:
            # IS AN IMAGE:
            if message.attachments[0].url.endswith(("jpg", "png", "gif", "bmp")):
                if message.content:
                    content = (
                        check_message_mention(message)
                        + "<br>"
                        + f'<a href="{message.attachments[0].url}" target="_blank"><img src="{message.attachments[0].url}" width="200" alt="Attachment" \\></a>'
                    )
                else:
                    content = f'<a href="{message.attachments[0].url}" target="_blank"><img src="{message.attachments[0].url}" width="200" alt="Attachment" \\></a>'

            # IS A VIDEO
            elif message.attachments[0].url.endswith(
                ("mp4", "ogg", "flv", "mov", "avi")
            ):
                if message.content:
                    content = (
                        check_message_mention(message)
                        + "<br>"
                        + f"""
                    <video width="320" height="240" controls>
                      <source src="{message.attachments[0].url}" type="video/{message.attachments[0].url[-3:]}">
                    Your browser does not support the video.
                    </video>
                    """
                    )
                else:
                    content = f"""
                    <video width="320" height="240" controls>
                      <source src="{message.attachments[0].url}" type="video/{message.attachments[0].url[-3:]}">
                    Your browser does not support the video.
                    </video>
                    """
            elif message.attachments[0].url.endswith(("mp3", "boh")):
                if message.content:
                    content = (
                        check_message_mention(message)
                        + "<br>"
                        + f"""
                    <audio controls>
                      <source src="{message.attachments[0].url}" type="audio/{message.attachments[0].url[-3:]}">
                    Your browser does not support the audio element.
                    </audio>
                    """
                    )
                else:
                    content = f"""
                    <audio controls>
                      <source src="{message.attachments[0].url}" type="audio/{message.attachments[0].url[-3:]}">
                    Your browser does not support the audio element.
                    </audio>
                    """
            # OTHER TYPE OF FILES
            else:
                # add things
                pass
        else:
            content = check_message_mention(message)
        if message.author.bot:
            isBot = """<span class="botTag">
                                <svg aria-label="Verified bot" class="botTagVerified" aria-hidden="false" width="16" height="16" viewBox="0 0 16 15.2">
                                    <path d="M7.4,11.17,4,8.62,5,7.26l2,1.53L10.64,4l1.36,1Z" fill="currentColor"></path>
                                 </svg>                                 
                                <span class="botText">BOT</span>
                            </span>"""
        else:
            isBot = ""
        f += f"""
        <div class="message-group">
            <div class="author-avatar-container"><img class=author-avatar src={message.author.avatar_url}></div>
            <div class="messages">
                <span class="author-name" >{message.author.name}</span>{isBot}<span class="timestamp">{message.created_at.strftime("%b %d, %Y %H:%M")}</span>
                <div class="message">
                    <div class="content"><span class="markdown">{content}</span></div>
                </div>
            </div>
        </div>
        """
    f += """
            </div>
        </body>
    </html>
    """
    id = uuid.uuid4()
    with open(f"transcripts/{str(id)}.html", mode="w+", encoding="utf-8") as file:
        print(io.StringIO(f).read(), file=file)
        await ctx.reply(f"Transcript: http://transcripts.boredman.net/{str(id)}.html")


@bot.command(
    description="Sends some info on what the self roles are", category="Utility"
)
async def rolehelp(ctx):
    embed = discord.Embed(
        title="How to assign your roles",
        description="Simply type /gimme-roles in any text channel to grab some roles, you can select more than one and can also choose your preferred pronouns",
    )
    embed.set_thumbnail(url="https://discordtemplates.me/icon.png")
    embed.add_field(
        name="Announcement gang",
        value="Want to be pinged for non essential announcements?",
        inline=True,
    )
    embed.add_field(
        name="Random gang",
        value="Sometimes random events happen. Grab this role to be notified of them",
        inline=True,
    )
    embed.add_field(
        name="Shush the bot pings",
        value="Don't want to be pinged when you level up? Grab this role",
        inline=True,
    )
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
    member_count = len([m for m in member.guild.members if not m.bot])
    if not str(banner_id) == "None":
        banner_url = (
            f"https://cdn.discordapp.com/banners/{member.id}/{banner_id}?size=1024"
        )
        req.prepare_url(
            url="https://api.xzusfin.repl.co/card?",
            params={
                "avatar": str(member.avatar_url_as(format="png")),
                "middle": f"{member.name} joined Prism",
                "name": "We now have",
                "bottom": f"{member_count} members",
                "text": discord.colour.Color.random(),
                "avatarborder": discord.colour.Color.random(),
                "avatarbackground": discord.colour.Color.random(),
                "background": banner_url,
            },
        )
        body = dict(parse_qsl(req.body))
        if "code" in body:
            print("Not sending a banner due to invalid response")
            print(body)
            print(req.url)
        else:
            img_data = requests.get(req.url).content
            with open("Banner.png", "wb") as handler:
                handler.write(img_data)
            try:
                Image.open("Banner.png")
                await ctx.send(file=discord.File("Banner.png"))
            except IOError:
                logger.error("Banner was not a valid image")
    else:
        req.prepare_url(
            url="https://api.xzusfin.repl.co/card?",
            params={
                "avatar": str(member.avatar_url_as(format="png")),
                "middle": f"{member.name} joined Prism",
                "name": "We now have",
                "bottom": f"{member_count} members",
                "text": discord.colour.Color.random(),
                "avatarborder": discord.colour.Color.random(),
                "avatarbackground": discord.colour.Color.random(),
                "background": "https://cdnb.artstation.com/p/assets/images/images/013/535/601/large/supawit-oat-fin1.jpg",
            },
        )
        body = dict(parse_qsl(req.body))
        if "code" in body:
            print("Not sending a banner due to invalid response")
            print(body)
            print(req.url)
        else:
            img_data = requests.get(req.url).content
            with open("Banner.png", "wb") as handler:
                handler.write(img_data)
            try:
                Image.open("Banner.png")
                await ctx.send(file=discord.File("Banner.png"))
            except IOError:
                logger.error("Banner was not a valid image")


@bot.event
async def on_message(message):
    if "plugin" in message.content.lower():
        await message.add_reaction("<:cranky:870165423272886282>")
    if "bored" in message.content.lower():
        await message.add_reaction("<:koalaPeek:950977674225020958>")
    if "koala" in message.content.lower():
        await message.add_reaction("<:koalaPeek:950977674225020958>")
    if "mod" in message.content.lower():
        await message.add_reaction("<:cranky:870165423272886282>")
    if "orenge" in message.content.lower():
        await message.add_reaction("<:orengesad:955476237726416916>")
    if "vanilla" in message.content.lower():
        await message.add_reaction("🍦")

    if "when is the bot going to be finished?" in message.content:
        await message.channel.send("<t:9999999999:R>")
    blacklist_channels = [
        907718985343197194,
        891614699374915584,
        891614663253585960,
        953987192190021673,
    ]  # Don't listen to the message logger channel to avoid looping
    if len(message.content) > 1500 and not message.channel.id in blacklist_channels:
        step = 1000
        for i in range(0, len(message.content), 1000):
            split = message.content[i:step]
            step += 1000
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(
                    config("LOG"), adapter=AsyncWebhookAdapter(session)
                )
                await webhook.send(
                    f"<#{message.channel.id}> {message.author.display_name} ({message.author.id}) sent: {split}",
                    username=message.author.display_name,
                    avatar_url=message.author.avatar_url,
                )

    if message.channel.id in blacklist_channels:
        return
    else:  # Otherwise, do the logging thing
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(
                config("LOG"), adapter=AsyncWebhookAdapter(session)
            )
            content = message.content.replace("324504908013240330", "BoredManPing")
            await webhook.send(
                f"<#{message.channel.id}> {message.author.display_name} ({message.author.id}) sent: {content}",
                username=message.author.display_name,
                avatar_url=message.author.avatar_url,
            )
    if message.author == bot.user:  # Don't listen to yourself
        return
    if (
        "https://discord.gift/" in message.content.lower()
    ):  # Some dumbass sent free nitro
        await message.channel.send(
            ":warning: FREE NITRO! :warning:\nThis link appears to be legitimate :D"
        )
        return
    if (
        not message.guild and message.author != bot.user
    ):  # If message not in a guild it must be a DM
        message_filtered = (
            str(message.content)
            .replace("www", "")
            .replace("http", "")
            .replace("@everyone", "ATTEMPTED EVERONE PING")
        )  # No links pls
        url = "https://neutrinoapi.net/bad-word-filter"  # Filter out bad boy words
        params = {
            "user-id": config("NaughtyBoy_user"),
            "api-key": config("NaughtyBoy_key"),
            "content": message_filtered,
            "censor-character": "•",
            "catalog": "strict",
        }
        postdata = parse.urlencode(params).encode()
        req = request.Request(url, data=postdata)
        response = request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(
                config("MOD"), adapter=AsyncWebhookAdapter(session)
            )
            await webhook.send(
                f"{result['censored-content']}",
                username=f"{message.author.display_name} in DM",
                avatar_url=message.author.avatar_url,
            )
    if str(bot.user.id) in message.content:
        reactions = [
            "<:iseeyou:876201272972304425>",
            "🇨",
            "🇦",
            "🇳",
            "▪️",
            "🇮",
            "◼️",
            "🇭",
            "🇪",
            "🇱",
            "��",
            "⬛",
            "🇾",
            "🇴",
            "🇺",
            "❓",
        ]
        for reaction in reactions:
            await message.add_reaction(reaction)
    await bot.process_commands(message)  # Continue processing bot.commands


@slash.slash(
    name="list-members",
    guild_ids=bot.guild_ids,
    description="Lists all members with a certain role",
    options=[
        create_option(
            name="role",
            description="The role you want to list",
            option_type=option_type["role"],
            required=True,
        )
    ],
)
async def list(ctx: SlashContext, role: discord.Role):
    usernames = [m.display_name for m in role.members]
    count = 0
    for m in role.members:
        count += 1
    check_len = (
        str(sorted(usernames, key=str.lower))
        .replace(",", "\n")
        .replace("[", "")
        .replace("]", "")
        .replace("'", "")
    )
    if len(check_len) > 2000:  # Ensure we don't go over the Discord embed limit
        title = f"**{count} members with the {role.name} role**"
        description = (
            str(sorted(usernames, key=str.lower))
            .replace(", ", "\n")
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )
        await ctx.send(
            f"{title}\n{description}\n\n`List too long to be sent as an embed`"
        )
    else:
        usernames = [m.display_name for m in role.members]
        title = f"**{count} members with the {role.mention} role**"
        description = (
            str(sorted(usernames, key=str.lower))
            .replace(", ", "\n")
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )
        embed = discord.Embed(description=f"{title}\n{description}", color=role.color)
        embed.set_footer(
            text=f"Issued by {ctx.author.display_name}", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)


@slash.slash(
    name="purge",
    guild_ids=bot.guild_ids,
    description="Purges the defined amount of messages from this channel",
    options=[
        create_option(
            name="amount",
            description="The amount you want to delete",
            option_type=option_type["integer"],
            required=True,
        )
    ],
)
@check(has_perms)
async def purge(ctx: SlashContext, limit: int = None):
    if limit is None:
        await ctx.send("You didn't tell me how many messages to purge", delete_after=20)
        return
    await ctx.channel.purge(limit=limit)
    await ctx.send(f"Purged {limit} messages")
    mod_log = bot.get_channel(897765157940396052)
    title = f"Messages Purged"
    embed = discord.Embed(
        title=title,
        color=ctx.message.author.color,
        description=f"Purged {limit} messages from <#{ctx.channel.id}>",
    )
    embed.set_footer(
        text=f"Discord name: {ctx.message.author.display_name}\nDiscord ID: {ctx.message.author.id}",
        icon_url=ctx.message.author.avatar_url,
    )
    await mod_log.send(embed=embed)


@slash.slash(
    name="clear",
    guild_ids=bot.guild_ids,
    description="Purges the defined amount of messages from this channel",
    options=[
        create_option(
            name="amount",
            description="The amount you want to delete",
            option_type=option_type["integer"],
            required=True,
        )
    ],
)
@check(has_perms)
async def clear(ctx: SlashContext, limit: int = None):
    if limit is None:
        await ctx.send("You didn't tell me how many messages to purge", delete_after=20)
        return
    await ctx.channel.purge(limit=limit)
    await ctx.send(f"Purged {limit} messages")
    mod_log = bot.get_channel(897765157940396052)
    title = f"Messages Purged"
    embed = discord.Embed(
        title=title,
        color=ctx.message.author.color,
        description=f"Purged {limit} messages from <#{ctx.channel.id}>",
    )
    embed.set_footer(
        text=f"Discord name: {ctx.message.author.display_name}\nDiscord ID: {ctx.message.author.id}",
        icon_url=ctx.message.author.avatar_url,
    )
    await mod_log.send(embed=embed)


@bot.command(pass_context=True)
@check(has_perms)
async def purge(ctx, limit: int = None):
    if limit is None:
        await ctx.send("You didn't tell me how many messages to purge", delete_after=20)
        return
    await ctx.channel.purge(limit=limit + 1)
    await ctx.send(f"Purged {limit} messages", delete_after=30)
    mod_log = bot.get_channel(897765157940396052)
    title = f"Messages Purged"
    embed = discord.Embed(
        title=title,
        color=ctx.message.author.color,
        description=f"Purged {limit} messages from <#{ctx.channel.id}>",
    )
    embed.set_footer(
        text=f"Discord name: {ctx.message.author.display_name}\nDiscord ID: {ctx.message.author.id}",
        icon_url=ctx.message.author.avatar_url,
    )
    await mod_log.send(embed=embed)


@purge.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You cant do that!")


@bot.command(
    description="Sends the welcome message in-case users need it again",
    category="Utility",
)
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

    embed = discord.Embed(
        title=title, description=description, color=discord.Color.blue()
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/avatars/890176674237399040/5716879890391b6204a71b05a77b2258.webp?size=1024"
    )
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    embed = discord.Embed(
        title=f"**Error in command: {ctx.command}**",
        description=f"```\n{error}\n```",
        colour=discord.Color.red(),
    )
    await ctx.send(embed=embed)
    raise error


@bot.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent):
    # print(payload)
    if int(payload.message_id) == 920460790354567258:
        channel = bot.get_channel(int(payload.data["channel_id"]))
        message = await channel.fetch_message(payload.message_id)
        with open("new.txt", "w", encoding="utf8") as text_file:
            print(message.content, file=text_file)
        old = open("old.txt").readlines()
        new = open("new.txt").readlines()
        differ = difflib.Differ()
        differ_output = differ.compare(old, new)
        changes = (
            "{0}".format("".join(differ_output))
            .replace("<a:tick:757490995720880159>", "✅")
            .replace("<@!890176674237399040>", "Prism Bot")
        )
        embed = discord.Embed(
            title="Changelog changed",
            url=message.jump_url,
            description=f"```diff\n{changes}\n```",
            color=discord.colour.Color.blurple(),
        )
        await channel.send(embed=embed)


@bot.event
async def on_member_join(member):
    if (
        member.guild.id == 858547359804555264
    ):  # Only detect if the user joined the Prism guild
        if member.bot:  # Bloody bots
            return
        else:
            if time.time() - member.created_at.timestamp() < 2592000:
                # Send a message to the mods
                mod_log = bot.get_channel(897765157940396052)
                title = f"{member.display_name} is potentially suspicious"
                embed = discord.Embed(title=title, color=discord.Color.red())
                embed.set_footer(
                    text=f"Discord name: {member.name}\nDiscord ID: {member.id}",
                    icon_url=member.avatar_url,
                )
                date_format = "%a, %d %b %Y %I:%M %p"
                embed.set_thumbnail(
                    url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/1200px-Warning.svg.png"
                )
                embed.add_field(
                    name="Joined Discord",
                    value=member.created_at.strftime(date_format),
                    inline=False,
                )
                await mod_log.send(embed=embed)
            else:
                # Send a message to the mods
                mod_log = bot.get_channel(897765157940396052)
                title = f"{member.display_name} joined the server"
                embed = discord.Embed(title=title, color=discord.Color.green())
                embed.set_footer(
                    text=f"Discord name: {member.name}\nDiscord ID: {member.id}",
                    icon_url=member.avatar_url,
                )
                date_format = "%a, %d %b %Y %I:%M %p"
                embed.add_field(
                    name="Joined Discord",
                    value=member.created_at.strftime(date_format),
                    inline=False,
                )
                await mod_log.send(embed=embed)
            # Give the user the New Member role
            role = discord.utils.get(member.guild.roles, name="New Member")
            await member.add_roles(role)
            # Send the welcome banner
            channel = bot.get_channel(858547359804555267)
            messages = [
                f"Welcome {member.name}\nIf you need anything from staff or simply have questions, ping a <@&858547638719086613>",
                f"Hi {member.name}!\nIf you need anything from staff or simply have questions, ping a <@&858547638719086613>",
                f"{member.name} joined us\nIf you need anything from staff or simply have questions, ping a <@&858547638719086613>",
                f"{member.name} is *one of us*\nIf you need anything from staff or simply have questions, ping a <@&858547638719086613>",
                f"Hoi {member.name}\nIf you need anything from staff or simply have questions, ping a <@&858547638719086613>",
                f"{member.name} is here!\nIf you need anything from staff or simply have questions, ping a <@&858547638719086613>",
                f"Welcome to the party {member.name}\nIf you need anything from staff or simply have questions, ping a <@&858547638719086613>",
                f"Hey `@everyone` {member.name} joined Prism\nIf you need anything from staff or simply have questions, ping a <@&858547638719086613>",
            ]
            await channel.send(random.choice(messages))
            req = PreparedRequest()
            users = await bot.http.request(
                discord.http.Route("GET", f"/users/{member.id}")
            )
            banner_id = users["banner"]
            # If statement because the user may not have a banner
            member_count = len([m for m in member.guild.members if not m.bot])
            if not str(banner_id) == "None":
                banner_url = f"https://cdn.discordapp.com/banners/{member.id}/{banner_id}?size=1024"
                req.prepare_url(
                    url="https://api.xzusfin.repl.co/card?",
                    params={
                        "avatar": str(member.avatar_url_as(format="png")),
                        "middle": f"{member.name} joined Prism",
                        "name": "We now have",
                        "bottom": f"{member_count} members",
                        "text": discord.colour.Color.random(),
                        "avatarborder": discord.colour.Color.random(),
                        "avatarbackground": discord.colour.Color.random(),
                        "background": banner_url,
                    },
                )
                body = dict(parse_qsl(req.body))
                if "code" in body:
                    print("Not sending a banner due to invalid response")
                    print(body)
                    print(req.url)
                else:
                    img_data = requests.get(req.url).content
                    with open("Banner.png", "wb") as handler:
                        handler.write(img_data)
                    try:
                        Image.open("Banner.png")
                        await channel.send(file=discord.File("Banner.png"))
                    except IOError:
                        logger.error("Banner was not a valid image")
            else:
                req.prepare_url(
                    url="https://api.xzusfin.repl.co/card?",
                    params={
                        "avatar": str(member.avatar_url_as(format="png")),
                        "middle": f"{member.name} joined Prism",
                        "name": "We now have",
                        "bottom": f"{member_count} members",
                        "text": discord.colour.Color.random(),
                        "avatarborder": discord.colour.Color.random(),
                        "avatarbackground": discord.colour.Color.random(),
                        "background": "https://cdnb.artstation.com/p/assets/images/images/013/535/601/large/supawit-oat-fin1.jpg",
                    },
                )
                body = dict(parse_qsl(req.body))
                if "code" in body:
                    print("Not sending a banner due to invalid response")
                    print(body)
                    print(req.url)
                else:
                    img_data = requests.get(req.url).content
                    with open("Banner.png", "wb") as handler:
                        handler.write(img_data)
                    try:
                        Image.open("Banner.png")
                        await channel.send(file=discord.File("Banner.png"))
                    except IOError:
                        logger.error("Banner was not a valid image")


@bot.event
async def on_member_remove(member):
    if (
        member.guild.id == 858547359804555264
    ):  # Only detect if the user left the Prism guild
        if member.bot:
            return
        else:
            messages = [
                f"Goodbye {member.name}",
                f"It appears {member.name} has left",
                f"{member.name} has disappeared :(",
                f"We wish {member.name} well in their travels",
                f"Toodles {member.name}!",
                f"{member.name} found love elsewhere :(",
                f"{member.name} left\nSee you later alligator",
                f"{member.name} left\nBye Felicia",
                f"{member.name} left\nSo long, and thanks for all the fish!",
                f"{member.name} left\nGoodbye, Vietnam! That’s right, I’m history, I’m outta here",
            ]
            general = bot.get_channel(858547359804555267)
            await general.send(random.choice(messages))
            channel = bot.get_channel(897765157940396052)
            title = f"{member.display_name} left the server"
            embed = discord.Embed(title=title, color=discord.Color.red())
            embed.set_footer(
                text=f"Discord name: {member.name}\nDiscord ID: {member.id}",
                icon_url=member.avatar_url,
            )
            date_format = "%a, %d %b %Y %I:%M %p"
            embed.set_author(name=str(member), icon_url=member.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(
                name="Joined Server",
                value=member.joined_at.strftime(date_format),
                inline=False,
            )
            embed.add_field(
                name="Joined Discord",
                value=member.created_at.strftime(date_format),
                inline=False,
            )
            embed.set_footer(text="ID: " + str(member.id))
            await channel.send(embed=embed)


@bot.command(
    name="lp",
    pass_context=True,
    description="Adds to the permission changelog",
    category="Moderation",
)
@check(has_perms)
async def lp(ctx, *, message):
    await ctx.message.delete()
    changes = f"```diff\n{message} ```"
    embed = discord.Embed(
        title="Permission Changelog", description=changes, color=0x00FF40
    )
    embed.set_footer(
        text=f"Issued by {ctx.message.author.display_name}",
        icon_url=ctx.message.author.avatar_url,
    )
    await ctx.send(embed=embed)


@slash.slash(
    name="embed",
    guild_ids=bot.guild_ids,
    description="creates an embed",
    options=[
        create_option(
            name="channel",
            description="The channel to send to",
            option_type=option_type["channel"],
            required=True,
        ),
        create_option(
            name="title",
            description="The title of the embed",
            option_type=option_type["string"],
            required=False,
        ),
        create_option(
            name="description",
            description="The description of the embed",
            option_type=option_type["string"],
            required=False,
        ),
        create_option(
            name="image",
            description="A valid URL to use as the big image",
            option_type=option_type["string"],
            required=False,
        ),
        create_option(
            name="thumbnail",
            description="A valid URL to use as the thumbnail",
            option_type=option_type["string"],
            required=False,
        ),
        create_option(
            name="footer",
            description="The footer of the embed",
            option_type=option_type["string"],
            required=False,
        ),
    ],
)
@check(has_perms)
async def embed(
    ctx: SlashContext,
    *,
    title=None,
    description=None,
    image=None,
    thumbnail=None,
    footer=None,
    channel: discord.TextChannel,
):
    if title is None:
        title = ""
    if description is None:
        description = ""
    embed = discord.Embed(title=title, description=description, color=ctx.author.color)
    if image is not None:
        embed.set_image(url=thumbnail)
    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)
    if footer is not None:
        embed.set_footer(text=footer)
    await ctx.send("Embed sent", hidden=True)
    await channel.send(embed=embed)


@slash.slash(
    name="whitelist",
    guild_ids=bot.guild_ids,
    description="Adds a user to the whitelist",
    options=[
        create_option(
            name="member",
            description="The user you want to whitelist",
            option_type=option_type["user"],
            required=True,
        )
    ],
)
@check(has_perms)
async def whitelist(ctx: SlashContext, member: discord.Member):
    role = discord.utils.get(member.guild.roles, name="Whitelisted")
    await member.add_roles(role)
    message = f"Added {member.mention} to the whitelist"
    embed = discord.Embed(description=message, color=ctx.author.color)
    embed.set_footer(
        text=f"Whitelisted by {ctx.author.display_name}", icon_url=ctx.author.avatar_url
    )
    embed.set_author(name="📋 User added to whitelist")
    await ctx.send(embed=embed)


@bot.command(
    name="whitelist",
    pass_context=True,
    description="Adds a user to the whitelisted role",
    category="Moderation",
)
@check(has_perms)
async def whitelist(ctx, member: discord.Member):
    await ctx.message.delete()
    channel = bot.get_channel(869280855657447445)
    role = discord.utils.get(member.guild.roles, id=899568696593367070)
    await member.add_roles(role)
    message = f"Added {member.mention} to the whitelist"
    embed = discord.Embed(description=message, color=ctx.author.color)
    embed.set_footer(
        text=f"Whitelisted by {ctx.author.display_name}", icon_url=ctx.author.avatar_url
    )
    embed.set_author(name="📋 User added to whitelist")
    await channel.send(embed=embed)
    await ctx.send("Done!", hidden=True)


@slash.slash(
    name="edit-embed",
    guild_ids=bot.guild_ids,
    description="edits an embed",
    options=[
        create_option(
            name="embedlink",
            description="The message link to edit",
            option_type=option_type["string"],
            required=True,
        ),
        create_option(
            name="title",
            description="The title of the embed",
            option_type=option_type["string"],
            required=False,
        ),
        create_option(
            name="description",
            description="The description of the embed",
            option_type=option_type["string"],
            required=False,
        ),
        create_option(
            name="image",
            description="A valid URL to use as the big image",
            option_type=option_type["string"],
            required=False,
        ),
        create_option(
            name="thumbnail",
            description="A valid URL to use as the thumbnail",
            option_type=option_type["string"],
            required=False,
        ),
        create_option(
            name="footer",
            description="The footer of the embed",
            option_type=option_type["string"],
            required=False,
        ),
    ],
)
@check(has_perms)
async def embed(
    ctx: SlashContext,
    *,
    embedlink,
    title=None,
    description=None,
    image=None,
    thumbnail=None,
    footer=None,
):
    if title is None:
        title = ""
    if description is None:
        description = ""
    newembed = discord.Embed(
        title=title, description=description, color=ctx.author.color
    )

    if image is not None:
        newembed.set_image(url=thumbnail)
    if thumbnail is not None:
        newembed.set_thumbnail(url=thumbnail)
    if footer is not None:
        newembed.set_footer(text=footer)
    await ctx.send("Embed edited", hidden=True)
    editembed = embedlink.split("/")
    message = (
        await bot.get_guild(int(editembed[-3]))
        .get_channel(int(editembed[-2]))
        .fetch_message(int(editembed[-1]))
    )
    await message.edit(embed=newembed)


def jsondump(v: dict):
    roles_json.seek(0)
    json.dump(v, roles_json)
    roles_json.truncate()
    roles_json.seek(0)


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
    hours = int(
        (secs - years * dyears - month * dmonth - weeks * dweeks - days * ddays)
        // dhours
    )
    minutes = int(
        (
            secs
            - years * dyears
            - month * dmonth
            - weeks * dweeks
            - days * ddays
            - hours * dhours
        )
        // dmins
    )
    seconds = int(
        (
            secs
            - years * dyears
            - month * dmonth
            - weeks * dweeks
            - days * ddays
            - hours * dhours
            - minutes * dmins
        )
        // 1
    )
    milliseconds = float(
        round(
            (
                (
                    secs
                    - years * dyears
                    - month * dmonth
                    - weeks * dweeks
                    - days * ddays
                    - hours * dhours
                    - minutes * dmins
                    - seconds
                )
                * 1000
            ),
            3,
        )
    )
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


# Command to set a role to expire
@slash.slash(
    name="role-expire",
    guild_ids=bot.guild_ids,
    description="Sets when a role will expire",
    options=[
        create_option(
            name="role",
            description="the role you want to expire",
            option_type=option_type["role"],
            required=True,
        ),
        create_option(
            name="time",
            description="how long you want people to have the role",
            option_type=option_type["string"],
            required=True,
        ),
    ],
)
@check(has_perms)
async def expire(ctx: Context, role: discord.Role, *, time: str):
    print(role.permissions)
    expire_duration = Duration(time)
    expire_duration = expire_duration.to_seconds()
    if int(expire_duration) == 0:
        await ctx.send(f"Check your syntax, /role-help")
        return
    roles_json_data = json.load(roles_json)
    roles_json.seek(0)
    found = False
    t = str(role.id)
    for expiring_role in roles_json_data["roles"]:
        if expiring_role[0] == t:
            for memberlist in RJD[t]:
                memberlist[1] -= expiring_role[1] - expire_duration
            for memberlist2 in roles_json_data[t]:
                memberlist2[1] -= expiring_role[1] - expire_duration
            expiring_role[1] = expire_duration
            RJD["roles"][roles_json_data["roles"].index(expiring_role)][
                1
            ] = expire_duration
            print(roles_json_data)
            found = True
            break
    if not found:
        RJD["roles"].append([t, expire_duration])
        RJD[t] = []
        roles_json_data["roles"].append([t, expire_duration])
        roles_json_data[t] = []
    jsondump(roles_json_data)
    await ctx.send(
        f"✓ set {role.name} to expire {str(Duration(time)).replace('<Duration ', 'after ').replace('>', '')}"
    )


@bot.command(description="Sets a role to expire", category="Moderation")
@check(has_perms)
async def expire(ctx: Context, role: discord.Role, *, time: str):
    print(role.permissions)
    expire_duration = Duration(time)
    expire_duration = expire_duration.to_seconds()
    if int(expire_duration) == 0:
        await ctx.send(f"Check your syntax, $role-help")
        return
    roles_json_data = json.load(roles_json)
    roles_json.seek(0)
    found = False
    t = str(role.id)
    for expiring_role in roles_json_data["roles"]:
        if expiring_role[0] == t:
            for memberlist in RJD[t]:
                memberlist[1] -= expiring_role[1] - expire_duration
            for memberlist2 in roles_json_data[t]:
                memberlist2[1] -= expiring_role[1] - expire_duration
            expiring_role[1] = expire_duration
            RJD["roles"][roles_json_data["roles"].index(expiring_role)][
                1
            ] = expire_duration
            print(roles_json_data)
            found = True
            break
    if not found:
        RJD["roles"].append([t, expire_duration])
        RJD[t] = []
        roles_json_data["roles"].append([t, expire_duration])
        roles_json_data[t] = []
    jsondump(roles_json_data)
    await ctx.message.add_reaction("✓")


@slash.slash(
    name="role-unexpire",
    guild_ids=bot.guild_ids,
    description="Sets a role to not expire",
    options=[
        create_option(
            name="role",
            description="the role you don't want to expire",
            option_type=option_type["role"],
            required=True,
        )
    ],
)
@check(has_perms)
async def unexpire(ctx, role: discord.Role):
    roles_json.seek(0)
    roles_json_data = json.load(roles_json)
    roles_json.seek(0)
    for expiring_role in roles_json_data["roles"]:
        if expiring_role[0] == str(role.id):
            roles_json_data["roles"].remove(expiring_role)
            RJD["roles"].remove(expiring_role)
            del roles_json_data[str(role.id)]
            del RJD[str(role.id)]
    jsondump(roles_json_data)
    await ctx.send(f"✓ set {role.name} to not expire")


@bot.command(description="Removes a role from expiration", category="Moderation")
@check(has_perms)
async def unexpire(ctx, role: discord.Role):
    roles_json.seek(0)
    roles_json_data = json.load(roles_json)
    roles_json.seek(0)
    for expiring_role in roles_json_data["roles"]:
        if expiring_role[0] == str(role.id):
            roles_json_data["roles"].remove(expiring_role)
            RJD["roles"].remove(expiring_role)
            del roles_json_data[str(role.id)]
            del RJD[str(role.id)]
    jsondump(roles_json_data)
    await ctx.message.add_reaction("✓")


@slash.slash(
    name="role-help",
    guild_ids=bot.guild_ids,
    description="Displays the role help embed",
)
async def _help(ctx: discord.ext.commands.Context):
    help_embed = discord.Embed(
        title=f"Role Help", description="slash commands", colour=discord.Colour.blue()
    )
    help_embed.add_field(
        name="role-expire",
        value=f"_Sets a role to expire after a certain amount of time_\n\n"
        f"`/role-expire <role> <time>`\n(eg, /role-expire @examplerole 1m 12s)",
        inline=False,
    )
    help_embed.add_field(
        name="role-unexpire",
        value=f"_Removes a role from the list of expiring roles_\n\n"
        f"`/role-unexpire <role>`\n(eg, /role-unexpire @examplerole2)",
        inline=False,
    )
    help_embed.add_field(
        name="AddPerm",
        value=f"_Gives a role permissions to use this bot."
        f" You need to have `Manage Roles` Permissions to use this command._\n\n`/addperm <role>`",
        inline=False,
    )
    help_embed.add_field(
        name="DelPerm",
        value=f"_Removes a role's permission to use this bot."
        f" You need to have `Manage Roles` Permissions to use this command._\n\n`/delperm <role>`",
        inline=False,
    )
    help_embed.add_field(
        name="ViewRoles",
        value=f"_Displays the current settings._\n\n`/viewroles`",
        inline=False,
    )
    help_embed.add_field(
        name="ViewPerms",
        value=f"_Displays which Roles have permissions to configure the Bot._\n\n`/viewperms`",
        inline=False,
    )
    help_embed.add_field(
        name="Ping", value=f"_Displays the bots latency._\n\n`/ping`", inline=False
    )
    await ctx.send(embed=help_embed)


@bot.command(
    name="role-help",
    description="Shows the role expiry settings help",
    category="Moderation",
)
async def _help(ctx: discord.ext.commands.Context):
    help_embed = discord.Embed(
        title=f"{bot_name} >> Help",
        description="Commands",
        colour=discord.Colour.blue(),
    )
    help_embed.add_field(
        name="Expire",
        value=f"_Sets a role to expire after a certain amount of time_\n\n"
        f"`$expire <role> <time>`\n(eg, $expire @examplerole 1m 12s)",
        inline=False,
    )
    help_embed.add_field(
        name="Unexpire",
        value=f"_Removes a role from the list of expiring roles_\n\n"
        f"`$unexpire <role>`\n(eg, $unexpire @examplerole2)",
        inline=False,
    )
    help_embed.add_field(
        name="AddPerm",
        value=f"_Gives a role permissions to use this bot."
        f" You need to have `Manage Roles` Permissions to use this command._\n\n`$addperm <role>`",
        inline=False,
    )
    help_embed.add_field(
        name="DelPerm",
        value=f"_Removes a role's permission to use this bot."
        f" You need to have `Manage Roles` Permissions to use this command._\n\n`$delperm <role>`",
        inline=False,
    )
    help_embed.add_field(
        name="ViewRoles",
        value=f"_Displays the current settings_\n\n`$viewroles`",
        inline=False,
    )
    help_embed.add_field(
        name="ViewPerms",
        value=f"_Displays which Roles have permissions to configure the Bot_\n\n`$viewperms`",
        inline=False,
    )
    help_embed.add_field(
        name="Ping", value=f"_Displays the bots latency.\n\n`$ping`", inline=False
    )
    await ctx.send(embed=help_embed)


@slash.slash(
    name="addperm",
    guild_ids=bot.guild_ids,
    description=f"Adds a role to manage {bot_name}",
    options=[
        create_option(
            name="role",
            description="the role",
            option_type=option_type["role"],
            required=True,
        )
    ],
)
@has_permissions(manage_roles=True)
async def addperm(ctx: Context, role: discord.Role):
    r = role.id
    if r not in RJD["perms"]:
        RJD["perms"].append(r)
        y = json.load(roles_json)
        roles_json.seek(0)
        y["perms"].append(r)
        jsondump(y)
        await ctx.send(f"✓ added {role.name} to the management team")
    else:
        await ctx.send("That role already has permissions!")


@bot.command(
    description="Adds a role to be allowed to manage the bot", category="Moderation"
)
@has_permissions(manage_roles=True)
async def addperm(ctx: Context, role: discord.Role):
    r = role.id
    if r not in RJD["perms"]:
        RJD["perms"].append(r)
        y = json.load(roles_json)
        roles_json.seek(0)
        y["perms"].append(r)
        jsondump(y)
        await ctx.send(f"✓ added {role.name} to the management team")
    else:
        await ctx.send("That role already has permissions!")


@slash.slash(
    name="delperm",
    guild_ids=bot.guild_ids,
    description=f"Removes a role from managing {bot_name}",
    options=[
        create_option(
            name="role",
            description="the role",
            option_type=option_type["role"],
            required=True,
        )
    ],
)
@has_permissions(manage_roles=True)
async def delperm(ctx: Context, role: discord.Role):
    r = role.id
    if r in RJD["perms"]:
        RJD["perms"].remove(r)
        y = json.load(roles_json)
        roles_json.seek(0)
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
        y = json.load(roles_json)
        roles_json.seek(0)
        y["perms"].remove(r)
        jsondump(y)
        await ctx.send(f"✓ removed {role.name} from the management role")
    else:
        await ctx.send("I don't think that role had permissions :confused:")


@slash.slash(
    name="viewroles",
    guild_ids=bot.guild_ids,
    description="View the roles that are set to expire",
)
async def viewroles(ctx: Context):
    roles = []
    for role in RJD["roles"]:
        roles.append(f"<@&{role[0]}>")
    expires = []
    for role in RJD["roles"]:
        expires.append(timeformat(role[1]))
    roles_embed = discord.Embed(
        title=f"{bot_name} >> Roles",
        description=f"Displays all Roles you added using /expire",
        colour=discord.Colour.blue(),
    )
    roles_embed.add_field(name="Role", value="\n".join(roles), inline=True)
    roles_embed.add_field(name="Expires After", value="\n".join(expires), inline=True)
    await ctx.send(embed=roles_embed)


@bot.command(
    description="Lists the roles that are set to expire", category="Moderation"
)
async def viewroles(ctx: Context):
    roles = []
    for role in RJD["roles"]:
        roles.append(f"<@&{role[0]}>")
    expires = []
    for role in RJD["roles"]:
        expires.append(timeformat(role[1]))
    roles_embed = discord.Embed(
        title=f"{bot_name} >> Roles",
        description=f"Displays all Roles you added using $expire",
        colour=discord.Colour.blue(),
    )
    roles_embed.add_field(name="Role", value="\n".join(roles), inline=True)
    roles_embed.add_field(name="Expires After", value="\n".join(expires), inline=True)
    await ctx.send(embed=roles_embed)


@slash.slash(
    name="viewperms",
    guild_ids=bot.guild_ids,
    description=f"Views the roles allowed to manage {bot_name}",
)
async def viewperms(ctx: Context):
    perms = []
    for role in RJD["perms"]:
        perms.append(f"<@&{role}>")
    perms_embed = discord.Embed(
        title=f"{bot_name} >> Permissions",
        description=f"Displays all Roles (you added using /addperm) that have permissions.",
        colour=discord.Colour.blue(),
    )
    perms_embed.add_field(
        name="Role(s) with Permissions", value="\n".join(perms), inline=False
    )
    await ctx.send(embed=perms_embed)


@bot.command(
    description="Views the roles that are allowed to manage the bot",
    category="Moderation",
)
async def viewperms(ctx: Context):
    perms = []
    for role in RJD["perms"]:
        perms.append(f"<@&{role}>")
    perms_embed = discord.Embed(
        title=f"{bot_name} >> Permissions",
        description=f"Displays all Roles (you added using $addperm) that have permissions.",
        colour=discord.Colour.blue(),
    )
    perms_embed.add_field(
        name="Role(s) with Permissions", value="\n".join(perms), inline=False
    )
    await ctx.send(embed=perms_embed)


@slash.slash(
    name="ping", guild_ids=bot.guild_ids, description=f"Checks {bot_name}'s ping"
)
async def ping(ctx):
    await ctx.send(f"My ping is {round((bot.latency * 1000), 3)} ms!")


@bot.command(description=f"Checks {bot_name}'s ping", category="")
async def ping(ctx):
    await ctx.send(f"My ping is {round((bot.latency * 1000), 3)} ms!")


@slash.context_menu(target=ContextMenuType.USER, name="Who is this?")
async def context_menu(ctx: MenuContext):
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

    top_role = user.roles[
        -1
    ]  # first element in roles is `@everyone` and last is top role
    embed = discord.Embed(color=top_role.color, description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar_url)
    if str(user.id) == "709089341007200288":  # FT :POGGERS:
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/861289278374150164/917731281503150090/"
            "3ee9a6c54e15a2929d276cd9ba366442.gif"
        )
    elif str(user.id) == "510748531926106113":  # Orang
        embed.set_thumbnail(
            url="https://c.tenor.com/aw-QZPYpGmkAAAAM/carrot-garden.gif"
        )
    elif str(user.id) == "103523893834166272":  # Apo
        embed.set_thumbnail(
            url="https://thumbs.gfycat.com/FrayedUncommonGrosbeak-size_restricted.gif"
        )
    elif str(user.id) == "690864077861421066":  # Alina
        embed.set_thumbnail(url="https://media4.giphy.com/media/QsTGfN7bYXUm4/200.gif")
    elif str(user.id) == "324504908013240330":  # ME!!!!!!!!111!!
        embed.set_thumbnail(
            url="https://64.media.tumblr.com/e12f4de9050b40e88d76d396bd848c08/"
            "tumblr_oi94oaK9Wl1rcqnnxo1_r1_400.gifv"
        )
    else:
        embed.set_thumbnail(url=user.avatar_url)
    if has_activity:
        try:
            if str(user.activities[0].details) == "None":
                embed.add_field(
                    name="Current Activity",
                    value=f"{activity} {user.activities[0].name}",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Current Activity",
                    value=f"{activity} {user.activities[0].name} | {user.activities[0].details}",
                    inline=False,
                )
        except:
            embed.add_field(
                name="Current Activity",
                value=f"{activity} {user.activities[0].name}",
                inline=False,
            )
    joined_time = str((user.joined_at - datetime(1970, 1, 1)).total_seconds()).split(
        "."
    )
    discord_joined_time = str(
        (user.created_at - datetime(1970, 1, 1)).total_seconds()
    ).split(".")

    embed.add_field(name="Joined Server", value=f"<t:{joined_time[0]}:R>", inline=False)
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(
        name="Join Position", value=str(members.index(user) + 1), inline=False
    )
    embed.add_field(
        name="Joined Discord", value=f"<t:{discord_joined_time[0]}:R>", inline=False
    )
    if len(user.roles) > 1:
        res = user.roles[::-1]
        role_string = " ".join([r.mention for r in res][:-1])
        embed.add_field(
            name="Roles [{}]".format(len(user.roles) - 1),
            value=role_string,
            inline=False,
        )
    embed.set_footer(text="ID: " + str(user.id))
    return await ctx.send(embed=embed, hidden=True)


@slash.slash(
    name="whois",
    guild_ids=bot.guild_ids,
    description="Shows some info on users",
    options=[
        create_option(
            name="user",
            description="The user to lookup",
            option_type=option_type["user"],
            required=False,
        )
    ],
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
    top_role = user.roles[
        -1
    ]  # first element in roles is `@everyone` and last is top role
    embed = discord.Embed(color=top_role.color, description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar_url)
    if str(user.id) == "709089341007200288":  # FT :POGGERS:
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/861289278374150164/917731281503150090/"
            "3ee9a6c54e15a2929d276cd9ba366442.gif"
        )
    elif str(user.id) == "510748531926106113":  # Orang
        embed.set_thumbnail(
            url="https://c.tenor.com/aw-QZPYpGmkAAAAM/carrot-garden.gif"
        )
    elif str(user.id) == "103523893834166272":  # Apo
        embed.set_thumbnail(
            url="https://thumbs.gfycat.com/FrayedUncommonGrosbeak-size_restricted.gif"
        )
    elif str(user.id) == "690864077861421066":  # Alina
        embed.set_thumbnail(url="https://media4.giphy.com/media/QsTGfN7bYXUm4/200.gif")
    elif str(user.id) == "324504908013240330":  # ME!!!!!!!!111!!
        embed.set_thumbnail(
            url="https://64.media.tumblr.com/e12f4de9050b40e88d76d396bd848c08/"
            "tumblr_oi94oaK9Wl1rcqnnxo1_r1_400.gifv"
        )
    else:
        embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(
        name="Current Status", value=f"{statusemoji} | {status}", inline=False
    )
    if has_activity:
        try:
            if str(user.activities[0].details) == "None":
                embed.add_field(
                    name="Current Activity",
                    value=f"{activity} {user.activities[0].name}",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Current Activity",
                    value=f"{activity} {user.activities[0].name} | {user.activities[0].details}",
                    inline=False,
                )
        except:
            embed.add_field(
                name="Current Activity",
                value=f"{activity} {user.activities[0].name}",
                inline=False,
            )
    joined_time = str((user.joined_at - datetime(1970, 1, 1)).total_seconds()).split(
        "."
    )
    discord_joined_time = str(
        (user.created_at - datetime(1970, 1, 1)).total_seconds()
    ).split(".")
    embed.add_field(name="Discord Name", value=f"{user.name}#{user.discriminator}")
    embed.add_field(name="Joined Server", value=f"<t:{joined_time[0]}:R>", inline=False)
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(
        name="Join Position", value=str(members.index(user) + 1), inline=False
    )
    embed.add_field(
        name="Joined Discord", value=f"<t:{discord_joined_time[0]}:R>", inline=False
    )
    if len(user.roles) > 1:
        res = user.roles[::-1]
        role_string = " ".join([r.mention for r in res][:-1])
        embed.add_field(
            name="Roles [{}]".format(len(user.roles) - 1),
            value=role_string,
            inline=False,
        )
    embed.set_footer(text="ID: " + str(user.id))
    await ctx.send(embed=embed)
    IP = config("GAME_IP")
    url = f"http://{IP}/players/{user.display_name}"
    headers = {"secret": config("SECRET")}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            content = await resp.text()
    if resp.status != 200:
        await ctx.send("Couldn't contact server")
        return
    stats = json.loads(content)
    try:
        if stats["error"]:
            return
    except:
        # Game time
        sec = int(stats["time"])
        sec_value = sec % (24 * 3600)
        hour_value = sec_value // 3600
        sec_value %= 3600
        min_value = sec_value // 60
        sec_value %= 60
        if hour_value != 0:
            game_time = f"{hour_value} hours, {min_value} minutes"
        else:
            game_time = f"{min_value} minutes"
        # Death time
        sec = int(stats["death"])
        sec_value = sec % (24 * 3600)
        hour_value = sec_value // 3600
        sec_value %= 3600
        min_value = sec_value // 60
        sec_value %= 60
        if hour_value != 0:
            death_time = f"{hour_value} hours, {min_value} minutes"
        else:
            death_time = f"{min_value} minutes"
        if stats["online"]:
            embed = discord.Embed(
                color=discord.colour.Color.green(),
                title=f"{user.display_name}'s current game stats",
            )
            last_online = "Now"
        else:
            embed = discord.Embed(
                color=discord.colour.Color.red(),
                title=f"{user.display_name}'s cached game stats",
            )
            last_online = f"<t:{str(stats['lastJoined'])[:-3]}:R>"
        # embed.add_field(name="Time spent in game:", value=game_time, inline=True)
        # embed.add_field(name="Time since last death:", value=death_time, inline=True)
        embed.add_field(name="Kills:", value=prettify(stats["kills"]), inline=True)
        embed.add_field(name="Deaths:", value=prettify(stats["deaths"]), inline=True)
        embed.add_field(name="XP level:", value=prettify(stats["level"]), inline=True)
        embed.add_field(name="Health:", value=stats["health"][:4], inline=True)
        embed.add_field(name="Hunger:", value=stats["food"][:4], inline=True)
        embed.add_field(
            name="Times jumped:", value=prettify(stats["jumps"]), inline=True
        )
        embed.add_field(name="World:", value=stats["world"], inline=True)
        # staff stuffs
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if (
            overwrite.read_messages
        ):  # if everyone does not have read messages permission, syntax is confuse
            embed.add_field(
                name="IP:",
                value=f"[{stats['address']}](https://iplocation.io/ip/{stats['address']} \"Click for more info\")",
                inline=True,
            )
            embed.add_field(
                name="UUID",
                value=f"[{stats['uuid']}](https://namemc.com/profile/{stats['username']} \"Click for more info\")",
                inline=True,
            )
            embed.add_field(
                name="Gamemode:", value=stats["gamemode"].lower(), inline=True
            )
            embed.add_field(name="Bed location:", value=stats["bed"], inline=True)
            location = stats["location"].split(",")
            embed.add_field(
                name="Their location:",
                value=f"{location[0].split('.')[0]},{location[1].split('.')[0]},{location[2].split('.')[0]}",
                inline=True,
            )
        embed.add_field(name="Last online:", value=last_online, inline=True)

        embed.set_thumbnail(
            url=f"https://heads.discordsrv.com/head.png?name={user.display_name}&overlay"
        )
        await ctx.send(embed=embed)


@bot.command()
async def game(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.guild.get_member(ctx.author.id)
    IP = config("GAME_IP")
    url = f"http://{IP}/players/{user.display_name}"
    headers = {"secret": config("SECRET")}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            content = await resp.text()
    if resp.status != 200:
        await ctx.send("Couldn't contact server")
        return
    stats = json.loads(content)
    try:
        if stats["error"]:
            return
    except:
        # Game time
        sec = int(stats["time"])
        sec_value = sec % (24 * 3600)
        hour_value = sec_value // 3600
        sec_value %= 3600
        min_value = sec_value // 60
        sec_value %= 60
        if hour_value != 0:
            game_time = f"{hour_value} hours, {min_value} minutes"
        else:
            game_time = f"{min_value} minutes"
        # Death time
        sec = int(stats["death"])
        sec_value = sec % (24 * 3600)
        hour_value = sec_value // 3600
        sec_value %= 3600
        min_value = sec_value // 60
        sec_value %= 60
        if hour_value != 0:
            death_time = f"{hour_value} hours, {min_value} minutes"
        else:
            death_time = f"{min_value} minutes"
        if stats["online"]:
            embed = discord.Embed(
                color=discord.colour.Color.green(),
                title=f"{user.display_name}'s current game stats",
            )
            last_online = "Now"
        else:
            embed = discord.Embed(
                color=discord.colour.Color.red(),
                title=f"{user.display_name}'s cached game stats",
            )
            last_online = f"<t:{str(stats['lastJoined'])[:-3]}:R>"
        # embed.add_field(name="Time spent in game:", value=game_time, inline=True)
        # embed.add_field(name="Time since last death:", value=death_time, inline=True)
        embed.add_field(name="Kills:", value=prettify(stats["kills"]), inline=True)
        embed.add_field(name="Deaths:", value=prettify(stats["deaths"]), inline=True)
        embed.add_field(name="XP level:", value=prettify(stats["level"]), inline=True)
        embed.add_field(name="Health:", value=stats["health"][:4], inline=True)
        embed.add_field(name="Hunger:", value=stats["food"][:4], inline=True)
        embed.add_field(
            name="Times jumped:", value=prettify(stats["jumps"]), inline=True
        )
        embed.add_field(name="World:", value=stats["world"], inline=True)
        # staff stuffs
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if (
            overwrite.read_messages
        ):  # if everyone does not have read messages permission, syntax is confuse
            embed.add_field(
                name="IP:",
                value=f"[{stats['address']}](https://iplocation.io/ip/{stats['address']} \"Click for more info\")",
                inline=True,
            )
            embed.add_field(
                name="UUID",
                value=f"[{stats['uuid']}](https://namemc.com/profile/{stats['username']} \"Click for more info\")",
                inline=True,
            )
            embed.add_field(
                name="Gamemode:", value=stats["gamemode"].lower(), inline=True
            )
            embed.add_field(name="Bed location:", value=stats["bed"], inline=True)
            location = stats["location"].split(",")
            embed.add_field(
                name="Their location:",
                value=f"{location[0].split('.')[0]},{location[1].split('.')[0]},{location[2].split('.')[0]}",
                inline=True,
            )
        embed.add_field(name="Last online:", value=last_online, inline=True)

        embed.set_thumbnail(
            url=f"https://heads.discordsrv.com/head.png?name={user.display_name}&overlay"
        )
        await ctx.send(embed=embed)


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
    top_role = user.roles[
        -1
    ]  # first element in roles is `@everyone` and last is top role
    embed = discord.Embed(color=top_role.color, description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar_url)
    if str(user.id) == "709089341007200288":  # FT :POGGERS:
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/861289278374150164/917731281503150090/"
            "3ee9a6c54e15a2929d276cd9ba366442.gif"
        )
    elif str(user.id) == "510748531926106113":  # Orang
        embed.set_thumbnail(
            url="https://c.tenor.com/aw-QZPYpGmkAAAAM/carrot-garden.gif"
        )
    elif str(user.id) == "103523893834166272":  # Apo
        embed.set_thumbnail(
            url="https://thumbs.gfycat.com/FrayedUncommonGrosbeak-size_restricted.gif"
        )
    elif str(user.id) == "690864077861421066":  # Alina
        embed.set_thumbnail(url="https://media4.giphy.com/media/QsTGfN7bYXUm4/200.gif")
    elif str(user.id) == "324504908013240330":  # ME!!!!!!!!111!!
        embed.set_thumbnail(
            url="https://64.media.tumblr.com/e12f4de9050b40e88d76d396bd848c08/"
            "tumblr_oi94oaK9Wl1rcqnnxo1_r1_400.gifv"
        )
    else:
        embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(
        name="Current Status", value=f"{statusemoji} | {status}", inline=False
    )
    if has_activity:
        try:
            if str(user.activities[0].details) == "None":
                embed.add_field(
                    name="Current Activity",
                    value=f"{activity} {user.activities[0].name}",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Current Activity",
                    value=f"{activity} {user.activities[0].name} | {user.activities[0].details}",
                    inline=False,
                )
        except:
            embed.add_field(
                name="Current Activity",
                value=f"{activity} {user.activities[0].name}",
                inline=False,
            )
    joined_time = str((user.joined_at - datetime(1970, 1, 1)).total_seconds()).split(
        "."
    )
    discord_joined_time = str(
        (user.created_at - datetime(1970, 1, 1)).total_seconds()
    ).split(".")
    embed.add_field(name="Discord Name", value=f"{user.name}#{user.discriminator}")
    embed.add_field(name="Joined Server", value=f"<t:{joined_time[0]}:R>", inline=False)
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(
        name="Join Position", value=str(members.index(user) + 1), inline=False
    )
    embed.add_field(
        name="Joined Discord", value=f"<t:{discord_joined_time[0]}:R>", inline=False
    )
    if len(user.roles) > 1:
        res = user.roles[::-1]
        role_string = " ".join([r.mention for r in res][:-1])
        embed.add_field(
            name="Roles [{}]".format(len(user.roles) - 1),
            value=role_string,
            inline=False,
        )
    embed.set_footer(text="ID: " + str(user.id))
    await ctx.send(embed=embed)
    # # Game stuffs
    # IP = config("GAME_IP")
    # url = f"http://{IP}/players/{user.display_name}/stats"
    # # print(f"http://{IP}/players/{user.display_name}/stats")
    # page = requests.get(url, headers={"secret":config("SECRET")})
    # stats = json.loads(page.text)
    # try:
    #     if stats['error']:
    #         return
    # except:
    #     # Game time
    #     sec = int(stats["time"])
    #     sec_value = sec % (24 * 3600)
    #     hour_value = sec_value // 3600
    #     sec_value %= 3600
    #     min_value = sec_value // 60
    #     sec_value %= 60
    #     if hour_value != 0:
    #         game_time = f"{hour_value} hours, {min_value} minutes"
    #     else:
    #         game_time = f"{min_value} minutes"
    #     # Death time
    #     sec = int(stats["death"])
    #     sec_value = sec % (24 * 3600)
    #     hour_value = sec_value // 3600
    #     sec_value %= 3600
    #     min_value = sec_value // 60
    #     sec_value %= 60
    #     if hour_value != 0:
    #         death_time = f"{hour_value} hours, {min_value} minutes"
    #     else:
    #         death_time = f"{min_value} minutes"
    #     embed = discord.Embed(color=discord.colour.Color.red(),
    #                           title=f"{user.display_name}'s current game stats")
    #     embed.add_field(name="Time spent in game:", value=game_time, inline=True)
    #     embed.add_field(name="Time since last death:", value=death_time, inline=True)
    #     embed.add_field(name="Kills:", value=stats["kills"], inline=True)
    #     embed.add_field(name="Deaths:", value=stats["deaths"], inline=True)
    #     embed.add_field(name="XP level:", value=stats["level"], inline=True)
    #     embed.add_field(name="Health:", value=stats["health"], inline=True)
    #     embed.add_field(name="Hunger:", value=stats["food"], inline=True)
    #     embed.add_field(name="Times jumped:", value=stats["jumps"], inline=True)
    #     embed.add_field(name="World:", value=stats["world"], inline=True)
    #     embed.set_thumbnail(url=f"https://heads.discordsrv.com/head.png?name={user.display_name}&overlay")
    #     await ctx.send(embed=embed)


@slash.slash(
    name="doggo", guild_ids=bot.guild_ids, description="Sends a photo of a doggo"
)
async def doggo(ctx: Context):
    f = r"https://random.dog/woof.json"
    page = requests.get(f)
    data = json.loads(page.text)
    await ctx.send(data["url"])


@slash.slash(
    name="catto", guild_ids=bot.guild_ids, description="Sends a photo of a catto"
)
async def catto(ctx: Context):
    f = r"https://aws.random.cat/meow"
    page = requests.get(f)
    data = json.loads(page.text)
    await ctx.send(data["file"])


@bot.command(
    name="auth",
    pass_context=True,
    description="Checks the validity of a token",
    category="Utility",
)
async def auth(ctx, message):
    nonce = "SuperSecretNonce"
    f = f"https://api2.yubico.com/wsapi/2.0/verify?id=1&otp={message}&nonce={nonce}"
    page = requests.get(f)
    if config("yubi_key") in message:
        if nonce in page.text:
            if "status=OK" in page.text:
                await ctx.message.add_reaction("🔓")
                log = f'<p class="white">Authenticated'

                with open("messages.log", "a", encoding="utf8") as text_file:
                    print(log, file=text_file)
            elif "status=REPLAYED_REQUEST" in page.text:
                await ctx.message.add_reaction("❌")
                log = f'<p class="white">Replayed OTP'
                with open("messages.log", "a", encoding="utf8") as text_file:
                    print(log, file=text_file)
            elif "status=BAD_OTP" in page.text:
                await ctx.message.add_reaction("❌")
                log = f'<p class="white">OTP was invalid'
                with open("messages.log", "a", encoding="utf8") as text_file:
                    print(log, file=text_file)
            else:
                log = f'<p class="white">Recieved an invalid nonce'
                with open("messages.log", "a", encoding="utf8") as text_file:
                    print(log, file=text_file)

        else:
            await ctx.send("Something funky is going on")
    else:
        await ctx.send("Something funky is going on")


@slash.slash(
    name="arrest",
    guild_ids=bot.guild_ids,
    description="Arrests a member",
    options=[
        create_option(
            name="user",
            description="The user to arrest",
            option_type=option_type["user"],
            required=True,
        ),
        create_option(
            name="reason",
            description="The reason for the arrest",
            option_type=option_type["string"],
            required=True,
        ),
    ],
)
@check(has_perms)
async def arrest(ctx: SlashContext, user, reason):
    await ctx.send(
        f"{user.mention} has been arrested. Please wait\n",
        hidden=True,
    )
    mod_log = bot.get_channel(897765157940396052)
    category_name = "👮 Police Station"
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    staff = discord.utils.get(ctx.guild.roles, name="Staff")
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
        user: discord.PermissionOverwrite(read_messages=True),
        staff: discord.PermissionOverwrite(read_messages=True),
    }
    if category is None:
        category = await ctx.guild.create_category(
            category_name, overwrites=None, reason=None
        )
    channel = await ctx.guild.create_text_channel(
        str(user.display_name), overwrites=overwrites, reason=None, category=category
    )
    whitelist = discord.utils.get(ctx.guild.roles, name="Whitelisted")
    muted = discord.utils.get(ctx.guild.roles, name="Muted")
    await user.remove_roles(whitelist)
    await user.add_roles(muted)

    await mod_log.send(
        f"{ctx.author.display_name} arrested " f"{user.display_name} for {reason}"
    )
    await channel.send(
        f"{user.mention} you have been arrested for "
        f"{reason}. Please stand-by\n"
        # f"```You do not have to say anything. But, it may harm your defence if you do not mention"
        # f" when questioned something which you later rely on in court. "
        # f"Anything you do say may be given in evidence. "
        # f"You have the right to have a lawyer present both during questioning and during court"
        # f" proceedings.```"
    )


@slash.slash(
    name="release",
    guild_ids=bot.guild_ids,
    description="Releases a member from police custody",
    options=[
        create_option(
            name="user",
            description="The user to release",
            option_type=option_type["user"],
            required=True,
        )
    ],
)
@check(has_perms)
async def release(ctx: SlashContext, user):
    select = create_select(
        options=[
            create_select_option("No punishment", value="No punishment"),
            create_select_option("Temp ban", value="Temp ban"),
            create_select_option("Perma ban", value="Perma ban"),
            create_select_option("Mute", value="Mute"),
        ],
        custom_id=f"release{user.id}",
        placeholder="Select a punishment",
        min_values=1,
        max_values=4,
    )
    await ctx.send("Punishments", components=[create_actionrow(select)], hidden=True)


@slash.slash(name="kill", guild_ids=bot.guild_ids, description=f"Kills {bot_name}")
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
        creation = str((emoji.created_at - datetime(1970, 1, 1)).total_seconds()).split(
            "."
        )
        await ctx.send(
            f"{emoji} {emoji.name} ({emoji.id}) Created: <t:{creation[0]}:R>"
        )


bot.run(toe_ken)
