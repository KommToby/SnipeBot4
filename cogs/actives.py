import interactions
from embed.actives import create_actives_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
import datetime


class Actives(Cog):  # must have interactions.Extension or this won't work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        # has to be osuauth since the command is called osu and it clashes
        self.osuauth = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="actives",
        description="displays a list of the top 10 users who submitted the most plays in the last week",
    )
    async def actives(self, ctx: interactions.CommandContext, *args, **kwargs):
        await ctx.defer()

        # First we need to get a list of user ids from both users and friends without duplicates
        user_ids = await self.database.get_all_users()
        friend_ids = await self.database.get_all_friends()

        # Now we iterate through each one and add the user id to the array if it's not already in it
        all_names = []
        all_ids = []
        for user_ids in user_ids:
            if user_ids[2] not in all_names:
                all_names.append(user_ids[2])
                all_ids.append(user_ids[1])
        for friend_id in friend_ids:
            if friend_id[2] not in all_names:
                all_names.append(friend_id[2])
                all_ids.append(friend_id[1])

        # Initialise the time exactly 7 days ago
        seven_days_ago = (datetime.datetime.utcnow(
        ) - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Initialise the best number of submitted scores with their user id
        submitted_scores = {}

        # Now we need to get the scores of each user in the last week
        for i, user_id in enumerate(all_ids):
            scores = await self.database.get_all_scores_after_date(user_id, seven_days_ago)
            submitted_scores[all_names[i]] = len(scores)

        # Sort the dictionary by the number of scores
        sorted_scores = sorted(submitted_scores.items(),
                               key=lambda x: x[1], reverse=True)

        # Make the dictionary only have the 10 best users
        sorted_scores = sorted_scores[:10]

        # Initialise the embed
        embed = await create_actives_embed(sorted_scores)

        await ctx.send(embeds=embed)


def setup(client):
    Actives(client)
