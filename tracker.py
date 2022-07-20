import time, asyncio
from embed.new_best_score import *
from embed.snipe import *
from interactions.ext.get import get


class SnipeTracker:
    def __init__(self, client):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    async def convert_datetime_to_int(self, datetime: str):
        #'2021-08-23T21:31:10+00:00'
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

    async def convert_mods_to_int(self, modarray): # converts modarray into a binary value
        value = 0
        if modarray:
            for mod in modarray:
                if mod == "NF": value+=1
                elif mod == "EZ": value+=2
                elif mod == "TD": value+=4
                elif mod == "HD": value+=8
                elif mod == "HR": value+=16
                elif mod == "SD": value+=32
                elif mod == "DT": value+=64
                elif mod == "RX": value+=128
                elif mod == "HT": value+=256
                elif mod == "NC": value+=512
                elif mod == "FL": value+=1024
                elif mod == "Autoplay": value+=2048
                elif mod == "SO": value+=4096
                elif mod == "Relax2": value+=8192
                elif mod == "PF": value+=16384
        return value

    async def update_decode(self, modint, value, modarray, mod):
        modarray.append(mod)
        modint = modint - value
        return modint, modarray

    async def decode_mods_to_array(self, modint): # converts mod integer back into array of mods
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
                if (modint-key)>=0:
                    modint, modarray = await self.update_decode(modint, key, modarray, moddict[key])
        if modint != 1:
            print("An error occured when decoding mod array")
        return modarray

    # Start point of the infinite loop
    async def start_loop(self):
        while True:
            try:
                await self.tracker_loop()
            except Exception as e:
                print(f"Error occured in tracker loop: {e}")
                pass

    async def check_main_beatmap(self, play):
        if not(await self.database.get_beatmap(play['beatmap']['id'])): # checks to see if the map is already stored in the database
            await self.database.add_beatmap(play['beatmap']['id'], play['beatmap']['difficulty_rating'], play['beatmapset']['artist'], play['beatmapset']['title'], play['beatmap']['version'], play['beatmap']['url'], play['beatmap']['total_length'], play['beatmap']['bpm'], play['beatmapset']['creator'], play['beatmap']['status'], play['beatmap']['beatmapset_id'], play['beatmap']['accuracy'], play['beatmap']['ar'], play['beatmap']['cs'], play['beatmap']['drain'])
            await self.add_snipes(play) # Checks all users in database for snipes on the new beatmap

    async def get_sniped_friends(self, play, main_user_discord):
        sniped_friends = []
        friends = await self.database.get_user_friends(main_user_discord) # gets list of friends linked to main user
        for friend in friends:
            friend_play = await self.osu.get_score_data(play['beatmap']['id'], friend[1]) # grabs the friends play on this map
            friend_id = f'{friend[1]}'
            friend_username = f'{friend[2]}'
            if friend_play: # if the friend has a score saved on this map
                score = friend_play['score']['score']
                if not (await self.database.get_user_beatmap_play(friend_id, play['beatmap']['id'])):
                    await self.database.add_score(play['user_id'], play['beatmap']['id'], play['score'], play['accuracy'], play['max_combo'], play['passed'], play['pp'], play['rank'], play['statistics']['count_300'], play['statistics']['count_100'], play['statistics']['count_50'], play['statistics']['count_miss'], play['created_at'], await self.convert_mods_to_int(play['mods']))
                if friend_play['score']['score'] < play['score']: # this is the snipe check                   # print(f"\t Adding active snipe for {friend_play['score']['user']['username]}")
                    sniped_friends.append(friend_username)
                    if not(await self.database.get_user_snipe_on_beatmap(play['user_id'], play['beatmap']['id'], friend_id)):
                        first_mods = await self.convert_mods_to_int(play['mods'])
                        second_mods = await self.convert_mods_to_int(friend_play['score']['mods'])
                        await self.database.add_snipe(play['user_id'], play['beatmap']['id'], friend_id, play['created_at'], play['score'], friend_play['score']['score'], play['accuracy'], friend_play['score']['accuracy'], first_mods, second_mods, play['pp'], friend_play['score']['pp']) # adds the snipe to the database
                        main_users = await self.database.get_all_users()
                        for main_user in main_users: # In case the main user from one server is a friend on another
                            if str(friend_play['score']['user']['id']) == str(main_user[1]):
                                await self.post_friend_snipe(friend_play['score'], play, friend_id)
        return sniped_friends

    async def check_main_user_play(self, play, id, data):
        await self.check_main_beatmap(play) # first checks the map to see if it is already stored or not
        user_play = await self.database.get_user_beatmap_play(id, play['beatmap']['id']) # grabs the local score of the user on the beatmap
        online_play = await self.osu.get_score_data(play['beatmap']['id'], id) # grabs the online score to compare with the local
        if user_play: # if the local play exists first, because if the local doesnt exist we dont have to compare
            if online_play: # this shouldnt fail, but if it does we can send an error message
                if play['score'] > int(user_play[2]): # if the recent score is larger than the local score
                    await self.database.update_score(user_play[0], user_play[1], play['score'], play['accuracy'], play['max_combo'], play['passed'], play['pp'], play['rank'], play['statistics']['count_300'], play['statistics']['count_100'], play['statistics']['count_50'], play['statistics']['count_miss'], play['created_at'], await self.convert_mods_to_int(play['mods']))
                    if play['score'] >= online_play['score']['score']: # If the recent play is the recent score, then its a new best
                        sniped_friends = await self.get_sniped_friends(play, f"{data[0]}")
                        discord_channel = f'{data[0]}'
                        post_channel = await get(self.client, interactions.Channel, channel_id=int(discord_channel))
                        beatmap_data = await self.osu.get_beatmap(play['beatmap']['id'])
                        await post_channel.send(embeds=await create_high_score_embed(play, sniped_friends, beatmap_data)) # posts the snipe embed
                        # Now we check if the main user has sniped another main user (if they are in another main users friend list)
                        main_users = await self.database.get_all_users()
                        for main_user in main_users:
                            if main_user[2] in sniped_friends: # why didnt i do it this way originally i will never know
                                friend_play = await self.osu.get_score_data(play['beatmap']['id'], play['user_id'])
                                await self.post_friend_snipe(play, friend_play['score'], play['user_id'])
        else:
            # even if the local play doesnt exist we still need to add it as a score
            await self.database.add_score(play['user_id'], play['beatmap']['id'], play['score'], play['accuracy'], play['max_combo'], play['passed'], play['pp'], play['rank'], play['statistics']['count_300'], play['statistics']['count_100'], play['statistics']['count_50'], play['statistics']['count_miss'], play['created_at'], await self.convert_mods_to_int(play['mods']))
            if online_play: # If they have also played online they may have got a new best thats never been scanned
                if play['score'] >= online_play['score']['score']:                    
                    sniped_friends = await self.get_sniped_friends(play, f"{data[0]}")
                    discord_channel = f'{data[0]}'
                    post_channel = await get(self.client, interactions.Channel, channel_id=int(discord_channel))
                    beatmap_data = await self.osu.get_beatmap(play['beatmap']['id'])
                    await post_channel.send(embeds=await create_high_score_embed(play, sniped_friends, beatmap_data))

    # The main infinite loop tracker
    async def tracker_loop(self):
        # Constructor for the loop
        local_time = time.time()
        check_time = time.time()
        active_users = []
        active_friends = []
        checked_users = []
        beatmaps_to_scan = [] # This is after we check for friends, we can scan the new beatmaps and add them to the database
        checked_users_count = 0
        # Beginning of the loop
        try:
            start_time = time.time()
            users = await self.database.get_all_users()
            for data in users:
                main_user_id = f"{data[1]}" # Stores the user id of the main user
                main_user_data = await self.osu.get_user_data(main_user_id) # Gets the data of the main user
                if main_user_data:
                    recent_plays = await self.osu.get_recent_plays(main_user_id) # Gets the recent plays of the main user
                    recent_score = await self.database.get_main_recent_score(main_user_id) # Gets the recent score of the main user from the database to compare
                    print(f"     checking main user {main_user_data['username']} [{round((time.time() - local_time), 2)}s]")
                    local_time = time.time() # reset the api timer
                    if recent_plays:
                        for play in recent_plays:
                            if int(play['score']) != int(recent_score[0]): # If these values dont match it means the user has submitted a new play. Simple
                                if main_user_id not in active_users: # because they have set a new score we can add them to the active users list
                                    active_users.append(main_user_id)
                                await self.check_main_user_play(play, main_user_id, data)
                                await self.database.update_main_recent_score(main_user_id, recent_plays[0]['score']) # this has to always update for the 0 index
                            else:
                                if main_user_id in active_users: # if the score is the same from the last loop we can consider removing them as an active user
                                    if (time.time() - check_time) > 300: # if said user hasnt set a play since 5 minutes they are removed from the active users list
                                        active_users.remove(main_user_id)
                                await self.database.update_main_recent_score(main_user_id, recent_plays[0]['score']) # we put this same command in because we break out of the loop
                                break # we break out of the loop because if the most recent play is the same, we do not need to continue checking other older plays
                    checked_users_count+=1 # Implement the checked users counter used for priority tracking
                    if main_user_id not in checked_users:
                        checked_users.append(main_user_id) # append the user to the priority tracking list
                else:
                    print(f"An issue occured when trying to get user data for {data[2]}")
            
            # Now we check all of the friends, the second part of the tracking loop
            all_friends = await self.database.get_all_friends()
            check_time = time.time() # we reset the check time
            # Below is dupe removal, it also removes any main users from the list.
            all_friends = await self.check_duplicate_friends(all_friends, users)
            for friend in all_friends:
                # active user check
                if checked_users_count > 15:
                    pass # TODO
                    # tbh this doesnt need to be implemented for a while, because its pretty fast
                friend_id = f"{friend[1]}"
                friend_data = await self.osu.get_user_data(friend_id)
                if friend_data:
                    await self.database.update_friend_username(friend_data['username'], friend_id)
                    print(f"     checking {friend_data['username']} [{round((time.time() - local_time), 2)}s]")
                    local_time = time.time() # reset api timer
                    ## Below we scan every single friend, which is why we did the removals above
                    recent_plays = await self.osu.get_recent_plays(friend_id)
                    if recent_plays:
                        recent_score = await self.database.get_friend_recent_score(friend_id)
                        if int(recent_plays[0]['score']) != int(recent_score[0]): # checks if their most recent play is the same as last loop
                            if friend_id not in active_friends:
                                active_friends.append(friend_id)
                            # This is when the score / snipe tracking really begins
                            for main_user in users:
                                friend_found = False # If we find the friend in the main users friend list, this will be the identifier
                                main_user_friends_list = await self.database.get_main_user_friends(main_user[1])
                                if main_user_friends_list is not None:
                                    for friend in main_user_friends_list:
                                        if friend[1] == friend_id:
                                            friend_found = True
                                            break
                                if friend_found: # If the main user has this friend on their friends list, we can scan their play against them
                                    # Now we can compare the friends recent plays against this main user
                                    for play in recent_plays:
                                        beatmap_id = play['beatmap']['id']
                                        # We can add this beatmap to the database if it hasnt been added before
                                        if not(await self.database.get_beatmap(beatmap_id)):
                                            if beatmap_id not in beatmaps_to_scan:
                                                beatmaps_to_scan.append(beatmap_id)
                                            # ^ adds the map to the database if it is not already stored
                                        if int(play['score']) != int(recent_score[0]): # Checks if its an old score, once it hits this, it doesnt need to loop anymore
                                            # Now we see if the bot has already scanned this score but it wasnt recent
                                            local_score = await self.database.get_user_score_with_zeros(friend_id, play['beatmap']['id'])
                                            if local_score:
                                                if str(play['score']) != local_score[2]: # the score is unique, so we can continue
                                                    # Comparison between friend and main user begins here
                                                    main_user_play = await self.osu.get_user_play(main_user[1], beatmap_id)
                                                    if main_user_play: # if the main user has actually played the map
                                                        if int(play['score']) > int(main_user_play['score']): # if it is a snipe
                                                            if not(await self.database.get_user_score_on_beatmap(friend_id, beatmap_id, play['score'])):
                                                                # Now we check if the friend has played the map before or not
                                                                if not(await self.database.get_score(friend_id, beatmap_id)):
                                                                    # this means its the friends first time playing the beatmap, so we add the score
                                                                    await self.database.add_score(friend_id, beatmap_id, play['score'], play['accuracy'], play['max_combo'], play['passed'], play['pp'], play['rank'], play['statistics']['count_300'], play['statistics']['count_100'], play['statistics']['count_50'], play['statistics']['count_miss'], play['created_at'], await self.convert_mods_to_int(play['mods']))
                                                                    # now we make sure the user hasnt (somehow) got a snipe on this beatmap before
                                                                    if not(await self.database.get_user_snipe_on_beatmap(friend_id, beatmap_id, main_user[1])):
                                                                        # Now we can post the friend snipe
                                                                        await self.post_friend_snipe(main_user_play, play, main_user)
                                                                        # But now we need to check if the friend is a main user in another server, and post their new best there
                                                                        for other_main_user in users:
                                                                            if other_main_user == play['user_id']: # They are!
                                                                                # now we need to post the new top play in the main users server
                                                                                sniped_friends = await self.get_sniped_friends(play, other_main_user[0])
                                                                                post_channel = await get(self.client, interactions.Channel, channel_id=int(other_main_user[0]))
                                                                                beatmap_data = await self.osu.get_beatmap_data(beatmap_id)
                                                                                await post_channel.send(embeds=await create_high_score_embed(play, sniped_friends, beatmap_data))
                                                                
                                                                else: # the user has played the beatmap before
                                                                    # note, this cant be the main user on another server, since the main user play score would have to be identical for a new high score
                                                                    local_score = await self.database.get_score(friend_id, beatmap_id)
                                                                    if int(play['score']) > int(local_score[2]): # if its their new best
                                                                        await self.database.update_score(friend_id, beatmap_id, play['score'], play['accuracy'], play['max_combo'], play['passed'], play['pp'], play['rank'], play['statistics']['count_300'], play['statistics']['count_100'], play['statistics']['count_50'], play['statistics']['count_miss'], play['created_at'], await self.convert_mods_to_int(play['mods']))
                                                                        # now we check if the user has got a snipe on this beatmap before
                                                                        if not(await self.database.get_user_snipe_on_beatmap(friend_id, beatmap_id, main_user[1])):
                                                                            # Now we can post the friend snipe
                                                                            await self.post_friend_snipe(main_user_play, play, main_user)
                                                        elif int(play['score']) == int(main_user_play['score']):
                                                            # this means they have the IDENTICAL score, so they might just be the main user on another server comparing against themself
                                                            if str(play['user_id']) == main_user[1]:
                                                                # this means that they are
                                                                await self.check_main_user_play(play, main_user[1], main_user)
                                                    if str(play['score']) > local_score[2]:
                                                        await self.database.update_score(friend_id, beatmap_id, play['score'], play['accuracy'], play['max_combo'], play['passed'], play['pp'], play['rank'], play['statistics']['count_300'], play['statistics']['count_100'], play['statistics']['count_50'], play['statistics']['count_miss'], play['created_at'], await self.convert_mods_to_int(play['mods']))
                                                    await self.database.update_friend_recent_score(friend_id, play['score'])
                                                else:
                                                    await self.database.update_friend_recent_score(friend_id, play['score'])
                                                    break
                                        else:
                                            # now we need to set the most recent play to their recent score, and break out of the loop
                                            await self.database.update_friend_recent_score(friend_id, recent_plays[0]['score'])
                                            break
                        else: # there has been no change since last loop
                            if friend_id in active_friends:
                                active_friends.remove(friend_id)
                            pass
                    checked_users_count+=1
                    if friend_id not in checked_users:
                        checked_users.append(friend_id)
            if beatmaps_to_scan != []:
                print(f"     checking {len(beatmaps_to_scan)} new beatmaps")
                await self.check_new_beatmaps(beatmaps_to_scan)
        except Exception as e:     
            print(f"Error occured during main tracking loop: {e}")            
            pass

    async def check_new_beatmaps(self, beatmaps_to_scan):
        # maps that are passed in shouldnt be in the db, but we double check anyway
        for beatmap_id in beatmaps_to_scan:
            if not(await self.database.get_beatmap(beatmap_id)):
                # beatmap is not in db
                beatmap_data = await self.osu.get_beatmap_data(beatmap_id)
                await self.database.add_beatmap(beatmap_id, beatmap_data['difficulty_rating'], beatmap_data['beatmapset']['artist'], beatmap_data['beatmapset']['title'], beatmap_data['version'], beatmap_data['url'], beatmap_data['total_length'], beatmap_data['bpm'], beatmap_data['beatmapset']['creator'], beatmap_data['status'], beatmap_data['beatmapset_id'], beatmap_data['accuracy'], beatmap_data['ar'], beatmap_data['cs'], beatmap_data['drain'])
                await self.add_new_beatmap_snipes(beatmap_data) # should all be passive snipes
            else: # this should not happen
                print(f"program attempted to check new beatmap that was already stored - {beatmap_id}")
                pass

    async def add_new_beatmap_snipes(self, data):
        # data is beatmap data
        # we need to check all users for snipes on this map - and scores too I guess
        main_users = await self.database.get_all_users()
        for main_user in main_users:
            main_play = await self.osu.get_score_data(data['id'], main_user[1])
            if main_play:
                # first we add the score of the main user
                await self.database.add_score(main_user[1], data['id'], main_play['score']['score'], main_play['score']['accuracy'], main_play['score']['max_combo'], main_play['score']['passed'], main_play['score']['pp'], main_play['score']['rank'], main_play['score']['statistics']['count_300'], main_play['score']['statistics']['count_100'], main_play['score']['statistics']['count_50'], main_play['score']['statistics']['count_miss'], main_play['score']['created_at'], await self.convert_mods_to_int(main_play['score']['mods']))
                friends = await self.database.get_user_friends(main_user[0])
                for friend in friends:
                    friend_play = await self.osu.get_score_data(data['id'], friend[1])
                    if friend_play:
                        await self.database.add_score(friend[1], data['id'], friend_play['score']['score'], friend_play['score']['accuracy'], friend_play['score']['max_combo'], friend_play['score']['passed'], friend_play['score']['pp'], friend_play['score']['rank'], friend_play['score']['statistics']['count_300'], friend_play['score']['statistics']['count_100'], friend_play['score']['statistics']['count_50'], friend_play['score']['statistics']['count_miss'], friend_play['score']['created_at'], await self.convert_mods_to_int(friend_play['score']['mods']))
                        if self.convert_datetime_to_int(friend_play['score']['created_at']) > self.convert_datetime_to_int(main_play['score']['created_at']):
                            # this means friend has sniped main play if they got higher score
                            if friend_play['score']['score'] > main_play['score']['score']:
                                # a passive snipe, but we need to check if they have sniped before
                                if not(await self.database.get_snipe(friend[1], data['id'], main_user[1])):
                                    # now its a first-time snipe
                                    first_mods = await self.convert_mods_to_int(friend_play['score']['mods'])
                                    second_mods = await self.convert_mods_to_int(main_play['score']['mods'])
                                    await self.database.add_snipe(friend[1], data['id'], main_user[1], friend_play['score']['created_at'], friend_play['score']['score'], main_play['score']['score'], friend_play['score']['accuracy'], main_play['score']['accuracy'], first_mods, second_mods, friend_play['score']['pp'], main_play['score']['pp'])
                            else:
                                if friend_play['score']['score'] < main_play['score']['score']:
                                    # a passive snipe from the main user onto the friend
                                    if not(await self.database.get_sniped(main_user[1], data['id'], friend[1])):
                                        first_mods = await self.convert_mods_to_int(main_play['score']['mods'])
                                        second_mods = await self.convert_mods_to_int(friend_play['score']['mods'])
                                        await self.database.add_snipe(main_user[1], data['id'], friend[1], main_play['score']['created_at'], main_play['score']['score'], friend_play['score']['score'], main_play['score']['accuracy'], friend_play['score']['accuracy'], first_mods, second_mods, main_play['score']['pp'], friend_play['score']['pp'])
                    else:
                        # if the friend has never played the map we add an empty score
                        await self.database.add_score(friend[1], data['id'], 0, False, False, False, False, False, False, False, False, False, False, False)

    async def check_duplicate_friends(self, friends, main_users):
        for friend in friends:
            while friends.count(friend) > 1: # we only want 1 of a friend
                friends.remove(friend)
        for main_user in main_users:
            while friends.count(main_user) > 0: # we dont want to check a main user as a friend
                friends.remove(main_user)
        return friends # returns altered array

    # When given a play, checks all users for snipes on that map.
    async def add_snipes(self, play):
        users_checked = []
        friends_to_skip = [] # for friends who dont have plays found when scanning the main user
        main_users = await self.database.get_all_users()
        for main_user in main_users: # Check all main users to see if they have played the map
            main_user_play = await self.osu.get_score_data(play['beatmap']['id'], main_user[1])
            main_user_friends = await self.database.get_user_friends(main_user[0])
            if main_user_play:
                for friend in main_user_friends:
                    if friend[1] not in friends_to_skip:
                        friend_play = await self.osu.get_score_data(play['beatmap']['id'], friend[1])
                        if friend_play:
                            if self.convert_datetime_to_int(friend_play['score']['created_at']) > self.convert_datetime_to_int(main_user_play['score']['created_at']):
                                if friend_play['score']['score'] > main_user_play['score']['score']:
                                    if not(await self.database.get_snipe(friend[1], play['beatmap']['id'], main_user[1])):
                                        # we can check to see if this is the snipe thats just been tracked
                                        if str(play['user']['id']) == str(friend[1]) and str(play['score']) == str(friend_play['score']['score']):
                                            await self.post_friend_snipe(main_user_play, play, main_user)
                                        else: # if the play is not exactly the same as their global, it may be newer somehow
                                            play_date = await self.convert_datetime_to_int(play['created_at'])
                                            if play_date > await self.convert_datetime_to_int(friend_play['score']['created_at']) and str(friend[1]) == str(play['user']['id']):
                                                # play is newer than their old play, and it is their play
                                                if play['score'] > main_user_play['score']['score']: # this is still an active snipe
                                                    await self.post_friend_snipe(main_user_play, play, main_user)
                                            else: # this means their global play is better than the one they just did, but it is a passive snipe since its never been added to db
                                                first_mods = await self.convert_mods_to_int(play['mods'])
                                                second_mods = await self.convert_mods_to_int(main_user_play['mods'])
                                                await self.database.add_snipe(play['user']['id'], play['beatmap']['id'], main_user[1], play['created_at'], play['score'], main_user_play['score'], play['accuracy'], main_user_play['accuracy'], first_mods, second_mods, play['pp'], main_user_play['pp'])
                            else: # if the main user play is more recent than the friend play (if they submitted in the exact same second, its not considered a snipe)
                                if main_user_play['score']['score'] > friend_play['score']['score']:
                                    if not(await self.database.get_snipe(main_user[1], play['beatmap']['id'], friend[1])):
                                        if main_user_play['score']['score'] > play['score']: # for sanity
                                            # this is a passive snipe for the main user
                                            first_mods = await self.convert_mods_to_int(main_user_play['mods'])
                                            second_mods = await self.convert_mods_to_int(play['mods'])
                                            await self.database.add_snipe(main_user[1], play['beatmap']['id'], friend[1], main_user_play['score']['created_at'], main_user_play['score']['score'], friend_play['score']['score'], main_user_play['accuracy'], friend_play['accuracy'], first_mods, second_mods, main_user_play['pp'], friend_play['pp'])
                            if friend[1] not in friends_to_skip:
                                friend_local_score = await self.database.get_score(friend[1], play['beatmap']['id'])
                                if friend_local_score is not None:
                                    if friend_play['score']['score'] > friend_local_score[2]:
                                        # we need to update their local score
                                        await self.database.update_score(friend[1], play['beatmap']['id'], friend_play['score']['score'], friend_play['score']['accuracy'], friend_play['score']['max_combo'], friend_play['score']['passed'], friend_play['score']['pp'], friend_play['score']['rank'], friend_play['score']['statistics']['count_300'], friend_play['score']['statistics']['count_100'], friend_play['score']['statistics']['count_50'], friend_play['score']['statistics']['count_miss'], friend_play['score']['created_at'], await self.convert_mods_to_int(friend_play['score']['mods']))
                        else: # if the friend play doesnt exist, we still add a 0-score to the database to speed up in future
                            if not(await self.database.get_user_score_with_zeros(friend[1], play['beatmap']['id'])):
                                await self.database.add_score(friend[1], play['beatmap']['id'], 0, None, None, None, None, None, None, None, None, None, None)
                            friends_to_skip.append(friend[1]) # when friends get scanned for plays, this user gets skipped as we know they dont have a play.
            else:
                # if the main user hasnt played the map, only scores need to be checked
                users_checked = self.add_scores(main_user_friends, main_user, play, users_checked)

    async def add_scores(self, main_user_friends, main_user, play, users_checked):
        if main_user[1] not in users_checked: # for main users who may be friends with other main users
            if not(await self.database.get_user_score_with_zeros(main_user, play['beatmap']['id'])):
                # if the user doesnt have a score and hasnt played the map, it just stores a 0 score
                await self.database.add_score(main_user[1], play['beatmap']['id'], 0, None, None, None, None, None, None, None, None, None, None)
                users_checked.append(main_user[1])
        for friend in main_user_friends:
            if friend[1] not in users_checked: # for duplicate friends over multiple main users
                if not(await self.database.get_user_score_with_zeros(friend[1], play['beatmap']['id'])):
                    # The friend has not played the map and has not got a score saved
                    await self.database.add_score(friend[1], play['beatmap']['id'], 0, None, None, None, None, None, None, None, None, None, None)
                else:
                    friend_play = self.osu.get_score_data(play['beatmap']['id'], friend[1])
                    if friend_play:
                        local_score = await self.database.get_user_beatmap_play(friend[1], play['beatmap']['id'])
                        if local_score is not None:
                            if friend_play['score']['score'] > int(local_score[2]): # if the new score is better than the stored one
                                await self.database.update_score(friend[1], friend_play['score']['beatmap']['id'], friend_play['score']['score'], friend_play['score']['accuracy'], friend_play['score']['max_combo'], friend_play['score']['passed'], friend_play['score']['pp'], friend_play['score']['rank'], friend_play['score']['statistics']['count_300'], friend_play['score']['statistics']['count_100'], friend_play['score']['statistics']['count_50'], friend_play['score']['statistics']['count_miss'], friend_play['score']['created_at'], await self.convert_mods_to_int(friend_play['score']['mods']))
                    else:
                        pass # because they already have a 0 score stored
                users_checked.append(friend[1])
        return users_checked

    ## this takes in the main users best play and their local play, adds the snipe data to the db, and posts the snipe embed to discord
    async def post_friend_snipe(self, main_user_play, play, main_user_db):
        main_username = main_user_play['user']['username']
        if not(await self.database.get_user_snipe_on_beatmap(play['user']['id'], play['beatmap']['id'], main_user_db[0])): #if the snipe doesnt exist
            first_mods = await self.convert_mods_to_int(play['mods'])
            second_mods = await self.convert_mods_to_int(main_user_play['mods'])
            await self.database.add_snipe(play['user']['id'], play['beatmap']['id'], main_user_db[0], play['created_at'], play['score'], main_user_play['score'], play['accuracy'], main_user_play['accuracy'], first_mods, second_mods, play['pp'], main_user_play['pp'])
        discord_channel = f'{main_user_db[0]}'
        post_channel = await get(self.client, interactions.Channel, channel_id=int(discord_channel))
        beatmap_data = await self.osu.get_beatmap(play['beatmap']['id'])
        await post_channel.send(embeds=await create_friend_snipe_embed(play, main_username, beatmap_data))
