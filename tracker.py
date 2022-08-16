import time
from embed.new_best_score import *
from embed.snipe import *
from interactions.ext.get import get
from data_types.osu import *
from data_types.interactions import CustomInteractionsClient
# TODO add type values to all methods
# TODO map json dictionaries to classes
# TODO make methods that dont use client, database, or osu static (dont contain self)
# TODO for all api returns create a class object "type" to refer to
# TODO for all "white" variable names, make a new submethod that passes in the correct Class Type


class SnipeTracker:
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    async def convert_datetime_to_int(self, datetime: str):
        # '2021-08-23T21:31:10+00:00'
        date = datetime.split('-')
        year = date[0]
        month = date[1]
        date = date[2].split('T')
        day = date[0]
        date = date[1].split(':')
        hour = date[0]
        minute = date[1]
        date = date[2].split("+")
        second = date[0]
        return int(second)+60*int(minute)+3600*int(hour)+86400*int(day)+2678400*int(month)+31536000*int(year)

    # converts modarray into a binary value
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

    async def update_decode(self, modint: int, value: int, modarray: list, mod: str):
        modarray.append(mod)
        modint = modint - value
        return modint, modarray

    # converts mod integer back into array of mods
    async def decode_mods_to_array(self, modint: int):
        modarray = []
        moddict = {
            16384: "PF",
            8192: "Relax2",
            4096: "SO",
            2048: "Autoplay",
            1024: "FL",
            512: "NC",
            256: "HT",
            128: "RX",
            64: "DT",
            32: "SD",
            16: "HR",
            8: "HD",
            4: "TD",
            2: "EZ",
            1: "NF"
        }
        for key in moddict:
            if modint >= key:
                if (modint-key) >= 0:
                    modint, modarray = await self.update_decode(modint, key, modarray, moddict[key])
        if modint != 1:
            print("An error occured when decoding mod array")
        return modarray

    # Start point of the infinite loop
    async def start_loop(self):
        while True:
            try:
                s = time.time()
                await self.tracker_loop()
                print(
                    f"Tracker loop took {round((time.time() - s),2)} seconds")
            except Exception as e:
                print(f"Error occured in tracker loop: {e}")
                pass

    # Checking a beatmap that the main user has played
    async def check_main_beatmap(self, play: OsuRecentScore):
        # checks to see if the map is already stored in the database
        if not(await self.database.get_beatmap(play.beatmap.id)):
            await self.database.add_beatmap(play.beatmap.id, play.beatmap.difficulty_rating, play.beatmapset.artist, play.beatmapset.title, play.beatmap.version, play.beatmap.url, play.beatmap.total_length, play.beatmap.bpm, play.beatmapset.creator, play.beatmap.status, play.beatmap.beatmapset_id, play.beatmap.accuracy, play.beatmap.ar, play.beatmap.cs, play.beatmap.drain)
            # Checks all users in database for snipes on the new beatmap
            await self.add_snipes(play)

    # If HR or DT/NC is used, this converts the bpm and star rating of the map for stats
    async def convert_stars_and_bpm(self, play: OsuScore):
        converted_stars = 0
        converted_bpm = 0
        # if at least hard rock
        if await self.convert_mods_to_int(play.mods) > 15:
            if "DT" in play.mods or "NC" in play.mods:
                converted_bpm = int(play.beatmap.bpm) * 1.5
        beatmap_mod_data = await self.osu.get_beatmap_mods(play.beatmap.id, await self.convert_mods_to_int(play.mods))
        if beatmap_mod_data:
            converted_stars = beatmap_mod_data.attributes.star_rating
            return converted_stars, converted_bpm
        print(
            f"Error occured when converting stars and bpm for map {play.beatmap.id}")
        return converted_stars, converted_bpm

    # Gets all the friends that the main user has sniped for a play
    async def get_sniped_friends(self, play: OsuScore, main_user_discord: str):
        sniped_friends = []
        # gets list of friends linked to main user
        friends = await self.database.get_user_friends(main_user_discord)
        for friend in friends:
            # grabs the friends play on this map
            friend_play = await self.osu.get_score_data(play.beatmap.id, friend[1])
            friend_id = f'{friend[1]}'
            friend_username = f'{friend[2]}'
            if not(friend_play):  # if the friend has a score saved on this map
                continue  # move onto the next value in the for loop
            if not (await self.database.get_user_beatmap_play(friend_id, play.beatmap.id)):
                # Converted score values
                converted_stars, converted_bpm = await self.convert_stars_and_bpm(play)
                await self.database.add_score(play.user_id, play.beatmap.id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), converted_stars, converted_bpm)
            # this is the snipe check                   # print(f"\t Adding active snipe for {friend_play.score.user.username}")
            if friend_play.score.score < play.score:
                sniped_friends.append(friend_username)
                if (await self.database.get_user_snipe_on_beatmap(play.user_id, play.beatmap.id, friend_id)):
                    continue
                first_mods = await self.convert_mods_to_int(play.mods)
                second_mods = await self.convert_mods_to_int(friend_play.score.mods)
                # adds the snipe to the database
                await self.database.add_snipe(play.user_id, play.beatmap.id, friend_id, play.created_at, play.score, friend_play.score.score, play.accuracy, friend_play.score.accuracy, first_mods, second_mods, play.pp, friend_play.score.pp)
                main_users = await self.database.get_all_users()
                for main_user in main_users:  # In case the main user from one server is a friend on another
                    if str(friend_play.score.user.id) == str(main_user[1]):
                        await self.post_friend_snipe(friend_play.score, play, friend_id)
        return sniped_friends

    # creates a string consisting of the user ids of linked users who want to be pinged
    async def construct_pinging_string(self, sniped_friends: list):
        all_friends = await self.database.get_all_friends()
        ping_string = ""
        for sniped_friend in sniped_friends:
            user_id = ""
            add_ping = False
            for friend in all_friends:
                if sniped_friend == friend[2]:
                    add_ping = True
                    user_id = friend[1]
                    break
            if add_ping:
                user_link = await self.database.get_discord_id_from_link(user_id)
                if user_link:
                    if user_link[2] == 1:
                        ping_string += f"<@{user_link[0]}> "
        return ping_string

    async def check_main_user_play(self, play: OsuRecentScore, id: str, data):
        # first checks the map to see if it is already stored or not
        await self.check_main_beatmap(play)
        # grabs the local score of the user on the beatmap
        user_play = await self.database.get_user_beatmap_play(id, play.beatmap.id)
        # grabs the online score to compare with the local
        online_play = await self.osu.get_score_data(play.beatmap.id, id)
        if user_play:  # if the local play exists first, because if the local doesnt exist we dont have to compare
            if online_play:  # this shouldnt fail, but if it does we can send an error message
                # if the recent score is larger than the local score
                if play.score > int(user_play[2]):
                    conv_stars, conv_bpm = await self.convert_stars_and_bpm(play)
                    await self.database.update_score(user_play[0], user_play[1], play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), conv_stars, conv_bpm)
                    # If the recent play is the recent score, then its a new best
                    if play.score >= online_play.score.score:
                        sniped_friends = await self.get_sniped_friends(play, f"{data[0]}")
                        discord_channel = f'{data[0]}'
                        post_channel = await get(self.client, interactions.Channel, channel_id=int(discord_channel))
                        beatmap_data = await self.osu.get_beatmap(play.beatmap.id)
                        # posts the snipe embed
                        await post_channel.send(embeds=await create_high_score_embed(play, sniped_friends, beatmap_data))
                        ping_string = await self.construct_pinging_string(sniped_friends)
                        if ping_string != "":
                            await post_channel.send(f"{ping_string}")
                        # Now we check if the main user has sniped another main user (if they are in another main users friend list)
                        main_users = await self.database.get_all_users()
                        for main_user in main_users:
                            # why didnt i do it this way originally i will never know
                            if not(main_user[2] in sniped_friends):
                                continue  # exit the index and continue for loop
                            friend_play = await self.osu.get_score_data(play.beatmap.id, play.user_id)
                            await self.post_friend_snipe(play, friend_play.score, play.user_id)
            return
        # even if the local play doesnt exist we still need to add it as a score
        converted_stars, converted_bpm = await self.convert_stars_and_bpm(play)
        await self.database.add_score(play.user_id, play.beatmap.id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), converted_stars, converted_bpm)
        if online_play:  # If they have also played online they may have got a new best thats never been scanned
            if play.score >= online_play.score.score:
                sniped_friends = await self.get_sniped_friends(play, f"{data[0]}")
                discord_channel = f'{data[0]}'
                post_channel = await get(self.client, interactions.Channel, channel_id=int(discord_channel))
                beatmap_data = await self.osu.get_beatmap(play.beatmap.id)
                await post_channel.send(embeds=await create_high_score_embed(play, sniped_friends, beatmap_data))
                ping_string = await self.construct_pinging_string(sniped_friends)
                if ping_string != "":
                    await post_channel.send(f"{ping_string}")

    # The main infinite loop tracker
    async def tracker_loop(self):
        # Constructor for the loop
        local_time = time.time()
        check_time = time.time()
        active_users = []
        active_friends = []
        checked_users = []
        # This is after we check for friends, we can scan the new beatmaps and add them to the database
        beatmaps_to_scan = []
        checked_users_count = 0
        # Beginning of the loop
        try:
            start_time = time.time()
            users = await self.database.get_all_users()
            for data in users:
                # Stores the user id of the main user
                main_user_id = f"{data[1]}"
                # Gets the data of the main user
                main_user_data = await self.osu.get_user_data(main_user_id)
                if main_user_data:
                    # Gets the recent plays of the main user
                    recent_plays = await self.osu.get_recent_plays(main_user_id)
                    # Gets the recent score of the main user from the database to compare
                    recent_score = await self.database.get_main_recent_score(main_user_id)
                    print(
                        f"     checking main user {main_user_data.username} [{round((time.time() - local_time), 2)}s]")
                    local_time = time.time()  # reset the api timer
                    if recent_plays:
                        for play in recent_plays:
                            # If these values dont match it means the user has submitted a new play. Simple
                            if int(play.score) != int(recent_score[0]):
                                if main_user_id not in active_users:  # because they have set a new score we can add them to the active users list
                                    active_users.append(main_user_id)
                                await self.check_main_user_play(play, main_user_id, data)
                                # this has to always update for the 0 index
                                await self.database.update_main_recent_score(main_user_id, recent_plays[0].score)
                            else:
                                if main_user_id in active_users:  # if the score is the same from the last loop we can consider removing them as an active user
                                    # if said user hasnt set a play since 5 minutes they are removed from the active users list
                                    if (time.time() - check_time) > 300:
                                        active_users.remove(main_user_id)
                                # we put this same command in because we break out of the loop
                                await self.database.update_main_recent_score(main_user_id, recent_plays[0].score)
                                break  # we break out of the loop because if the most recent play is the same, we do not need to continue checking other older plays
                    # Implement the checked users counter used for priority tracking
                    checked_users_count += 1
                    if main_user_id not in checked_users:
                        # append the user to the priority tracking list
                        checked_users.append(main_user_id)
                else:
                    print(
                        f"An issue occured when trying to get user data for {data[2]}")

            # Now after all the main users have been scanned, we can move on to check the friend users
            local_time = await self.tracker_loop_friends(users, active_friends, checked_users, checked_users_count, beatmaps_to_scan, local_time)

        except Exception as e:
            print(f"Error occured during main tracking loop: {e}")
            pass

    async def tracker_loop_friends(self, users: list, active_friends: list, checked_users: list, checked_users_count: int, beatmaps_to_scan: list, local_time: float):
        # Now we check all of the friends, the second part of the tracking loop
        all_friends = await self.database.get_all_friends()
        # Below is dupe removal, it also removes any main users from the list.
        all_friends = await self.check_duplicate_friends(all_friends, users)
        for friend in all_friends:
            # active user check
            if checked_users_count > 15:
                pass  # TODO tbh this doesnt need to be implemented for a while, because its pretty fast
            friend_id = f"{friend[1]}"
            friend_data = await self.osu.get_user_data(friend_id)
            if not(friend_data):
                continue
            await self.database.update_friend_username(friend_data.username, friend_id)
            print(
                f"     checking {friend_data.username} [{round((time.time() - local_time), 2)}s]")
            local_time = time.time()  # reset api timer
            # Below we scan every single friend, which is why we did the removals above
            recent_plays = await self.osu.get_recent_plays(friend_id)
            if recent_plays:
                recent_score = await self.database.get_friend_recent_score(friend_id)
                if recent_score is None:
                    break  # this is if they were removed as a friend mid loop
                # checks if their most recent play is the same as last loop
                if int(recent_plays[0].score) != int(recent_score[0]):
                    beatmaps_to_scan = await self.check_friend_recent_score(active_friends, friend_id, users, recent_plays, beatmaps_to_scan, recent_score)
                else:  # there has been no change since last loop
                    if friend_id in active_friends:
                        active_friends.remove(friend_id)
                    pass
            checked_users_count += 1
            if friend_id not in checked_users:
                checked_users.append(friend_id)
        if beatmaps_to_scan != []:
            print(f"     checking {len(beatmaps_to_scan)} new beatmaps")
            await self.check_new_beatmaps(beatmaps_to_scan)
        return local_time

    async def check_friend_recent_score(self, active_friends: list, friend_id: str, users: list, recent_plays: list[OsuRecentScore], beatmaps_to_scan: list, recent_score):
        if friend_id not in active_friends:
            active_friends.append(friend_id)
        # This is when the score / snipe tracking really begins
        for main_user in users:
            # If we find the friend in the main users friend list, this will be the identifier
            friend_found = False
            main_user_friends_list = await self.database.get_main_user_friends(main_user[0])
            if main_user_friends_list is not None:
                for friend in main_user_friends_list:
                    if friend[1] == friend_id:
                        friend_found = True
                        break
            # If the main user has this friend on their friends list, we can scan their play against them
            if not(friend_found):
                continue
            # Now we can compare the friends recent plays against this main user
            for play in recent_plays:
                beatmap_id = play.beatmap.id
                # We can add this beatmap to the database if it hasnt been added before
                if not(await self.database.get_beatmap(beatmap_id)):
                    if beatmap_id not in beatmaps_to_scan:
                        beatmaps_to_scan.append(
                            beatmap_id)
                    # ^ adds the map to the database if it is not already stored
                # Checks if its an old score, once it hits this, it doesnt need to loop anymore
                if int(play.score) == int(recent_score[0]):
                    # we need to set the most recent play to their recent score, and break out of the loop
                    await self.database.update_friend_recent_score(friend_id, recent_plays[0].score)
                    break
                # Now we see if the bot has already scanned this score but it wasnt recent
                local_score = await self.database.get_user_score_with_zeros(friend_id, play.beatmap.id)
                if local_score is None:  # in case the user has never played it before and its not stored
                    await self.database.add_score(friend_id, play.beatmap.id, 0, False, False, False, False, False, False, False, False, False, False, False, 0, 0)
                    local_score = await self.database.get_user_score_with_zeros(friend_id, play.beatmap.id)
                # the score is unique, so we can continue
                if str(play.score) != local_score[2] or local_score is None:
                    # Comparison between friend and main user begins here
                    main_user_play = await self.osu.get_score_data(beatmap_id, main_user[1])
                    if main_user_play:  # if the main user has actually played the map
                        # if it is a snipe
                        if int(play.score) > int(main_user_play.score.score):
                            await self.handle_friend_snipe(friend_id, beatmap_id, play, main_user, main_user_play, users)
                        elif int(play.score) == int(main_user_play.score.score):
                            # this means they have the IDENTICAL score, so they might just be the main user on another server comparing against themself
                            if str(play.user_id) == main_user[1]:
                                # this means that they are
                                await self.check_main_user_play(play, main_user[1], main_user)
                    if str(play.score) > str(local_score[2]):
                        conv_stars, conv_bpm = await self.convert_stars_and_bpm(play)
                        await self.database.update_score(friend_id, beatmap_id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), conv_stars, conv_bpm)
                    await self.database.update_friend_recent_score(friend_id, play.score)
                else:
                    await self.database.update_friend_recent_score(friend_id, play.score)
                    pass
        return beatmaps_to_scan

    async def handle_friend_snipe(self, friend_id: str, beatmap_id, play: OsuRecentScore, main_user, main_user_play: OsuScore, users: list):
        if not(await self.database.get_user_score_on_beatmap(friend_id, beatmap_id, play.score)):
            # Now we check if the friend has played the map before or not
            if not(await self.database.get_score(friend_id, beatmap_id)):
                # this means its the friends first time playing the beatmap, so we add the score
                converted_stars, converted_bpm = await self.convert_stars_and_bpm(play)
                await self.database.add_score(friend_id, beatmap_id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), converted_stars, converted_bpm)
                # now we make sure the user hasnt (somehow) got a snipe on this beatmap before
                if not(await self.database.get_user_snipe_on_beatmap(friend_id, beatmap_id, main_user[1])):
                    # Now we can post the friend snipe
                    await self.post_friend_snipe(main_user_play.score, play, main_user)
                    # But now we need to check if the friend is a main user in another server, and post their new best there
                    for other_main_user in users:
                        # They are!
                        if other_main_user == play.user_id:
                            # now we need to post the new top play in the main users server
                            sniped_friends = await self.get_sniped_friends(play, other_main_user[0])
                            post_channel = await get(self.client, interactions.Channel, channel_id=int(other_main_user[0]))
                            beatmap_data = await self.osu.get_beatmap(beatmap_id)
                            await post_channel.send(embeds=await create_high_score_embed(play, sniped_friends, beatmap_data))
                            ping_string = await self.construct_pinging_string(sniped_friends)
                            if ping_string != "":
                                await post_channel.send(f"{ping_string}")

            else:  # the user has played the beatmap before
                # note, this cant be the main user on another server, since the main user play score would have to be identical for a new high score
                local_score = await self.database.get_score(friend_id, beatmap_id)
                # if its their new best
                if int(play.score) > int(local_score[2]):
                    conv_stars, conv_bpm = await self.convert_stars_and_bpm(play)
                    await self.database.update_score(friend_id, beatmap_id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_300, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), conv_stars, conv_bpm)
                    # now we check if the user has got a snipe on this beatmap before
                    if not(await self.database.get_user_snipe_on_beatmap(friend_id, beatmap_id, main_user[1])):
                        # Now we can post the friend snipe
                        await self.post_friend_snipe(main_user_play.score, play, main_user)

    async def check_new_beatmaps(self, beatmaps_to_scan: list):
        # maps that are passed in shouldnt be in the db, but we double check anyway
        counter = -1
        for beatmap_id in beatmaps_to_scan:
            counter += 1
            print(f"scanning {beatmap_id} - {counter}/{len(beatmaps_to_scan)}")
            if not(await self.database.get_beatmap(beatmap_id)):
                # beatmap is not in db
                beatmap_data = await self.osu.get_beatmap(beatmap_id)
                if not(beatmap_data):
                    continue
                if beatmap_data.mode == 'osu':
                    await self.database.add_beatmap(beatmap_id, beatmap_data.difficulty_rating, beatmap_data.beatmapset.artist, beatmap_data.beatmapset.title, beatmap_data.version, beatmap_data.url, beatmap_data.total_length, beatmap_data.bpm, beatmap_data.beatmapset.creator, beatmap_data.status, beatmap_data.beatmapset_id, beatmap_data.accuracy, beatmap_data.ar, beatmap_data.cs, beatmap_data.drain)
                    # should all be passive snipes
                    await self.add_new_beatmap_snipes(beatmap_data)
            else:  # this should not happen
                print(
                    f"program attempted to check new beatmap that was already stored - {beatmap_id}")

    async def add_new_beatmap_snipes(self, data: Beatmap):
        # data is beatmap data
        # we need to check all users for snipes on this map - and scores too I guess
        main_users = await self.database.get_all_users()
        for main_user in main_users:
            main_play = await self.osu.get_score_data(data.id, main_user[1])
            if not(main_play):
                await self.database.add_score(main_user[1], data.id, 0, False, False, False, False, False, False, False, False, False, False, False, 0, 0)
                continue
            # first we add the score of the main user
            converted_stars, converted_bpm = await self.convert_stars_and_bpm(main_play.score)
            await self.database.add_score(main_user[1], data.id, main_play.score.score, main_play.score.accuracy, main_play.score.max_combo, main_play.score.passed, main_play.score.pp, main_play.score.rank, main_play.score.statistics.count_300, main_play.score.statistics.count_100, main_play.score.statistics.count_50, main_play.score.statistics.count_miss, main_play.score.created_at, await self.convert_mods_to_int(main_play.score.mods), converted_stars, converted_bpm)
            friends = await self.database.get_user_friends(main_user[0])
            for friend in friends:
                friend_play = await self.osu.get_score_data(data.id, friend[1])
                if friend_play:
                    converted_stars = 0
                    friend_play.score.mods = 0
                    converted_bpm = 0
                    if not(await self.convert_mods_to_int(friend_play.score.mods) > 15):
                        await self.database.add_score(friend[1], data.id, 0, False, False, False, False, False, False, False, False, False, False, False, 0, 0)
                        continue
                    if "DT" in friend_play.score.mods or "NC" in friend_play.score.mods:
                        converted_bpm = int(
                            friend_play.score.beatmap.bpm) * 1.5
                    beatmap_mod_data = await self.osu.get_beatmap_mods(friend_play.score.beatmap.id, await self.convert_mods_to_int(friend_play.score.mods))
                    if beatmap_mod_data:
                        converted_stars = beatmap_mod_data.attributes.star_rating
                    await self.database.add_score(friend[1], friend_play.score.beatmap.id, friend_play.score.score, friend_play.score.accuracy, friend_play.score.max_combo, friend_play.score.passed, friend_play.score.pp, friend_play.score.rank, friend_play.score.statistics.count_300, friend_play.score.statistics.count_100, friend_play.score.statistics.count_50, friend_play.score.statistics.count_miss, friend_play.score.created_at, await self.convert_mods_to_int(friend_play.score.mods))
                    if await self.convert_datetime_to_int(friend_play.score.created_at) > await self.convert_datetime_to_int(main_play.score.created_at):
                        # this means friend has sniped main play if they got higher score
                        if friend_play.score.score > main_play.score.score:
                            # a passive snipe, but we need to check if they have sniped before
                            if not(await self.database.get_snipe(friend[1], friend_play.score.beatmap.id, main_user[1])):
                                # now its a first-time snipe
                                first_mods = await self.convert_mods_to_int(friend_play.score.mods)
                                second_mods = await self.convert_mods_to_int(main_play.score.mods)
                                await self.database.add_snipe(friend[1], friend_play.score.beatmap.id, main_user[1], friend_play.score.created_at, friend_play.score.score, main_play.score.score, friend_play.score.accuracy, main_play.score.accuracy, first_mods, second_mods, friend_play.score.pp, main_play.score.pp)
                        else:
                            if friend_play.score.score < main_play.score.score:
                                # a passive snipe from the main user onto the friend
                                if not(await self.database.get_snipe(main_user[1], friend_play.score.beatmap.id, friend[1])):
                                    first_mods = await self.convert_mods_to_int(main_play.score.mods)
                                    second_mods = await self.convert_mods_to_int(friend_play.score.mods)
                                    await self.database.add_snipe(main_user[1], friend_play.score.beatmap.id, friend[1], main_play.score.created_at, main_play.score.score, friend_play.score.score, main_play.score.accuracy, friend_play.score.accuracy, first_mods, second_mods, main_play.score.pp, friend_play.score.pp)

    async def check_duplicate_friends(self, friends: list, main_users: list):
        for friend in friends:
            while friends.count(friend) > 1:  # we only want 1 of a friend
                friends.remove(friend)
        for main_user in main_users:
            # we dont want to check a main user as a friend
            while friends.count(main_user) > 0:
                friends.remove(main_user)
        return friends  # returns altered array

    # When given a play, checks all users for snipes on that map.
    async def add_snipes(self, play: OsuRecentScore):
        users_checked = []
        friends_to_skip = []  # for friends who dont have plays found when scanning the main user
        main_users = await self.database.get_all_users()
        for main_user in main_users:  # Check all main users to see if they have played the map
            main_user_play = await self.osu.get_score_data(play.beatmap.id, main_user[1])
            main_user_friends = await self.database.get_user_friends(main_user[0])
            if not(main_user_play):
                # if the main user hasnt played the map, only scores need to be checked
                users_checked = self.add_scores(
                    main_user_friends, main_user, play, users_checked)
                continue
            for friend in main_user_friends:
                if friend[1] in friends_to_skip:
                    continue
                friend_play = await self.osu.get_score_data(play.beatmap.id, friend[1])
                if friend_play:
                    await self.check_friend_snipe_on_beatmap(friend_play, main_user_play, friend, main_user, play, friends_to_skip)
                else:  # if the friend play doesnt exist, we still add a 0-score to the database to speed up in future
                    if not(await self.database.get_user_score_with_zeros(friend[1], play.beatmap.id)):
                        await self.database.add_score(friend[1], play.beatmap.id, 0, None, None, None, None, None, None, None, None, None, None, None, 0, 0)
                    # when friends get scanned for plays, this user gets skipped as we know they dont have a play.
                    friends_to_skip.append(friend[1])

    async def check_friend_snipe_on_beatmap(self, friend_play: OsuScore, main_user_play: OsuScore, friend, main_user, play: OsuRecentScore, friends_to_skip: list):
        if await self.convert_datetime_to_int(friend_play.score.created_at) > await self.convert_datetime_to_int(main_user_play.score.created_at):
            if not(friend_play.score.score > main_user_play.score.score):
                if not(await self.database.get_snipe(friend[1], play.beatmap.id, main_user[1])):
                    # we can check to see if this is the snipe thats just been tracked
                    if str(play.user.id) == str(friend[1]) and str(play.score) == str(friend_play.score.score):
                        await self.post_friend_snipe(main_user_play.score, play, main_user)
                    else:  # if the play is not exactly the same as their global, it may be newer somehow
                        play_date = await self.convert_datetime_to_int(play.created_at)
                        if play_date > await self.convert_datetime_to_int(friend_play.score.created_at) and str(friend[1]) == str(play.user.id):
                            # play is newer than their old play, and it is their play
                            # this is still an active snipe
                            if play.score > main_user_play.score.score:
                                await self.post_friend_snipe(main_user_play.score, play, main_user)
                        else:  # this means their global play is better than the one they just did, but it is a passive snipe since its never been added to db
                            first_mods = await self.convert_mods_to_int(play.mods)
                            second_mods = await self.convert_mods_to_int(main_user_play.score.mods)
                            await self.database.add_snipe(play.user.id, play.beatmap.id, main_user[1], play.created_at, play.score, main_user_play.score, play.accuracy, main_user_play.score.accuracy, first_mods, second_mods, play.pp, main_user_play.score.pp)
        # if the main user play is more recent than the friend play (if they submitted in the exact same second, its not considered a snipe)
        else:
            if main_user_play.score.score > friend_play.score.score:
                if not(await self.database.get_snipe(main_user[1], play.beatmap.id, friend[1])):
                    # for sanity
                    if main_user_play.score.score > play.score:
                        # this is a passive snipe for the main user
                        first_mods = await self.convert_mods_to_int(main_user_play.score.mods)
                        second_mods = await self.convert_mods_to_int(play.mods)
                        await self.database.add_snipe(main_user[1], friend_play.score.beatmap.id, friend[1], main_user_play.score.created_at, main_user_play.score.score, friend_play.score.score, main_user_play.score.accuracy, friend_play.score.accuracy, first_mods, second_mods, main_user_play.score.pp, friend_play.score.pp)
        if friend[1] not in friends_to_skip:
            friend_local_score = await self.database.get_score(friend[1], play.beatmap.id)
            if friend_local_score is not None:
                if friend_play.score.score > friend_local_score[2]:
                    # we need to update their local score
                    conv_stars, conv_bpm = await self.convert_stars_and_bpm(friend_play.score)
                    await self.database.update_score(friend[1], play.beatmap.id, friend_play.score.score, friend_play.score.accuracy, friend_play.score.max_combo, friend_play.score.passed, friend_play.score.pp, friend_play.score.rank, friend_play.score.statistics.count_300, friend_play.score.statistics.count_100, friend_play.score.statistics.count_50, friend_play.score.statistics.count_miss, friend_play.score.created_at, await self.convert_mods_to_int(friend_play.score.mods), conv_stars, conv_bpm)

    async def add_scores(self, main_user_friends: list, main_user, play: OsuRecentScore, users_checked: list):
        # for main users who may be friends with other main users
        if main_user[1] not in users_checked:
            if not(await self.database.get_user_score_with_zeros(main_user, play.beatmap.id)):
                # if the user doesnt have a score and hasnt played the map, it just stores a 0 score
                await self.database.add_score(main_user[1], play.beatmap.id, 0, None, None, None, None, None, None, None, None, None, None, 0, 0)
                users_checked.append(main_user[1])
        for friend in main_user_friends:
            if friend[1] in users_checked:  # for duplicate friends over multiple main users
                continue
            if not(await self.database.get_user_score_with_zeros(friend[1], play.beatmap.id)):
                # The friend has not played the map and has not got a score saved
                await self.database.add_score(friend[1], play.beatmap.id, 0, None, None, None, None, None, None, None, None, None, None, 0, 0)
            else:
                friend_play = self.osu.get_score_data(
                    play.beatmap.id, friend[1])
                if friend_play:
                    local_score = await self.database.get_user_beatmap_play(friend[1], play.beatmap.id)
                    if local_score is not None:
                        # if the new score is better than the stored one
                        if friend_play.score.score > int(local_score[2]):
                            await self.convert_stars_and_bpm(friend_play.score)
                            await self.database.update_score(friend[1], friend_play.score.beatmap.id, friend_play.score.score, friend_play.score.accuracy, friend_play.score.max_combo, friend_play.score.passed, friend_play.score.pp, friend_play.score.rank, friend_play.score.statistics.count_300, friend_play.score.statistics.count_100, friend_play.score.statistics.count_50, friend_play.score.statistics.count_miss, friend_play.score.created_at, await self.convert_mods_to_int(friend_play.score.mods))
                else:
                    pass  # because they already have a 0 score stored
            users_checked.append(friend[1])
        return users_checked

    # this takes in the main users best play and their local play, adds the snipe data to the db, and posts the snipe embed to discord
    async def post_friend_snipe(self, main_user_play: OsuRecentScore, play: OsuRecentScore, main_user_db):
        main_username = main_user_play.user.username
        # if the snipe doesnt exist
        if not(await self.database.get_user_snipe_on_beatmap(play.user.id, play.beatmap.id, main_user_db[0])):
            first_mods = await self.convert_mods_to_int(play.mods)
            second_mods = await self.convert_mods_to_int(main_user_play.mods)
            await self.database.add_snipe(play.user.id, play.beatmap.id, main_user_db[1], play.created_at, play.score, main_user_play.score, play.accuracy, main_user_play.accuracy, first_mods, second_mods, play.pp, main_user_play.pp)
        discord_channel = f'{main_user_db[0]}'
        post_channel = await get(self.client, interactions.Channel, channel_id=int(discord_channel))
        beatmap_data = await self.osu.get_beatmap(play.beatmap.id)
        await post_channel.send(embeds=await create_friend_snipe_embed(play, main_username, beatmap_data))
