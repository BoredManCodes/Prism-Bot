import discord.ext
from discord.ext import commands
import discord
from decouple import config
from discord_slash import SlashCommand, SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import wait_for_component

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


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


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
@commands.has_role('Staff')
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
@commands.has_role('Staff')
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


@bot.command(name='bolte', aliases=['boltecommands', 'bc'], pass_context=True)
async def bolte(ctx):

    help = "**Prismian Commands:**\n`/iam` Allows you to choose roles\n`/iamnot` Removes those roles\n"\
           "`/reminder create` Kinda self-explanatory\n`/reminder view` See above\n"\
           "`/suggestion create` Creates a suggestion for the staff to review\n"\
           "`/spotify` Easily share what you're currently listening to\n`$play <song>` Plays music in your VC\n`$skip` Skips your song"
    embed = discord.Embed(title="Prism Bot Command Help", description=help, color=ctx.message.author.color)
    embed.set_footer(text="Issued by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@slash.slash(name="staff-commands",
             guild_ids=guilds,
             description="displays the list of staff commands")
@commands.has_role('Staff')
async def staff(ctx):

    help = "**Staff Commands**\n"\
           "`/self-roles add` Adds a role to the `/iam` command\n`/self-roles remove` Does the opposite\n"\
           "`/poll` Creates a poll for people to vote on\n"\
           "`/suggestion view` A nifty menu for viewing suggestions\n"\
           "`$warn <user> <reason>` Warns the mentioned user for the stated reason\n"\
           "`$ban <user> <reason>` Bans the mentioned user for the stated reason\n`/whitelist <user>` Whitelists the user"
    embed = discord.Embed(title="Prism Bot Command Help", description=help, color=ctx.author.color)
    embed.set_footer(text="Issued by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='staff', aliases=['staffcommands', 'sc'], pass_context=True)
@commands.has_role('Staff')
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


# @bot.command(name='list', pass_context=True)
# @commands.has_role('Staff')
# async def list(ctx, *, role: discord.Role):
#     usernames = [m.display_name for m in role.members]
#     count = 0
#     for m in role.members:
#         count += 1
#     title_text = count, "members with the", role.name, "role"
#     title = str(title_text).replace(',', '').replace('(', '').replace(')', '').replace('\'', '')
#     description = str(sorted(usernames, key=str.lower)).replace(',', '\n').replace('[', '').replace(']', '').replace('\'', '')
#     embed = discord.Embed(title=title, description=description, color=discord.Color.random())
#     embed.set_footer(text="Issued by " + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
#     await ctx.send(embed=embed)


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
                     required=False
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
@commands.has_role('Staff')
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
@commands.has_role('Staff')
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
@commands.has_role('Staff')
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
                     required=False
                 ), create_option(
                     name="silent",
                     description="Whether to show the creator",
                     option_type=option_type["boolean"],
                     required=True
                 )
             ])
@commands.has_role('Staff')
async def embed(ctx: SlashContext, *, embedlink, title, description, silent):
    #msg = await oldembed.channel.fetch_message(757114312413151272)
    newembed = discord.Embed(title=title, description=description, color=ctx.author.color)
    if not silent:
        embed.set_footer(text="Issued by " + ctx.author.display_name, icon_url=ctx.author.avatar_url)
    await ctx.send("Embed edited", hidden=True)
    editembed = embedlink.split('/')
    message = await bot.get_guild(int(editembed[-3])).get_channel(int(editembed[-2])).fetch_message(int(editembed[-1]))
    await message.edit(embed=newembed)


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
bot.run(toe_ken)



