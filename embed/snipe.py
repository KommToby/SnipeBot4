import interactions

from data_types.osu import Beatmap, OsuRecentScore


async def create_friend_snipe_embed(play: OsuRecentScore, main_user: str, beatmap_data: Beatmap, main_user_score: int):
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
    title_message = f"{play.user.username} just sniped {main_user} with {modstr}!"
    score_message = f"▸ {play.score:,} > {main_user_score:,} (+{play.score-main_user_score})" + \
                    f"▸ {round((float(play.accuracy) * 100), 2)}%" + \
                    f"▸ {play.rank} Rank ▸ pp: {pp}pp"

    # Avatar Handling
    if play.user.avatar_url[0] == "/":
        image = "https://osu.ppy.sh" + \
                str(play.user.avatar_url)
    else:
        image = str(play.user.avatar_url)

    # Embed Creation
    embed = interactions.Embed(
        title=title_message,
        description=f"{beatmap_data.beatmapset.artist} - {beatmap_data.beatmapset.title} [{play.beatmap.version}]" +
                    f" - {play.beatmap.difficulty_rating}:star:",
        color=327424
    )
    embed.set_thumbnail(url=beatmap_data.beatmapset.covers.list2x)
    embed.set_author(name='Snipebot by Komm', icon_url=str(image))

    # Score Details
    embed.add_field(
        name=score_message, value=f"**▸ [{play.statistics.count_300}/{play.statistics.count_100}/{play.statistics.count_50}/{play.statistics.count_miss}] ▸ {play.max_combo}x/{beatmap_data.max_combo}x ▸** [link to map]("
        + str(play.beatmap.url)
        + ")", inline=False
    )

    return embed
