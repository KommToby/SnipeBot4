import interactions
import random
from data_types.osu import UserData


async def create_snipable_embed(username: str, scores: list, beatmaps: list):
    embed = interactions.Embed(
        title=f"(Up to) 10 Most Snipable Maps for {username}",
        color=16753920,
    )
    # shuffle the beatmaps and links so that they are in a random order but the same order
    for i, _ in enumerate(scores):
        if i < 10:
            beatmap_index = i
            beatmap_string = f"{beatmaps[beatmap_index][2]} - {beatmaps[beatmap_index][3]} [{beatmaps[beatmap_index][4]}]"
            embed.add_field(name=str(i+1) + ". " + beatmap_string,
                            value="[Link to map](" + str(beatmaps[beatmap_index][5]) + ")", inline=False)
        else:
            break
    return embed
