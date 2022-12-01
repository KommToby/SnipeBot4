import interactions
import datetime


async def create_best_embed(best_plays, username: str, period: str, beatmap: list):
    embed = interactions.Embed(
        title=f"<=10 Best plays for {username} in the past {period}",
        color=65280,
    )
    for i, play in enumerate(best_plays):
        if i > 9:
            break
        # if they are in the top 3 we give a gold, silver, or bronze medal before their name
        if i == 0:
            medal = "🥇"
        elif i == 1:
            medal = "🥈"
        elif i == 2:
            medal = "🥉"
        else:
            medal = ""
        
        mods = ""
        if play[13] != 0:
            modarray = await decode_mods_to_array(play[13])
            for mod in modarray:
                mods += mod
        else:
            mods = "No Mods"

        embed.add_field(
            name=f"**#{i+1}** - {beatmap[i][2]} - {beatmap[i][3]} [{beatmap[i][4]}] +{mods} {medal}",
            value=f"<t:{await convert_datetime_to_timestamp(play[12])}:R>** - {play[6]}pp**",
            inline=False,
        )

    if len(best_plays) == 0:
        embed.add_field(
            name=f"No plays found in the past {period}",
            value="",
            inline=False,
        )

    embed.set_footer(text=f"NOTE: Plays only store if one of the main users has also played the map!")

    return embed

async def convert_datetime_to_timestamp(dateandtime: str):
    # convert the dateandtime string to a datetime object
    dateandtime = datetime.datetime.strptime(dateandtime, "%Y-%m-%dT%H:%M:%SZ")
    # convert the datetime object to an epoch timestamp
    timestamp = datetime.datetime.timestamp(dateandtime)
    return int(timestamp)

async def update_decode(modint: int, value: int, modarray: list, mod: str):
        modarray.append(mod)
        modint = modint - value
        return modint, modarray

# converts mod integer back into array of mods
async def decode_mods_to_array(modint: int):
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
                modint, modarray = await update_decode(modint, key, modarray, moddict[key])
    if modint != 0:
        print("An error occured when decoding mod array")
    return modarray
