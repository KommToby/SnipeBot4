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
        ),
        interactions.Option(
            name="sort",
            description="the sort of the snipeback list: random, snipability",
            type=interactions.OptionType.STRING,
            required=False,
        ),
        interactions.Option(
            name="max-sr",
            description="maximum SR of the maps",
            type=interactions.OptionType.NUMBER,
            required=False,
        ),
        interactions.Option(
            name="min-sr",
            description="minimum SR of the maps",
            type=interactions.OptionType.NUMBER,
            required=False,
        ),
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
        if await self.handle_sort(ctx, kwargs):
            sort_type = await self.handle_sort(ctx, kwargs)
        else:
            return
        beatmaps, links = await self.get_scores(main_user_data.id, user_data.id, sort_type, kwargs)
        if beatmaps == []:
            await ctx.send(f"Main user has no scores on any maps that {user_data.username} has")
            return
        embed = await create_recommend_embed(user_data.username, beatmaps, links, sort_type)
        await ctx.send(embeds=embed)

    async def get_scores(self, main_id: int, friend_id: int, sort_type: str, kwargs):
        if len(kwargs) > 0:
            if "max-sr" in kwargs:
                max_sr = kwargs["max-sr"]
            else:
                max_sr = 1000
            if "min-sr" in kwargs:
                min_sr = kwargs["min-sr"]
            else:
                min_sr = 0
        if sort_type == "random":
            friend_scores_local = await self.database.get_min_max_scores_snipable_beatmap_ids(friend_id, min_sr, max_sr)
            main_scores = await self.database.get_min_max_scores_snipable_beatmap_ids(main_id, min_sr, max_sr)
            random.shuffle(friend_scores_local)
            random.shuffle(main_scores)
        elif sort_type == "snipability":
            friend_scores_local = await self.database.get_min_max_scores_snipable_beatmap_ids(friend_id, min_sr, max_sr) # these include scores with no snipability
            friend_scores = await self.database.get_min_max_scores_snipable(friend_id, min_sr, max_sr) # these only include scores with snipability
            main_scores = await self.database.get_min_max_scores_snipable(main_id, min_sr, max_sr)
            friend_scores.sort(key=lambda x: x[16], reverse=True)
            main_scores.sort(key=lambda x: x[16], reverse=True)

            # now we convert main_scores and friend_scores to only have beatmap ids
            friend_scores = [x[1] for x in friend_scores]
            main_scores = [x[1] for x in main_scores]

        beatmaps = []
        beatmaps_data = []
        checked_beatmap_ids = []
        links = []
        # elements that are in main_scores but not in friend_scores
        for _, score in enumerate(main_scores):
            if len(beatmaps) >= 10:
                break
            if score not in friend_scores_local:
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
            if "username" in kwargs:
                return kwargs['username']
            else:
                pass
        username_array = await self.database.get_linked_user_osu_id(ctx.author.id._snowflake)
        if not username_array:
            await ctx.send("You are not linked to an osu! account - use `/link` to link your account\n"
                            "Alternatively you can do `/recommend username:username` to get a specific persons profile")
            return False
        return username_array[0]

    async def handle_sort(self, ctx, kwargs):
        if len(kwargs) > 0:
            if "sort" in kwargs:
                if kwargs["sort"] == "random":
                    return "random"
                elif kwargs["sort"] == "snipability":
                    return "snipability"
                else:
                    await ctx.send("Invalid sort type! Valid types are `random` and `snipability`")
                    return False
            else:
                return "random"
        else:
            return "random"

def setup(client):
    Recommend(client)
