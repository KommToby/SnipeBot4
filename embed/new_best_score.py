import interactions
from data_types.osu import OsuRecentScore, Beatmap


async def create_high_score_embed(play: OsuRecentScore, sniped_friends: list, beatmap_data: Beatmap):
    # Mod handling
    if play.mods:
        modstr = ""
        for mod in play.mods:
            modstr += mod
    else:
        modstr = "No Mods"

    # PP handling
    if not play.pp:
        pp = "No"
    else:
        pp = f"{round(float(play.pp), 2)}"

    # Message Handling
    title_message = f"{play.user.username} got a new high score with {modstr}!"
    score_message = f"▸ {play.score:,} ▸ {round((float(play.accuracy) * 100), 2)}%" + \
                    f"▸ {play.rank} Rank ▸ pp: {pp}pp"

    # Number of friends sniped
    if sniped_friends:
        friend_message = f"`{', '.join(sniped_friends[:4])}{' and more!' if len(sniped_friends) > 4 else ''}`"
        friend_num = f"{len(sniped_friends)} friend(s) sniped!"

    # Avatar Handling
    if play.user.avatar_url[0] == "/":
        image = "https://osu.ppy.sh" + \
                str(play.user.avatar_url)
    else:
        image = str(play.user.avatar_url)

    # Embed Creation
    embed = interactions.Embed(
        title=title_message,
        description=f"{play.beatmapset.artist} - {play.beatmapset.title} [{play.beatmap.version}]" +
                    f" - {play.beatmap.difficulty_rating}:star:",
        color=1752220
    )
    embed.set_thumbnail(url=play.beatmapset.covers.list2x)
    embed.set_author(name='Snipebot by Komm', icon_url=str(image))

    # Sniped friends optional
    if sniped_friends:
        embed.add_field(name=friend_num, value=friend_message, inline=False)

    # Score Details
    embed.add_field(
        name=score_message, value=f"**▸ [{play.statistics.count_300}/{play.statistics.count_100}/{play.statistics.count_50}/{play.statistics.count_miss}] ▸ {play.max_combo}x/{beatmap_data.max_combo}x ▸** [link to map]("
        + str(play.beatmap.url)
        + ")", inline=False
    )

    return embed
