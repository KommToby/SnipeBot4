import interactions
import math
from data_types.osu import UserData
from embed.snipes import create_snipes_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog


class Snipes(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="snipes",
        description="gets snipe details for user",
        options=[interactions.Option(
            name="username",
            description="the username of the user",
            type=interactions.OptionType.STRING,
            required=False,
        )
        ]
    )
    async def snipes(self, ctx: interactions.CommandContext, *args, **kwargs):
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
            await ctx.send(f"{username} is not a valid osu! username! Please try again.")
            return
        if main_user_id_array[2] == username or main_user_id_array[1] == username:
            await ctx.send(f"{username} is the main user, and therefore cannot be sniped by themself!")
            return
        main_user_id = main_user_id_array[1]
        user_sniped_array = await self.database.get_user_snipes(main_user_id, user_data.id)
        user_snipes_array = await self.database.get_user_snipes(user_data.id, main_user_id)
        total_snipes_array = await self.database.get_main_user_snipes(main_user_id)
        position, pp, not_sniped_back, held_snipes = await self.handle_user_placements(main_user_id_array, user_data)
        if position == -1:
            await ctx.send(f"{username} is not a friend of the main user!")
            return
        embed = await create_snipes_embed(position, round(pp, 2), not_sniped_back, held_snipes, user_data, len(user_snipes_array), len(user_sniped_array), len(total_snipes_array))
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

    async def handle_user_placements(self, main_user_id_array, user_data: UserData):
        leaderboard = []
        discord_channel = main_user_id_array[0]
        all_friends = await self.database.get_user_friends(discord_channel)
        if not all_friends:
            return
        for _, friend in enumerate(all_friends):
            leaderboard = await self.handle_friend_leaderboard(friend, main_user_id_array[1], leaderboard, main_user_id_array)
        leaderboard.sort(
            reverse=True, key=lambda friends_data: friends_data['snipe_pp']
        )
        friend_dict = []  # Initialisation for a check later
        for _, friend_leaderboard_data in enumerate(leaderboard):
            if friend_leaderboard_data['username'] == user_data.username:
                friend_dict = friend_leaderboard_data
                snipe_pp = friend_leaderboard_data['snipe_pp']
                not_sniped_back = friend_leaderboard_data['not_sniped_back']
                held_snipes = friend_leaderboard_data['held_snipes']
                break
        if friend_dict == []:
            return -1, 0, 0, 0
        return leaderboard.index(friend_dict), snipe_pp, not_sniped_back, held_snipes

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
        one_way_snipes = []
        for snipe in snipes:
            add_to_array = True
            for sniped_play in sniped:
                if snipe[1] == sniped_play[1]:
                    add_to_array = False
                    break
            if add_to_array is True:
                one_way_snipes.append(snipe)
        return one_way_snipes

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

    def sort_friend_snipes(self, friends_data):
        # NOT async because it's a local function
        friends_data.sort(
            reverse=True, key=lambda friends_data: friends_data['snipe_pp']
        )


def setup(client):
    Snipes(client)
