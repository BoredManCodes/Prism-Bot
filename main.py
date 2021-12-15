Diffchecker logo
Diffchecker


Text


Images


PDF


Excel


Folders
Desktop App
Pricing
Sign in
Create an account
Download Diffchecker Desktop
Saved Diffs
You must be signed in to save diffs
Sign In
Diff history
now
Clear
Diff history is cleared on refresh
Real-timeRegular
SplitUnified
WordCharacter

Tools
-3 Removals+9 Additions
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
@bot.command()
async def welcomemsg(ctx):
    # Send the welcome message
    title = "Welcome to Prism SMP!"
    description = "You can grab some self roles over in <#861288424640348160>.\n" \
                  "The IP is in <#858549386962272296>" \
                  " (You don't have to read the entirety of that)\n" \
                  " Ask in <#869280855657447445> to get yourself whitelisted.\n\n" \
                  "**Rules:**\n" \
                  "1. Follow the [Discord ToS](https://discord.com/terms).\n" \
                  "2. No hate speech or harassment.\n" \
                  "3. Keep the server PG-13.\n" \
                  "4. Do not hack or use any unofficial applications that give you an advantage. Optifine is ok.\n" \
                  "5. Respect player's claims and boundaries.\n" \
                  "6. Do not grief the server. This includes stealing from other players.\n" \
                  "7. Do not go around killing everyone you see. Essentially, be nice.\n" \
                  "8. Listen to the staff, they're here to help.\n" \
                  "9. Don't spam in the discord or the server.\n" \
                  "10. Please don't build in a 500 block radius around spawn. " \
                  "This space is dedicated to community projects such as the shopping and mini-games districts\n" \
                  "11. Have fun!\n\n" \
                  "For a full list of your rights as a member, see the constitution. "
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
Editor
Compare & merge
Clear
Export as PDF
Save DiffShare
No file chosenOriginal Text
2018
2019
2020
2021
2022
2023
2024
2025
2026
2027
2028
2029
2030
2031
2032
2033
2034
2035
2036
2037
2038
2039
2040
2041
2042
2043
2044
2045
2046
2047
2048
2049
2050
2051
2052
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


@bot.command()
async def snowflake(ctx, snowflake = None):
    if snowflake is None:
        snowflake = ctx.message.author
    creation = str((snowflake.created_at - datetime(1970, 1, 1)).total_seconds()).split('.')
    await ctx.send(f"Snowflake {snowflake} was created: <t:{creation[0]}:R>")


@bot.command()
@is_owner()
async def emojilist(ctx):
    await ctx.message.delete()
    for emoji in ctx.guild.emojis:
        creation = str((emoji.created_at - datetime(1970, 1, 1)).total_seconds()).split('.')
        await ctx.send(f"{emoji} {emoji.name} ({emoji.id}) Created: <t:{creation[0]}:R>")


bot.run(toe_ken)

No file chosenChanged Text
2023
2024
2025
2026
2027
2028
2029
2030
2031
2032
2033
2034
2035
2036
2037
2038
2039
2040
2041
2042
2043
2044
2045
2046
2047
2048
2049
2050
2051
2052
2053
2054
2055
2056
2057

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


@bot.command()
async def snowflake(ctx, snowflake = None):
    if snowflake is None:
        snowflake = ctx.message.author
    creation = str((snowflake.created_at - datetime(1970, 1, 1)).total_seconds()).split('.')
    await ctx.send(f"Snowflake {snowflake} was created: <t:{creation[0]}:R>")


@bot.command()
@is_owner()
async def emojilist(ctx):
    await ctx.message.delete()
    for emoji in ctx.guild.emojis:
        creation = str((emoji.created_at - datetime(1970, 1, 1)).total_seconds()).split('.')
        await ctx.send(f"{emoji} {emoji.name} ({emoji.id}) Created: <t:{creation[0]}:R>")


bot.run(toe_ken)
