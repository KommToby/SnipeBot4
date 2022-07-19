# pip install -U discord-py-interactions
# pip install -u interactions-get
import json, interactions, os
from osu_auth import auth
from database import _init_db
from tracker import SnipeTracker

with open("config.json") as f:
    DISCORD_CONFIG_DATA = json.load(f)["discord"]
    TOKEN = DISCORD_CONFIG_DATA["token"]

# Define Bot
client = interactions.Client(TOKEN)
client.auth = auth.Auth()
client.database  = _init_db.Database()
client.tracker = SnipeTracker(client)

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
        await client.tracker.start_loop()
    except Exception as e:
        print(f"An Error Occured: {e}")

# must be final line
if __name__ == '__main__':
    client.start()