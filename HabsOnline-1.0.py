import discord
import requests

# Create a new instance of a client for the Discord bot
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# Replace with your Discord bot token
DISCORD_BOT_TOKEN = 'YOUR_DISCORD_BOT_TOKEN'

# Custom list of usernames to check
custom_usernames = ["Summer", "Cai", "Earwig"]  # Add any usernames you want

# Function to fetch user data from the Habbo API
def fetch_user_data(username):
    url = f'https://origins.habbo.com/api/public/users?name={username}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for 4xx/5xx status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user data: {e}")
        return None

# Event handler when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

# Event handler when the bot receives a message
@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message starts with !online
    if message.content == '!online':
        # Iterate over the custom list of usernames and fetch their data
        for username in custom_usernames:
            user_data = fetch_user_data(username)

            if user_data:
                # Extract relevant user data from the response
                online_status = 'online' if user_data.get('online', False) else 'offline'
                user_info = (
                    f"**Username:** {user_data.get('name', 'N/A')}\n"
                    f"**Motto:** {user_data.get('motto', 'N/A')}\n"
                    f"**Online Status:** {online_status}\n"
                    f"**Creation Date:** {user_data.get('memberSince', 'N/A')}\n"
                    f"**Current Level:** {user_data.get('currentLevel', 'N/A')}\n"
                    "-----------------------"
                )
                await message.channel.send(user_info)
            else:
                await message.channel.send(f'Could not fetch data for user: {username}')

# Start the bot using your token
client.run(DISCORD_BOT_TOKEN)
