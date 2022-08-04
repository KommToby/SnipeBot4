from database._init_db import Database
db = Database()

async def test_db_friends():
    friend_data = {
        "id": 1,
        "username": "Komm",
        "country_code": "GB",
        "avatar_url": "https://a.ppy.sh/7671790?1650659121.jpeg",
        "is_supporter": 1,
        "cover_url": "https://assets.ppy.sh/user-profile-covers/7671790/10e75039cd0ee3e30b50877f90d3a8be4e324f8c8e0e79144d3a63481387f565.png",
        "playmode": "osu"
    }

    channel_id = 10

    await db.add_friend(channel_id, friend_data)
