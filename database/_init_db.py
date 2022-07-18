import sqlite3
from osu_auth.auth import Auth

class Database:
    def __init__(self):
        self.osu = Auth()
        self.db = sqlite3.connect('database.db', timeout=5)
        self.cursor = self.db.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                discord_channel varchar(32) not null primary key,
                osu_id varchar(32) not null,
                username varchar(32),
                country_code varchar(32),
                avatar_url varchar(256),
                is_supporter boolean,
                cover_url varchar(256),
                playmode varchar(32),
                recent_score varchar(32)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores(
                user_id varchar(32) not null,
                beatmap_id varchar(32),
                score varchar(32),
                accuracy varchar(32),
                max_combo varchar(32),
                passed boolean,
                pp varchar(16),
                rank varchar(16),
                count_300 varchar(16),
                count_100 varchar(16),
                count_50 varchar(16),
                count_miss varchar(16),
                date varchar(32)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends(
                discord_channel varchar(32) not null primary key,
                osu_id varchar(32) not null,
                username varchar(32),
                country_code varchar(32),
                avatar_url varchar(256),
                is_supporter boolean,
                cover_url varchar(256),
                playmode varchar(32),
                recent_score varchar(32),
                ping boolean,
                leaderboard varchar(16)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS beatmaps(
                beatmap_id varchar(32) not null,
                stars int,
                artist varchar(32),
                song_name varchar(32),
                difficulty_name varchar(32),
                url varchar(32),
                length int,
                bpm int,
                mapper varchar(32),
                status varchar(16),
                beatmapset_id varchar(32),
                od varchar(16),
                ar varchar(16),
                cs varchar(16),
                hp varchar(16),
                max_combo int
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS snipes(
                user_id varchar(32) not null,
                beatmap_id varchar(32),
                second_user_id varchar(32),
                date varchar(16),
                first_score int,
                second_score int,
                first_accuracy varchar(16),
                second_accuracy varchar(16),
                first_mods int,
                second_mods int,
                first_pp varchar(16),
                second_pp varchar(16)
            )
        ''')  # for storing if someone has been sniped on a specific beatmap

    ## GETS
    async def get_channel(self, discord_id):
        return self.cursor.execute(
            "SELECT * FROM users WHERE discord_channel=?",
            (discord_id,)).fetchone()
        
    ## ADDS
    async def add_channel(self, channel_id, user_id, user_data):
        user_data = await self.osu.get_user_data(str(user_id))
        self.cursor.execute(
            "INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?)",
            (channel_id, user_data['id'], user_data['username'], user_data['country_code'], user_data['avatar_url'], user_data['is_supporter'], user_data['cover_url'], user_data['playmode'], 0)
        )
        self.db.commit()        
    ## UPDATES
    ## DELETES