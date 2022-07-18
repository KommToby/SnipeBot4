import discord, interactions

class Osu(interactions.Extension): # must have commands.cog or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.extension_command(
            name="osu", 
            description="get a users osu profile details",
            options=[interactions.Option(
                name="username",
                description="the username of the user",
                type=interactions.OptionType.STRING,
                required=True,
            )
        ]
    )
    async def osu(self, ctx: interactions.CommandContext, username: str):
        await ctx.send(f"You are '{username}'")

def setup(client):
    Osu(client)