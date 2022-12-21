import interactions
from embed.snipeback import create_snipeback_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
import random
from interactions.ext.get import get


class Snipeback(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="snipeback",
        description="shows some maps the main user needs to play to snipe a friend",
        options=[interactions.Option(
            name="sort",
            description="the sort of the snipeback list",
            type=interactions.OptionType.STRING,
            required=True,
            choices=[
                {
                    "name": "Random",
                    "value": "random"
                },
                {
                    "name": "Snipability",
                    "value": "snipability"
                }
            ]
        ),
        interactions.Option(
            name="username",
            description="the username of the friend of the main user",
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
        beatmaps, links, sort = await self.get_scores(main_user_data.id, user_data.id, sort_type, kwargs)
        # beatmaps = await self.osu.get_beatmaps(beatmaps) not needed in this command
        if not(beatmaps):
            await ctx.send(f"Main user has no scores on any maps that {user_data.username} has with the given parameters!")
            return
        if beatmaps == []:
            await ctx.send(f"Main user has no scores on any maps that {user_data.username} has with the given parameters!")
            return
        embed = await create_snipeback_embed(user_data.username, beatmaps, links, sort)
        await ctx.send(embeds=embed)

    async def double_check_scores(self, beatmaps, friend_id, ctx, links):
        # This checks all 10 beatmaps to see if the user actually has a score on it
        # Since the database is not 100% accurate, this is needed
        for i, beatmap in enumerate(beatmaps):
            scores = await self.osu.get_score_data(beatmap[0], friend_id)
            if scores:
                # The program should update the score data if it is not up to date
                # First we check if the score is local, but just 0
                beatmaps.remove(beatmap)
                links.remove(links[i])
                newctx = await get(self.client, interactions.Channel,
                                       channel_id=int(ctx.channel_id._snowflake))
                await newctx.send(f"Queued score data Scan for {beatmap[0]}...")
                # Now we tell the program to rescan the beatmap
                self.client.tracker.rescan_beatmaps.append(beatmap[0])
        return beatmaps, links

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
        else:
            max_sr = 1000
            min_sr = 0
        if sort_type == "random":
            # first we get the snipes of the main user and friends
            sniped = await self.database.get_single_user_snipes_ids(main_id, friend_id)
            snipes = await self.database.get_single_user_snipes_ids(friend_id, main_id)

            # Now we get the scores of the main user and friends with min and max sr
            main_scores = await self.database.get_min_max_scores_beatmap_ids(main_id, min_sr, max_sr)
            friend_scores = await self.database.get_min_max_scores_beatmap_ids(friend_id, min_sr, max_sr)

            # Check if the scores exist for the parameters
            if not(main_scores) or not(friend_scores):
                return False, False, False

            # Now shuffle the sniped and snipes lists
            random.shuffle(sniped)
            random.shuffle(snipes)
        
        if sort_type == "snipability":
            # first we get all snipability beatmaps from both users
            snipability_ids_main = await self.database.get_min_max_scores_snipable_beatmap_ids(main_id, min_sr, max_sr)
            snipability_ids_friend = await self.database.get_min_max_scores_snipable_beatmap_ids(friend_id, min_sr, max_sr)

            # then we get the snipability values
            snipability_main = await self.database.get_min_max_scores_snipable_values(main_id, min_sr, max_sr)
            snipability_friend = await self.database.get_min_max_scores_snipable_values(friend_id, min_sr, max_sr)

            # Now we get all snipes from both users
            sniped = await self.database.get_single_user_snipes_ids(main_id, friend_id)
            snipes = await self.database.get_single_user_snipes_ids(friend_id, main_id)

            # Now we only keep the snipes that are in the snipability list and append the snipability score to the snipe
            sniped = [x for x in sniped if x in snipability_ids_friend]
            snipes = [x for x in snipes if x in snipability_ids_main]

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

        beatmaps_data = []
        links = []
        # elements that are in snipes but not in sniped
        for snipe in snipes:
            if len(beatmaps_data) > 10:
                break
            if snipe not in sniped:
                beatmap_data = await self.database.get_beatmap(snipe)
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
        else:
            return "random"

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


def setup(client):
    Snipeback(client)
