import pytest
from osu_auth.auth import Auth

# Note that most of these will FAIL the pipeline because there will be no api key
# Stored on the github repo, so they will fail to authenticate.
# These tests are purely to be used LOCALLY. If you want to run them, you will need to add your own api key (and oauth2 details) to the config.json file

def auth_handler(func):
    async def inner_wrapper():
        auth = Auth()
        await func(auth)
    return inner_wrapper


@pytest.mark.asyncio
async def test_create_auth():
    auth = Auth()

@pytest.mark.asyncio
@auth_handler
async def test_auth_token_valid(auth: Auth):
    assert auth.auth_token_valid() == True

@pytest.mark.asyncio
@auth_handler
async def test_get_user_data(auth: Auth):
    user_data = await auth.get_user_data('7671790')
    assert user_data.id == 7671790
    assert user_data.country_code == 'GB'
    assert user_data.has_supported == True

@pytest.mark.asyncio
@auth_handler
async def test_get_user_data_invalid(auth: Auth):
    user_data = await auth.get_user_data('this_is_an_invalid_username_that_should_not_exist_on_osu_ever_hopefully_694201804012345')
    assert user_data == False

@pytest.mark.asyncio
@auth_handler
async def test_get_user_data_invalid_id(auth: Auth):
    user_data = await auth.get_user_data('694201804012345')
    assert user_data == False

@pytest.mark.asyncio
@auth_handler
async def test_get_score_data(auth: Auth):
    score_data = await auth.get_score_data('1219094', '7671790')
    assert score_data.score.max_combo == 1789
    assert score_data.score.user_id == 7671790
    assert score_data.score.beatmap.id == 1219094

@pytest.mark.asyncio
@auth_handler
async def test_get_score_data_invalid(auth: Auth):
    score_data = await auth.get_score_data('0', '7671790') # 0 is an invalid beatmap id
    assert score_data == False

@pytest.mark.asyncio
@auth_handler
async def test_get_user_scores(auth: Auth):
    user_scores = await auth.get_user_scores('7671790')
    assert user_scores[0].max_combo == 1789
    assert user_scores[0].user_id == 7671790
    assert user_scores[0].beatmap.id == 1219094

@pytest.mark.asyncio
@auth_handler
async def test_get_beatmap(auth: Auth):
    beatmap = await auth.get_beatmap('1219094')
    assert beatmap.id == 1219094
    assert beatmap.total_length == 297

@pytest.mark.asyncio
@auth_handler
async def test_get_beatmap_invalid(auth: Auth):
    beatmap = await auth.get_beatmap('0')
    assert beatmap == False

@pytest.mark.asyncio
@auth_handler
async def test_get_beatmaps_mods(auth: Auth):
    beatmap = await auth.get_beatmap_mods('1219094', 64) # 64 is DT
    assert beatmap.attributes.star_rating == 8.968700408935547
