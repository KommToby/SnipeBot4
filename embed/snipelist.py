import interactions


async def create_snipelist_embed(friend_username: str, beatmaps: list, links: list, type: str):
    if type.lower() == "snipability":
        title = f"<=10 most snipable that {friend_username} should snipe the main user back on"
    else:
        title = f"<=10 random maps that {friend_username} should snipe the main user back on"
    embed = interactions.Embed(
        title=title,
        color=16753920,
    )
    # shuffle the beatmaps and links so that they are in a random order but the same order
    for i, _ in enumerate(beatmaps):
        if i < 10:
            beatmap_index = i
            beatmap_string = f"{beatmaps[beatmap_index][2]} - {beatmaps[beatmap_index][3]} [{beatmaps[beatmap_index][4]}]"
            embed.add_field(name=str(i+1) + ". " + beatmap_string,
                            value="[Link to map](" + str(links[beatmap_index]) + ")", inline=False)
        else:
            break
    return embed
