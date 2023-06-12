# Contact Photron#2028 for any assistance | Made with <3

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
ROLE_ID = None
PREFIX = "."

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user.name}')

@bot.command()
async def start(ctx):
    global ROLE_ID
    channel_name = f'{bot.user.name}_staffmail'
    guild = ctx.guild

    channel = await guild.create_text_channel(channel_name)
    await channel.send("Please enter the ROLE_ID as an integer:")
    def check(message):
        return message.channel and message.content.isdigit()
    msg = await bot.wait_for('message', check=check, timeout=60)
    ROLE_ID = int(msg.content)

    embed = discord.Embed(title='INITIATED!', description="hello! this is staff mail bot made by Photron. Please type `.send` to start sending staff mails or `.help` for assistance")
    await channel.send(embed=embed)


@bot.command()
async def send(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Type the full message then hit the send button")

    message = await bot.wait_for("message", check=check, timeout=60)
    confirmation_message = await ctx.send(f"Confirm sending the following message to all members? \n\n{message.content}")

    await confirmation_message.add_reaction("✅")
    await confirmation_message.add_reaction("❌")

    def reaction_check(reaction, user):
        return (
            user == ctx.author
            and reaction.message.id == confirmation_message.id
            and str(reaction.emoji) in ["✅", "❌"]
        )

    reaction, _ = await bot.wait_for("reaction_add", check=reaction_check, timeout=60)

    if str(reaction.emoji) == "✅":
        role = ctx.guild.get_role(ROLE_ID)
        if not role:
            await ctx.send('Invalid role ID.')
            return

        members = role.members
        for member in members:
            embed = discord.Embed(title=f'Staff announcement: {ctx.guild}', description=message.content, color=0x0000FF)
            try:
                await member.send(embed=embed)
                await ctx.send(f"Message sent to the members with the role `<@&{ROLE_ID}>`")
                print(f'Sent message to {member.name}#{member.discriminator}')
            except discord.Forbidden:
                channel = await ctx.guild.create_text_channel(name=f"{member.name.lower()}-announcement")
                await channel.send(member.mention)
                await channel.send(embed=embed)
                print(f'Failed to send message to {member.name}#{member.discriminator}. Created channel: {channel.name}')
                channel_deletion = await channel.send("I've read the message already. [Please try keeping the DMs open for the bot to function smoothly.]")
                await channel_deletion.add_reaction("✅")
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) == '✅'
                reaction, user = await bot.wait_for('reaction_add', check=check)
                await channel.delete()
                print(f"{member.name}#{member.discriminator} has read the message and deleted the channel.")

    else:
        await ctx.send("Message sending canceled.")

bot.run(TOKEN)
