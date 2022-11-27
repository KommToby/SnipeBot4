import time
from embed.new_best_score import *
from embed.snipe import *
from interactions.ext.get import get
from data_types.osu import *
from data_types.interactions import CustomInteractionsClient
import asyncio
import random
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
        date = date[0].split("Z")
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
        if modint != 0:
            print("An error occured when decoding mod array")
        return modarray

    # Start point of the infinite loop
    async def start_loop(self):
        plays = {}
        while True:
            try:
                if plays is None:
                    plays = {}
                s = time.time()
                plays = await self.tracker_loop(plays)
                await asyncio.sleep(1)
                print(
                    f"Tracker loop took {round((time.time() - s),2)} seconds")
                tracker_time = time.time() - s
                while tracker_time < 150:
                    all_scores = await self.database.get_all_scores_all_users_without_zeros_no_snipability()
                    random.shuffle(all_scores)
                    for i, score in enumerate(all_scores):
                        try:
                            asyncio.sleep(0.1)
                            tracker_time = time.time() - s
                            if tracker_time > 150:
                                break
                            # print the percentage every 100 scores with the estimated time remaining
                            print(f"{i}/{len(all_scores)}")
                            # map_length, normal_difficulty, stats, bpm, mods, rank, spinner_count, pp):
                            beatmap = await self.database.get_beatmap(score[1])
                            if beatmap:
                                a = await self.osu.get_score_data(score[1], score[0])
                                _, _2, max_combo = await self.convert_stars_and_bpm(a.score)
                                await self.database.update_snipability(score[0], score[1], score[2], await self.calculate_snipability(beatmap[6], beatmap[1], {"AR": beatmap[12], "OD": beatmap[11]}, beatmap[7], await self.decode_mods_to_array(score[13]), score[7], 0, score[6], score[3], score[11], score[4], max_combo))
                        except Exception as e:
                            print(e)
                            print(score)
                            continue
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
        max_combo = 0
        # if at least hard rock
        if await self.convert_mods_to_int(play.mods) > 15:
            if "DT" in play.mods or "NC" in play.mods:
                converted_bpm = int(play.beatmap.bpm) * 1.5
        beatmap_mod_data = await self.osu.get_beatmap_mods(play.beatmap.id, await self.convert_mods_to_int(play.mods))
        if beatmap_mod_data:
            converted_stars = beatmap_mod_data.attributes.star_rating
            max_combo = beatmap_mod_data.attributes.max_combo
            return converted_stars, converted_bpm, max_combo
        print(
            f"Error occured when converting stars and bpm for map {play.beatmap.id}")
        return converted_stars, converted_bpm, max_combo

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
                converted_stars, converted_bpm, max_combo = await self.convert_stars_and_bpm(play)
                snipability = await self.calculate_snipability(play.beatmap.drain, play.beatmap.difficulty_rating, {"AR": play.beatmap.ar, "OD": play.beatmap.accuracy}, play.beatmap.bpm, play.mods, play.rank, play.beatmap.count_spinners, play.pp, play.accuracy, play.statistics.count_miss, play.max_combo, max_combo)
                await self.database.add_score(play.user_id, play.beatmap.id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), converted_stars, converted_bpm, snipability)
            # this is the snipe check                   # print(f"\t Adding active snipe for {friend_play.score.user.username}")
            if friend_play.score.score < play.score:
                sniped_friends.append(friend_username)
                if (await self.database.get_user_snipe_on_beatmap(play.user_id, play.beatmap.id, friend_id)):
                    continue
                first_mods = await self.convert_mods_to_int(play.mods)
                second_mods = await self.convert_mods_to_int(friend_play.score.mods)
                # adds the snipe to the database
                await self.database.add_snipe(play.user_id, play.beatmap.id, int(friend_id), play.created_at, play.score, friend_play.score.score, play.accuracy, friend_play.score.accuracy, first_mods, second_mods, play.pp, friend_play.score.pp)
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
                    conv_stars, conv_bpm, max_combo = await self.convert_stars_and_bpm(play)
                    snipability = await self.calculate_snipability(play.beatmap.drain, play.beatmap.difficulty_rating, {"AR": play.beatmap.ar, "OD": play.beatmap.accuracy}, play.beatmap.bpm, play.mods, play.rank, play.beatmap.count_spinners, play.pp, play.accuracy, play.statistics.count_miss, play.max_combo, max_combo)
                    await self.database.update_score(user_play[0], user_play[1], play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), conv_stars, conv_bpm, snipability)
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
                            friend_play = await self.osu.get_score_data(play.beatmap.id, main_user[1])
                            await self.post_friend_snipe(friend_play.score, play, main_user)
            return
        # even if the local play doesnt exist we still need to add it as a score
        converted_stars, converted_bpm, max_combo = await self.convert_stars_and_bpm(play)
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
            else:
                snipability = await self.calculate_snipability(play.beatmap.total_length, play.beatmap.difficulty_rating, {"AR": play.beatmap.ar, "OD": play.beatmap.accuracy}, play.beatmap.bpm, play.mods, play.rank, play.beatmap.count_spinners, play.pp, play.accuracy, play.statistics.count_miss, play.max_combo, max_combo)
                await self.database.add_score(play.user_id, play.beatmap.id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), converted_stars, converted_bpm, snipability)
        else:
            snipability = await self.calculate_snipability(play.beatmap.total_length, play.beatmap.difficulty_rating, {"AR": play.beatmap.ar, "OD": play.beatmap.accuracy}, play.beatmap.bpm, play.mods, play.rank, play.beatmap.count_spinners, play.pp, play.accuracy, play.statistics.count_miss, play.max_combo, max_combo)
            await self.database.add_score(play.user_id, play.beatmap.id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), converted_stars, converted_bpm, snipability)

    # The main infinite loop tracker
    async def tracker_loop(self, plays):
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
            # plays = {} # this is used to store the plays we get from the api, and check for duplicates to prevent api pinging :D
            # above line is now introduced in the loop beginning since we need to store the previous loops data
            users = await self.database.get_all_users()
            for data in users:
                # Stores the user id of the main user
                main_user_id = f"{data[1]}"
                # Gets the data of the main user
                main_user_data = await self.osu.get_user_data(main_user_id)
                if main_user_data:
                    # Gets the recent plays of the main user
                    recent_plays = await self.osu.get_recent_plays(main_user_id)
                    if not main_user_data.id in plays:
                        plays[main_user_data.id] = []
                    if plays[main_user_data.id] == recent_plays:
                        continue  # No need to do anything if the plays are the same
                    plays[main_user_data.id] = recent_plays
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
            local_time, plays = await self.tracker_loop_friends(users, active_friends, checked_users, checked_users_count, beatmaps_to_scan, local_time, plays)
            return plays

        except Exception as e:
            print(f"Error occured during main tracking loop: {e}")
            pass

    async def tracker_loop_friends(self, users: list, active_friends: list, checked_users: list, checked_users_count: int, beatmaps_to_scan: list, local_time: float, plays: dict):
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
            if not friend_data.id in plays:
                plays[friend_data.id] = []
            if plays[friend_data.id] == recent_plays:
                continue
            plays[friend_data.id] = recent_plays
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
                # We need to check if the friend is a main user on another server, and if they are, we check their beatmap as a main user as well
                for user in users:
                    if str(user[1]) == friend_id:
                        # get the user data from the database
                        user_data = await self.database.get_channel_from_username(user[2])
                        for play in recent_plays:
                            await self.check_main_user_play(play, friend_id, user_data)
                        # this has to always update for the 0 index
                        await self.database.update_main_recent_score(friend_id, recent_plays[0].score)
            checked_users_count += 1
            if friend_id not in checked_users:
                checked_users.append(friend_id)
        if beatmaps_to_scan != []:
            print(f"     checking {len(beatmaps_to_scan)} new beatmaps")
            await self.check_new_beatmaps(beatmaps_to_scan)
        return local_time, plays

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
                    if str(friend[1]) == friend_id:
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
                    await self.database.add_score(friend_id, play.beatmap.id, 0, False, False, False, False, False, False, False, False, False, False, False, 0, 0, None)
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
                        conv_stars, conv_bpm, max_combo = await self.convert_stars_and_bpm(play)
                        snipability = await self.calculate_snipability(play.beatmap.drain, play.beatmap.difficulty_rating, {"AR": play.beatmap.ar, "OD": play.beatmap.accuracy}, play.beatmap.bpm, play.mods, play.rank, play.beatmap.count_spinners, play.pp, play.accuracy, play.statistics.count_miss, play.max_combo, max_combo)
                        await self.database.update_score(friend_id, beatmap_id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), conv_stars, conv_bpm, snipability)
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
                converted_stars, converted_bpm, max_combo = await self.convert_stars_and_bpm(play)
                snipability = await self.calculate_snipability(play.beatmap.total_length, play.beatmap.difficulty_rating, {"AR": play.beatmap.ar, "OD": play.beatmap.accuracy}, play.beatmap.bpm, play.mods, play.rank, play.beatmap.count_spinners, play.pp, play.accuracy, play.statistics.count_miss, play.max_combo, max_combo)
                await self.database.add_score(friend_id, beatmap_id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_100, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), converted_stars, converted_bpm, snipability)
                # now we make sure the user hasnt (somehow) got a snipe on this beatmap before
                if not(await self.database.get_user_snipe_on_beatmap(friend_id, beatmap_id, main_user[1])):
                    # Now we can post the friend snipe
                    await self.post_friend_snipe(main_user_play.score, play, main_user)

            else:  # the user has played the beatmap before
                # note, this cant be the main user on another server, since the main user play score would have to be identical for a new high score
                local_score = await self.database.get_score(friend_id, beatmap_id)
                # if its their new best
                if int(play.score) > int(local_score[2]):
                    conv_stars, conv_bpm, max_combo = await self.convert_stars_and_bpm(play)
                    snipability = await self.calculate_snipability(play.beatmap.total_length, play.beatmap.difficulty_rating, {"AR": play.beatmap.ar, "OD": play.beatmap.accuracy}, play.beatmap.bpm, play.mods, play.rank, play.beatmap.count_spinners, play.pp, play.accuracy, play.statistics.count_miss, play.max_combo, max_combo)
                    await self.database.update_score(friend_id, beatmap_id, play.score, play.accuracy, play.max_combo, play.passed, play.pp, play.rank, play.statistics.count_300, play.statistics.count_300, play.statistics.count_50, play.statistics.count_miss, play.created_at, await self.convert_mods_to_int(play.mods), conv_stars, conv_bpm, snipability)
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
                await self.database.add_score(main_user[1], data.id, 0, False, False, False, False, False, False, False, False, False, False, False, 0, 0, None)
                continue
            # first we add the score of the main user
            converted_stars, converted_bpm, max_combo = await self.convert_stars_and_bpm(main_play.score)
            snipability = await self.calculate_snipability(main_play.score.beatmap.drain, main_play.score.beatmap.difficulty_rating, {"AR": main_play.score.beatmap.ar, "OD": main_play.score.beatmap.accuracy}, main_play.score.beatmap.bpm, main_play.score.mods, main_play.score.rank, main_play.score.max_combo, main_play.score.rank, main_play.score.beatmap.count_spinners, main_play.score.pp, main_play.score.max_combo, max_combo)
            await self.database.add_score(main_user[1], data.id, main_play.score.score, main_play.score.accuracy, main_play.score.max_combo, main_play.score.passed, main_play.score.pp, main_play.score.rank, main_play.score.statistics.count_300, main_play.score.statistics.count_100, main_play.score.statistics.count_50, main_play.score.statistics.count_miss, main_play.score.created_at, await self.convert_mods_to_int(main_play.score.mods), converted_stars, converted_bpm)
            friends = await self.database.get_user_friends(main_user[0])
            for friend in friends:
                friend_play = await self.osu.get_score_data(data.id, friend[1])
                if friend_play:
                    converted_stars = 0
                    friend_play.score.mods = 0
                    converted_bpm = 0
                    if not(await self.convert_mods_to_int(friend_play.score.mods) > 15):
                        await self.database.add_score(friend[1], data.id, 0, False, False, False, False, False, False, False, False, False, False, False, 0, 0, None)
                        continue
                    if "DT" in friend_play.score.mods or "NC" in friend_play.score.mods:
                        converted_bpm = int(
                            friend_play.score.beatmap.bpm) * 1.5
                    beatmap_mod_data = await self.osu.get_beatmap_mods(friend_play.score.beatmap.id, await self.convert_mods_to_int(friend_play.score.mods))
                    if beatmap_mod_data:
                        converted_stars = beatmap_mod_data.attributes.star_rating
                    snipability = await self.calculate_snipability(friend_play.score.beatmap.drain, friend_play.score.beatmap.difficulty_rating, {"AR": friend_play.score.beatmap.ar, "OD": friend_play.score.beatmap.accuracy}, friend_play.score.beatmap.bpm, friend_play.score.mods, friend_play.score.rank, friend_play.score.max_combo, friend_play.score.rank, friend_play.score.beatmap.count_spinners, friend_play.score.pp, friend_play.score.accuracy, friend_play.score.statistics.count_miss, friend_play.score.accuracy, friend_play.score.statistics.count_miss)
                    await self.database.add_score(friend[1], friend_play.score.beatmap.id, friend_play.score.score, friend_play.score.accuracy, friend_play.score.max_combo, friend_play.score.passed, friend_play.score.pp, friend_play.score.rank, friend_play.score.statistics.count_300, friend_play.score.statistics.count_100, friend_play.score.statistics.count_50, friend_play.score.statistics.count_miss, friend_play.score.created_at, await self.convert_mods_to_int(friend_play.score.mods), snipability)
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
        seen_friends = []
        # First we remove any friend duplicates
        for friend in friends:
            add = True  # if we are going to add or not
            for seen_friend in seen_friends:
                if seen_friends == []:
                    seen_friends.append(friend)
                    break
                if friend[2] == seen_friend[2]:
                    add = False
                    break
            if add:
                seen_friends.append(friend)

        # Now we get rid of any main users that are left in the seen friends
        for main_user in main_users:
            for seen_friend in seen_friends:
                if main_user[2] == seen_friend[2]:
                    seen_friends.remove(seen_friend)
                    break

        return seen_friends  # returns altered array

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
                users_checked = await self.add_scores(
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
                        await self.database.add_score(friend[1], play.beatmap.id, 0, None, None, None, None, None, None, None, None, None, None, None, 0, 0, None)
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
                    conv_stars, conv_bpm, max_combo = await self.convert_stars_and_bpm(friend_play.score)
                    snipability = await self.calculate_snipability(play.beatmap.drain, play.beatmap.difficulty_rating, {"AR": play.beatmap.ar, "OD": play.beatmap.accuracy}, play.beatmap.bpm, friend_play.score.mods, friend_play.score.rank, friend_play.score.max_combo, friend_play.score.rank, play.beatmap.count_spinners, play.pp, play.accuracy, play.statistics.count_miss, play.max_combo, max_combo)
                    await self.database.update_score(friend[1], play.beatmap.id, friend_play.score.score, friend_play.score.accuracy, friend_play.score.max_combo, friend_play.score.passed, friend_play.score.pp, friend_play.score.rank, friend_play.score.statistics.count_300, friend_play.score.statistics.count_100, friend_play.score.statistics.count_50, friend_play.score.statistics.count_miss, friend_play.score.created_at, await self.convert_mods_to_int(friend_play.score.mods), conv_stars, conv_bpm, snipability)

    async def add_scores(self, main_user_friends: list, main_user, play: OsuRecentScore, users_checked: list):
        # for main users who may be friends with other main users
        if main_user[1] not in users_checked:
            if not(await self.database.get_user_score_with_zeros(main_user[1], play.beatmap.id)):
                # if the user doesnt have a score and hasnt played the map, it just stores a 0 score
                await self.database.add_score(main_user[1], play.beatmap.id, 0, None, None, None, None, None, None, None, None, None, None, None, 0, 0, None)
                users_checked.append(main_user[1])
        for friend in main_user_friends:
            if friend[1] in users_checked:  # for duplicate friends over multiple main users
                continue
            if not(await self.database.get_user_score_with_zeros(friend[1], play.beatmap.id)):
                # The friend has not played the map and has not got a score saved
                await self.database.add_score(friend[1], play.beatmap.id, 0, None, None, None, None, None, None, None, None, None, None, None, 0, 0, None)
            else:
                friend_play = await self.osu.get_score_data(
                    play.beatmap.id, friend[1])
                if friend_play:
                    local_score = await self.database.get_user_beatmap_play(friend[1], play.beatmap.id)
                    if local_score is not None:
                        # if the new score is better than the stored one
                        if friend_play.score.score > int(local_score[2]):
                            _, _2, max_combo = await self.convert_stars_and_bpm(friend_play.score)
                            snipability = await self.calculate_snipability(play.beatmap.drain, play.beatmap.difficulty_rating, {"AR": play.beatmap.ar, "OD": play.beatmap.accuracy}, play.beatmap.bpm, friend_play.score.mods, friend_play.score.rank, friend_play.score.max_combo, friend_play.score.rank, play.beatmap.count_spinners, play.pp, play.accuracy, play.statistics.count_miss, play.max_combo, max_combo)
                            await self.database.update_score(friend[1], friend_play.score.beatmap.id, friend_play.score.score, friend_play.score.accuracy, friend_play.score.max_combo, friend_play.score.passed, friend_play.score.pp, friend_play.score.rank, friend_play.score.statistics.count_300, friend_play.score.statistics.count_100, friend_play.score.statistics.count_50, friend_play.score.statistics.count_miss, friend_play.score.created_at, await self.convert_mods_to_int(friend_play.score.mods), snipability)
                else:
                    pass  # because they already have a 0 score stored
            users_checked.append(friend[1])
        return users_checked

    # This calculates the maps snipability and returns a value between 0 and 1
    async def calculate_snipability(self, map_length: int, normal_difficulty: float, stats: dict, bpm: int, mods: list, rank: str, spinner_count: int, pp: float, accuracy: float, miss_count: int, user_combo: int, max_combo: int):
        snipability = 1
        # map length handler
        # for every interval of 30 seconds, the snipability increases by 0.025*
        # this maxes at 300 seconds with the snipability increasing 1*
        # this is to prevent snipes from being too easy on long maps
        if map_length > 300:
            map_length = 300
        # floor to the nearest 30 seconds
        map_length = map_length - (map_length % 30)
        # the shorter the map, the easier it is to snipe
        snipability *= (1 - ((map_length/30)*0.025))

        # map difficulty handler
        # this is for specific cases
        if stats['AR'] > 9.5:
            snipability *= 0.97
        if stats['AR'] > 10.9:
            snipability *= 0.97
        if stats['OD'] > 9:
            snipability *= 0.99
        if stats['OD'] > 9.5:
            snipability *= 0.99
        if stats['OD'] > 10:
            snipability *= 0.99

        # bpm handler
        if bpm > 200:
            snipability *= 0.99
        if bpm > 210:
            snipability *= 0.99
        if bpm > 220:
            snipability *= 0.99
        if bpm > 230:
            snipability *= 0.99
        if bpm > 240:
            snipability *= 0.99
        if bpm > 250:
            snipability *= 0.99

        # pp handler
        if pp is not None:
            if pp > 50:
                snipability *= 0.98
            elif pp > 100:
                snipability *= 0.95
            elif pp > 200:
                snipability *= 0.9
            elif pp > 300:
                snipability *= 0.8
            elif pp > 400:
                snipability *= 0.5
            elif pp > 500:
                snipability *= 0.4
            elif pp > 600:
                snipability *= 0.2

        # accuracy handler
        if miss_count == 0:
            snipability *= 0.8 # if they didnt miss, its harder to snipe
        elif miss_count > 0:
            if miss_count < 3:
                snipability = snipability + 0.1*(1-snipability) # add 10% back to the snipability
            elif miss_count < 5:
                snipability = snipability + 0.25*(1-snipability) # add 25% back to the snipability
            elif miss_count > 4:
                snipability = snipability + 0.4*(1-snipability) # add 40% back to the snipability

        if accuracy > 96:
            snipability *= 0.98
        if accuracy > 98:
            snipability *= 0.95
        if accuracy > 99:
            snipability *= 0.9
        if accuracy > 99.5:
            snipability *= 0.8
        if accuracy > 99.9:
            snipability *= 0.7

        # combo handler
        if user_combo == max_combo:
            snipability *= 0.9
        else:
            # if the users combo is between 90% and 100% of the max combo
            if user_combo >= (max_combo*0.9):
                snipability *= 0.95
            elif user_combo >= (max_combo*0.8):
                snipability *= 0.98
            elif user_combo >= (max_combo*0.7):
                snipability *= 0.99
            elif user_combo >= (max_combo*0.6):
                snipability *= 1
            elif user_combo >= (max_combo*0.5):
                snipability = snipability + 0.25*(1-snipability) # add 25% back to the snipability
            elif user_combo >= (max_combo*0.25):
                snipability = snipability + 0.60*(1-snipability) # add 60% back to the snipability
            elif user_combo >= (max_combo*0.10):
                snipability = snipability + 0.90*(1-snipability) # add 90% back to the snipability


        # difficulty handler
        # for every difficulty interval of 1, the snipability multiplier reduces by 0.25
        # maxing at 10 difficulty, the snipability multiplier is 0.5
        if normal_difficulty > 10:
            snipability *= 0.5
        else:
            snipability *= (1 - (normal_difficulty/10))
        # The easier the map, the more snipable it is.
        # This is so 6 star maps arent sniped as easily as 4 star maps, it sort of makes sense if you include passing.

        # rank handler MAKE LAST
        if rank == 'F':
            snipability = 1
        if rank == 'D':
            # half the effect of the snipability
            snipability = snipability + 0.5*(1-snipability) # add 50% back to the snipability
        if rank == 'C':
            snipability = snipability + 0.3*(1-snipability) # add 30% back to the snipability
        if rank == 'B':
            snipability = snipability + 0.2*(1-snipability) # add 20% back to the snipability
        if rank == 'A':
            snipability = snipability + 0.1*(1-snipability) # add 10% back to the snipability
        if rank == 'S':
            snipability *= 0.98
        if rank == 'SH':
            snipability *= 0.97
        remove_dt = False
        if "NC" in mods:
            remove_dt = True
            mods.append("DT") # simple fix
        if "DT" in mods and "HR" not in mods and "HD" not in mods:
            if rank == 'X':
                snipability *= 0.9 # DT SS
            if rank == 'XH':
                snipability *= 0.5 # DTFL SS
            if rank == "S":
                snipability *= 0.95 # DT S
        if "DT" in mods and "HR" in mods and "HD" not in mods:
            if rank == 'X':
                snipability *= 0.7 # DTHR SS
            if rank == 'XH':
                snipability *= 0.2 # DTHRFL SS
            if rank == "S":
                snipability *= 0.85 # DTHR S
            if rank == "SH":
                snipability *= 0.4 # DTHRFL S
        if "DT" in mods and "HD" in mods and "HR" not in mods:
            if rank == 'XH':
                snipability *= 0.8 # HDDT SS
            if rank == "SH":
                snipability *= 0.9 # HDDT S
        if "DT" in mods and "HD" in mods and "HR" in mods:
            if rank == 'XH':
                snipability *= 0.2 # HDDTHR SS
            if rank == "SH":
                snipability *= 0.5 # HDDTHR S

        # Nofail Handling
        if "NF" in mods:
            # Only nofail plays on maps less than 6 stars will really be worth, since people are more likely to use NF on higher SR maps
            if normal_difficulty < 6:
                snipability = snipability + 0.9*(1-snipability) # add 90% back to the snipability
            elif normal_difficulty < 7:
                snipability = snipability + 0.6*(1-snipability) # add 60% back to the snipability
            elif normal_difficulty < 8:
                snipability = snipability + 0.1*(1-snipability) # add 10% back to the snipability

        # spinner handler
        if spinner_count > 0:
            snipability = snipability + 0.25*(1-snipability) # add 25% back to the snipability if map has a spinner
        if spinner_count > 5:
            snipability = snipability + 0.25*(1-snipability) # add another 25% if there are lots of spinners

        # Remove DT if needed
        if remove_dt:
            mods.remove("DT")

        # return the snipability
        return snipability

    # this takes in the main users best play and their local play, adds the snipe data to the db, and posts the snipe embed to discord

    async def post_friend_snipe(self, main_user_play: OsuRecentScore, play: OsuRecentScore, main_user_db):
        main_username = main_user_db[2]
        # if the snipe doesnt exist
        if not(await self.database.get_user_snipe_on_beatmap(play.user.id, play.beatmap.id, main_user_db[0])):
            first_mods = await self.convert_mods_to_int(play.mods)
            second_mods = await self.convert_mods_to_int(main_user_play.mods)
            await self.database.add_snipe(play.user.id, play.beatmap.id, main_user_db[1], play.created_at, play.score, main_user_play.score, play.accuracy, main_user_play.accuracy, first_mods, second_mods, play.pp, main_user_play.pp)
        discord_channel = await self.database.get_channel(int(main_user_db[0]))
        while type(discord_channel) is tuple:
            discord_channel = discord_channel[0]
        post_channel = await get(self.client, interactions.Channel, channel_id=int(discord_channel))
        beatmap_data = await self.osu.get_beatmap(play.beatmap.id)
        await post_channel.send(embeds=await create_friend_snipe_embed(play, main_username, beatmap_data, main_user_play.score))
