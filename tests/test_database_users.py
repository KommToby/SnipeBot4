import pytest
from database._init_db import Database
from data_types.osu import *
import datetime

# Mock Data

# osu api get user response
friend_data = UserData({
    "id": 1,
    "username": "Komm",
    "country_code": "GB",
    "country": {
        "code": "GB",
        "name": "United Kingdom"
    },
    "cover": {
        "custom_url": 'https://assets.ppy.sh/user-profile-covers/7671790/10e75039cd0ee3e30b50877f90d3a8be4e324f8c8e0e79144d3a63481387f565.png',
        "id": None,
        "url": 'https://assets.ppy.sh/user-profile-covers/7671790/10e75039cd0ee3e30b50877f90d3a8be4e324f8c8e0e79144d3a63481387f565.png'
    },
    "account_history": [],
    "active_tournament_banner": None,
    "badges": [],
    "beatmap_playcounts_count": 9894,
    "comments_count": 62,
    "avatar_url": "https://a.ppy.sh/7671790?1650659121.jpeg",
    "is_supporter": 1,
    "cover_url": "https://assets.ppy.sh/user-profile-covers/7671790/10e75039cd0ee3e30b50877f90d3a8be4e324f8c8e0e79144d3a63481387f565.png",
    "playmode": "osu",
    "favourite_beatmapset_count": 32,
    "default_group": "",
    "is_active": 1,
    "is_bot": 0,
    "is_deleted": 0,
    "is_online": 1,
    "last_visit": None,
    "pm_friends_only": 0,
    "profile_colour": None,
    "discord": "Kommsu#4701",
    "favourite_beatmap_count": 32,
    "follower_count": 273,
    "graveyard_beatmapset_count": 24,
    "groups": [],
    "guest_beatmapset_count": 0,
    "has_supported": True,
    "interests": "Clarz",
    "join_date": '2015-12-31T22:29:55+00:00',
    "kudosu": {
        "available": 44,
        "total": 44
    },
    "last_visit": '2022-08-10T19:23:54+00:00',
    "location": "Scotland",
    "loved_beatmapset_count": 0,
    "mapping_follower_count": 6,
    "max_blocks": 100,
    "max_friends": 500,
    "monthly_playcounts": [],
    "occupation": "University Student",
    "page": {
        "html": "dummyhtml",
        "raw": "dummymarkdown"
    },
    "pending_beatmapset_count": 1,
    "playmode": "osu",
    "playstyle": ["Keyboard", "Tablet"],
    "pm_friends_only": False,
    "post_count": 97,
    "previous_usernames": ["TobyCharles", "Komm107"],
    "profile_order": ['me', 'top_ranks', 'beatmaps', 'medals', 'recent_activity', 'historical', 'kudosu'],
    "rankHistory": {
        "mode": "osu",
        "data": [1, 2, 3, 4]
    },
    "rank_history": {
        "mode": "osu",
        "data": [1, 2, 3, 4]
    },
    "ranked_and_approved_beatmapset_count": 0,
    "ranked_beatmapset_count": 0,
    "replays_watched_counts": [],
    "scores_best_count": 100,
    "scores_first_count": 0,
    "scores_pinned_count": 13,
    "scores_recent_count": 0,
    "statistics": {
        "country_rank": 399,
        "global_rank": 11026,
        "grade_counts": {
            "a": 1187,
            "s": 1909,
            "sh": 1261,
            "ss": 277,
            "ssh": 415
        },
        "hit_accuracy": 99.1405,
        "is_ranked": True,
        "level": {
            "current": 101,
            "progress": 13
        },
        "maximum_combo": 3938,
        "play_count": 52558,
        "play_time": 3405118,
        "pp": 7478.83,
        "rank": {
            "country": 399
        },
        "ranked_score": 43718434279,
        "replays_watched_by_others": 233,
        "total_score": 140797732815
    },
    "support_level": 3,
    "title": None,
    "title_url": None,
    "twitter": "tobykomm",
    "unranked_beatmapset_count": 1,
    "user_achievements": [],
    "website": "https://www.google.com"

})
friend_channel_id = 10

# osu api get score response
score_data = OsuScore({
    'position': 959,
    'score': {
        'accuracy': 1,
        'created_at': '2021-10-09T20:13:54+00:00',
        'best_id': None,
        'id': '3901735030',
        'max_combo': 533,
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
        'mode_int': 0,
        'current_user_attributes': {
            'pin': None
        },
        'beatmap': {
            'beatmapset_id': '993619',
            'difficulty_rating': 3.89,
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
})

# osu api get beatmap response
beatmap_data = Beatmap({
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
        'video': False,
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
    },
    'failtimes': {
        'fail': ['not adding this into tests rn'],
        'exit': ['not adding this into tests rn']
    },
    'max_combo': 781
})


def db_handler(func):
    async def inner_wrapper():
        db_name = ":memory:"
        db = Database(db_name)
        await func(db)
    return inner_wrapper


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_friend_from_username(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    friend_from_username = await db.get_friend_from_username(friend_data.username)
    assert (friend_from_username[2] == "Komm")

@pytest.mark.asyncio
@db_handler
async def test_db_add_update_get_friend_recent_score(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    await db.update_friend_recent_score(friend_data.id, 69420)
    friend_from_username = await db.get_friend_from_username(friend_data.username)
    assert (friend_from_username[2] == "Komm")
    assert friend_from_username[8] == 69420

@pytest.mark.asyncio
@db_handler
async def test_db_add_update_get_friend_username(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    await db.update_friend_username("Jam", friend_data.id)
    friend_from_username = await db.get_friend_from_username("Jam")
    assert (friend_from_username[2] == "Jam")
    assert friend_from_username[8] == 0

@pytest.mark.asyncio
@db_handler
async def test_db_add_update_get_friend_leaderboard(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    await db.update_friend_leaderboard_score(friend_channel_id, friend_data.id, 727)
    friend_from_username = await db.get_friend_from_username(friend_data.username)
    assert (friend_from_username[2] == friend_data.username)
    assert friend_from_username[8] == 0
    assert friend_from_username[10] == 727


@pytest.mark.asyncio
@db_handler
async def test_db_add_delete_friend(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    await db.delete_friend(friend_data.id, friend_channel_id)
    friend_database_data = await db.get_friend_from_username(friend_data.username)
    assert friend_database_data is None


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_score(db: Database):
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    database_score = await db.get_score(score_data.score.user_id, score_data.score.beatmap.id)
    assert type(database_score[0]) == int
    assert database_score[0] == score_data.score.user_id
    assert database_score[1] == score_data.score.beatmap.id
    assert database_score[13] == 64
    assert database_score[14] == score_data.score.beatmap.difficulty_rating
    assert database_score[15] == score_data.score.beatmap.bpm


@pytest.mark.asyncio
@db_handler
async def test_db_add_update_get_score(db: Database):
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    await db.update_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score + 1,
        score_data.score.accuracy + 0.5,
        score_data.score.max_combo + 1,
        score_data.score.passed,
        score_data.score.pp + 5,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        68,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating + 0.5,
        score_data.score.beatmap.bpm + 100,
        0
    )
    database_score = await db.get_score(score_data.score.user_id, score_data.score.beatmap.id)
    assert type(database_score[0]) == int
    assert database_score[0] == score_data.score.user_id
    assert database_score[1] == score_data.score.beatmap.id
    assert database_score[13] == 68
    assert database_score[14] == score_data.score.beatmap.difficulty_rating + 0.5
    assert database_score[15] == score_data.score.beatmap.bpm + 100

@pytest.mark.asyncio
@db_handler
async def test_db_add_update_get_score_zeros(db: Database):
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    await db.update_score_zeros(
        score_data.score.user_id,
        score_data.score.beatmap.id,
    )
    database_score = await db.get_score(score_data.score.user_id, score_data.score.beatmap.id)
    assert type(database_score[0]) == int
    assert database_score[0] == score_data.score.user_id
    assert database_score[1] == score_data.score.beatmap.id
    assert database_score[13] == False
    assert database_score[14] == False
    assert database_score[15] == False


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_all_scores(db: Database):
    for i in range(10):
        await db.add_score(
            score_data.score.user_id,
            score_data.score.beatmap.id+i,
            score_data.score.score,
            score_data.score.accuracy,
            score_data.score.max_combo,
            score_data.score.passed,
            score_data.score.pp,
            score_data.score.rank,
            score_data.score.statistics.count_300,
            score_data.score.statistics.count_100,
            score_data.score.statistics.count_50,
            score_data.score.statistics.count_miss,
            score_data.score.created_at,
            64,  # This is the mod integer value for DT
            score_data.score.beatmap.difficulty_rating,
            i,
            0
        )
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id+i+1,
        0,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        i,
        0
    )
    database_score = await db.get_all_scores(score_data.score.user_id)
    assert len(database_score) == 10
    assert type(database_score[0][0]) == int
    assert database_score[0][0] == score_data.score.user_id
    assert database_score[0][1] == score_data.score.beatmap.id
    assert database_score[0][13] == 64
    assert database_score[0][14] == score_data.score.beatmap.difficulty_rating


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_all_scores_all_users_with_zeros(db: Database):
    for i in range(10):
        await db.add_score(
            score_data.score.user_id,
            score_data.score.beatmap.id+i,
            score_data.score.score,
            score_data.score.accuracy,
            score_data.score.max_combo,
            score_data.score.passed,
            score_data.score.pp,
            score_data.score.rank,
            score_data.score.statistics.count_300,
            score_data.score.statistics.count_100,
            score_data.score.statistics.count_50,
            score_data.score.statistics.count_miss,
            score_data.score.created_at,
            64,  # This is the mod integer value for DT
            score_data.score.beatmap.difficulty_rating,
            score_data.score.beatmap.bpm,
            0
        )
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id+i+1,
        0,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    database_score = await db.get_all_scores_all_users_with_zeros()
    assert len(database_score) == 11
    assert type(database_score[0][0]) == int
    assert database_score[0][0] == score_data.score.user_id
    assert database_score[0][1] == score_data.score.beatmap.id
    assert database_score[0][13] == 64
    assert database_score[0][14] == score_data.score.beatmap.difficulty_rating
    assert database_score[0][15] == score_data.score.beatmap.bpm


@pytest.mark.asyncio
@db_handler
async def test_db_get_converted_scores(db: Database):
    """
    Converted scores are scores that have been converted to the new snipebot format
    It is found by checking if the converted bpm has a value in the table
    because all scores should have a converted bpm stored, even if the map is played
    without any mods

    Returns as an array of beatmap ids as values, not tuples
    """
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )

    await db.add_score(
        score_data.score.user_id,
        80,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        0,
        0,
        0,
        0
    )

    # this wont work with dictionary return because its fetchall
    converted_score = await db.get_converted_scores(score_data.score.user_id)
    assert len(converted_score) == 1
    assert converted_score[0][1] == score_data.score.beatmap.id


@pytest.mark.asyncio
@db_handler
async def test_db_get_zero_scores(db: Database):
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )

    await db.add_score(
        score_data.score.user_id,
        80,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        0,
        0,
        0,
        0
    )

    await db.add_score(
        score_data.score.user_id,
        75,
        0,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        0,
        0,
        0,
        0
    )

    await db.add_score(
        score_data.score.user_id,
        69420,
        0,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        0,
        0,
        0,
        0
    )

    zero_scores = await db.get_zero_scores(score_data.score.user_id)
    assert len(zero_scores) == 2
    assert zero_scores[0] == 75
    assert zero_scores[1] == 69420


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_link(db: Database):
    await db.add_link(
        191602759504625674,
        score_data.score.user_id
    )

    link = await db.get_link(191602759504625674)
    assert link[0] == 191602759504625674
    assert link[1] == score_data.score.user_id
    assert link[2] == False


@pytest.mark.asyncio
@db_handler
async def test_db_add_update_get_link(db: Database):
    await db.add_link(
        191602759504625674,
        score_data.score.user_id
    )

    await db.update_link(
        191602759504625674,
        1234
    )

    link = await db.get_link(191602759504625674)
    assert link[0] == 191602759504625674
    assert link[1] == 1234
    assert link[2] == False

@pytest.mark.asyncio
@db_handler
async def test_db_add_update_get_link_ping(db: Database):
    await db.add_link(
        191602759504625674,
        score_data.score.user_id
    )

    await db.update_ping(
        True,
        191602759504625674,
    )

    link = await db.get_link(191602759504625674)
    assert link[0] == 191602759504625674
    assert link[1] == score_data.score.user_id
    assert link[2] == True


@pytest.mark.asyncio
@db_handler
async def test_db_get_discord_id_from_link(db: Database):
    await db.add_link(
        191602759504625674,
        score_data.score.user_id
    )

    link = await db.get_discord_id_from_link(score_data.score.user_id)
    assert link[0] == 191602759504625674
    assert link[1] == score_data.score.user_id
    assert link[2] == False


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_channel(db: Database):
    await db.add_channel(
        843020728773378070,
        friend_data
    )
    channel = await db.get_channel(843020728773378070)
    assert channel[0] == 843020728773378070
    assert channel[2] == friend_data.username
    assert channel[8] == 0

@pytest.mark.asyncio
@db_handler
async def test_db_add_update_get_channel_user_recent_score(db: Database):
    await db.add_channel(
        843020728773378070,
        friend_data
    )
    await db.update_main_recent_score(
        friend_data.id,
        69420
    )
    channel = await db.get_channel(843020728773378070)
    assert channel[0] == 843020728773378070
    assert channel[2] == friend_data.username
    assert channel[8] == 69420


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_all_users(db: Database):
    await db.add_channel(
        843020728773378070,
        friend_data
    )
    await db.add_channel(
        843020728773378071,
        friend_data
    )
    users = await db.get_all_users()
    assert len(users) == 2
    assert users[0][0] == 843020728773378070
    assert users[0][2] == friend_data.username
    assert users[0][8] == 0
    assert users[1][0] == 843020728773378071


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_main_recent_score(db: Database):
    await db.add_channel(
        843020728773378070,
        friend_data
    )
    recent_score = await db.get_main_recent_score(friend_data.id)
    assert recent_score[0] == 0


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_beatmap(db: Database):
    await db.add_beatmap(
        beatmap_data.id,
        beatmap_data.difficulty_rating,
        beatmap_data.beatmapset.artist,
        beatmap_data.beatmapset.title,
        beatmap_data.version,
        beatmap_data.url,
        beatmap_data.total_length,
        beatmap_data.bpm,
        beatmap_data.beatmapset.creator,
        beatmap_data.status,
        beatmap_data.beatmapset.id,
        beatmap_data.accuracy,
        beatmap_data.ar,
        beatmap_data.cs,
        beatmap_data.drain
    )
    beatmap = await db.get_beatmap(beatmap_data.id)
    assert beatmap[0] == beatmap_data.id
    assert beatmap[14] == beatmap_data.drain


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_all_beatmaps(db: Database):
    for i in range(10):
        await db.add_beatmap(
            beatmap_data.id+i,
            beatmap_data.difficulty_rating,
            beatmap_data.beatmapset.artist,
            beatmap_data.beatmapset.title,
            beatmap_data.version,
            beatmap_data.url,
            beatmap_data.total_length,
            beatmap_data.bpm,
            beatmap_data.beatmapset.creator,
            beatmap_data.status,
            beatmap_data.beatmapset.id,
            beatmap_data.accuracy,
            beatmap_data.ar,
            beatmap_data.cs,
            beatmap_data.drain
        )
    beatmaps = await db.get_all_beatmaps()
    assert len(beatmaps) == 10
    assert beatmaps[0][0] == beatmap_data.id
    assert beatmaps[5][14] == beatmap_data.drain


@pytest.mark.asyncio
@db_handler
async def test_db_get_user_from_channel(db: Database):
    await db.add_channel(
        843020728773378070,
        friend_data
    )
    user = await db.get_user_from_channel(843020728773378070)
    assert user[0] == 843020728773378070
    assert user[2] == friend_data.username


@pytest.mark.asyncio
@db_handler
async def test_db_get_channel_from_username(db: Database):
    await db.add_channel(
        843020728773378070,
        friend_data
    )
    user = await db.get_channel_from_username(friend_data.username)
    assert user[0] == 843020728773378070
    assert user[2] == friend_data.username


@pytest.mark.asyncio
@db_handler
async def test_db_add_get_snipe(db: Database):
    await db.add_snipe(
        7671790,
        3601629,
        7562902,
        score_data.score.created_at,
        score_data.score.score,
        score_data.score.score + 1,
        score_data.score.accuracy,
        score_data.score.accuracy + 1,
        64,
        16,
        score_data.score.pp,
        score_data.score.pp + 1
    )
    snipe = await db.get_snipe(7671790, 3601629, 7562902)
    assert snipe[0] == 7671790
    assert snipe[3] == score_data.score.created_at
    assert snipe[5] == score_data.score.score + 1
    assert snipe[8] == 64


@pytest.mark.asyncio
@db_handler
async def test_db_get_user_friends(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    await db.add_friend(friend_channel_id, friend_data)
    await db.add_friend(friend_channel_id, friend_data)
    friends = await db.get_user_friends(friend_channel_id)
    assert len(friends) == 3
    assert friends[0][0] == friend_channel_id


@pytest.mark.asyncio
@db_handler
async def test_db_get_user_beatmap_play(db: Database):
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    beatmap_play = await db.get_user_beatmap_play(score_data.score.user_id, score_data.score.beatmap.id)
    assert beatmap_play[0] == score_data.score.user.id
    assert beatmap_play[1] == score_data.score.beatmap.id
    assert beatmap_play[6] == score_data.score.pp




@pytest.mark.asyncio
@db_handler
async def test_db_get_user_snipe_on_beatmap(db: Database):
    await db.add_snipe(
        7671790,
        3601629,
        7562902,
        score_data.score.created_at,
        score_data.score.score,
        score_data.score.score + 1,
        score_data.score.accuracy,
        score_data.score.accuracy + 1,
        64,
        16,
        score_data.score.pp,
        score_data.score.pp + 1
    )
    snipe = await db.get_user_snipe_on_beatmap(7671790, 3601629, 7562902)
    assert snipe[0] == 7671790


@pytest.mark.asyncio
@db_handler
async def test_db_get_user_score_with_zeros(db: Database):
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        0,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    scores = await db.get_user_score_with_zeros(score_data.score.user_id, score_data.score.beatmap.id)
    assert scores[0] == score_data.score.user.id
    assert scores[1] == score_data.score.beatmap.id
    assert scores[2] == 0
    assert scores[3] == score_data.score.accuracy


@pytest.mark.asyncio
@db_handler
async def test_db_get_all_friends(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    await db.add_friend(friend_channel_id, friend_data)
    await db.add_friend(friend_channel_id, friend_data)
    friends = await db.get_all_friends()
    assert len(friends) == 3
    assert friends[0][0] == friend_channel_id


@pytest.mark.asyncio
@db_handler
async def test_db_get_friend_recent_score(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    friend_recent_score = await db.get_friend_recent_score(friend_data.id)
    assert friend_recent_score[0] == 0


@pytest.mark.asyncio
@db_handler
async def test_db_get_friend_from_channel(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    friend = await db.get_friend_from_channel(friend_data.id, friend_channel_id)
    assert friend[0] == friend_channel_id
    assert friend[3] == friend_data.country_code


@pytest.mark.asyncio
@db_handler
async def test_db_get_main_user_friends(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    await db.add_friend(friend_channel_id, friend_data)
    await db.add_friend(friend_channel_id, friend_data)
    friends = await db.get_main_user_friends(friend_channel_id)
    assert len(friends) == 3
    assert friends[0][0] == friend_channel_id

@pytest.mark.asyncio
@db_handler
async def test_db_get_main_user_score_on_beatmap(db: Database):
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    score = await db.get_user_score_on_beatmap(score_data.score.user_id, score_data.score.beatmap.id, score_data.score.score)
    assert score[0] == score_data.score.user.id
    assert score[1] == score_data.score.beatmap.id
    assert score[6] == score_data.score.pp


@pytest.mark.asyncio
@db_handler
async def test_db_get_friend_leaderboard_score(db: Database):
    await db.add_friend(friend_channel_id, friend_data)
    lb = await db.get_friend_leaderboard_score(friend_data.id)
    assert lb[0] == 0

@pytest.mark.asyncio
@db_handler
async def test_db_get_user_snipes(db: Database):
    await db.add_snipe(
        7671790,
        3601629,
        7562902,
        score_data.score.created_at,
        score_data.score.score,
        score_data.score.score + 1,
        score_data.score.accuracy,
        score_data.score.accuracy + 1,
        64,
        16,
        score_data.score.pp,
        score_data.score.pp + 1
    )
    snipes = await db.get_user_snipes(7671790, 7562902)
    assert len(snipes) == 1
    assert snipes[0][0] == 7671790
    assert snipes[0][3] == score_data.score.created_at
    assert snipes[0][11] == score_data.score.pp + 1

@pytest.mark.asyncio
@db_handler
async def test_db_get_main_user_snipes(db: Database):
    await db.add_snipe(
        7671790,
        3601629,
        7562902,
        score_data.score.created_at,
        score_data.score.score,
        score_data.score.score + 1,
        score_data.score.accuracy,
        score_data.score.accuracy + 1,
        64,
        16,
        score_data.score.pp,
        score_data.score.pp + 1
    )
    await db.add_snipe(
        12345,
        3601629,
        7671790,
        score_data.score.created_at,
        score_data.score.score,
        score_data.score.score + 1,
        score_data.score.accuracy,
        score_data.score.accuracy + 1,
        64,
        16,
        score_data.score.pp,
        score_data.score.pp + 1
    )
    main_user_snipes = await db.get_main_user_snipes(7671790)
    assert len(main_user_snipes) == 1
    assert main_user_snipes[0][0] == 7671790
    assert main_user_snipes[0][3] == score_data.score.created_at
    assert main_user_snipes[0][11] == score_data.score.pp + 1

@pytest.mark.asyncio
@db_handler
async def test_db_get_main_user_sniped(db: Database):
    await db.add_snipe(
        7671790,
        3601629,
        7562902,
        score_data.score.created_at,
        score_data.score.score,
        score_data.score.score + 1,
        score_data.score.accuracy,
        score_data.score.accuracy + 1,
        64,
        16,
        score_data.score.pp,
        score_data.score.pp + 1
    )
    await db.add_snipe(
        12345,
        3601629,
        7671790,
        score_data.score.created_at,
        score_data.score.score,
        score_data.score.score + 1,
        score_data.score.accuracy,
        score_data.score.accuracy + 1,
        64,
        16,
        score_data.score.pp,
        score_data.score.pp + 1
    )
    main_user_snipes = await db.get_main_user_sniped(7671790)
    assert len(main_user_snipes) == 1
    assert main_user_snipes[0][0] == 12345
    assert main_user_snipes[0][3] == score_data.score.created_at
    assert main_user_snipes[0][11] == score_data.score.pp + 1

@pytest.mark.asyncio
@db_handler
async def test_db_get_linked_user_osu_id(db: Database):
    await db.add_link(
        191602759504625674,
        score_data.score.user_id
    )
    linked_user_osu_id = await db.get_linked_user_osu_id(191602759504625674)
    assert linked_user_osu_id[0] == score_data.score.user_id

@pytest.mark.asyncio
@db_handler
async def test_db_get_week_old_score(db: Database):
    six_days_ago_datetime = datetime.datetime.utcnow() - datetime.timedelta(days=6)
    eight_days_ago_datetime = datetime.datetime.utcnow() - datetime.timedelta(days=8)
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        # date one week ago,
        six_days_ago_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id+1,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        # date one week ago,
        eight_days_ago_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
        32,  # This is the mod integer value for not DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    last_weeks_scores = await db.get_last_weeks_scores(score_data.score.user_id)
    assert len(last_weeks_scores) == 1

@pytest.mark.asyncio
@db_handler
async def test_db_get_single_user_snipes(db: Database):
    await db.add_snipe(
        7671790,
        3601629,
        7562902,
        score_data.score.created_at,
        score_data.score.score,
        score_data.score.score + 1,
        score_data.score.accuracy,
        score_data.score.accuracy + 1,
        64,
        16,
        score_data.score.pp,
        score_data.score.pp + 1
    )
    await db.add_snipe(
        12345,
        3601629,
        7671790,
        score_data.score.created_at,
        score_data.score.score,
        score_data.score.score + 1,
        score_data.score.accuracy,
        score_data.score.accuracy + 1,
        64,
        16,
        score_data.score.pp,
        score_data.score.pp + 1
    )
    main_user_snipes = await db.get_single_user_snipes(7671790, 7562902)
    assert len(main_user_snipes) == 1
    main_user_snipes = await db.get_single_user_snipes(12345, 7671790)
    assert len(main_user_snipes) == 1

@pytest.mark.asyncio
@db_handler
async def test_db_get_all_scores_beatmap_ids(db: Database):
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        64,  # This is the mod integer value for DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id+1,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        32,  # This is the mod integer value for not DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    beatmap_ids = await db.get_all_scores_beatmap_ids(score_data.score.user_id)
    assert len(beatmap_ids) == 2
    assert beatmap_ids[0] == score_data.score.beatmap.id

@pytest.mark.asyncio
@db_handler
async def test_db_get_all_beatmaps_mapper(db: Database):
    await db.add_beatmap(
        beatmap_data.id,
        beatmap_data.difficulty_rating,
        beatmap_data.beatmapset.artist,
        beatmap_data.beatmapset.title,
        beatmap_data.version,
        beatmap_data.url,
        beatmap_data.total_length,
        beatmap_data.bpm,
        beatmap_data.beatmapset.creator,
        beatmap_data.status,
        beatmap_data.beatmapset.id,
        beatmap_data.accuracy,
        beatmap_data.ar,
        beatmap_data.cs,
        beatmap_data.drain
    )
    await db.add_beatmap(
        beatmap_data.id+1,
        beatmap_data.difficulty_rating,
        beatmap_data.beatmapset.artist,
        beatmap_data.beatmapset.title,
        beatmap_data.version,
        beatmap_data.url,
        beatmap_data.total_length,
        beatmap_data.bpm,
        "Kommothy",
        beatmap_data.status,
        beatmap_data.beatmapset.id,
        beatmap_data.accuracy,
        beatmap_data.ar,
        beatmap_data.cs,
        beatmap_data.drain
    )
    beatmaps = await db.get_all_beatmaps_mapper("Kommothy")
    assert len(beatmaps) == 1
    assert beatmaps[0] == beatmap_data.id+1

@pytest.mark.asyncio
@db_handler
async def test_db_update_snipability(db: Database):
    await db.add_score(
        score_data.score.user_id,
        score_data.score.beatmap.id,
        score_data.score.score,
        score_data.score.accuracy,
        score_data.score.max_combo,
        score_data.score.passed,
        score_data.score.pp,
        score_data.score.rank,
        score_data.score.statistics.count_300,
        score_data.score.statistics.count_100,
        score_data.score.statistics.count_50,
        score_data.score.statistics.count_miss,
        score_data.score.created_at,
        32,  # This is the mod integer value for not DT
        score_data.score.beatmap.difficulty_rating,
        score_data.score.beatmap.bpm,
        0
    )
    await db.update_snipability(score_data.score.user_id, score_data.score.beatmap.id, score_data.score.score, 1)
    a = await db.get_score(score_data.score.user_id, score_data.score.beatmap.id)
    assert a[16] == 1