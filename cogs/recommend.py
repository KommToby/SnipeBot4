import interactions
from data_types.osu import UserData
from embed.recommend import create_recommend_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
import random


class Recommend(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="recommend",
        description="shows some maps the friend should snipe the main user on",
        options=[interactions.Option(
            name="username",
            description="the username of the friend of the main user",
            type=interactions.OptionType.STRING,
            required=False,
        )
        ]
    )
    async def recommend(self, ctx: interactions.CommandContext, *args, **kwargs):
        await ctx.defer()
        username = await self.handle_linked_account(ctx, kwargs)
        if not(username):
            return
        main_user_id_array = await self.database.get_channel(ctx.channel_id._snowflake)
        if not(main_user_id_array):
            await ctx.send(f"Either nobody is being tracked in this channel, or you've used the command in the wrong channel!")
            return
        user_data = await self.osu.get_user_data(username)
        if not(user_data):
            await ctx.send(f"User {username} not found!")
            return
        main_user_data = await self.osu.get_user_data(main_user_id_array[1])
        if not(main_user_data):
            await ctx.send(f"Main user not found!")
            return
        beatmaps, links = await self.get_scores(main_user_data.id, user_data.id)
        if beatmaps == []:
            await ctx.send(f"Main user has no scores on any maps that {user_data.username} has")
            return
        embed = await create_recommend_embed(user_data.username, beatmaps, links)
        await ctx.send(embeds=embed)

    async def get_scores(self, main_id: int, friend_id: int):
        friend_scores = await self.database.get_all_scores_beatmap_ids(friend_id)
        main_scores = await self.database.get_all_scores_beatmap_ids(main_id)
        random.shuffle(friend_scores)
        random.shuffle(main_scores)
        beatmaps = []
        beatmaps_data = []
        checked_beatmap_ids = []
        links = []
        # elements that are in main_scores but not in friend_scores
        for _, score in enumerate(main_scores):
            if len(beatmaps) >= 10:
                break
            if score not in friend_scores:
                beatmaps.append(score)
                if score not in checked_beatmap_ids:
                    beatmap_data = await self.database.get_beatmap(score)
                    if beatmap_data:
                        beatmaps_data.append(beatmap_data)
                        links.append(beatmap_data[5])
                        checked_beatmap_ids.append(score)
        return beatmaps_data, links

    async def handle_linked_account(self, ctx, kwargs):
        if len(kwargs) > 0:
            return kwargs['username']
        else:
            username_array = await self.database.get_linked_user_osu_id(ctx.author.id._snowflake)
            if not username_array:
                await ctx.send("You are not linked to an osu! account - use `/link` to link your account\n"
                               "Alternatively you can do `/recommend username:username` to get a specific persons profile")
                return False
            return username_array[0]


def setup(client):
    Recommend(client)
