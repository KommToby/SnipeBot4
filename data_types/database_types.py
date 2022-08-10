# I think this only works for fetchone()'s
class User:
    def __init__(self, user):
        self.discord_channel = user[0]
        self.osu_id = user[1]
        self.username = user[2]
        self.country_code = user[3]
        self.avatar_url = user[4]
        self.is_supporter = user[5]
        self.cover_url = user[6]
        self.playmode = user[7]
        self.recent_score = user[8]
        

class Score:
    def __init__(self, score):
        score = self.validate_score(score)
        self.user_id = score[0]
        self.beatmap_id = score[1]
        self.score = score[2]
        self.accuracy = score[3]
        self.max_combo = score[4]
        self.passed = score[5]
        self.pp = score[6]
        self.rank = score[7]
        self.count_300 = score[8]
        self.count_100 = score[9]
        self.count_50 = score[10]
        self.count_miss = score[11]
        self.date = score[12]
        self.mods = score[13]
        self.converted_stars = score[14]
        self.converted_bpm = score[15]

    def validate_score(self, score):
        if score is None:
            score = []
            for _ in range(16):
                score.append(None)
        return score

class Friend:
    def __init__(self, friend):
        friend = self.validate_friend(friend)
        self.discord_channel = friend[0]
        self.osu_id = friend[1]
        self.username = friend[2]
        self.country_code = friend[3]
        self.avatar_url = friend[4]
        self.is_supporter = friend[5]
        self.cover_url = friend[6]
        self.playmode = friend[7]
        self.recent_score = friend[8]
        self.ping = friend[9]
        self.leaderboard = friend[10]

    # Checks to see if the friend tuple returns values
    def validate_friend(self, friend):
        if friend is None:
            friend = []
            for _ in range(11):
                friend.append(None)
        return friend

class Beatmap:
    def __init__(self, beatmap):
        self.beatmap_id = beatmap[0]
        self.stars = beatmap[1]
        self.artist = beatmap[2]
        self.song_name = beatmap[3]
        self.difficulty_name = beatmap[4]
        self.url = beatmap[5]
        self.length = beatmap[6]
        self.bpm = beatmap[7]
        self.mapper = beatmap[8]
        self.status = beatmap[9]
        self.beatmapset_id = beatmap[10]
        self.od = beatmap[11]
        self.ar = beatmap[12]
        self.cs = beatmap[13]
        self.hp = beatmap[14]


class Snipe:
    def __init__(self, snipe):
        self.user_id = snipe[0]
        self.beatmap_id = snipe[1]
        self.second_user_id = snipe[2]
        self.date = snipe[3]
        self.first_score = snipe[4]
        self.second_score = snipe[5]
        self.first_accuracy = snipe[6]
        self.second_accuracy = snipe[7]
        self.first_mods = snipe[8]
        self.second_mods = snipe[9]
        self.first_pp = snipe[10]
        self.second_pp = snipe[11]

class Link:
    def __init__(self, link):
        self.discord_id = link[0]
        self.osu_id = link[1]
        self.ping = link[2]