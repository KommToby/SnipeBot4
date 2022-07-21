import interactions

async def create_friend_list_embed(user, friends):
    embed = interactions.Embed(
        title=f"Friend list for {user['username']}",
        color=16776960,
    )
    
    if len(friends)>0:
        friend_string = ""
        for friend in friends:
            friend_string += f"{friend[2]}\n"
        embed.add_field(name=f"User has {len(friends)} friends:", value=friend_string, inline=False)
    else:
        embed.add_field(name=f"User has 0 friends", value="No friends found!", inline=False)

    return embed