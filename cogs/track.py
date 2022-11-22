import interactions
from data_types.interactions import CustomInteractionsClient
from data_types.cogs import Cog
import time
import asyncio


class Track(Cog):  # must have interactions.Extension or this wont work
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="track",
        description="add a user to be tracked in the channel",
        options=[interactions.Option(
            name="username",
            description="the username of the user",
            type=interactions.OptionType.STRING,
            required=True,
        )
        ]
    )
    async def track(self, ctx: interactions.CommandContext, username: str):
        await ctx.defer()
        if await self.database.get_channel(ctx.channel_id._snowflake):
            await ctx.send(f"<@{ctx.author.id}> channel is already being tracked! (1 tracked user per channel)")
            return

        user_data = await self.osu.get_user_data(str(username))
        await self.database.add_channel(ctx.channel_id._snowflake, user_data)
        message = await ctx.send(f"Started tracking user {user_data.username} in this channel! \nScanning plays...")

        # now we can check if they have any scores in the database.
        # if they do, we can also update their scores to the new format

        beatmaps = await self.database.get_all_beatmaps()
        beatmaps = await self.handle_user_already_stored_scores(user_data.id, beatmaps)
        start_time = time.time()
        message_update_time = time.time()
        for i, beatmap in enumerate(beatmaps):
            try:
                await asyncio.sleep(0.05)
                # every 5 seconds update the message to show the % progress
                if time.time() - message_update_time > 5:
                    await message.edit(f"Started tracking user {user_data.username} in this channel! \nScanning plays... {i}/{len(beatmaps)}")
                    message_update_time = time.time()

                if not(await self.database.get_score(user_data.id, beatmap[0])):
                    user_play = await self.osu.get_score_data(beatmap[0], user_data.id)
                    if user_play:
                        converted_stars = 0
                        converted_bpm = 0
                        if await self.convert_mods_to_int(user_play.score.mods) > 15:
                            if "DT" in user_play.score.mods or "NC" in user_play.score.mods:
                                converted_bpm = int(
                                    user_play.score.beatmap.bpm) * 1.5
                            beatmap_mod_data = await self.osu.get_beatmap_mods(user_play.score.beatmap.id, await self.convert_mods_to_int(user_play.score.mods))
                            if beatmap_mod_data:
                                converted_stars = beatmap_mod_data.attributes.star_rating
                            else:
                                converted_stars = beatmap[1]
                        await self.database.add_score(user_data.id, beatmap[0], user_play.score.score, user_play.score.accuracy, user_play.score.max_combo, user_play.score.passed, user_play.score.pp, user_play.score.rank, user_play.score.statistics.count_300, user_play.score.statistics.count_100, user_play.score.statistics.count_50, user_play.score.statistics.count_miss, user_play.score.created_at, await self.convert_mods_to_int(user_play.score.mods), converted_stars, converted_bpm)
                    else:
                        await self.database.add_score(user_data.id, beatmap[0], 0, False, False, False, False, False, False, False, False, False, False, False, False, False)
                else:
                    # This means its a snipebot3 score or a user has been added and then removed
                    local_score_data = await self.database.get_score(user_data.id, beatmap[0])
                    # accuracy being None signifies old format
                    if local_score_data[3] == None:
                        user_play = await self.osu.get_score_data(beatmap[0], user_data.id)
                        if not(user_play):
                            if i != 0:
                                elapsed_time = time.time() - start_time
                                try:
                                    if int(time.time()) - int(message_update_time) > 5:
                                        message_update_time = time.time()
                                except interactions.LibraryException as l:
                                    pass
                            continue
                        converted_stars = int(beatmap[1])
                        converted_bpm = int(beatmap[7])
                        if await self.convert_mods_to_int(user_play.score.mods) > 15:
                            if "DT" in user_play.score.mods or "NC" in user_play.score.mods:
                                converted_bpm = int(
                                    user_play.score.beatmap.bpm) * 1.5
                            beatmap_mod_data = await self.osu.get_beatmap_mods(user_play.score.beatmap.id, await self.convert_mods_to_int(user_play.score.mods))
                            if beatmap_mod_data:
                                converted_stars = beatmap_mod_data.attributes.star_rating
                            else:
                                converted_stars = beatmap[1]
                        await self.database.update_score(user_data.id, beatmap[0], user_play.score.score, user_play.score.accuracy, user_play.score.max_combo, user_play.score.passed, user_play.score.pp, user_play.score.rank, user_play.score.statistics.count_300, user_play.score.statistics.count_100, user_play.score.statistics.count_50, user_play.score.statistics.count_miss, user_play.score.created_at, await self.convert_mods_to_int(user_play.score.mods), converted_stars, converted_bpm)
                        print(
                            f"Converted Snipebot3 Formatted score to Snipebot4 Format")

            except Exception as e:
                print(e)
                continue
        await message.edit(f"Started tracking user {user_data.username} in this channel! \nScanning plays... {len(beatmaps)}/{len(beatmaps)} - **Done!**")

    async def handle_user_already_stored_scores(self, user_id, beatmaps: list):
        return_beatmaps = []
        conv_scores = await self.database.get_converted_scores(user_id)
        zero_scores = await self.database.get_zero_scores(user_id)
        for beatmap in beatmaps:
            add_beatmap = True
            if int(beatmap[0]) in conv_scores or int(beatmap[0]) in zero_scores:
                add_beatmap = False
            if add_beatmap is True:
                return_beatmaps.append(beatmap)
        return return_beatmaps

    async def convert_mods_to_int(self, modarray: list):
        value = 0
        if modarray:
            for mod in modarray:
                if mod == "NF":
                    value += 1
                elif mod == "EZ":
                    value += 2
                elif mod == "TD":
                    value += 4
                elif mod == "HD":
                    value += 8
                elif mod == "HR":
                    value += 16
                elif mod == "SD":
                    value += 32
                elif mod == "DT":
                    value += 64
                elif mod == "RX":
                    value += 128
                elif mod == "HT":
                    value += 256
                elif mod == "NC":
                    value += 512
                elif mod == "FL":
                    value += 1024
                elif mod == "Autoplay":
                    value += 2048
                elif mod == "SO":
                    value += 4096
                elif mod == "Relax2":
                    value += 8192
                elif mod == "PF":
                    value += 16384
        return value


def setup(client):
    Track(client)
