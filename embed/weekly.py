import interactions
from data_types.osu import *
import datetime


async def create_weekly_embed(scores: list, username: str, beatmaps: list):
    embed = interactions.Embed(
        title=f"Best Weekly Plays By {username}",
        color=3709183
    )
    for i, score in enumerate(scores):
        if i <= 9:
            timestamp = await convert_datetime_to_timestamp(score[12])
            embed.add_field(name=f"{i+1}: {beatmaps[i].beatmapset.artist} - {beatmaps[i].beatmapset.title} [{beatmaps[i].version}] - <t:{timestamp}:R>",
                            value=f"▸ {score[2]:,} ▸ {round((float(score[3]) * 100), 2)}% ▸ pp: {round(float(score[6]), 2)}pp ▸ [{score[8]}/{score[9]}/{score[10]}/{score[11]}]",
                            inline=False)
    return embed


async def convert_datetime_to_timestamp(dateandtime: str):
    # convert the dateandtime string to a datetime object
    dateandtime = datetime.datetime.strptime(dateandtime, "%Y-%m-%dT%H:%M:%SZ")
    # convert the datetime object to an epoch timestamp
    timestamp = datetime.datetime.timestamp(dateandtime)
    return int(timestamp)
