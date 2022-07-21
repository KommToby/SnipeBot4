import interactions, time, asyncio
from embed.friend_list import create_friend_list_embed
from tracker import SnipeTracker
class Friend(interactions.Extension): # must have commands.cog or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client
        self.osu = client.auth
        self.database = client.database
        self.tracker = SnipeTracker(client)

    @interactions.extension_command(
        name="friend",
        description="add to, remove, or check a main users friend list",
        options= [interactions.Option(
            name="add",
            description="provide the username of the player you want to add",
            type=interactions.OptionType.STRING,
        ),
        interactions.Option(
            name="remove",
            description="provide the username of the player you want to remove",
            type=interactions.OptionType.STRING,
        ),
        interactions.Option(
            name="list",
            description="provide the username of the main user you want to list the friends of",
            type=interactions.OptionType.STRING,
    )],
    )
    async def friend(self, ctx: interactions.CommandContext, *args, **kwargs):
        if len(kwargs)>1:
            await ctx.send("Too many arguments!")
            return
        elif len(kwargs) == 0:
            await ctx.send("Please select an argument `add`, `remove`, or `list`")
            return
        elif len(kwargs) == 1:
            if "add" in kwargs:
                await self.handle_add(ctx, kwargs["add"])
            elif "remove" in kwargs:
                await self.handle_remove(ctx, kwargs["remove"])
            elif "list" in kwargs:
                await self.handle_list(ctx, kwargs["list"])

    async def handle_add(self, ctx, username: str):
        message = await ctx.send(f"Adding {username} to the friend list...")
        user_data = await self.osu.get_user_data(username)
        if user_data:
            if not(await self.database.get_friend_from_channel(user_data["id"], ctx.channel_id._snowflake)):
                await self.database.add_friend(ctx.channel_id._snowflake, user_data)
                await message.reply(f"Added {user_data['username']} to the friend list!")
                # if they arent a main user or a friend you should scan their plays on all beatmaps next TODO
                await self.scan_users_plays(ctx, username, message)
            else:
                await message.reply(f"{user_data['username']} is already in the friend list!")
                return
        else:
            await message.reply(f"Could not find the user {username} on the osu! servers")
            return
        

    async def handle_remove(self, ctx, username: str):
        message = await ctx.send(f"Removing {username} from the friend list...")
        if username.isupper() or username.islower(): # check if contains letters
            user_data = await self.osu.get_user_data(username)
            if user_data:
                if (await self.database.get_friend_from_channel(user_data['id'], ctx.channel_id._snowflake)):
                    await self.database.delete_friend(user_data['id'], ctx.channel_id._snowflake)
                    await message.reply(f"Removed {user_data['username']} from the friend list!")
                else:
                    await message.reply(f"User {user_data['username']} isn't in the friend list, so cannot be removed")
            else:
                await message.reply(f"Could not find the user {username} on the osu! servers, please try using their id")
                return
        else:
            if (await self.database.get_friend_from_channel(username, ctx.channel_id._snowflake)):
                await self.database.delete_friend(username, ctx.channel_id._snowflake)
                await ctx.send(f"Removed {user_data['username']} from the friend list!")

    async def handle_list(self, ctx, username: str):
        message = await ctx.send(f"Generating Friends List...")
        if (await self.database.get_channel_from_username(username)):
            user_data = await self.osu.get_user_data(username)
            channel = await self.database.get_channel_from_username(username)
            friends = await self.database.get_user_friends(channel[0])
            embed = await create_friend_list_embed(user_data, friends)
            await message.reply(embeds=embed)
        else:
            await message.reply(f"User {username} is not a main user")

    async def scan_users_plays(self, ctx, username: str, message):
        await message.reply(f"Scanning {username}'s top plays...")
        beatmaps = await self.database.get_all_beatmaps()
        user_data = await self.osu.get_user_data(username)
        if user_data:
            top_plays = await self.osu.get_user_scores(user_data['id'])
            for top_play in top_plays:
                beatmap_data = await self.osu.get_beatmap(top_play['beatmap']['id'])
                # if the beatmap has never been scanned before
                if not(await self.database.get_beatmap(top_play['beatmap']['id'])):
                    if beatmap_data:
                        await self.database.add_beatmap(await self.database.add_beatmap(beatmap_data['id'], beatmap_data['difficulty_rating'], beatmap_data['beatmapset']['artist'], beatmap_data['beatmapset']['title'], beatmap_data['version'], beatmap_data['url'], beatmap_data['total_length'], beatmap_data['bpm'], beatmap_data['beatmapset']['creator'], beatmap_data['status'], beatmap_data['beatmapset_id'], beatmap_data['accuracy'], beatmap_data['ar'], beatmap_data['cs'], beatmap_data['drain']))
                        await self.tracker.check_new_beatmaps([str(beatmap_data['id'])])
                else: # beatmap has been scanned before
                    # we check for snipes against the user
                    main_users = await self.database.get_all_users()
                    for main_user in main_users:
                        main_user_friends = await self.database.get_user_friends(main_user[0])
                        found_friend = False
                        for main_user_friend in main_user_friends:
                            if str(main_user_friend[1]) == str(user_data['id']):
                                found_friend = True
                        if found_friend is True:
                            main_user_play = await self.osu.get_score_data(beatmap_data['id'], main_user[1])
                            if main_user_play:
                                first_mods = await self.tracker.convert_mods_to_int(top_play['mods'])
                                second_mods = await self.tracker.convert_mods_to_int(main_user_play['score']['mods'])
                                if await self.tracker.convert_datetime_to_int(main_user_play['score']['created_at']) < await self.tracker.convert_datetime_to_int(top_play['created_at']):
                                    # friend user gets passive snipe
                                    if int(main_user_play['score']['score']) < int(top_play['score']):
                                        await self.database.add_snipe(user_data['id'], beatmap_data['id'], main_user_play['score']['user_id'], top_play['created_at'], top_play['score'], main_user_play['score']['score'], top_play['accuracy'], main_user_play['score']['accuracy'], first_mods, second_mods, top_play['pp'], main_user_play['score']['pp'])

                                else:
                                    # main user gets passive snipe
                                    if int(main_user_play['score']['score']) > int(top_play['score']):
                                        await self.database.add_snipe(main_user_play['score']['user_id'], beatmap_data['id'], user_data['id'], main_user_play['score']['created_at'], main_user_play['score']['score'], top_play['score'], main_user_play['score']['accuracy'], top_play['accuracy'], second_mods, first_mods, main_user_play['score']['pp'], top_play['pp'])

        # now we scan them on every single beatmap. Fun.
        response = await message.reply(f"Finished scanning top plays. Now scanning user on all beatmaps. ETA {round(((len(beatmaps)*20)/3600), 2)} hours\n 0% complete")
        for i, beatmap in enumerate(beatmaps):
            scan_timer = time.time()
            user_play = await self.osu.get_score_data(beatmap[0], user_data['id'])
            if user_play:
                await self.database.add_score(user_data['id'], beatmap[0], user_play['score']['score'], user_play['score']['accuracy'], user_play['score']['max_combo'], user_play['score']['passed'], user_play['score']['pp'], user_play['score']['rank'], user_play['score']['statistics']['count_300'], user_play['score']['statistics']['count_100'], user_play['score']['statistics']['count_50'], user_play['score']['statistics']['count_miss'], user_play['score']['created_at'], await self.tracker.convert_mods_to_int(user_play['score']['mods']))
                main_users = await self.database.get_all_users()
                for main_user in main_users:
                    main_user_friends = await self.database.get_user_friends(main_user[0])
                    found_friend = False
                    for main_user_friend in main_user_friends:
                        if str(main_user_friend[1]) == str(user_data['id']):
                            found_friend = True
                    if found_friend is True:
                        main_user_play = await self.osu.get_score_data(beatmap[0], main_user[1])
                        if main_user_play:
                            first_mods = await self.tracker.convert_mods_to_int(user_play['score']['mods'])
                            second_mods = await self.tracker.convert_mods_to_int(main_user_play['score']['mods'])
                            if await self.tracker.convert_datetime_to_int(main_user_play['score']['created_at']) < await self.tracker.convert_datetime_to_int(user_play['score']['created_at']):
                                if int(user_play['score']['score']) > int(main_user_play['score']['score']):
                                    # friend user gets passive snipe
                                    await self.database.add_snipe(user_data['id'], beatmap[0], main_user_play['score']['user_id'], user_play['score']['created_at'], user_play['score']['score'], main_user_play['score']['score'], user_play['score']['accuracy'], main_user_play['score']['accuracy'], first_mods, second_mods, user_play['score']['pp'], main_user_play['score']['pp'])

                            else:
                                if int(user_play['score']['score']) < int(main_user_play['score']['score']):
                                    # main user gets passive snipe
                                    await self.database.add_snipe(main_user_play['score']['user_id'], beatmap[0], user_data['id'], main_user_play['score']['created_at'], main_user_play['score']['score'], user_play['score']['score'], main_user_play['score']['accuracy'], user_play['score']['accuracy'], second_mods, first_mods, main_user_play['score']['pp'], user_play['score']['pp'])

            else:
                await self.database.add_score(user_data['id'], beatmap[0], 0, False, False, False, False, False, False, False, False, False, False, False)
            await response.edit(content=f"Finished scanning top plays. Now scanning user on all beatmaps. ETA {round(((len(beatmaps)*20)/3600), 2)} hours\n {round((i/len(beatmaps)), 2)}% complete")
            # if (scan_timer - time.time()) < 20:
            #     await asyncio.sleep(20 - (scan_timer - time.time()))
        else:
            await ctx.send(f"{username} couldn't be scanned. Did you write their name correctly?")

def setup(client):
    Friend(client)