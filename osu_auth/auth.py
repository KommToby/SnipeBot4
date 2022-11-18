import json
import requests
import os
import asyncio
import time
from data_types.osu import *


class Auth:
    def __init__(self):
        self._load_config()
        self.api_timer = time.time()
        self._get_auth_token()

    # Loads the details saved in the config json
    def _load_config(self):
        with open(os.path.dirname(__file__) + "/../config.json") as f:
            data = json.load(f)['osu']
            self.address = data['address']
            self.apiv1_key = data['apiv1_key']
            self.client_id = data['client_id']
            self.client_secret = data['client_secret']

    # Requests an authorisation token from the osu api
    def _get_auth_token(self) -> None:
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "public",
        }
        r = requests.post("https://osu.ppy.sh/oauth/token", data=params)
        if r.status_code == 401:
            raise requests.RequestException("Invalid Credentials Given")
        response = r.json()
        self.refresh_time = time.time()
        self.token_type = response["token_type"]
        self.expires_in = response["expires_in"]
        self.access_token = response["access_token"]

    # Returns if the token is still valid or not
    def auth_token_valid(self) -> bool:
        return time.time() < self.refresh_time + self.expires_in

    # General api call, where it takes in the url as a parameter
    async def get_api_v2(self, url: str, params=None):
        try:
            if time.time() - self.api_timer < 0.05:  # This is the maximum api time allowed by ppy
                # If the time is exceeded, tell it to wait until its available again (not very long)
                await asyncio.sleep(0.05 - (time.time() - self.api_timer))
            # Every time the api is called, print the ping time
            print("Ping Time: ", "%.2f" %
                  (time.time()-self.api_timer) + "s", end="\r")
            self.api_timer = time.time()
            if params is None:
                params = {}
            if not self.auth_token_valid():
                self._get_auth_token()
            headers = {"Authorization": f"Bearer {self.access_token}"}
            r = requests.get(
                f"https://osu.ppy.sh/api/v2/{url}", headers=headers, params=params, timeout=(5, 10)
            )
            self.api_timer = time.time()
            if r.status_code == 200:
                return r.json()
            else:
                return False
        except:
            return False

    # POST requests (new)
    async def get_api_v2_post_mods(self, url: str, mods, params=None):
        try:
            if time.time() - self.api_timer < 0.05:  # This is the maximum api time allowed by ppy
                # If the time is exceeded, tell it to wait until its available again (not very long)
                await asyncio.sleep(0.05 - (time.time() - self.api_timer))
            # Every time the api is called, print the ping time
            print("Ping Time: ", "%.2f" %
                  (time.time()-self.api_timer) + "s", end="\r")
            self.api_timer = time.time()
            if params is None:
                params = {}
            if not self.auth_token_valid():
                self._get_auth_token()
            headers = {"Authorization": f"Bearer {self.access_token}"}
            r = requests.post(
                f"https://osu.ppy.sh/api/v2/{url}", headers=headers, params=params, timeout=(5, 10), data={"mods": mods}
            )
            self.api_timer = time.time()
            if r.status_code == 200:
                return r.json()
            else:
                return False
        except:
            return False

    # Api call urls below

    # User profile data, user id or username both are acceptable I believe
    async def get_user_data(self, user_id: str) -> UserData:
        user_data = await self.get_api_v2(f"users/{user_id}")
        if not user_data:
            return False
        return UserData(user_data)

    # Users scores on a specific beatmap, returns their best score for every mod combination they have played
    async def get_score_data(self, beatmap_id: str, user_id: str):
        # has to be user id cannot be username
        osu_score = await self.get_api_v2(f"beatmaps/{beatmap_id}/scores/users/{user_id}")
        if not osu_score:
            return False
        return OsuScore(osu_score)

    # Users most recent plays on osu, only returns their 5 most recent plays
    async def get_recent_plays(self, user_id: str):
        recent = await self.get_api_v2(f"users/{user_id}/scores/recent?mode=osu")
        if not recent:
            return False
        # recent_plays = []
        # for recent_play in recent:
        #     recent_plays.append(OsuRecentScore(recent_play))
        return [OsuRecentScore(recent_play) for recent_play in recent]

    # Users top 100 scores on osu
    async def get_user_scores(self, user_id: str):
        best_score = await self.get_api_v2(f"users/{user_id}/scores/best")
        if not best_score:
            return False
        return [OsuBestScore(score) for score in best_score]

    # Gets details about a specific beatmap. The beatmap id has to be the difficulty id, not the beatmapset id
    async def get_beatmap(self, beatmap_id: str):
        beatmap = await self.get_api_v2(f"beatmaps/{beatmap_id}")
        if not beatmap:
            return False
        return Beatmap(beatmap)

    async def get_beatmap_mods(self, beatmap_id: str, mods):
        beatmap_mods = await self.get_api_v2_post_mods(f"beatmaps/{beatmap_id}/attributes", mods)
        if not beatmap_mods:
            return False
        return BeatmapMods(beatmap_mods)

    # Users recent activity, I think this returns every single beatmap they have played in the last 24 hours, which can be used for a buffer when the api is down / slow
    #TODO do something with this
    async def get_user_recent_activity(self, user_id: str):
        return await self.get_api_v2(f"users/{user_id}/recent_activity")
