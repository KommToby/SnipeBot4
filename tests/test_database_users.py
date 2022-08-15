import pytest
import os
from database._init_db import Database

# Mock Data

# osu api get user response
friend_data = {
    "id": 1,
    "username": "Komm",
    "country_code": "GB",
    "avatar_url": "https://a.ppy.sh/7671790?1650659121.jpeg",
    "is_supporter": 1,
    "cover_url": "https://assets.ppy.sh/user-profile-covers/7671790/10e75039cd0ee3e30b50877f90d3a8be4e324f8c8e0e79144d3a63481387f565.png",
    "playmode": "osu"
}
friend_channel_id = 10

# osu api get score response
score_data = {
    'position': 959,
    'score': {
        'accuracy': 1,
        'created_at': '2021-10-09T20:13:54+00:00',
        'id': '3901735030',
        'max_combo': '533',
        'mode': 'osu',
        'mods': ['DT'],
        'passed': True,
        'perfect': True,
        'pp': 727.27,
        'rank': 'X',
        'replay': True,
        'score': 7146575,
        'user_id': 1,
        'statistics': {
            'count_100': 0,
            'count_300': 392,
            'count_50': 0,
            'count_geki': 82,
            'count_katu': 0,
            'count_miss': 0,
            'user_id': 1,
        },
        'current_user_attributes': {
            'pin': None
        },
        'beatmap': {
            'beatmapset_id': '993619',
            'difficulty_rating': '3.89',
            'id': 2077721,
            'mode': 'osu',
            'status': 'ranked',
            'total_length': 231,
            'user_id': 1,
            'version': 'Star-Crossed',
            'accuracy': 6.7,
            'ar': 7.8,
            'bpm': 119,
            'convert': False,
            'count_circles': 391,
            'count_sliders': 192,
            'count_spinners': 0,
            'cs': 4.5,
            'deleted_at': None,
            'drain': 4.8,
            'hit_length': 197,
            'is_scoreable': True,
            'last_updated': '2019-06-26T23:02:20+00:00',
            'mode_int': 0,
            'passcount': 26073,
            'playcount': 148734,
            'ranked': 1,
            'url': 'https://osu.ppy.sh/beatmaps/2077721',
            'checksum': 'e2a9ff51449e438821c8cc8374baedf3',
            'max_combo': 781
        },
        'user': {
            'avatar_url': 'https://a.ppy.sh/7671790?1650659121.jpeg',
            'country_code': 'GB',
            'default_group': 'default',
            'id': 1,
            'is_active': True,
            'is_bot': False,
            'is_deleted': False,
            'is_online': False,
            'is_supporter': True,
            'last_visit': '2022-08-03T22:37:28+00:00',
            'pm_friends_only': False,
            'profile_colour': None,
            'username': 'Komm',
            'country': {
                'code': 'GB',
                'name': 'United Kingdom'
            },
            'cover': {
                'custom_url': 'https://assets.ppy.sh/user-profile-covers/10609949/00a19a0142852209596389c3bd74f328966cd723e4e7760af7a3826cc0effa6c.png',
                'url': 'https://assets.ppy.sh/user-profile-covers/10609949/00a19a0142852209596389c3bd74f328966cd723e4e7760af7a3826cc0effa6c.png'
            }
        }
    }
}

# osu api get beatmap response
beatmap_data = {
    'beatmapset_id': '993619',
    'difficulty_rating': '3.89',
    'id': 2077721,
    'mode': 'osu',
    'status': 'ranked',
    'total_length': 231,
    'user_id': 1,
    'version': 'Star-Crossed',
    'accuracy': 6.7,
    'ar': 7.8,
    'bpm': 119,
    'convert': False,
    'count_circles': 391,
    'count_sliders': 192,
    'count_spinners': 0,
    'cs': 4.5,
    'deleted_at': None,
    'drain': 4.8,
    'hit_length': 197,
    'is_scoreable': True,
    'last_updated': '2019-06-26T23:02:20+00:00',
    'mode_int': 0,
    'passcount': 26073,
    'playcount': 148734,
    'ranked': 1,
    'url': 'https://osu.ppy.sh/beatmaps/2077721',
    'checksum': 'e2a9ff51449e438821c8cc8374baedf3',
    'max_combo': 781,
    'beatmapset': {
        'artist': 'Taylor Swift',
        'artist_unicode': 'Taylor Swift',
        'covers': {
            'cover': 'https://assets.ppy.sh/beatmaps/993619/covers/cover.jpg?1622164790',
            'cover@2x': 'https://assets.ppy.sh/beatmaps/993619/covers/cover@2x.jpg?1622164790',
            'card': 'https://assets.ppy.sh/beatmaps/993619/covers/card.jpg?1622164790',
            'card@2x': 'https://assets.ppy.sh/beatmaps/993619/covers/card@2x.jpg?1622164790',
            'list': 'https://assets.ppy.sh/beatmaps/993619/covers/list.jpg?1622164790',
            'list@2x': 'https://assets.ppy.sh/beatmaps/993619/covers/list@2x.jpg?1622164790',
            'slimcover': 'https://assets.ppy.sh/beatmaps/993619/covers/slimcover.jpg?1622164790',
            'slimcover@2x': 'https://assets.ppy.sh/beatmaps/993619/covers/slimcover@2x.jpg?1622164790'
        },
        'creator': 'Nao Tomori',
        'favourite_count': 187,
        'hype': None,
        'id': 993619,
        'nsfw': False,
        'offset': 0,
        'play_count': 239067,
        'preview_url': '//b.ppy.sh/preview/993619.mp3',
        'source': '',
        'spotlight': False,
        'status': 'ranked',
        'title': 'Love Story',
        'title_unicode': 'Love Story',
        'track_id': None,
        'user_id': '5364763',
        'vide': False,
        'availability': {
            'download_disabled': False,
            'more_information': None
        },
        'bpm': 119,
        'can_be_hyped': False,
        'discussion_enabled': True,
        'discussion_locked': False,
        'is_scoreable': True,
        'last_updated': '2019-06-26T23:02:19+00:00',
        'legacy_thread_url': 'https://osu.ppy.sh/community/forums/topics/926427',
        'nominations_summary': {
            'current': 2,
            'required': 2
        },
        'ranked': 1,
        'ranked_date': '2019-07-04T11:00:02+00:00',
        'storyboard': False,
        'submitted_date': '2019-06-26T01:12:44+00:00',
        'tags': 'country english pop guitar fearless',
        'ratings': [0, 5, 3, 3, 0, 2, 3, 14, 26, 42, 260],
        'failtimes': {
            'fail': ['not adding this into tests rn'],
            'exit': ['not adding this into tests rn']
        },
        'max_combo': 781
    }
}


async def delete_database(db):
    db.db.close()
    os.remove("test_database.db")


def db_handler(func):
    async def inner_wrapper():
        db = Database('test_database.db')
        await func(db)
        await delete_database(db)
    return inner_wrapper


@pytest.mark.asyncio
@db_handler
async def test_db_add_friend(db):
    await db.add_friend(friend_channel_id, friend_data)
    assert (await db.get_friend_username_from_username(friend_data['username'])) == ("Komm",)


@pytest.mark.asyncio
@db_handler
async def test_db_add_delete_friend(db):
    await db.add_friend(friend_channel_id, friend_data)
    await db.delete_friend(friend_data['id'], friend_channel_id)
    assert (await db.get_friend_username_from_username(friend_data['username'])) == None


@pytest.mark.asyncio
@db_handler
async def test_db_add_update_friend_username(db):
    await db.add_friend(friend_channel_id, friend_data)
    friend_data['username'] = "Komm2"
    await db.update_friend_username(friend_data['username'], friend_data['id'])
    assert (await db.get_friend_username_from_username(friend_data['username'])) == ("Komm2",)


@pytest.mark.asyncio
@db_handler
async def test_db_add_new_score(db):
    await db.add_score(
        score_data['score']['user_id'],
        score_data['score']['beatmap']['id'],
        score_data['score']['score'],
        score_data['score']['accuracy'],
        score_data['score']['max_combo'],
        score_data['score']['passed'],
        score_data['score']['pp'],
        score_data['score']['rank'],
        score_data['score']['statistics']['count_300'],
        score_data['score']['statistics']['count_100'],
        score_data['score']['statistics']['count_50'],
        score_data['score']['statistics']['count_miss'],
        score_data['score']['created_at'],
        64,  # This is the mod integer value for DT
        score_data['score']['beatmap']['difficulty_rating'],
        score_data['score']['beatmap']['bpm']
    )
    database_score = await db.get_score(score_data['score']['user_id'], score_data['score']['beatmap']['id'])
    assert type(database_score[0]) == int
    assert database_score[0] == score_data['score']['user_id']
    assert database_score[1] == score_data['score']['beatmap']['id']
    assert database_score[13] == 64
    assert database_score[14] == score_data['score']['beatmap']['difficulty_rating']
    assert database_score[15] == score_data['score']['beatmap']['bpm']


@pytest.mark.asyncio
@db_handler
async def test_db_get_converted_scores(db):
    """
    Converted scores are scores that have been converted to the new snipebot format
    It is found by checking if the converted bpm has a value in the table
    because all scores should have a converted bpm stored, even if the map is played
    without any mods

    Returns as an array of beatmap ids as values, not tuples
    """
    await db.add_score(
        score_data['score']['user_id'],
        score_data['score']['beatmap']['id'],
        score_data['score']['score'],
        score_data['score']['accuracy'],
        score_data['score']['max_combo'],
        score_data['score']['passed'],
        score_data['score']['pp'],
        score_data['score']['rank'],
        score_data['score']['statistics']['count_300'],
        score_data['score']['statistics']['count_100'],
        score_data['score']['statistics']['count_50'],
        score_data['score']['statistics']['count_miss'],
        score_data['score']['created_at'],
        64,  # This is the mod integer value for DT
        score_data['score']['beatmap']['difficulty_rating'],
        score_data['score']['beatmap']['bpm']
    )

    await db.add_score(
        score_data['score']['user_id'],
        80,
        score_data['score']['score'],
        score_data['score']['accuracy'],
        score_data['score']['max_combo'],
        score_data['score']['passed'],
        score_data['score']['pp'],
        score_data['score']['rank'],
        score_data['score']['statistics']['count_300'],
        score_data['score']['statistics']['count_100'],
        score_data['score']['statistics']['count_50'],
        score_data['score']['statistics']['count_miss'],
        score_data['score']['created_at'],
        0,
        0,
        0
    )

    converted_score = await db.get_converted_scores(score_data['score']['user_id'])
    assert len(converted_score) == 1
    assert converted_score[0] == score_data['score']['beatmap']['id']


@pytest.mark.asyncio
@db_handler
async def test_db_get_zero_scores(db):
    await db.add_score(
        score_data['score']['user_id'],
        score_data['score']['beatmap']['id'],
        score_data['score']['score'],
        score_data['score']['accuracy'],
        score_data['score']['max_combo'],
        score_data['score']['passed'],
        score_data['score']['pp'],
        score_data['score']['rank'],
        score_data['score']['statistics']['count_300'],
        score_data['score']['statistics']['count_100'],
        score_data['score']['statistics']['count_50'],
        score_data['score']['statistics']['count_miss'],
        score_data['score']['created_at'],
        64,  # This is the mod integer value for DT
        score_data['score']['beatmap']['difficulty_rating'],
        score_data['score']['beatmap']['bpm']
    )

    await db.add_score(
        score_data['score']['user_id'],
        80,
        score_data['score']['score'],
        score_data['score']['accuracy'],
        score_data['score']['max_combo'],
        score_data['score']['passed'],
        score_data['score']['pp'],
        score_data['score']['rank'],
        score_data['score']['statistics']['count_300'],
        score_data['score']['statistics']['count_100'],
        score_data['score']['statistics']['count_50'],
        score_data['score']['statistics']['count_miss'],
        score_data['score']['created_at'],
        0,
        0,
        0
    )

    await db.add_score(
        score_data['score']['user_id'],
        75,
        0,
        score_data['score']['accuracy'],
        score_data['score']['max_combo'],
        score_data['score']['passed'],
        score_data['score']['pp'],
        score_data['score']['rank'],
        score_data['score']['statistics']['count_300'],
        score_data['score']['statistics']['count_100'],
        score_data['score']['statistics']['count_50'],
        score_data['score']['statistics']['count_miss'],
        score_data['score']['created_at'],
        0,
        0,
        0
    )

    await db.add_score(
        score_data['score']['user_id'],
        69420,
        0,
        score_data['score']['accuracy'],
        score_data['score']['max_combo'],
        score_data['score']['passed'],
        score_data['score']['pp'],
        score_data['score']['rank'],
        score_data['score']['statistics']['count_300'],
        score_data['score']['statistics']['count_100'],
        score_data['score']['statistics']['count_50'],
        score_data['score']['statistics']['count_miss'],
        score_data['score']['created_at'],
        0,
        0,
        0
    )

    zero_scores = await db.get_zero_scores(score_data['score']['user_id'])
    assert len(zero_scores) == 2
    assert zero_scores[0] == 75
    assert zero_scores[1] == 69420


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_link(db):
    await db.add_link(
        191602759504625674,
        score_data['score']['user_id']
    )

    link = await db.get_link(191602759504625674)
    assert link[0] == 191602759504625674
    assert link[1] == score_data['score']['user_id']
    assert link[2] == False


@pytest.mark.asyncio
@db_handler
async def test_db_get_discord_id_from_link(db):
    await db.add_link(
        191602759504625674,
        score_data['score']['user_id']
    )

    link = await db.get_discord_id_from_link(score_data['score']['user_id'])
    assert link[0] == 191602759504625674
    assert link[1] == score_data['score']['user_id']
    assert link[2] == False


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_channel(db):
    await db.add_channel(
        843020728773378070,
        score_data['score']['user_id'],
        {
            'id': score_data['score']['user_id'],
            'username': 'Komm',
            'country_code': score_data['score']['user']['country_code'],
            'avatar_url': score_data['score']['user']['avatar_url'],
            'is_supporter': score_data['score']['user']['is_supporter'],
            'cover_url': score_data['score']['user']['cover']['url'],
            'playmode': friend_data['playmode']
        }
    )
    channel = await db.get_channel(843020728773378070)
    assert channel[0] == 843020728773378070
    assert channel[2] == score_data['score']['user']['username']
    assert channel[8] == 0

@pytest.mark.asyncio
@db_handler
async def test_db_add_get_beatmap(db):
    await db.add_beatmap(
        beatmap_data['id'],
        beatmap_data['difficulty_rating'],
        beatmap_data['beatmapset']['artist'],
        beatmap_data['beatmapset']['title'],
        beatmap_data['version'],
        beatmap_data['url'],
        beatmap_data['total_length'],
        beatmap_data['bpm'],
        beatmap_data['beatmapset']['creator'],
        beatmap_data['status'],
        beatmap_data['beatmapset_id'],
        beatmap_data['accuracy'],
        beatmap_data['ar'],
        beatmap_data['cs'],
        beatmap_data['drain']
    )
    beatmap = await db.get_beatmap(beatmap_data['id'])
    assert beatmap[0] == beatmap_data['id']
    assert beatmap[14] == beatmap_data['drain']
