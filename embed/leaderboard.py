import interactions

async def create_leaderboard_embed(leaderboard, main_username, main_snipes, main_sniped):
    embed = interactions.Embed(
        title=f"Snipe Leaderboard For {main_username}: {main_snipes} | {main_sniped}",
        color=13404313
    )

    for i, friend in enumerate(leaderboard):
        if i<=9: # only show top 10
            pp_difference = await calculate_snipe_pp_difference(friend)
            friend_message = f"{i+1}: {friend['username']}"
            friend_description = f"**Held Snipes: {friend['held_snipes']} | To-snipe: {friend['not_sniped_back']} | Snipe PP: {round(friend['snipe_pp'], 2)}** ({pp_difference})"
            embed.add_field(name=friend_message,
                            value=friend_description,
                            inline=False)
    return embed

async def calculate_snipe_pp_difference(friend):
    weight_difference = round(float(friend['snipe_pp']) - float(friend['old_pp']), 2)
    if weight_difference > 0:
        weight_difference = f"+{weight_difference}"
    return weight_difference
