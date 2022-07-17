import json
from discord.ext import commands

with open("config.json") as f:
    DISCORD_CONFIG_DATA = json.load(f)["discord"]
    TOKEN = DISCORD_CONFIG_DATA["token"]

# Define Bot
client = commands.Bot(command_prefix="-")

# Bot Online
@client.event
async def on_ready():
    try:
        print("Bot Connected To Discord")
        # Add Cog Data Here
    except Exception as e:
        print("Bot Failed To Connect To Discord")

# must be final line
if __name__ == '__main__':
    client.run(TOKEN)