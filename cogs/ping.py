import discord, interactions

class Ping(interactions.Extension): # must have commands.cog or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="ping", description="pong!")
    async def ping(self, ctx):
        await ctx.send("Pong!")

def setup(client):
    Ping(client)