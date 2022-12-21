import interactions


async def create_actives_embed(active_users: dict):
    embed = interactions.Embed(
        title=f"10 Most Active Users Being Tracked This Week",
        color=8421504,
    )
    for i, user in enumerate(active_users):
        # if they are in the top 3 we give a gold, silver, or bronze medal before their name
        if i == 0:
            medal = "🥇"
        elif i == 1:
            medal = "🥈"
        elif i == 2:
            medal = "🥉"
        else:
            medal = ""
        embed.add_field(
            name=f"**#{i+1} - {user[0]} {medal}**",
            value=f"{user[1]} Plays This Week",
            inline=False,
        )

    return embed
