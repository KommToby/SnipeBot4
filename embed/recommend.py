import interactions
import random
from data_types.osu import UserData

async def create_recommend_embed(friend_username: str, beatmaps: list, links: list):
    embed = interactions.Embed(
        title=f"<=10 maps the {friend_username} should snipe the main user on",
        color=16753920,
    )
    # shuffle the beatmaps and links so that they are in a random order but the same order
    for i, _ in enumerate(beatmaps):
        if i < 10:
            beatmap_index = i
            beatmap_string = f"{beatmaps[beatmap_index][2]} - {beatmaps[beatmap_index][3]} [{beatmaps[beatmap_index][4]}]"
            embed.add_field(name=str(i+1) + ". " + beatmap_string, value="[Link to map](" + str(links[beatmap_index]) + ")", inline=False)
        else:
            break
    return embed