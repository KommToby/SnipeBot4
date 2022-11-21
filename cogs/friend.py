import interactions
import time
from embed.friend_list import create_friend_list_embed
from tracker import SnipeTracker
from interactions.ext.get import get
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
# TODO make all friend adding in the same instances of the FIRST friend add.
# This can be done by regularly checking a value of friends that need to be added
# And if a new friend has been added to that list, it can start scanning them.
# This will reduce the number of "Friend" Class instances, and keep all the scanning
# To one singular thread. Not as efficient, but more reliable, and it doesnt really matter
# What order it goes in, since the api is limited anyway.

# TODO make the ETR data pull from the last ~10 seconds instead of the whole instance,
# Because it becomes more inaccurate the more friends you add.

# TODO remove the live updates of friend adding, and make a new command /status that shows
# all the users who are currently being scanned


class Friend(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database
        self.tracker = SnipeTracker(client)

    @interactions.extension_command(
        name="friend",
        description="add to, remove, or check a main users friend list",
        options=[interactions.Option(
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
        await ctx.defer()
        if len(kwargs) > 1:
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

    async def convert_mods_to_int(self, modarray: list):
        value = 0
        if modarray:
            for mod in modarray:
                if mod == "NF":
                    value += 1
                elif mod == "EZ":
                    value += 2
                elif mod == "TD":
                    value += 4
                elif mod == "HD":
                    value += 8
                elif mod == "HR":
                    value += 16
                elif mod == "SD":
                    value += 32
                elif mod == "DT":
                    value += 64
                elif mod == "RX":
                    value += 128
                elif mod == "HT":
                    value += 256
                elif mod == "NC":
                    value += 512
                elif mod == "FL":
                    value += 1024
                elif mod == "Autoplay":
                    value += 2048
                elif mod == "SO":
                    value += 4096
                elif mod == "Relax2":
                    value += 8192
                elif mod == "PF":
                    value += 16384
        return value

    async def handle_add(self, ctx, username: str):
        message = await ctx.send(f"Adding {username} to the friends list...")
        user_data = await self.osu.get_user_data(username)
        if user_data:
            if not(await self.database.get_friend_from_channel(user_data.id, ctx.channel_id._snowflake)):
                await self.database.add_friend(ctx.channel_id._snowflake, user_data)
                await message.edit(content=f"Adding {username} to the friends list... **Done!**")
                # if they arent a main user or a friend you should scan their plays on all beatmaps next TODO
                await self.scan_users_plays(ctx, username, message)
                newctx = get(self.client, interactions.Channel,
                             channel_id=int(ctx.channel_id._snowflake))
                await newctx.send(f"Finished scanning {username}'s plays")
            else:
                await ctx.send(f"{user_data.username} is already in the friend list!")
                return
        else:
            await ctx.send(f"Could not find the user {username} on the osu! servers")
            return

    async def handle_remove(self, ctx, username: str):
        message = await ctx.send(f"Removing {username} from the friend list...")
        if username.isupper() or username.islower():  # check if contains letters
            user_data = await self.osu.get_user_data(username)
            if user_data:
                if (await self.database.get_friend_from_channel(user_data.id, ctx.channel_id._snowflake)):
                    await self.database.delete_friend(user_data.id, ctx.channel_id._snowflake)
                    await message.reply(f"Removed {user_data.username} from the friend list!")
                else:
                    await message.reply(f"User {user_data.username} isn't in the friend list, so cannot be removed")
            else:
                await message.reply(f"Could not find the user {username} on the osu! servers, please try using their id")
                return
        else:
            if (await self.database.get_friend_from_channel(username, ctx.channel_id._snowflake)):
                await self.database.delete_friend(username, ctx.channel_id._snowflake)
                await ctx.send(f"Removed {user_data.username} from the friend list!")

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
        await message.edit(f"Adding {username} to the friends list... **Done!**\nScanning top plays...")
        beatmaps = await self.database.get_all_beatmaps()
        user_data = await self.osu.get_user_data(username)
        if user_data:
            top_plays = await self.osu.get_user_scores(user_data.id)
            for top_play in top_plays:
                beatmap_data = await self.osu.get_beatmap(top_play.beatmap.id)
                # if the beatmap has never been scanned before
                if not(await self.database.get_beatmap(top_play.beatmap.id)):
                    if beatmap_data:
                        await self.tracker.check_new_beatmaps([str(beatmap_data.id)])
                else:  # beatmap has been scanned before
                    # we check for snipes against the user
                    main_users = await self.database.get_all_users()
                    for main_user in main_users:
                        main_user_friends = await self.database.get_user_friends(main_user[0])
                        found_friend = False
                        for main_user_friend in main_user_friends:
                            if str(main_user_friend[1]) == str(user_data.id):
                                found_friend = True
                        if found_friend is True:
                            main_user_play = await self.osu.get_score_data(beatmap_data.id, main_user[1])
                            if main_user_play:
                                first_mods = await self.tracker.convert_mods_to_int(top_play.mods)
                                second_mods = await self.tracker.convert_mods_to_int(main_user_play.score.mods)
                                if await self.tracker.convert_datetime_to_int(main_user_play.score.created_at) < await self.tracker.convert_datetime_to_int(top_play.created_at):
                                    # friend user gets passive snipe
                                    if int(main_user_play.score.score) < int(top_play.score):
                                        await self.database.add_snipe(user_data.id, beatmap_data.id, main_user_play.score.user_id, top_play.created_at, top_play.score, main_user_play.score.score, top_play.accuracy, main_user_play.score.accuracy, first_mods, second_mods, top_play.pp, main_user_play.score.pp)

                                else:
                                    # main user gets passive snipe
                                    if int(main_user_play.score.score) > int(top_play.score):
                                        await self.database.add_snipe(main_user_play.score.user_id, beatmap_data.id, user_data.id, main_user_play.score.created_at, main_user_play.score.score, top_play.score, main_user_play.score.accuracy, top_play.accuracy, second_mods, first_mods, main_user_play.score.pp, top_play.pp)

        else:
            await ctx.send(f"{username} couldn't be scanned. Did you write their name correctly?")
            return
        # now we scan them on every single beatmap. Fun.
        await message.edit(content=f"Adding {username} to the friends list... **Done!**\nScanning top plays... **Done!**\nScanning user on all beatmaps... 0% complete\n`calculating` hours remaining")
        beatmaps = await self.handle_user_already_stored_scores(user_data.id, beatmaps)
        start_time = time.time()
        message_update_time = time.time()
        for i, beatmap in enumerate(beatmaps):
            try:
                if not(await self.database.get_score(user_data.id, beatmap[0])):
                    user_play = await self.osu.get_score_data(beatmap[0], user_data.id)
                    if user_play:
                        converted_stars = 0
                        converted_bpm = 0
                        if await self.convert_mods_to_int(user_play.score.mods) > 15:
                            if "DT" in user_play.score.mods or "NC" in user_play.score.mods:
                                converted_bpm = int(
                                    user_play.score.beatmap.bpm) * 1.5
                            beatmap_mod_data = await self.osu.get_beatmap_mods(user_play.score.beatmap.id, await self.convert_mods_to_int(user_play.score.mods))
                            if beatmap_mod_data:
                                converted_stars = beatmap_mod_data.attributes.star_rating
                            else:
                                converted_stars = beatmap[1]
                        await self.database.add_score(user_data.id, beatmap[0], user_play.score.score, user_play.score.accuracy, user_play.score.max_combo, user_play.score.passed, user_play.score.pp, user_play.score.rank, user_play.score.statistics.count_300, user_play.score.statistics.count_100, user_play.score.statistics.count_50, user_play.score.statistics.count_miss, user_play.score.created_at, await self.tracker.convert_mods_to_int(user_play.score.mods), converted_stars, converted_bpm)
                        main_users = await self.database.get_all_users()
                        for main_user in main_users:
                            main_user_friends = await self.database.get_user_friends(main_user[0])
                            found_friend = False
                            # can move this to before the beatmap enumeration and get a list of main users the friend is a friend of instead
                            for main_user_friend in main_user_friends:
                                if str(main_user_friend[1]) == str(user_data.id):
                                    found_friend = True
                            if found_friend is True:
                                main_user_play = await self.osu.get_score_data(beatmap[0], main_user[1])
                                if main_user_play:
                                    first_mods = await self.tracker.convert_mods_to_int(user_play.score.mods)
                                    second_mods = await self.tracker.convert_mods_to_int(main_user_play.score.mods)
                                    if await self.tracker.convert_datetime_to_int(main_user_play.score.created_at) < await self.tracker.convert_datetime_to_int(user_play.score.created_at):
                                        if int(user_play.score.score) > int(main_user_play.score.score):
                                            # friend user gets passive snipe
                                            await self.database.add_snipe(user_data.id, beatmap[0], main_user_play.score.user_id, user_play.score.created_at, user_play.score.score, main_user_play.score.score, user_play.score.accuracy, main_user_play.score.accuracy, first_mods, second_mods, user_play.score.pp, main_user_play.score.pp)

                                    else:
                                        if int(user_play.score.score) < int(main_user_play.score.score):
                                            # main user gets passive snipe
                                            await self.database.add_snipe(main_user_play.score.user_id, beatmap[0], user_data.id, main_user_play.score.created_at, main_user_play.score.score, user_play.score.score, main_user_play.score.accuracy, user_play.score.accuracy, second_mods, first_mods, main_user_play.score.pp, user_play.score.pp)

                    else:
                        await self.database.add_score(user_data.id, beatmap[0], 0, False, False, False, False, False, False, False, False, False, False, False, False, False)
                else:
                    # This is the case that if the score that is stored here is from SnipeBot3, it needs to update it. Painful Stuff.
                    local_score_data = await self.database.get_score(user_data.id, beatmap[0])
                    # accuracy being 0 signifies old format
                    if str(local_score_data[3]) == "0":
                        user_play = await self.osu.get_score_data(beatmap[0], user_data.id)
                        if not(user_play):
                            if i != 0:
                                elapsed_time = time.time() - start_time
                                try:
                                    if int(time.time()) - int(message_update_time) > 5:
                                        message_update_time = time.time()
                                        await message.edit(content=f"Adding {username} to the friends list... **Done!**\nScanning top plays... **Done!**\nScanning user on all beatmaps... {round(((i/len(beatmaps))*100), 2)}% complete\n{round((((len(beatmaps) * elapsed_time)/i)-elapsed_time)/3600, 2)} hours remaining")
                                except interactions.LibraryException as l:
                                    pass
                            continue
                        converted_stars = int(beatmap[1])
                        converted_bpm = int(beatmap[7])
                        if await self.convert_mods_to_int(user_play.score.mods) > 15:
                            if "DT" in user_play.score.mods or "NC" in user_play.score.mods:
                                converted_bpm = int(
                                    user_play.score.beatmap.bpm) * 1.5
                            beatmap_mod_data = await self.osu.get_beatmap_mods(user_play.score.beatmap.id, await self.convert_mods_to_int(user_play.score.mods))
                            if beatmap_mod_data:
                                converted_stars = beatmap_mod_data.attributes.star_rating
                            else:
                                converted_stars = beatmap[1]
                        await self.database.update_score(user_data.id, beatmap[0], user_play.score.score, user_play.score.accuracy, user_play.score.max_combo, user_play.score.passed, user_play.score.pp, user_play.score.rank, user_play.score.statistics.count_300, user_play.score.statistics.count_100, user_play.score.statistics.count_50, user_play.score.statistics.count_miss, user_play.score.created_at, await self.tracker.convert_mods_to_int(user_play.score.mods), converted_stars, converted_bpm)
                        print(
                            f"Converted Snipebot3 Formatted score to Snipebot4 Format")
                if i != 0:
                    elapsed_time = time.time() - start_time
                    try:
                        if int(time.time()) - int(message_update_time) > 5:
                            message_update_time = time.time()
                            await message.edit(content=f"Adding {username} to the friends list... **Done!**\nScanning top plays... **Done!**\nScanning user on all beatmaps... {round(((i/len(beatmaps))*100), 2)}% complete\n{round((((len(beatmaps) * elapsed_time)/i)-elapsed_time)/3600, 2)} hours remaining")
                    except interactions.LibraryException as l:
                        pass
            except Exception as e:
                print(f"Error while scanning user: {e}")
        await message.edit(content=f"Adding {username} to the friends list... **Done!**\nScanning top plays... **Done!**\nScanning user on all beatmaps... 100% complete\nNo hours remaining")

    async def handle_user_already_stored_scores(self, user_id, beatmaps: list):
        return_beatmaps = []
        conv_scores = await self.database.get_converted_scores(user_id)
        zero_scores = await self.database.get_zero_scores(user_id)
        for beatmap in beatmaps:
            add_beatmap = True
            if int(beatmap[0]) in conv_scores or int(beatmap[0]) in zero_scores:
                add_beatmap = False
            if add_beatmap is True:
                return_beatmaps.append(beatmap)
        return return_beatmaps


def setup(client):
    Friend(client)
