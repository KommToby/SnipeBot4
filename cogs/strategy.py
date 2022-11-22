
import interactions
from embed.strategy import create_strategy_embed
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
from data_types.osu import *
import math


class Strategy(Cog):  # must have commands.cog or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="strategy",
        description="states what snipe strategy is most efficient for the user",
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
        main_user_id_array = await self.database.get_channel(ctx.channel_id._snowflake)
        if not(main_user_id_array):
            await ctx.send(f"Either nobody is being tracked in this channel, or you've used the command in the wrong channel!")
            return
        user_data = await self.osu.get_user_data(username)
        if not(user_data):
            await ctx.send(f"{username} is not a valid osu! username! Please try again.")
            return
        if main_user_id_array[2] == username or main_user_id_array[1] == username:
            await ctx.send(f"{username} is the main user, and therefore cannot snipe themselves!")
            return
        main_user_id = main_user_id_array[1]
        # how many times the user has been sniped by the main user
        user_sniped_array = await self.database.get_user_snipes(main_user_id, user_data.id)
        # how many times the user has sniped the main user
        user_snipes_array = await self.database.get_user_snipes(user_data.id, main_user_id)
        # how many snipes the user has against the main user, that the main user hasnt sniped back
        held_snipes_array = await self.calculate_one_way_snipes(user_snipes_array, user_sniped_array)
        # how many times the user has been sniped by the main user, that the user hasnt sniped back
        not_sniped_back_array = await self.calculate_one_way_snipes(user_sniped_array, user_snipes_array)
        snipe_pp = await self.calculate_snipe_pp(main_user_id, len(user_snipes_array), len(not_sniped_back_array), len(held_snipes_array), len(user_sniped_array))

        # how much pp will they have if they snipe back the main user
        snipe_back_pp = await self.calculate_snipe_pp(main_user_id, len(user_snipes_array)+1, len(not_sniped_back_array)-1, len(held_snipes_array), len(user_sniped_array))

        # how much pp will they have if they snipe the main user on a map theyve never played
        new_snipe_pp = await self.calculate_snipe_pp(main_user_id, len(user_snipes_array)+1, len(not_sniped_back_array), len(held_snipes_array)+1, len(user_sniped_array))

        # what is the most efficient strategy
        if snipe_back_pp > new_snipe_pp:
            strategy = "Snipe back the main user; `/snipelist`"
        elif snipe_back_pp < new_snipe_pp:
            strategy = "Snipe the main user on a new map; `/recommend`"
        else:
            strategy = "Both Methods are equally efficient; `/snipelist` and `/recommend`."

        embed = await create_strategy_embed(strategy, snipe_pp, new_snipe_pp, snipe_back_pp, username)
        await ctx.send(embeds=embed)

    async def calculate_snipe_pp(self, main_user_id, snipes, not_sniped_back, not_sniped_main, sniped):
        """
        main_user_id - the osu! id of the main user
        snipes - the number of snipes that this user has made against the main user
        not_sniped_back - the number of snipes that this user hasnt sniped back against the main user
        not_sniped_main - the number of snipes that this user has sniped on the main user, AND the main user hasnt sniped back
        sniped - the number of snipes that this user has sniped on by the main user
        """
        multiplier = 1
        total_scores = await self.database.get_all_scores(main_user_id)
        total_scores = len(total_scores)
        if snipes < total_scores:
            multiplier = (5/100) + (0.95 * (snipes/(total_scores+1)))
        calculated_pp = round((multiplier*((3*snipes + 7*not_sniped_main) /
                              (10*not_sniped_back+(snipes/(not_sniped_main+1))*sniped+1)*30000)), 2)
        weighted_pp = await self.weight_snipe_pp(calculated_pp)
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


def setup(client):
    Strategy(client)
