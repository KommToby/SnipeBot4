import interactions
import random
from data_types.osu import *


async def update_decode(modint, value, modarray, mod):
    modarray.append(mod)
    modint = modint - value
    return modint, modarray


# converts mod integer back into array of mods
async def decode_mods_to_array(modint):
    modarray = []
    if modint == '':
        return modarray
    modint = int(modint)
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
                modint, modarray = await update_decode(modint, key, modarray, moddict[key])
    if modint != 1:
        print("An error occured when decoding mod array")
    return modarray


async def frequency_check(array):
    title = ""
    best_occurences = 0
    for i in array:
        frequency = array.count(i)
        if frequency > best_occurences:
            best_occurences = frequency
            title = i
    return title, best_occurences


async def create_stats_embed(user: UserData, user_score_data, top_ten_artists, scores):
    embed = interactions.Embed(
        title=f"osu! stats for {user.username}",
        color=16737962,
    )
    embed.set_author(name="Snipebot by Komm",
                     icon_url=f"https://osu.ppy.sh/images/flags/{user.country_code}.png")

    if user.avatar_url[0] == "/":
        embed.set_thumbnail(url=f"https://osu.ppy.sh{user.avatar_url}")
    else:
        embed.set_thumbnail(url=user.avatar_url)

    artist_string = f"\n__**{user.username}'s top 10 most popular Artists:**__\n```\n"
    for _, artist in enumerate(top_ten_artists):
        artist_string += f"{artist[0]} ({artist[1]})\n"
    artist_string = artist_string + "```"

    # average map length
    average_map_length = round(
        sum(user_score_data['lengths'])/len(user_score_data['lengths']))
    if average_map_length < 60:
        average_map_length_string = f"{average_map_length} seconds"
    else:
        modulus = average_map_length % 60
        if modulus < 10:
            modulus = f"0{modulus}"
        average_map_length_string = f"{round(average_map_length/60)}:{modulus}"

    best_song, best_song_freq = await frequency_check(user_score_data['songs'])
    best_guest, best_guest_freq = await frequency_check(user_score_data['guests'])
    best_mapper, best_mapper_freq = await frequency_check(user_score_data['mappers'])
    best_mod, best_mod_freq = await frequency_check(user_score_data['mods'])
    best_mod_array = await decode_mods_to_array(best_mod)
    best_mod_string = ""
    for mod in reversed(best_mod_array):
        best_mod_string += f"{mod}"
    best_mod_string = best_mod_string

    embed.description = artist_string
    if len(user_score_data['stars']) == 0:
        average_sr = "None yet"
    else:
        average_sr = round(
            sum(user_score_data['stars'])/len(user_score_data['stars']), 2)
    # check to see if bpm values exist
    if user_score_data['bpm'] == []:
        average_bpm = "N/A"
    else:
        average_bpm = round(
            sum(user_score_data['bpm'])/len(user_score_data['bpm']))
    embed.add_field(name=f"Average SR of all your stored plays: `{average_sr}` ({len(scores)} stored plays!)\nAverage length of stored plays: `{average_map_length_string}`\nAverage BPM of stored plays: `{average_bpm}`",
                    value=f"**Most played song: `{best_song}` ({best_song_freq} instances)**\n**Favourite guest difficulty mapper: `{best_guest}` ({best_guest_freq} instances)**\n**Favourite mapper: `{best_mapper}` ({best_mapper_freq} instances)**\n**Favourite mod combination: `{best_mod_string}` ({best_mod_freq} instances)**")

    # I got bullied into this
    facts_of_the_day = ["Did you know that Shii is the mapper of Lagtrain?",
                        "Did you know that this fact of the day is new?",
                        "I am inside your walls!",
                        "Carcharodontosaurus had relatively weak jaws with a bite force estimated at 3,000 pounds per square inch.",
                        "osu! is a game that was created",
                        "flubb",
                        "Furytail sucks at facts",
                        "flubb can't use cutlery!",
                        "Did you know that Shii is the mapper of the big black?",
                        "Cookiezi is better than chocomint",
                        "China can't go 3 years without cheating in OWC",
                        "Doomsday is the sexiest osu! player",
                        "if you want to start a conversation, ask the highest ranked osu! player their thoughts on minorities",
                        "you are not hanzer",
                        "my ex wife still misses me",
                        "my ex wife asked me to stop singing wonderwall",
                        "osu! isn't real",
                        "osu! is real",
                        "You will die in 19 years, 3 months, 23 days, 9 hours, 52 minutes and 5 seconds",
                        "Help i'm trapped in a discord bot factory",
                        "The moon looks the same on the other side",
                        "Toilet water swirls the other way in Australia",
                        "Wine isn't an anagram of grape",
                        "RIP Asparagus",
                        "'This December' mapped by Komm is the best taiko map of this decade",
                        "Did you know thelewa FC'd road of resistance's hardest stream on membrane keys",
                        "99% Of osu! players give up on a map right before they are about to FC it!",
                        "Did you know, before computers were invented people used to play osu! on paper?",
                        "Did you know, the first osu! player was a monkey?",
                        "freedom dive (the old one) has more HR only FCs than HD only passes",
                        "The original My Love set was discovered on a cave wall in Cornwall, England",
                        "You will never be the best at osu!. Give up now.",
                        "penguins are 90% torso",
                        "did you know spamming mappers will get them to mod your map faster",
                        "did you know, shigetora's brother was the original owner of his account",
                        "freedom dive girl has 0 posts on r34",
                        "every planet can fit between the earth and the moon",
                        "the earth is more smooth than any non lab-made ball",
                        "it took 7 years and 8 months between the first and second SS on Kokou no Sousei",
                        "around 8180 litres of water is required to grow enough cotton to create one pair of jeans",
                        "I have rigged your home with 100 sticks of dynamite and you have 10 seconds to run",
                        "Toy is our boy",
                        "Karcher has earned more via map bounties than the winning owc team will earn total in 2022",
                        "Left right left right left right left right left right left right hold",
                        "Did you know happystick is responsible for mrekk's cycle hit DT fc"]

    embed.set_footer(text=f"Fact of the day: {random.choice(facts_of_the_day)}",
                     icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Blue_question_mark_icon.svg/1200px-Blue_question_mark_icon.svg.png")

    return embed
