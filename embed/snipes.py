import interactions
from data_types.osu import *

async def create_snipes_embed(position, pp, not_sniped_back, held_snipes, user_data: UserData, user_snipes, user_sniped, total_snipes):
    snipe_difference = user_snipes - user_sniped
    snipe_percentage = round(((user_snipes / total_snipes) * 100), 2)

    # User avatar
    if user_data.avatar_url[0] == "/":
        image = "https://osu.ppy.sh" + \
                str(user_data.avatar_url)
    else:
        image = str(user_data.avatar_url)

    # Flag
    flag = "https://osu.ppy.sh/images/flags/" + \
    user_data.country_code+".png"

    # Stats
    title = f"Snipe stats for {user_data.username} (#{position+1})"
    description = "**● Number of Snipes: **" + \
        str(user_snipes) + "\n" + "**○ Times Sniped: **" + str(user_sniped) + \
        "\n▻ **Snipe Difference: **" + \
        str(snipe_difference) + \
        "\n► **Snipe PP: **" + \
        str(pp) + \
        "\n⯀ **Held Snipes: **" + \
        str(held_snipes) + \
        "\n☐ **To-Snipe: **" + \
        str(not_sniped_back) + \
        "\nContributed **" + str(snipe_percentage) + "%**" + " of snipes!"

    # Embed object
    embed = interactions.Embed(
        title = title,
        color = 3329330
    )

    embed.description = description
    embed.set_author(name='Snipebot by Komm', icon_url = flag)
    embed.set_thumbnail(url=str(image))

    return embed