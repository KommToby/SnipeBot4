import interactions

async def create_leaderboard_embed(leaderboard, main_username, main_snipes, main_sniped, sort):
    if sort == "snipe_pp":
        sort = "Snipe PP"
    elif sort == "held":
        sort = "Held Snipes"
    elif sort == "tosnipe":
        sort = "To-snipe"
    embed = interactions.Embed(
        title=f"Snipe Leaderboard For {main_username}: {main_snipes} | {main_sniped} | Sort by {sort}",
        color=3152180
    )

    for i, friend in enumerate(leaderboard):
        if i<=9: # only show top 10
            pp_difference = await calculate_snipe_pp_difference(friend)
            friend_message = f"{i+1}: {friend['username']}"
            friend_description = f"**Held Snipes: {friend['held_snipes']} | To-snipe: {friend['not_sniped_back']} | Snipe PP: {round(friend['snipe_pp'], 2)}** ({pp_difference})"
            embed.add_field(name=friend_message,
                            value=friend_description,
                            inline=False)
    embed.set_footer(text=f"Snipe PP Penalty Maxes At ~1940pp (5 Raw Snipe PP = 1 Snipe PP)", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Blue_question_mark_icon.svg/1200px-Blue_question_mark_icon.svg.png")
    return embed

async def calculate_snipe_pp_difference(friend):
    weight_difference = round(float(friend['snipe_pp']) - float(friend['old_pp']), 2)
    if weight_difference > 0:
        weight_difference = f"+{weight_difference}"
    return weight_difference
