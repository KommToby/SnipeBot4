import interactions

async def create_osu_embed(user):
    embed = interactions.Embed(
        title=f"osu! profile for {user['username']}",
        color=16711680,
    )
    embed.description = \
        f"""**Rank**: #{user['statistics']['global_rank']:,} **Weighted pp**: {round(user['statistics']['pp']):,}
**Country Rank**: #{user['statistics']['country_rank']:,}
**Accuracy**: {round(user['statistics']['hit_accuracy'], 2)}%
"""
    embed.set_author(name="Snipebot 3 by Komm",
                    icon_url=f"https://osu.ppy.sh/images/flags/{user['country_code']}.png")
    if user['avatar_url'][0] == "/":
        embed.set_thumbnail(url=f"https://osu.ppy.sh{user['avatar_url']}")
    else:
        embed.set_thumbnail(url=user['avatar_url'])
    if user['cover_url']:
        embed.set_image(url=user["cover_url"])
    return embed