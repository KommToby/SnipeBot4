import interactions
from embed.osu import create_osu_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog

class Osu(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="osu",
        description="get a users osu profile details",
        options=[interactions.Option(
            name="username",
            description="the username of the user",
            type=interactions.OptionType.STRING,
            required=False,
        )
        ]
    )
    async def osu(self, ctx: interactions.CommandContext, *args, **kwargs):
        await ctx.defer()
        username = await self.handle_linked_account(ctx, kwargs)
        if not username:
            return
        recent_plays = await self.osu.get_recent_plays("4934554")
        score_data = await self.osu.get_score_data("848345", "10609949")
        score_data_mods = await self.osu.get_beatmap_mods("848345", "64")
        beatmap_data = await self.osu.get_beatmap("2077721")
        user_data = await self.osu.get_user_data(username)
        embed = await create_osu_embed(user_data)
        await ctx.send(embeds=embed)

    async def handle_linked_account(self, ctx, kwargs):
        if len(kwargs) > 0:
            return kwargs['username']
        else:
            username_array = await self.database.get_linked_user_osu_id(ctx.author.id._snowflake)
            if not username_array:
                await ctx.send("You are not linked to an osu! account - use `/link` to link your account\n"
                               "Alternatively you can do `/osu username:username` to get a specific persons profile")
                return False
            return username_array[0]


def setup(client):
    Osu(client)
