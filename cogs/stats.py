
import interactions
from embed.stats import create_stats_embed


class Stats(interactions.Extension):  # must have commands.cog or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="stats",
        description="get a users statistics",
        options=[interactions.Option(
            name="username",
            description="the username of the user",
            type=interactions.OptionType.STRING,
            required=False,
        )
        ]
    )
    async def stats(self, ctx: interactions.CommandContext, *args, **kwargs):
        await ctx.defer()  # is thinking... message - 15 minutes timer
        username = await self.handle_linked_account(ctx, kwargs)
        if not(username):
            return
        user_data = await self.osu.get_user_data(username)
        if user_data:
            user_id = user_data['id']
            scores = await self.database.get_all_scores(user_id)
            all_beatmaps = await self.database.get_all_beatmaps()
            user_score_data = {}
            if scores:
                played_beatmap_ids = []
                user_score_data['stars'] = []
                user_score_data['bpm'] = []
                user_score_data['mods'] = []
                # unique beatmaps only from the score (just in case)
                for score in scores:
                    if score[1] not in played_beatmap_ids:
                        played_beatmap_ids.append(score[1])
                        if score[14] is not None and int(score[14]) != 0:
                            user_score_data['stars'].append(float(score[14]))
                        if score[15] is not None and int(score[15]) != 0:
                            user_score_data['bpm'].append(float(score[15]))
                        if score[13] is not None:
                            if int(score[13]) != 0:
                                user_score_data['mods'].append(int(score[13]))
                # add to dictionary
                user_score_data['beatmaps'] = played_beatmap_ids
                user_score_data['lengths'] = []
                user_score_data['artists'] = []
                user_score_data['songs'] = []
                user_score_data['mappers'] = []
                user_score_data['guests'] = []
                checked_beatmapsets = []
                for beatmap in all_beatmaps:  # loop through all stored beatmaps
                    if int(beatmap[0]) in played_beatmap_ids:
                        user_score_data['lengths'].append(beatmap[6])
                        # unique map artist checking
                        if beatmap[10] not in checked_beatmapsets:
                            user_score_data['artists'].append(beatmap[2])
                            user_score_data['songs'].append(beatmap[3])
                            user_score_data['mappers'].append(beatmap[8])
                            checked_beatmapsets.append(beatmap[10])

                        # guest difficulty mapper check
                        for letter in beatmap[4]:
                            if letter == "'":  # apostrophy i.e. Komm's Insane
                                user_score_data['guests'].append(
                                    beatmap[4].split("'")[0])
                                user_score_data['mappers'].append(
                                    beatmap[4].split("'")[0])

                        # beatmap checks done

                # Frequency checks of dictionary values

                # Top 10 artists
                top_ten_artists = []
                checked_artists = []
                artist_frequencies = {}
                for j in user_score_data['artists']:
                    if j not in checked_artists:
                        artist_frequency = user_score_data['artists'].count(j)
                        artist_frequencies[j] = int(artist_frequency)

                sorted_artist_frequencies = sorted(
                    artist_frequencies.items(), key=lambda x: x[1], reverse=True)
                for _ in range(0, 10):
                    top_ten_artists.append(sorted_artist_frequencies[0])
                    sorted_artist_frequencies.remove(
                        sorted_artist_frequencies[0])

                stats_embed = await create_stats_embed(user_data, user_score_data, top_ten_artists, scores)
                await ctx.send(embeds=stats_embed)

            else:
                await ctx.send(f"{username} as not found in the database. Did you enter the correct name?")
                return
        else:
            await ctx.send(f"{username} was not found as an osu! user. Did you enter the correct name?")
            return

    async def handle_linked_account(self, ctx, kwargs):
        if len(kwargs) > 0:
            return kwargs['username']
        else:
            username_array = await self.database.get_linked_user_osu_id(ctx.author.id._snowflake)
            if not username_array:
                await ctx.send("You are not linked to an osu! account - use `/link` to link your account\n"
                               "Alternatively you can do `/stats username:username` to get a specific persons profile")
                return False
            return username_array[0]


def setup(client):
    Stats(client)
