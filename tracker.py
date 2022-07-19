import time, asyncio
from embed.new_best_score import *
from embed.snipe import *

class SnipeTracker:
    def __init__(self, client):
        self.client = client
        self.osu = client.osu
        self.database = client.database

    async def convert_mods_to_int(self, modarray): # converts modarray into a binary value
        value = 0
        if modarray:
            for mod in modarray:
                value+=1 if mod == "NF" else value==value
                value+=2 if mod == "EZ" else value==value
                value+=4 if mod == "TD" else value==value
                value+=8 if mod == "HD" else value==value
                value+=16 if mod == "HR" else value==value
                value+=32 if mod == "SD" else value==value
                value+=64 if mod == "DT" else value==value
                value+=128 if mod == "RX" else value==value
                value+=256 if mod == "HT" else value==value
                value+=512 if mod == "NC" else value==value
                value+=1024 if mod == "FL" else value==value
                value+=2048 if mod == "Autoplay" else value==value
                value+=4096 if mod == "SO" else value==value
                value+=8192 if mod == "Relax2" else value==value
                value+=16384 if mod == "PF" else value==value
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
                if modint%key==0:
                    modint, modarray = await self.update_decode(modint, key, modarray, moddict[key])
        if modint != 1:
            print("An error occured when decoding mod array")
        return modarray

    # Start point of the infinite loop
    async def start_loop(self):
        while True:
            try:
                await self.tracker_loop
            except Exception as e:
                print(f"Error occured in tracker loop: {e}")
                pass

    async def check_main_beatmap(self, play):
        if not(await self.database.get_beatmap(play['beatmap']['id'])): # checks to see if the map is already stored in the database
            await self.database.add_beatmap(play['beatmap']['id'], play['beatmap']['difficulty_rating'], play['beatmapset']['artist'], play['beatmapset']['title'], play['beatmap']['version'], play['beatmap']['url'], play['beatmap']['total_length'], play['beatmap']['bpm'], play['beatmapset']['creator'], play['beatmap']['status'], play['beatmap']['accuracy'], play['beatmap']['ar'], play['beatmap']['cs'], play['beatmap']['drain'], play['beatmap']['max_combo'])
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
                    await self.database.add_score(play['user_id'], play['beatmap']['id'], play['score'], play['accuracy'], play['max_combo'], play['passed'], play['pp'], play['rank'], play['statistics']['count_300'], play['statistics']['count_100'], play['statistics']['count_50'], play['statistics']['count_miss'], play['created_at'])
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
        user_play = await self.database.get_user_play(id, play['beatmap']['id']) # grabs the local score of the user on the beatmap
        online_play = await self.osu.get_score_data(play['beatmap']['id'], id) # grabs the online score to compare with the local
        if user_play: # if the local play exists first, because if the local doesnt exist we dont have to compare
            if online_play: # this shouldnt fail, but if it does we can send an error message
                if play['score'] > int(user_play[2]): # if the recent score is larger than the local score
                    await self.database.update_score(user_play[0], user_play[1], play['score'], play['accuracy'], play['max_combo'], play['passed'], play['pp'], play['rank'], play['statistics']['count_300'], play['statistics']['count_100'], play['statistics']['count_50'], play['statistics']['count_miss'], play['created_at'])
                    if play['score'] >= online_play['score']['score']: # If the recent play is the recent score, then its a new best
                        sniped_friends = await self.get_sniped_friends(play, f"{data[0]}")
                        discord_channel = f'{data[0]}'
                        post_channel = await self.client.get_channel(int(discord_channel))
                        beatmap_data = await self.osu.get_beatmap(play['beatmap']['id'])
                        await post_channel.send(embed=create_high_score_embed(play, sniped_friends, beatmap_data)) # posts the snipe embed
                        # Now we check if the main user has sniped another main user (if they are in another main users friend list)
                        main_users = await self.database.get_all_users()
                        for main_user in main_users:
                            if main_user[2] in sniped_friends: # why didnt i do it this way originally i will never know
                                friend_play = await self.osu.get_score_data(play['beatmap']['id'], play['user_id'])
                                await self.post_friend_snipe(play, friend_play['score'], play['user_id'])
        else:
            # even if the local play doesnt exist we still need to add it as a score
            await self.database.add_score(play['user_id'], play['beatmap']['id'], play['score'], play['accuracy'], play['max_combo'], play['passed'], play['pp'], play['rank'], play['statistics']['count_300'], play['statistics']['count_100'], play['statistics']['count_50'], play['statistics']['count_miss'], play['created_at'])
            if online_play: # If they have also played online they may have got a new best thats never been scanned
                if play['score'] >= online_play['score']['score']:
                    sniped_friends = await self.get_sniped_friends(play, f"{data[0]}")
                    discord_channel = f'{data[0]}'
                    post_channel = await self.client.get_channel(int(discord_channel))
                    beatmap_data = await self.osu.get_beatmap(play['beatmap']['id'])
                    await post_channel.send(embed=create_high_score_embed(play, sniped_friends, beatmap_data))

    # The main infinite loop tracker
    async def tracker_loop(self):
        # Constructor for the loop
        local_time = time.time()
        check_time = time.time()
        active_users = []
        active_friends = []
        checked_users = []
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
                            if int(play['score']) != int(recent_score): # If these values dont match it means the user has submitted a new play. Simple
                                if main_user_id not in active_users: # because they have set a new score we can add them to the active users list
                                    active_users.append(main_user_id)
                                await self.check_main_user_play(play, main_user_id, main_user_data)
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
        except:
            pass

    ## this takes in the main users best play and their local play, adds the snipe data to the db, and posts the snipe embed to discord
    async def post_friend_snipe(self, main_user_play, play, main_user_db):
        main_username = main_user_play['user']['username']
        if not(await self.database.get_user_snipe_on_beatmap(play['user']['id'], play['beatmap']['id'], main_user_db[0])): #if the snipe doesnt exist
            first_mods = await self.convert_mods_to_int(play['mods'])
            second_mods = await self.convert_mods_to_int(main_user_play['mods'])
            await self.database.add_snipe(play['user']['id'], play['beatmap']['id'], main_user_db[0], play['created_at'], play['score'], main_user_play['score'], play['accuracy'], main_user_play['accuracy'], first_mods, second_mods, play['pp'], main_user_play['pp'])
        discord_channel = f'{main_user_db[0]}'
        post_channel = await self.client.fetch_channel(int(discord_channel))
        beatmap_data = await self.osu.get_beatmap(play['beatmap']['id'])
        await post_channel.send(embed=create_friend_snipe_embed(play, main_username, beatmap_data))
