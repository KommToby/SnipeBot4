import interactions
from embed.osu import create_osu_embed
class Osu(interactions.Extension): # must have commands.cog or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client
        self.osu = client.auth

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
        recent_plays = await self.osu.get_recent_plays("7671790")
        score_data = await self.osu.get_score_data("2077721", "7671790")
        beatmap_data = await self.osu.get_beatmap("2077721")
        user_data = await self.osu.get_user_data(username)
        embed = await create_osu_embed(user_data)
        await ctx.send(embeds=embed)

def setup(client):
    Osu(client)