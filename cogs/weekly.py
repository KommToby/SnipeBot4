import interactions
import math
import datetime
from data_types.osu import UserData
from embed.weekly import create_weekly_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog

# datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


class Weekly(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="weekly",
        description="showcases some weekly stats",
        options=[interactions.Option(
            name="username",
            description="the username of the user",
            type=interactions.OptionType.STRING,
            required=False,
        )
        ]
    )
    async def weekly(self, ctx: interactions.CommandContext, *args, **kwargs):
        await ctx.defer()
        username = await self.handle_linked_account(ctx, kwargs)
        if not(username):
            return
        user_data = await self.osu.get_user_data(username)
        if not(user_data):
            await ctx.send(f"{username} is not a valid osu! username! Please try again.")
            return
        user_weekly_array = await self.database.get_last_weeks_scores(user_data.id)
        if not(user_weekly_array):
            await ctx.send(f"{username} has no scores in the last week!")
            return
        user_weekly_array = await self.sort_weekly_array(user_weekly_array)
        # make the weekly array max at 10 elements
        if len(user_weekly_array) > 10:
            user_weekly_array = user_weekly_array[:10]
        # for every beatmap in the array, get the beatmap data
        beatmap_array = []
        for beatmap in user_weekly_array:
            beatmap_array.append(await self.osu.get_beatmap(beatmap[1]))
        # create the embed
        embed = await create_weekly_embed(user_weekly_array, username, beatmap_array)
        await ctx.send(embeds=embed)

    async def handle_linked_account(self, ctx, kwargs):
        if len(kwargs) > 0:
            return kwargs['username']
        else:
            username_array = await self.database.get_linked_user_osu_id(ctx.author.id._snowflake)
            if not username_array:
                await ctx.send("You are not linked to an osu! account - use `/link` to link your account\n"
                               "Alternatively you can do `/snipes username:username` to get a specific persons profile")
                return False
            return username_array[0]

    async def sort_weekly_array(self, array):
        # remove all the values that have None as the 6th element
        array = [x for x in array if x[6] is not None]
        # sort the array by the 6th element of each value (pp)
        array.sort(key=lambda x: x[6], reverse=True)
        return array


def setup(client):
    Weekly(client)
