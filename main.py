import discord
import discord.ext
from discord.ext import commands
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)
bot.remove_command('help')


@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.errors.CheckFailure):
        embed = discord.Embed(title="We ran into an error", description="You are not staff", color=discord.Color.red())
        embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="We ran into an error", description="You forgot to define a message", color=discord.Color.red())
        embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.BotMissingPermissions):
        embed = discord.Embed(title="We ran into an error", description="I am missing permissions to delete my invoking command", color=discord.Color.red())
        embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.CommandNotFound):
        try:
            print("Doing nothing since this command doesn't exist")
        except:
            crash = True
    else:
        embed = discord.Embed(title="We ran into an undefined error", description=error, color=discord.Color.red())
        embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command(name='lp', pass_context=True)
@commands.has_role('Staff')
async def lp(ctx, *, message):
    await ctx.message.delete()
    changes = "```diff\n" + message + "```"
    embed = discord.Embed(title="Permission Changelog", description=changes, color=0x00ff40)
    embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='game', aliases=['gamecommands', 'gc'], pass_context=True)
async def game(ctx):

    help = "**Discord Commands:** (can only be run in #in-game-chat)\n`/inv` Shows the contents of your inventory\n"\
           "`/ender` Shows the contents of your enderchest\n\n**In-game Commands**\n"\
           "`[ec]` Broadcasts the contents of your enderchest\n[inv]` Broadcasts the contents of your inventory\n"\
           "`[item]` Broadcasts your currently held item\n`[pos]` Broadcasts your position\n"\
           "`[ping]` Catching on yet?\n`/t <message>` Shortcut for team message"
    embed = discord.Embed(title="Game Command Help", description=help, color=discord.Color.blue())
    embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='bolte', aliases=['boltecommands', 'bc'], pass_context=True)
async def bolte(ctx):

    help = "**Prismian Commands:**\n`/iam` Allows you to choose roles\n`/iamnot` Removes those roles\n"\
           "`/reminder create` Kinda self-explanatory\n`/reminder view` See above\n"\
           "`/suggestion create` Creates a suggestion for the staff to review\n"\
           "`/spotify` Easily share what you're currently listening to\n\n**Staff Commands**\n"\
           "`/self-roles add` Adds a role to the `/iam` command\n`/self-roles remove` Does the opposite\n"\
           "`/poll` Creates a poll for people to vote on\n"\
           "`/suggestion view` A nifty menu for viewing suggestions\n"\
           "`$warn <user> <reason>` Warns the mentioned user for the stated reason\n"\
           "`$ban <user> <reason>` Bans the mentioned user for the stated reason"
    embed = discord.Embed(title="Bolte:tm: Command Help", description=help, color=discord.Color.blue())
    embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)



@bot.command(name='embed', pass_context=True)
@commands.has_role('Staff')
async def embed(ctx, title, description, color):
    if color == "red":
        color = discord.Color.red()
    elif color == "blue":
        color = discord.Color.blue()
    elif color == "green":
        color = discord.Color.green()
    elif color == "yellow":
        color = discord.Color.yellow()
    elif color == "black":
        color = discord.Color.black()
    else:
        color = discord.Color.green()
    await ctx.message.delete()
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='whitelist', pass_context=True)
@commands.has_role('Staff')
async def whitelist(ctx, member: discord.Member):
    await ctx.message.delete()
    channel = bot.get_channel(869280855657447445)
    role = discord.utils.get(member.guild.roles, id=899568696593367070)
    await member.add_roles(role)
    message = "Added " + member.display_name + " to the whitelist"
    embed = discord.Embed(title="Whitelisted", description=message, color=discord.Color.green())
    embed.set_footer(text="Whitelisted by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await channel.send(embed=embed)


@bot.command(name='warn', pass_context=True)
@commands.has_role('Staff')
async def warn(ctx, member: discord.Member):
    channel = bot.get_channel(869280855657447445)
    role = discord.utils.get(member.guild.roles, id=900351762395975691)
    await member.add_roles(role)


bot.run('NEARLY CAUGHT ME')



