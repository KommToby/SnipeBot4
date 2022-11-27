import interactions
from embed.snipeback import create_snipeback_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
import random


class Snipeback(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="snipeback",
        description="shows some maps the main user needs to play to snipe a friend",
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
        )
        ]
    )
    async def snipeback(self, ctx: interactions.CommandContext, *args, **kwargs):
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
        beatmaps, links, sort = await self.get_scores(main_user_data.id, user_data.id, sort_type)
        if beatmaps == []:
            await ctx.send(f"Main user has no scores on any maps that {user_data.username} has")
            return
        embed = await create_snipeback_embed(user_data.username, beatmaps, links, sort)
        await ctx.send(embeds=embed)

    async def get_scores(self, main_id: int, friend_id: int, sort_type: str):
        if sort_type == "random":
            sniped = await self.database.get_single_user_snipes_ids(main_id, friend_id)
            snipes = await self.database.get_single_user_snipes_ids(friend_id, main_id)
            random.shuffle(sniped)
            random.shuffle(snipes)
        
        if sort_type == "snipability":
            # first we get all snipability beatmaps from both users
            snipability_ids_main = await self.database.get_snipable_scores_beatmap_ids(main_id)
            snipability_ids_friend = await self.database.get_snipable_scores_beatmap_ids(friend_id)

            # then we get the snipability values
            snipability_main = await self.database.get_snipable_scores_values(main_id)
            snipability_friend = await self.database.get_snipable_scores_values(friend_id)

            # Now we get all snipes from both users
            sniped = await self.database.get_single_user_snipes_ids(main_id, friend_id)
            snipes = await self.database.get_single_user_snipes_ids(friend_id, main_id)

            # Now we only keep the snipes that are in the snipability list and append the snipability score to the snipe
            sniped = [x for x in sniped if x in snipability_ids_main]
            snipes = [x for x in snipes if x in snipability_ids_friend]

            new_sniped = []
            new_snipes = []
            for i in range(len(sniped)):
                # append to new_sniped the values of sniped with the snipability score as the last value
                new_sniped.append([sniped[i], snipability_main[i]])
            for i in range(len(snipes)):
                # append to new_snipes the values of snipes with the snipability score as the last value
                new_snipes.append([snipes[i], snipability_friend[i]])

            new_sniped.sort(key=lambda x: x[1], reverse=True)
            new_snipes.sort(key=lambda x: x[1], reverse=True)
            sniped = [x[0] for x in new_sniped]
            snipes = [x[0] for x in new_snipes]

        beatmaps = []
        beatmaps_data = []
        links = []
        # elements that are in snipes but not in sniped
        for snipe in snipes:
            if len(beatmaps) > 10:
                break
            if snipe not in sniped:
                beatmaps.append(snipe)
        for beatmap in beatmaps:
            beatmap_data = await self.database.get_beatmap(beatmap)
            if not(beatmap_data):
                continue
            beatmaps_data.append(beatmap_data)
            links.append(beatmap_data[5])
        return beatmaps_data, links, sort_type

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

    async def handle_linked_account(self, ctx, kwargs):
        if len(kwargs) > 0:
            return kwargs['username']
        else:
            username_array = await self.database.get_linked_user_osu_id(ctx.author.id._snowflake)
            if not username_array:
                await ctx.send("You are not linked to an osu! account - use `/link` to link your account\n"
                               "Alternatively you can do `/snipeback username:username` to get a specific persons profile")
                return False
            return username_array[0]


def setup(client):
    Snipeback(client)
