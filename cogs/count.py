import interactions
from data_types.osu import UserData
from embed.count import create_count_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
import random


class Count(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="count",
        description="shows how many maps a player has played mapped by another player",
        options=[interactions.Option(
            name="player",
            description="the username of the player",
            type=interactions.OptionType.STRING,
            required=True,
        ),interactions.Option(
            name="mapper",
            description="the username of the mapper",
            type=interactions.OptionType.STRING,
            required=True,
        )
        ]
    )
    async def count(self, ctx: interactions.CommandContext, *args, **kwargs):
        await ctx.defer()
        username, mapper = await self.handle_linked_account(ctx, kwargs)
        if not(username):
            return
        user_data = await self.osu.get_user_data(username)
        mapper_data = await self.osu.get_user_data(mapper)
        if not(user_data):
            await ctx.send(f"User {username} not found!")
            return
        if not(mapper_data):
            await ctx.send(f"User {mapper} not found!")
            return

        # first we get all scores that the user has played
        all_user_scores = await self.database.get_all_scores(user_data.id)

        # then we get all maps that the mapper has mapped
        all_beatmaps = await self.database.get_all_beatmaps_mapper(mapper_data.username)

        # then we get all scores that the user has played that the mapper has mapped
        all_user_scores_mapper = []
        for score in all_user_scores:
            if str(score[1]) in all_beatmaps:
                all_user_scores_mapper.append(score)

        embed = await create_count_embed(user_data.username, mapper_data.username, all_user_scores_mapper)
        await ctx.send(embeds=embed)

    async def handle_linked_account(self, ctx, kwargs):
        if len(kwargs) <2:
            await ctx.send("You need to specify both a player and a mapper!")
            return False, False
        username = kwargs["player"]
        mapper = kwargs["mapper"]
        return username, mapper

def setup(client):
    Count(client)
