import interactions


class Ping(interactions.Extension):  # must have interactions.Extension or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_command(name="ping", description="pong!")
    async def ping(self, ctx):
        await ctx.defer()
        await ctx.send("Pong!")


def setup(client):
    Ping(client)
