# pip install -U discord-py-interactions
import json, discord, interactions, os
from discord.ext import commands

with open("config.json") as f:
    DISCORD_CONFIG_DATA = json.load(f)["discord"]
    TOKEN = DISCORD_CONFIG_DATA["token"]

# Define Bot
client = interactions.Client(TOKEN)

# Bot Online
@client.event
async def on_ready():
    print("\n\n\n\n\n\n\n\n")
    try:
        print("Bot Connected To Discord")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                client.load(f"cogs.{filename[:-3]}")
        print("All cogs loaded successfully")
    except Exception as e:
        print(f"An Error Occured: {e}")

# must be final line
if __name__ == '__main__':
    client.start()