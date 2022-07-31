import interactions, asyncio
from embed.leaderboard import create_leaderboard_embed
class Leaderboard(interactions.Extension): # must have interactions.Extension or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
            name="leaderboard", 
            description="gets the snipe leaderboard for this server",
    )
    async def leaderboard(self, ctx: interactions.CommandContext):
        await ctx.defer()
        leaderboard = [] # The final leaderboard
        main_user_array = await self.database.get_user_from_channel(ctx.channel_id._snowflake)
        if not main_user_array:
            await ctx.send(f"Nobody is being tracked in this channel, please make sure you use the command in the correct channel")
            return
        main_user_id = main_user_array[1]
        main_user_friends = await self.database.get_user_friends(ctx.channel_id._snowflake)
        for friend in main_user_friends:
            leaderboard = await self.handle_friend_leaderboard(friend, main_user_id, leaderboard)
        self.sort_friend_snipes(leaderboard)
        main_snipes_array = await self.database.get_main_user_snipes(main_user_id)
        main_sniped_array = await self.database.get_main_user_sniped(main_user_id)
        main_snipes = len(main_snipes_array)
        main_sniped = len(main_sniped_array)
        embed = await create_leaderboard_embed(leaderboard, main_user_array[2], main_snipes, main_sniped)
        await ctx.send(embeds=embed)

    async def handle_friend_leaderboard(self, friend, main_user_id, leaderboard):
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
        leaderboard.append({'username': friend[2], 'not_sniped_back': not_sniped_back, 'held_snipes': held_snipes, 'snipe_pp': snipe_pp, 'old_pp': friend_old_pp})
        return leaderboard

    async def calculate_one_way_snipes(self, snipes, sniped):
        one_way_snipes = []
        for snipe in snipes:
            add_to_array = True
            for sniped_play in sniped:
                if sniped[1] == sniped_play[1]:
                    add_to_array = False
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
        multiplier = 1
        total_scores = await self.database.get_all_scores(main_user_id)
        total_scores = len(total_scores)
        if snipes < total_scores:
            multiplier = (5/100) + (0.95 * (snipes/(total_scores+1)))
        return round((multiplier*((3*snipes + 7*not_sniped_back)/(2*not_sniped_main+(snipes/(not_sniped_back+1))*sniped+1)*4000)), 2)

    def sort_friend_snipes(self, friends_data):
        # NOT async because it's a local function
        friends_data.sort(
            reverse=True, key=lambda friends_data: friends_data['snipe_pp']
        )

def setup(client):
    Leaderboard(client)