import interactions
from embed.snipable import create_snipable_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
import random
from interactions.ext.get import get


class Snipable(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="snipable",
        description="shows a list of the most snipable maps for that user",
        options=[interactions.Option(
            name="username",
            description="the username of the user",
            type=interactions.OptionType.STRING,
            required=False,
        )
        ]
    )
    async def snipable(self, ctx: interactions.CommandContext, *args, **kwargs):
        await ctx.defer()
        username = await self.handle_linked_account(ctx, kwargs)
        if not (username):
            return
        main_user_id_array = await self.database.get_channel(ctx.channel_id._snowflake)
        if not (main_user_id_array):
            await ctx.send(f"Either nobody is being tracked in this channel, or you've used the command in the wrong channel!")
            return
        user_data = await self.osu.get_user_data(username)
        if not (user_data):
            await ctx.send(f"User {username} not found!")
            return
        snipable_scores = await self.database.get_snipable_scores(user_data.id)
        if not (snipable_scores):
            await ctx.send(f"User {username} has no snipable scores! - Did you check the correct user?")
            return
        await self.sort_scores(snipable_scores)
        beatmaps, snipable_scores = await self.get_beatmaps_from_scores(snipable_scores)

        # # now we check if the top ten are up to date
        checked_scores = 0
        for i, beatmap in enumerate(beatmaps):
            scores = await self.osu.get_score_data(beatmap[0], user_data.id)
            if scores is False:
                checked_scores += 1
            elif checked_scores>10:
                break
            else:
                # if the score is not the same as the one in the database, we update it
                if scores.score.score != snipable_scores[i][2]:
                    # print(f"{scores.score.score} is not the same as {snipable_scores[i][2]}")
                    beatmaps.remove(beatmap)
                    snipable_scores.remove(snipable_scores[i])
                    newctx = await get(self.client, interactions.Channel,
                                   channel_id=int(ctx.channel_id._snowflake))
                    await newctx.send(f"Rescanning beatmap {beatmap[0]}...")
                    self.client.tracker.rescan_beatmap(beatmap[0])

        embed = await create_snipable_embed(user_data.username, snipable_scores, beatmaps)
        await ctx.send(embeds=embed)

    async def get_scores(self, main_id: int, friend_id: int):
        snipes = await self.database.get_single_user_snipes_ids(main_id, friend_id)
        sniped = await self.database.get_single_user_snipes_ids(friend_id, main_id)
        random.shuffle(snipes)
        random.shuffle(sniped)
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
            if not (beatmap_data):
                continue
            beatmaps_data.append(beatmap_data)
            links.append(beatmap_data[5])
        return beatmaps_data, links

    async def handle_linked_account(self, ctx, kwargs):
        if len(kwargs) > 0:
            return kwargs['username']
        else:
            username_array = await self.database.get_linked_user_osu_id(ctx.author.id._snowflake)
            if not username_array:
                await ctx.send("You are not linked to an osu! account - use `/link` to link your account\n"
                               "Alternatively you can do `/snipelist username:username` to get a specific persons profile")
                return False
            return username_array[0]

    async def get_beatmaps_from_scores(self, scores: list):
        new_scores = scores.copy()
        beatmaps = []
        for i, _ in enumerate(scores):
            if i > 10:
                break
            beatmap = await self.database.get_beatmap(scores[i][1])
            if not (beatmap):
                new_scores.remove(scores[i])
                self.client.tracker.rescan_beatmaps.append(scores[i][1])
                print(f"added {scores[i][1]} to be scanned as a new beatmap")
                continue
            beatmaps.append(beatmap)
            if len(beatmaps) >= 10:
                break
        return beatmaps, new_scores

    async def sort_scores(self, scores):
        # sort by the 16th value in the array (snipability) descending
        scores.sort(key=lambda x: x[16], reverse=True)


def setup(client):
    Snipable(client)
