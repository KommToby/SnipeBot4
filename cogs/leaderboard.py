import interactions
import math
from embed.leaderboard import create_leaderboard_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog

# must have interactions.Extension or this wont work


class Leaderboard(Cog):
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="leaderboard",
        description="gets the snipe leaderboard for this server",
        options=[interactions.Option(
            name="sort",
            description="sort order of leaderboard",
            type=interactions.OptionType.STRING,
            required=False,
            choices=[
                {
                    "name": "Snipe PP",
                    "value": "pp"
                },
                {
                    "name": "Held Snipes",
                    "value": "held"
                },
                {
                    "name": "To-Snipe Plays",
                    "value": "tosnipe"
                }
            ]
        )
        ]
    )
    async def leaderboard(self, ctx: interactions.CommandContext, *args, **kwargs):
        await ctx.defer()
        sort = await self.handle_kwargs(kwargs)
        if sort == "":
            await ctx.send("Invalid sort order. Valid options are: `pp`, `held`, `tosnipe`")
            return
        leaderboard = []  # The final leaderboard
        main_user_array = await self.database.get_user_from_channel(ctx.channel_id._snowflake)
        if not main_user_array:
            await ctx.send(f"Nobody is being tracked in this channel, please make sure you use the command in the correct channel")
            return
        main_user_id = main_user_array[1]
        main_user_friends = await self.database.get_user_friends(ctx.channel_id._snowflake)
        for friend in main_user_friends:
            leaderboard = await self.handle_friend_leaderboard(friend, main_user_id, leaderboard, main_user_array)
        self.sort_friend_snipes(leaderboard, sort)
        main_snipes_array = await self.database.get_main_user_snipes(main_user_id)
        main_sniped_array = await self.database.get_main_user_sniped(main_user_id)
        main_snipes = len(main_snipes_array)
        main_sniped = len(main_sniped_array)
        embed = await create_leaderboard_embed(leaderboard, main_user_array[2], main_snipes, main_sniped, sort)
        await ctx.send(embeds=embed)

    async def handle_kwargs(self, kwargs):
        if len(kwargs) == 0:
            return 'snipe_pp'
        else:
            if kwargs['sort'] == 'pp':
                return 'snipe_pp'
            elif kwargs['sort'] == 'held':
                return 'held_snipes'
            elif kwargs['sort'] == 'tosnipe':
                return 'not_sniped_back'
            else:
                return ""

    async def handle_friend_leaderboard(self, friend, main_user_id, leaderboard, main_user_array):
        friend_old_pp_array = await self.database.get_friend_leaderboard_score(friend[1])
        friend_old_pp = friend_old_pp_array[0]
        friend_snipes_array = await self.database.get_user_snipes(friend[1], main_user_id)
        friend_sniped_array = await self.database.get_user_snipes(main_user_id, friend[1])
        held_snipes_array = await self.calculate_one_way_snipes(friend_snipes_array, friend_sniped_array)
        not_sniped_back_array = await self.calculate_one_way_snipes(friend_sniped_array, friend_snipes_array)
        friend_snipes = len(friend_snipes_array)
        friend_sniped = len(friend_sniped_array)
        held_snipes = len(held_snipes_array)
        not_sniped_back = len(not_sniped_back_array)
        snipe_pp = await self.calculate_snipe_pp(main_user_id, friend_snipes, not_sniped_back, held_snipes, friend_sniped)
        await self.database.update_friend_leaderboard_score(main_user_array[0], friend[1], snipe_pp)
        leaderboard.append({'username': friend[2], 'not_sniped_back': not_sniped_back,
                           'held_snipes': held_snipes, 'snipe_pp': snipe_pp, 'old_pp': friend_old_pp})
        return leaderboard

    async def calculate_one_way_snipes(self, snipes, sniped):
        sniped_plays = {sniped_play[1] for sniped_play in sniped}
        return [snipe for snipe in snipes if snipe[1] not in sniped_plays]

    async def calculate_snipe_pp(self, main_user_id, snipes, not_sniped_back, not_sniped_main, sniped):
        """
        main_user_id - the osu! id of the main user
        snipes - the number of snipes that this user has made against the main user
        not_sniped_back - the number of snipes that this user hasnt sniped back against the main user
        not_sniped_main - the number of snipes that this user has sniped on the main user, AND the main user hasnt sniped back
        sniped - the number of snipes that this user has sniped on by the main user
        """
        calculated_pp = 1000  # Everyone starts with 1000 base pp
        total_scores = await self.database.get_all_scores(main_user_id)
        total_scores = len(total_scores)
        # First we apply the general score multiplier for the main user
        if snipes < total_scores:
            # Penalty for players who havent sniped enough
            calculated_pp = calculated_pp * \
                ((5/100) + (0.95 * (snipes/(total_scores+1))))

        # worst case 50pp

        # Now we add 1pp for every single held snipe the user has
        calculated_pp += not_sniped_main
        # Now we multiply this pp by their snipe/sniped history, if they have been sniped more than they have sniped
        if sniped > snipes:
            calculated_pp = calculated_pp * (snipes/sniped)
        # If they have over 100 more, then we add 0.5pp for every snipe they have more than sniped
        elif sniped < snipes and (snipes - sniped) > 100:
            calculated_pp += ((snipes - sniped)-100) * 0.5
        # Now we reduce the pp by the ratio of held snipes against to-snipes, if they have more to-snipes than held snipes
        if not_sniped_back > not_sniped_main:
            calculated_pp *= (not_sniped_back / not_sniped_main)
            # we will also do a base reduction of 0.5 for every held snipe they have as a general penalty
            calculated_pp = calculated_pp / \
                (1 + 0.01*(not_sniped_back - not_sniped_main))
        # If they have more held snipes than to-snipes, then we add 0.5pp for every held snipe they have more than to-snipes
        elif not_sniped_back < not_sniped_main:
            calculated_pp += (not_sniped_main - not_sniped_back) * 0.5

        # If they have less than 100 snipes, then we reduce their pp by 50%
        if snipes < 100:
            calculated_pp *= 0.25
        elif snipes < 200:
            calculated_pp *= 0.5
        elif snipes < 300:
            calculated_pp *= 0.75
        elif snipes < 400:
            calculated_pp *= 0.95

        # Now we normalise the pp (30x)
        calculated_pp *= 30

        weighted_pp = await self.weight_snipe_pp(calculated_pp)
        weighted_pp = math.log2(weighted_pp) * 300
        return weighted_pp

    async def weight_snipe_pp(self, pp):
        # PP gets harder to gain every 1000pp that you have.
        # This penalty maxes out at 5x harder to gain
        if pp <= 1000:
            return pp
        new_pp = 0
        frac = math.floor(pp/1000)
        for i in range(0, frac+1):
            if i > 4:  # the weighting maxes out at 1/5 penalty
                new_pp += (1/5) * pp
                break
            elif pp < 1000:
                new_pp += (1/(i+1))*pp
            else:
                new_pp += (1/(i+1))*1000
            pp = (pp - 1000)
        return new_pp

    def sort_friend_snipes(self, friends_data, sort):
        # NOT async because it's a local function
        friends_data.sort(
            reverse=True, key=lambda friends_data: friends_data[sort]
        )


def setup(client):
    Leaderboard(client)
