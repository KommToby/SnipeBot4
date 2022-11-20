import interactions, random
from data_types.osu import *

async def create_weekly_embed(scores: list, username: str, beatmaps: list):
    embed = interactions.Embed(
        title=f"Best Weekly Plays By {username}",
        color=3709183
    )
    for i, score in enumerate(scores):
        if i<=9:
            embed.add_field(name=f"{i+1}: {beatmaps[i].beatmapset.artist} - {beatmaps[i].beatmapset.title} [{beatmaps[i].version}]",
                            value=f"▸ {score[2]:,} ▸ {round((float(score[3]) * 100), 2)}% ▸ pp: {round(float(score[6]), 2)}pp ▸ [{score[8]}/{score[9]}/{score[10]}/{score[11]}]",
                            inline=False)
    return embed
