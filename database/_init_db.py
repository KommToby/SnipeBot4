import sqlite3
from data_types.osu import *
import datetime


class Database:
    def __init__(self, database_name):
        self.db = sqlite3.connect(database_name)
        self.cursor = self.db.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                discord_channel int not null primary key,
                osu_id int not null,
                username varchar(32),
                country_code varchar(32),
                avatar_url varchar(256),
                is_supporter boolean,
                cover_url varchar(256),
                playmode varchar(32),
                recent_score int
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores(
                user_id int not null,
                beatmap_id int,
                score int,
                accuracy real,
                max_combo int,
                passed boolean,
                pp real,
                rank varchar(16),
                count_300 int,
                count_100 int,
                count_50 int,
                count_miss int,
                date varchar(32),
                mods int(32),
                converted_stars real,
                converted_bpm real,
                snipability real
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends(
                discord_channel int not null,
                osu_id int not null,
                username varchar(32),
                country_code varchar(32),
                avatar_url varchar(256),
                is_supporter boolean,
                cover_url varchar(256),
                playmode varchar(32),
                recent_score int,
                ping boolean,
                leaderboard real
            )
        ''')  # Ping value for this is redundant but will take time to alter so keeping it for now

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS beatmaps(
                beatmap_id int not null,
                stars int,
                artist varchar(32),
                song_name varchar(32),
                difficulty_name varchar(32),
                url varchar(32),
                length int,
                bpm int,
                mapper varchar(32),
                status varchar(16),
                beatmapset_id int,
                od real,
                ar real,
                cs real,
                hp real
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS snipes(
                user_id int not null,
                beatmap_id int,
                second_user_id int,
                date varchar(16),
                first_score int,
                second_score int,
                first_accuracy real,
                second_accuracy real,
                first_mods int,
                second_mods int,
                first_pp real,
                second_pp real
            )
        ''')  # for storing if someone has been sniped on a specific beatmap

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS link(
                discord_id int not null,
                osu_id int not null,
                ping boolean
            )
        ''')

    # GETS
    async def get_converted_scores(self, user_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND converted_bpm>?",
            (user_id, 0)).fetchall()

    async def get_snipable_scores(self, user_id): # TODO test for this function
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND snipability>?",
            (user_id, 0)).fetchall()

    async def get_snipable_scores_beatmap_ids(self, user_id): # TODO test for this function
        a = self.cursor.execute(
            "SELECT beatmap_id FROM scores WHERE user_id=? AND snipability>?",
            (user_id, 0)).fetchall()
        return [x[0] for x in a]

    async def get_snipable_scores_values(self, user_id): # TODO test for this function
        a = self.cursor.execute(
            "SELECT snipability FROM scores WHERE user_id=? AND snipability>?",
            (user_id, 0)).fetchall()
        return [x[0] for x in a]

    async def get_zero_scores(self, user_id):
        # using row factory ensures it returns an arr_iray of values not tuples
        self.cursor.row_factory = lambda cursor, row: row[0]
        array = self.cursor.execute(
            "SELECT beatmap_id FROM scores WHERE user_id=? AND score=?",
            (user_id, 0)).fetchall()
        self.cursor.row_factory = None
        return array

    # Only to be used in tests
    async def get_friend_from_username(self, username):
        return self.cursor.execute(
            "SELECT * FROM friends WHERE username=?",
            (username,)).fetchone()

    async def get_friend_from_user_id_and_channel(self, username, channel): # TODO test for this function
        return self.cursor.execute(
            "SELECT * FROM friends WHERE osu_id=? AND discord_channel=?",
            (username, channel)).fetchone()

    async def get_link(self, discord_id):
        return self.cursor.execute(
            "SELECT * FROM link WHERE discord_id=?",
            (discord_id,)).fetchone()

    async def get_discord_id_from_link(self, osu_id):
        return self.cursor.execute(
            "SELECT * FROM link WHERE osu_id=?",
            (osu_id,)).fetchone()

    async def get_channel(self, discord_id):
        return self.cursor.execute(
            "SELECT * FROM users WHERE discord_channel=?",
            (discord_id,)).fetchone()

    async def get_user_from_channel(self, channel_id):
        return self.cursor.execute(
            "SELECT * FROM users WHERE discord_channel=?",
            (channel_id,)).fetchone()

    async def get_channel_from_username(self, username):
        username = username.lower()
        return self.cursor.execute(
            "SELECT * FROM users WHERE lower(username)=?",
            (username,)).fetchone()

    async def get_snipe(self, user1, beatmap, user2):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE user_id=? AND beatmap_id=? AND second_user_id=?",
            (user1, beatmap, user2)).fetchone()

    async def get_single_user_snipes(self, friend_user_id, main_user_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE user_id=? AND second_user_id=?",
            (friend_user_id, main_user_id)).fetchall()

    # beatmap ids only
    async def get_single_user_snipes_ids(self, friend_user_id, main_user_id):
        a = self.cursor.execute(
            "SELECT beatmap_id FROM snipes WHERE user_id=? AND second_user_id=?",
            (friend_user_id, main_user_id)).fetchall()
        # convert to array of beatmap ids
        return [x[0] for x in a]

    async def get_beatmap(self, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM beatmaps WHERE beatmap_id=?",
            (beatmap_id,)
        ).fetchone()

    async def get_all_beatmaps_mapper(self, mapper_username):
        a = self.cursor.execute(
            "SELECT beatmap_id FROM beatmaps WHERE mapper=?",
            (mapper_username,)
        ).fetchall()
        return [x[0] for x in a]

    async def get_all_beatmaps(self):
        return self.cursor.execute(
            "SELECT * FROM beatmaps").fetchall()

    async def get_score(self, user_id, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=?",
            (user_id, beatmap_id)
        ).fetchone()

    async def get_all_scores(self, user_id):  # does not include 0s
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND score!=?",
            (user_id, 0)).fetchall()

    async def get_all_scores_after_date(self, user_id, date):  # does not include 0s TODO test this
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND score!=? AND date>? ORDER BY date ASC",
            (user_id, 0, date)).fetchall()

    async def get_min_max_scores(self, user_id, min, max): # TODO test this
        # return the values from scores where converted_stars is larger than min and lower than max
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND converted_stars>? AND converted_stars<?",
            (user_id, min, max)).fetchall()

    async def get_min_max_scores_beatmap_ids(self, user_id, min, max): # TODO test this
        # return the values from scores where converted_stars is larger than min and lower than max
        a = self.cursor.execute(
            "SELECT beatmap_id FROM scores WHERE user_id=? AND converted_stars>? AND converted_stars<?",
            (user_id, min, max)).fetchall()
        return [x[0] for x in a]

    async def get_min_max_scores_snipable_beatmap_ids(self, user_id, min, max): # TODO test this
        # return the values from scores where converted_stars is larger than min and lower than max
        a = self.cursor.execute(
            "SELECT beatmap_id FROM scores WHERE user_id=? AND converted_stars>? AND converted_stars<? AND snipability>?",
            (user_id, min, max, 0)).fetchall()
        return [x[0] for x in a]

    async def get_min_max_scores_snipable_user_ids(self, user_id, min, max): # TODO test this
        # return the values from scores where converted_stars is larger than min and lower than max
        a = self.cursor.execute(
            "SELECT user_id FROM scores WHERE user_id=? AND converted_stars>? AND converted_stars<? AND snipability>?",
            (user_id, min, max, 0)).fetchall()
        return [x[0] for x in a]

    async def get_min_max_scores_snipable_values(self, user_id, min, max): # TODO test this
        # return the values from scores where converted_stars is larger than min and lower than max
        a = self.cursor.execute(
            "SELECT snipability FROM scores WHERE user_id=? AND converted_stars>? AND converted_stars<? AND snipability>?",
            (user_id, min, max, 0)).fetchall()
        return [x[0] for x in a]

    async def get_min_max_scores_snipable(self, user_id, min, max): # TODO test this
        # return the values from scores where converted_stars is larger than min and lower than max
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND converted_stars>? AND converted_stars<? AND snipability>?",
            (user_id, min, max, 0)).fetchall()

    # does not include 0s and only returns beatmap ids
    async def get_all_scores_beatmap_ids(self, user_id):
        a = self.cursor.execute(
            "SELECT beatmap_id FROM scores WHERE user_id=? AND score!=?",
            (user_id, 0)).fetchall()
        return [x[0] for x in a]

    async def get_all_scores_all_users_with_zeros(self):  # does include 0s
        return self.cursor.execute(
            "SELECT * FROM scores").fetchall()

    async def get_all_scores_all_users_without_zeros_no_snipability(self):  # does include 0s
        return self.cursor.execute(
            "SELECT * FROM scores WHERE score!=? AND accuracy>=? AND snipability IS NULL",
            ('0', 0.01)).fetchall()

    async def get_all_users(self):
        return self.cursor.execute(
            "SELECT * FROM users").fetchall()

    async def get_main_recent_score(self, user_id):
        return self.cursor.execute(
            "SELECT recent_score FROM users WHERE osu_id=?",
            (user_id,)).fetchone()

    async def get_user_friends(self, discord_id):
        return self.cursor.execute(
            "SELECT * FROM friends WHERE discord_channel=?",
            (discord_id,)).fetchall()

    async def get_user_beatmap_play(self, user_id, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=?",
            (user_id, beatmap_id)
        ).fetchone()

    async def get_user_snipe_on_beatmap(self, user_id, beatmap_id, sniped_user_id):
        return self.cursor.execute(
            "SELECT user_id FROM snipes WHERE user_id=? AND beatmap_id=? AND second_user_id=?",
            (user_id, beatmap_id, sniped_user_id)
        ).fetchone()

    async def get_user_score_with_zeros(self, user_id, beatmap_id):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=?",
            (user_id, beatmap_id)
        ).fetchone()

    async def get_all_friends(self):
        return self.cursor.execute(
            "SELECT * FROM friends").fetchall()

    async def get_friend_recent_score(self, id):
        return self.cursor.execute(
            "SELECT recent_score FROM friends WHERE osu_id=?",
            (id,)).fetchone()

    async def get_friend_from_channel(self, id, channel_id):
        return self.cursor.execute(
            "SELECT * FROM friends WHERE osu_id=? AND discord_channel=?",
            (id, channel_id)).fetchone()

    async def get_main_user_friends(self, id):
        return self.cursor.execute(
            "SELECT * FROM friends WHERE discord_channel=?",
            (id,)).fetchall()

    async def get_user_score_on_beatmap(self, osu_id, beatmap_id, score):
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=? AND score=?",
            (osu_id, beatmap_id, score)
        ).fetchone()

    async def get_user_score_on_beatmap_no_zeros(self, osu_id, beatmap_id): # TODO test this
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND beatmap_id=? AND score!=?",
            (osu_id, beatmap_id, 0)
        ).fetchone()

    async def get_friend_leaderboard_score(self, friend_id):
        return self.cursor.execute(
            "SELECT leaderboard FROM friends WHERE osu_id=?",
            (friend_id,)).fetchone()

    async def get_user_snipes(self, user_id, second_user_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE user_id=? AND second_user_id=?",
            (user_id, second_user_id)
        ).fetchall()

    async def get_main_user_snipes(self, main_user_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE user_id=?",
            (main_user_id,)).fetchall()

    async def get_main_user_sniped(self, main_user_id):
        return self.cursor.execute(
            "SELECT * FROM snipes WHERE second_user_id=?",
            (main_user_id,)).fetchall()

    async def get_linked_user_osu_id(self, discord_id):
        return self.cursor.execute(
            "SELECT osu_id FROM link WHERE discord_id=?",
            (discord_id,)).fetchone()

    async def get_last_weeks_scores(self, user_id):
        one_week_ago_datetime = datetime.datetime.now() - datetime.timedelta(days=7)
        one_week_ago_utc = one_week_ago_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        return self.cursor.execute(
            "SELECT * FROM scores WHERE user_id=? AND date>=?",
            (user_id, one_week_ago_utc)).fetchall()

    # ADDS

    async def add_channel(self, channel_id, user_data: UserData):
        self.cursor.execute(
            "INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?)",
            (channel_id, user_data.id, user_data.username, user_data.country_code,
             user_data.avatar_url, user_data.is_supporter, user_data.cover_url, user_data.playmode, 0)
        )
        self.db.commit()

    async def add_beatmap(self, id, sr, artist, song, diff, url, len, bpm, mapper, status, bms_id, od, ar, cs, hp, test=False):
        if status != "ranked" and status != "loved" or test is True:
            if not(await self.get_beatmap(id)):
                self.cursor.execute(
                    "INSERT INTO beatmaps VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (id, sr, artist, song, diff, url, len, bpm,
                    mapper, status, bms_id, od, ar, cs, hp)
                )
                self.db.commit()
        else:
            print(f"Beatmap {id} is ranked or loved, not adding to database")

    async def add_snipe(self, user_id, beatmap_id, second_user_id, date, first_score, second_score, first_accuracy, second_accuracy, first_mods, second_mods, first_pp, second_pp, test=False):
        if not(await self.get_snipe(user_id, beatmap_id, second_user_id)):
            # check to see if the beatmap exists
            if not(await self.get_beatmap(beatmap_id)) and test is False:
                print(f"Beatmap not found for score, not adding to database")
                return
            self.cursor.execute(
                "INSERT INTO snipes VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (user_id, beatmap_id, second_user_id, date, first_score, second_score,
                 first_accuracy, second_accuracy, first_mods, second_mods, first_pp, second_pp)
            )
            self.db.commit()

    async def add_score(self, user_id, beatmap_id, score, accuracy, max_combo, passed, pp, rank, count_300, count_100, count_50, count_miss, date, mods, converted_score, converted_bpm, snipability, test=False):
        # check to see if the beatmap exists
        if not(await self.get_beatmap(beatmap_id)) and test is False:
            print(f"Beatmap not found for score, not adding to database")
            return
        # if score already exists throw an error
        if not(await self.get_score(user_id, beatmap_id)):
            self.cursor.execute(
                "INSERT INTO scores VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (user_id, beatmap_id, score, accuracy, max_combo, passed, pp, rank, count_300,
                 count_100, count_50, count_miss, date, mods, converted_score, converted_bpm, snipability)
            )
            self.db.commit()
            return
        else:
            print(f"Duplicate Score Error on beatmap {beatmap_id}")
            return

    async def add_friend(self, channel_id, user_data: User):
        self.cursor.execute(
            "INSERT INTO friends VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (channel_id, user_data.id, user_data.username, user_data.country_code, user_data.avatar_url,
             user_data.is_supporter, user_data.cover_url, user_data.playmode, 0, False, 0)
        )
        self.db.commit()

    async def add_link(self, discord_id, user_id):
        self.cursor.execute(
            "INSERT INTO link VALUES(?,?,?)",
            (discord_id, user_id, False)
        )
        self.db.commit()

    # UPDATES
    async def update_link(self, discord_id, user_id):
        self.cursor.execute(
            "UPDATE link SET osu_id=? WHERE discord_id=?",
            (user_id, discord_id)
        )
        self.db.commit()

    async def update_ping(self, ping: bool, discord_id):
        self.cursor.execute(
            "UPDATE link SET ping=? WHERE discord_id=?",
            (ping, discord_id)
        )
        self.db.commit()

    async def update_score(self, user_id, beatmap_id, score, accuracy, max_combo, passed, pp, rank, count_300, count_100, count_50, count_miss, date, mods, conv_stars, conv_bpm, snipability):
        self.cursor.execute(
            "UPDATE scores SET score=?, accuracy=?, max_combo=?, passed=?, pp=?, rank=?, count_300=?, count_100=?, count_50=?, count_miss=?, date=?, mods=?, converted_stars=?, converted_bpm=?, snipability=? WHERE user_id=? AND beatmap_id=?",
            (score, accuracy, max_combo, passed, pp, rank, count_300, count_100,
             count_50, count_miss, date, mods, conv_stars, conv_bpm, snipability, user_id, beatmap_id)
        )
        self.db.commit()

    async def update_score_zeros(self, user_id, beatmap_id):
        self.cursor.execute(
            "UPDATE scores SET score=?, accuracy=?, max_combo=?, passed=?, pp=?, rank=?, count_300=?, count_100=?, count_50=?, count_miss=?, date=?, mods=?, converted_stars=?, converted_bpm=? WHERE user_id=? AND beatmap_id=?",
            (0, False, False, False, False, False, False, False, False,
             False, False, False, False, False, user_id, beatmap_id)
        )
        self.db.commit()

    async def update_main_recent_score(self, main_user_id, score):
        self.cursor.execute(
            "UPDATE users SET recent_score=? WHERE osu_id=?",
            (score, main_user_id)
        )
        self.db.commit()

    async def update_friend_recent_score(self, friend_user_id, score):
        self.cursor.execute(
            "UPDATE friends SET recent_score=? WHERE osu_id=?",
            (score, friend_user_id)
        )
        self.db.commit()

    async def update_friend_username(self, username, osu_id):
        self.cursor.execute(
            "UPDATE friends SET username=? WHERE osu_id=?",
            (username, osu_id)
        )
        self.db.commit()

    async def update_friend_leaderboard_score(self, discord_channel, friend_id, pp):
        self.cursor.execute(
            "UPDATE friends SET leaderboard=? WHERE discord_channel=? AND osu_id=?",
            (pp, discord_channel, friend_id)
        )
        self.db.commit()

    async def update_snipability(self, user_id, beatmap_id, score, snipability):
        self.cursor.execute(
            "UPDATE scores SET snipability=? WHERE user_id=? AND beatmap_id=? AND score=?",
            (snipability, user_id, beatmap_id, score)
        )
        self.db.commit()


    # DELETES
    async def delete_friend(self, user_id, discord_id):
        self.cursor.execute(
            "DELETE FROM friends WHERE osu_id=? AND discord_channel=?",
            (user_id, discord_id)
        )
        self.db.commit()
