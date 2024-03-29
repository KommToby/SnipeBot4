import interactions
import random
from data_types.osu import UserData


async def create_snipable_embed(username: str, scores: list, beatmaps: list):
    embed = interactions.Embed(
        title=f"(Up to) 10 Most Snipable Maps for {username}",
        color=16753920,
    )
    # shuffle the beatmaps and links so that they are in a random order but the same order
    for i, score in enumerate(scores):
        if i < 10 and i < len(beatmaps):
            beatmap_string = f"{beatmaps[i][2]} - {beatmaps[i][3]} [{beatmaps[i][4]}]"
            embed.add_field(name=str(i+1) + ". " + beatmap_string,
                            value="[Link to map](" + str(beatmaps[i][5]) + ") " + f"({round(score[16]*100, 2)}% snipable)", inline=False)
        else:
            break
    return embed
