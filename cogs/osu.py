import interactions, asyncio
from embed.osu import create_osu_embed
class Osu(interactions.Extension): # must have interactions.Extension or this wont work
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
        await ctx.defer()
        recent_plays = await self.osu.get_recent_plays("3637436")
        score_data = await self.osu.get_score_data("848345", "10609949")
        score_data_mods = await self.osu.get_beatmap_mods("848345", "64")
        beatmap_data = await self.osu.get_beatmap("2077721")
        user_data = await self.osu.get_user_data(username)
        embed = await create_osu_embed(user_data)
        await ctx.send(embeds=embed)

def setup(client):
    Osu(client)