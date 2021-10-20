import discord
import discord.ext
from discord.ext import commands
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='?', intents=intents)
bot.remove_command('help')


@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.errors.CheckFailure):
        embed = discord.Embed(title="We ran into an error", description="You are not staff", color=discord.Color.red())
        embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="We ran into an error", description="You forgot to define any changes", color=discord.Color.red())
        embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.BotMissingPermissions):
        embed = discord.Embed(title="We ran into an error", description="I am missing permissions to delete my invoking command", color=discord.Color.red())
        embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="We ran into an undefined error", description=error, color=discord.Color.red())
        embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command(name='lp', pass_context=True)
@commands.has_role('staff')
async def lp(ctx, *, message):

    changes = "```diff\n" + message + "```"
    embed = discord.Embed(title="Permission Changelog", description=changes, color=0x00ff40)
    embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='embed', pass_context=True)
@commands.has_role('staff')
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
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Issued by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


bot.run('NEARLY CAUGHT ME')



