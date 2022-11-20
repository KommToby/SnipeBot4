import interactions, random
from data_types.osu import *

async def create_strategy_embed(strategy, current_pp, new_pp, back_pp, username):
    embed = interactions.Embed(
        title=f"Best strategy for sniping for {username}",
        color=16711680,
    )
    embed.description = f"**Current pp**: {round(current_pp, 2):,}\n **New pp**: {round(new_pp, 2):,}\n **Back pp**: {round(back_pp, 2):,}\n **Best Strategy**: {strategy}"
    return embed