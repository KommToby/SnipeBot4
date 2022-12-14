import interactions
import random
from data_types.osu import *


async def create_strategy_embed(strategy, current_pp, new_pp, back_pp, username):
    embed = interactions.Embed(
        title=f"Best strategy for sniping for {username}",
        color=16711680,
    )
    embed.description = f"**Current PP**: {round(current_pp, 2):,}\n **PP if New Snipe**: {round(new_pp, 2):,} ({(round(new_pp - current_pp, 2)):,} change)\n **PP If Snipe Back**: {round(back_pp, 2):,} ({(round(back_pp - current_pp, 2)):,} change)\n **Best Strategy**: {strategy}"
    return embed
