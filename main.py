# pip install -U discord-py-interactions
# pip install -u interactions-get
# pip install -U git+https://github.com/interactions-py/library@unstable
import json, interactions, os, asyncio
from osu_auth import auth
from database import _init_db
from tracker import SnipeTracker

with open("config.json") as f:
    DISCORD_CONFIG_DATA = json.load(f)["discord"]
    TOKEN = DISCORD_CONFIG_DATA["token"]

# Define Bot

# IMPORTANT: IF NOT CHANGING ANY COGS - ENABLE DISABLE_SYNC BELOW
# WHEN DISABLE_SYNC IS TRUE IT DOES NOT CALL THE DISCORD API FOR INTERACTIONS
client = interactions.Client(TOKEN, disable_sync=True)
client.auth = auth.Auth()
client.database  = _init_db.Database('database.db')
client.tracker = SnipeTracker(client)
client.running = False

# Bot Online
@client.event
async def on_ready():
    print("\n\n\n\n\n\n\n\n")
    try:
        print("Bot Connected To Discord")
        if client.running == False:
            client.running = True
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    client.load(f"cogs.{filename[:-3]}")
            print("All cogs loaded successfully")
            print("Starting main loop in 10 seconds")
            await asyncio.sleep(10)
            await client.tracker.start_loop()
        else:
            pass
    except Exception as e:
        print(f"An Error Occured: {e}")

# must be final line
if __name__ == '__main__':
    client.start()