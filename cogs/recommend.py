import interactions
from data_types.osu import UserData
from embed.recommend import create_recommend_embed, create_recommend_embed_main
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
import random
from interactions.ext.get import get
import asyncio


class Recommend(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="recommend",
        description="shows some maps the friend should snipe the main user on",
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
        if str(main_user_data.id) == str(user_data.id):
            await self.main_user_recommendations(main_user_data, ctx, kwargs)
            return
        if await self.handle_sort(ctx, kwargs):
            sort_type = await self.handle_sort(ctx, kwargs)
        else:
            return
        beatmaps, links = await self.get_scores(main_user_data.id, user_data.id, sort_type, kwargs)
        beatmaps, links = await self.double_check_scores(beatmaps, user_data.id, ctx, links)
        if beatmaps == []:
            await ctx.send(f"Main user has no scores on any maps that {user_data.username} has")
            return
        embed = await create_recommend_embed(user_data.username, beatmaps, links, sort_type)
        await ctx.send(embeds=embed)

    async def main_user_recommendations(self, main_user_data, ctx, kwargs):
        # first we get all of the friends of the main user
        friends = await self.database.get_main_user_friends(ctx.channel_id._snowflake)
        if not friends:
            await ctx.send("Either main user has no friends, or you've used the command in the wrong channel!")
            return
        
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

        snipable_plays_snipability = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        snipable_plays_ids = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        snipable_plays_user_ids = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        # Now we randomise the friends list
        random.shuffle(friends)

        # now we get all the non-zero scores for every friend
        # if the snipability of the score is in the top 25 lowest in the list, we add it to the list and remove the highest
        for friend in friends:
            await asyncio.sleep(0.1)
            # if the lowest snipability is 70% or higher, we stop
            if min(snipable_plays_snipability) >= 0.7:
                break
            scores_snipability = await self.database.get_min_max_scores_snipable_values(friend[1], min_sr, max_sr)
            scores_ids = await self.database.get_min_max_scores_snipable_beatmap_ids(friend[1], min_sr, max_sr)
            scores_user_ids = await self.database.get_min_max_scores_snipable_user_ids(friend[1], min_sr, max_sr)
            # we need to sort scores_snipability but maintain the order of the other two lists
            # we do this by zipping the lists together, sorting the zipped list in reverse order, and then unzipping the list
            scores_snipability, scores_ids, scores_user_ids = zip(*sorted(zip(scores_snipability, scores_ids, scores_user_ids), reverse=True))
            # Now we make every list only have 10 elements
            scores_snipability = scores_snipability[:10]
            scores_ids = scores_ids[:10]
            scores_user_ids = scores_user_ids[:10]
            if not scores_snipability:
                continue
            for i in range(len(scores_snipability)):
                # we need to make sure the main user hasnt played the map
                if await self.database.get_user_score_on_beatmap_no_zeros(main_user_data.id, scores_ids[i]):
                    continue
                if scores_snipability[i] == 0:
                    continue
                if scores_snipability[i] < min(snipable_plays_snipability):
                    continue
                index = snipable_plays_snipability.index(min(snipable_plays_snipability))
                snipable_plays_snipability[index] = scores_snipability[i]
                snipable_plays_ids[index] = scores_ids[i]
                snipable_plays_user_ids[index] = scores_user_ids[i]

        # now we sort the snipability list and make sure the ids are in the same order in reverse
        snipable_plays_snipability, snipable_plays_ids, snipable_plays_user_ids = zip(*sorted(zip(snipable_plays_snipability, snipable_plays_ids, snipable_plays_user_ids), reverse=True))

        # Now we get rid of any initialised values left in the arrays
        snipable_plays_snipability = [x for x in snipable_plays_snipability if x != 0]
        snipable_plays_ids = [x for x in snipable_plays_ids if x != 0]
        snipable_plays_user_ids = [x for x in snipable_plays_user_ids if x != 0]

        # now we get the beatmaps from the ids
        beatmaps = []
        snipability = []
        user_ids = []
        for i in range(len(snipable_plays_ids)):
            if i > 24: # 25 beatmaps is good for safety buffer
                break
            beatmap = await self.database.get_beatmap(snipable_plays_ids[i])
            if beatmap:
                beatmaps.append(beatmap)
                snipability.append(snipable_plays_snipability[i])
                user_ids.append(snipable_plays_user_ids[i])

        # now we get the usernames of the users to snipe
        usernames = []
        for user_id in user_ids:
            user = await self.database.get_friend_from_user_id_and_channel(user_id, ctx.channel_id._snowflake)
            usernames.append(user[2])

        # now we check the scores
        checked_scores = 0
        for i, beatmap in enumerate(beatmaps):
            scores = await self.osu.get_score_data(beatmap[0], main_user_data.id)
            if not scores:
                checked_scores += 1
                continue
            if checked_scores > 10:
                break
            else:
                # if the main user has happened to play it, we need to remove it from all lists
                # we also need the beatmap id to be added to the rescan list
                beatmaps.remove(beatmap)
                snipability.remove(snipability[i])
                user_ids.remove(user_ids[i])
                usernames.remove(usernames[i])
                newctx = await get(self.client, interactions.Channel,
                                       channel_id=int(ctx.channel_id._snowflake))
                await newctx.send(f"Queued score data Scan for {beatmap[0]}...")
                self.client.tracker.rescan_beatmaps.append(beatmap[0])

        # now we get and post the embed
        embed = await create_recommend_embed_main(main_user_data.username, beatmaps, snipability, usernames)
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
            min_sr = 0
            max_sr = 1000
        if sort_type == "random":
            friend_scores_local = await self.database.get_min_max_scores_beatmap_ids(friend_id, min_sr, max_sr)
            main_scores = await self.database.get_min_max_scores_beatmap_ids(main_id, min_sr, max_sr)
            random.shuffle(friend_scores_local)
            random.shuffle(main_scores)
        elif sort_type == "snipability":
            friend_scores_local = await self.database.get_min_max_scores_snipable_beatmap_ids(friend_id, min_sr, max_sr)
            friend_scores = await self.database.get_min_max_scores_snipable(friend_id, min_sr, max_sr)
            main_scores = await self.database.get_min_max_scores_snipable(main_id, min_sr, max_sr)
            # sort both arrays by snipability
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
