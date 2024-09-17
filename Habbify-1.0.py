import discord
from discord.ext import commands
import requests
import random
import string

# Initialize the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True  # Ensure the bot can receive member updates
bot = commands.Bot(command_prefix='!', intents=intents)

# Replace with your Discord bot token
TOKEN = "TOKEN CODE LULZ"

# Replace with your Discord role name
ROLE_NAME = 'Verified'

# Replace with your verification channel ID
VERIFICATION_CHANNEL_ID = 1266113768631566367  # Replace with your verification channel ID

# Dictionary to store user verification codes
verification_codes = {}

# Function to generate a random verification code
def generate_verification_code(length=6):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.event
async def on_member_join(member):
    # Create an embed with introduction message
    embed_intro = discord.Embed(
        title="Welcome to the Server!",
        description=(
            "To get verified, follow these steps:\n"
            "1. Type `!verify <your_habbo_username>` in any channel to start the verification process.\n"
            "2. You will receive a DM from the bot with a verification code.\n"
            "3. Add the code to your Habbo motto.\n"
            "4. Return to this server and type `!verify <your_habbo_username> confirm` to complete the verification.\n"
            "5. If the code is correct, you will be granted the Verified role.\n\n"
            "If you encounter any issues, please contact a server admin."
        ),
        color=discord.Color.blue()
    )
    try:
        await member.send(embed=embed_intro)
        print(f"Sent introduction message to {member.name}.")
    except discord.Forbidden:
        print(f"Could not send introduction message to {member.name}. They may have DMs disabled.")

@bot.command(name='verify')
async def verify(ctx, username: str, action: str = None):
    if action is None:
        # Start the verification process
        code = generate_verification_code()
        verification_codes[username] = {'code': code, 'user': ctx.author}

        # Fetch Habbo user data
        response = requests.get(f"https://origins.habbo.com/api/public/users?name={username}")
        if response.status_code != 200:
            embed_error = discord.Embed(
                title="Error",
                description=f"Failed to fetch data for {username}. Please try again.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_error)
            return

        habbo_data = response.json()
        if not habbo_data:
            embed_error = discord.Embed(
                title="Error",
                description=f"No data found for Habbo username `{username}`.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_error)
            return

        # Send verification code to user via DM
        embed_dm = discord.Embed(
            title="Verification Code",
            description=f"Your verification code is: **{code}**. Please add this code to your Habbo motto and confirm by typing `!verify {username} confirm`.",
            color=discord.Color.blue()
        )
        await ctx.author.send(embed=embed_dm)

        # Notify the user
        embed_channel = discord.Embed(
            title="Verification Started",
            description=f"A verification code has been sent to your DMs, {ctx.author.mention}.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed_channel)

    elif action == 'confirm':
        # Confirm the verification code
        if username in verification_codes:
            user_data = verification_codes[username]
            if user_data['user'] != ctx.author:
                await ctx.send("You are not authorized to confirm this verification process.")
                return

            response = requests.get(f"https://origins.habbo.com/api/public/users?name={username}")
            if response.status_code != 200:
                embed_error = discord.Embed(
                    title="Error",
                    description=f"Failed to fetch data for {username}. Please try again.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed_error)
                return

            habbo_data = response.json()
            code = user_data['code']
            if 'motto' in habbo_data and code in habbo_data['motto']:
                # Check if role exists in the guild
                role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)
                if role is None:
                    embed_error = discord.Embed(
                        title="Error",
                        description=f"The role '{ROLE_NAME}' does not exist in this server.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed_error)
                    return
                
                # Ensure the bot has permission to assign roles
                if ctx.guild.me.guild_permissions.manage_roles:
                    await ctx.author.add_roles(role)
                    embed_success = discord.Embed(
                        title="Verification Successful",
                        description=f"Welcome, {ctx.author.mention}! You have been verified.",
                        color=discord.Color.green()
                    )
                    await ctx.send(embed=embed_success)
                    del verification_codes[username]
                else:
                    embed_error = discord.Embed(
                        title="Error",
                        description="I don't have permission to manage roles.",
                        color=discord.Color.red()
                    )
                    await ctx.send(embed=embed_error)
            else:
                embed_error = discord.Embed(
                    title="Verification Failed",
                    description="The code is not in your motto.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed_error)
        else:
            embed_error = discord.Embed(
                title="Error",
                description=f"No verification process found for {username}. Please start with `!verify {username}`.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed_error)

bot.run(TOKEN)
