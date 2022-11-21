import interactions
import random
from data_types.osu import UserData

async def create_count_embed(player_username: str, mapper_username: str, scores: list):
    embed = interactions.Embed(
        title=f"Maps by {mapper_username} that {player_username} has played",
        color=8421504,
    )
    embed.add_field(
        name="Maps",
        value=f"{len(scores)}",
        inline=True,
    )
    return embed