import interactions
from embed.osu import create_osu_embed
class Friend(interactions.Extension): # must have commands.cog or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="friend",
        description="add to, remove, or check a main users friend list",
        options= [interactions.Option(
            name="add",
            description="provide the username of the player you want to add",
            type=interactions.OptionType.STRING,
        ),
        interactions.Option(
            name="remove",
            description="provide the username of the player you want to remove",
            type=interactions.OptionType.STRING,
        ),
        interactions.Option(
            name="list",
            description="provide the username of the main user you want to list the friends of",
            type=interactions.OptionType.STRING,
    )],
    )
    async def __test(self, ctx: interactions.CommandContext, *args, **kwargs):
        pass

def setup(client):
    Friend(client)