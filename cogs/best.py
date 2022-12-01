import interactions
from embed.best import create_best_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
import datetime


class Best(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="best",
        description="Displays your top 10 plays for a specific time period",
        options=[interactions.Option(
            name="time",
            description="time period of the top 10 plays: all, year, month, week, day",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="username",
            description="the username of the player",
            type=interactions.OptionType.STRING,
            required=False,
        )
        ]
    )
    async def count(self, ctx: interactions.CommandContext, *args, **kwargs):
        await ctx.defer()
        username = await self.handle_linked_account(ctx, kwargs)
        if not(username):
            return
        user_data = await self.osu.get_user_data(username)
        if not(user_data):
            await ctx.send(f"User {username} not found!")
            return
        date, period = await self.handle_time(ctx, kwargs)
        if not(date):
            return
        best_plays_time = await self.database.get_all_scores_after_date(user_data.id, date)

        # now we remove the scores that dont have pp
        best_plays_time = [x for x in best_plays_time if x[6] is not None]

        # now we sort the best plays by pp
        best_plays_time.sort(key=lambda x: x[6], reverse=True)

        # now we make the list ~25 plays long
        best_plays_time = best_plays_time[:25]

        # now we make an array with the beatmap data
        best_plays = []
        best_plays_times = []
        for play in best_plays_time:
            beatmap_data = await self.database.get_beatmap(play[1])
            if beatmap_data:
                best_plays.append(beatmap_data)
                best_plays_times.append(play)

        embed = await create_best_embed(best_plays_times, user_data.username, period, best_plays)
        await ctx.send(embeds=embed)

    async def handle_time(self, ctx, kwargs):
        if len(kwargs) > 0:
            if "time" in kwargs:
                # we check if one of the options was chosen
                if kwargs['time'].lower() == "all":
                    return (datetime.datetime.utcnow() - datetime.timedelta(days=20000)).strftime("%Y-%m-%dT%H:%M:%SZ"), kwargs['time']
                elif kwargs['time'].lower() == "year":
                    return (datetime.datetime.utcnow() - datetime.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ"), kwargs['time']
                elif kwargs['time'].lower() == "month":
                    return (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"), kwargs['time']
                elif kwargs['time'].lower() == "week":
                    return (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"), kwargs['time']
                elif kwargs['time'].lower() == "day":
                    return (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"), kwargs['time']
                else:
                    await ctx.send("Invalid time period: all, year, month, week, day")
                    return False
            else:
                return (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"), "week"
        else:
            await ctx.send("You need to specify a time period: all, year, month, week, day")
            return False

    async def handle_linked_account(self, ctx, kwargs):
        if len(kwargs) > 0:
            if "username" in kwargs:
                return kwargs['username']
        username_array = await self.database.get_linked_user_osu_id(ctx.author.id._snowflake)
        if not username_array:
            await ctx.send("You are not linked to an osu! account - use `/link` to link your account\n"
                            "Alternatively you can do `/best username:username` to get specific user data")
            return False
        return username_array[0]


def setup(client):
    Best(client)
