class OsuRecentScore:
    def __init__(self, recent_score_data):
        self.accuracy = recent_score_data['accuracy']
        self.best_id = recent_score_data['best_id']
        self.created_at = recent_score_data['created_at']
        self.id = recent_score_data['id']
        self.max_combo = recent_score_data['max_combo']
        self.mode = recent_score_data['mode']
        self.mode_int = recent_score_data['mode_int']
        self.mods = recent_score_data['mods']
        self.passed = recent_score_data['passed']
        self.perfect = recent_score_data['perfect']
        self.pp = recent_score_data['pp']
        self.rank = recent_score_data['rank']
        self.replay = recent_score_data['replay']
        self.score = recent_score_data['score']
        self.statistics = BeatmapStatistics(recent_score_data['statistics'])
        self.user_id = recent_score_data['user_id']
        self.current_user_attributes = CurrentUserAttributes(
            recent_score_data['current_user_attributes'])
        self.beatmap = RecentBeatmap(recent_score_data['beatmap'])
        self.beatmapset = RecentBeatmapset(recent_score_data['beatmapset'])
        self.user = User(recent_score_data['user'])


class OsuScore(OsuRecentScore):
    def __init__(self, osu_score_data):
        self.position = osu_score_data['position']
        super().__init__(self, osu_score_data['score'])


class OsuScoreMods():
    def __init__(self, score_data_mods):
        self.attributes = Attributes(score_data_mods['attributes'])


class Attributes():
    def __init__(self, attributes):
        self.star_rating = attributes['star_rating']
        self.max_combo = attributes['max_combo']
        self.aim_difficulty = attributes['aim_difficulty']
        self.speed_difficulty = attributes['speed_difficulty']
        self.flashlight_difficulty = attributes['flashlight_difficulty']
        self.slider_factor = attributes['slider_factor']
        self.approach_rate = attributes['approach_rate']
        self.overall_difficulty = attributes['overall_difficulty']


class User:
    def __init__(self, user):
        self.avatar_url = user['avatar_url']
        self.country_code = user['country_code']
        self.default_group = user['default_group']
        self.id = user['id']
        self.is_active = user['is_active']
        self.is_bot = user['is_bot']
        self.is_deleted = user['is_deleted']
        self.is_online = user['is_online']
        self.is_supporter = user['is_supporter']
        self.last_visit = user['last_visit']
        self.pm_friends_only = user['pm_friends_only']
        self.profile_colour = user['profile_colour']
        self.username = user['username']


class UserData(User):
    def __init__(self, user_data):
        super().__init__(user_data)
        self.cover_url = user_data['cover_url']
        self.discord = user_data['discord']
        self.has_supported = user_data['has_supported']
        self.discord = user_data['discord']
        self.has_supported = user_data['has_supported']
        self.interests = user_data['interests']
        self.join_date = user_data['join_date']
        self.kudosu = Kudosu(user_data['kudosu'])
        self.location = user_data['location']
        self.max_blocks = user_data['max_blocks']
        self.max_friends = user_data['max_friends']
        self.occupation = user_data['occupation']
        self.playmode = user_data['playmode']
        self.playstyle = user_data['playstyle']
        self.post_count = user_data['post_count']
        self.profile_order = user_data['profile_order']
        self.title = user_data['title']
        self.title_url = user_data['title_url']
        self.twitter = user_data['twitter']
        self.website = user_data['website']
        self.country = Country(user_data['country'])
        self.cover = Cover(user_data['cover'])
        self.account_history = user_data['account_history']
        self.active_tournament_banner = user_data['active_tournament_banner']
        self.badges = user_data['badges']
        self.beatmap_playcounts_count = user_data['beatmap_playcounts_count']
        self.comments_count = user_data['comments_count']
        self.favourite_beatmapset_count = user_data['favourite_beatmapset_count']
        self.follower_count = user_data['follower_count']
        self.graveyard_beatmapset_count = user_data['graveyard_beatmapset_count']
        self.groups = user_data['groups']
        self.guest_beatmapset_count = user_data['guest_beatmapset_count']
        self.loved_beatmapset_count = user_data['loved_beatmapset_count']
        self.mapping_follower_count = user_data['mapping_follower_count']
        self.monthly_playcounts = user_data['monthly_playcounts']
        self.page = Page(user_data['page'])
        self.pending_beatmapset_count = user_data['pending_beatmapset_count']
        self.ranked_beatmapset_count = user_data['ranked_beatmapset_count']
        self.replays_watched_count = user_data['replays_watched_count']
        self.scores_best_count = user_data['scores_best_count']
        self.scores_first_count = user_data['scores_first_count']
        self.scores_pinned_count = user_data['scores_pinned_count']
        self.scores_recent_count = user_data['scores_recent_count']
        self.statistics = UserStatistics(user_data['statistics'])
        self.support_level = user_data['support_level']
        self.user_achievements = user_data['user_achievements']
        self.rankHistory = user_data['rankHistory']
        self.rank_history = user_data['rank_history']
        self.ranked_and_approved_beatmapset_count = user_data['ranked_and_approved_beatmapset_count']
        self.unranked_beatmapset_count = user_data['unranked_beatmapset_count']


class RankHistory():
    def __init__(self, rank_history):
        self.mode = rank_history['mode']
        self.data = rank_history['data']


class UserStatistics():
    def __init__(self, statistics):
        self.level = Level(statistics['level'])
        self.global_rank = statistics['global_rank']
        self.pp = statistics['pp']
        self.ranked_score = statistics['ranked_score']
        self.hit_accuracy = statistics['hit_accuracy']
        self.play_count = statistics['play_count']
        self.play_time = statistics['play_time']
        self.total_score = statistics['total_score']
        self.maximum_combo = statistics['maximum_combo']
        self.replays_watched_by_others = statistics['replays_watched_by_others']
        self.is_ranked = statistics['is_ranked']
        self.grade_counts = GradeCounts(statistics['grade_counts'])
        self.country_rank = statistics['country_rank']
        self.rank = Rank(statistics['rank'])


class Rank():
    def __init__(self, rank):
        self.country = rank['country']


class GradeCounts():
    def __init__(self, grade_counts):
        self.ss = grade_counts['ss']
        self.ssh = grade_counts['ssh']
        self.s = grade_counts['s']
        self.sh = grade_counts['sh']
        self.a = grade_counts['a']


class Level():
    def __init__(self, level):
        self.current = level['current']
        self.progress = level['progress']


class Page():
    def __init__(self, page):
        self.html = page['html']
        self.raw = page['raw']


class Cover:
    def __init__(self, cover):
        self.url = cover['url']
        self.custom_url = cover['custom_url']
        self.id = cover['id']


class Country:
    def __init__(self, country):
        self.code = country['code']
        self.name = country['name']


class Kudosu:
    def __init__(self, kudosu):
        self.total = kudosu['total']
        self.available = kudosu['available']


# Beatmapset data returned in recent score
class RecentBeatmapset:
    def __init__(self, beatmapset):
        self.artist = beatmapset['artist']
        self.artist_unicode = beatmapset['artist_unicode']
        self.covers = Covers(beatmapset['covers'])
        self.creator = beatmapset['creator']
        self.favourite_count = beatmapset['favourite_count']
        self.hype = beatmapset['hype']
        self.id = beatmapset['id']
        self.nsfw = beatmapset['nsfw']
        self.offset = beatmapset['offset']
        self.play_count = beatmapset['play_count']
        self.preview_url = beatmapset['preview_url']
        self.source = beatmapset['source']
        self.spotlight = beatmapset['spotlight']
        self.status = beatmapset['status']
        self.title = beatmapset['title']
        self.title_unicode = beatmapset['title_unicode']
        self.track_id = beatmapset['track_id']
        self.user_id = beatmapset['user_id']
        self.video = beatmapset['video']


class Covers:
    def __init__(self, covers):
        self.cover = covers['cover']
        self.cover2x = covers['cover@2x']
        self.card = covers['card']
        self.card2x = covers['card@2x']
        self.list = covers['list']
        self.list2x = covers['list@2x']
        self.slimcover = covers['slimcover']
        self.slimcover2x = covers['slimcover@2x']


# Beatmaps within recent scores
class RecentBeatmap:
    def __init__(self, beatmap):
        self.beatmapset_id = beatmap['beatmapset_id']
        self.difficulty_rating = beatmap['difficulty_rating']
        self.id = beatmap['id']
        self.mode = beatmap['mode']
        self.status = beatmap['status']
        self.total_length = beatmap['total_length']
        self.user_id = beatmap['user_id']
        self.version = beatmap['version']
        self.accuracy = beatmap['accuracy']
        self.ar = beatmap['ar']
        self.bpm = beatmap['bpm']
        self.convert = beatmap['convert']
        self.count_circles = beatmap['count_circles']
        self.count_sliders = beatmap['count_sliders']
        self.count_spinners = beatmap['count_spinners']
        self.cs = beatmap['cs']
        self.deleted_at = beatmap['deleted_at']
        self.drain = beatmap['drain']
        self.hit_length = beatmap['hit_length']
        self.is_scoreable = beatmap['is_scoreable']
        self.last_updated = beatmap['last_updated']
        self.mode_int = beatmap['mode_int']
        self.passcount = beatmap['passcount']
        self.playcount = beatmap['playcount']
        self.ranked = beatmap['ranked']
        self.url = beatmap['url']
        self.checksum = beatmap['checksum']


# Returned when requesting beatmap data from the api
class Beatmap(RecentBeatmap):
    def __init__(self, beatmap_data):
        super().__init__(beatmap_data)
        self.beatmapset = Beatmapset(beatmap_data['beatmapset'])
        self.failtimes = FailTimes(beatmap_data['failtimes'])
        self.max_combo = beatmap_data['max_combo']


class FailTimes():
    def __init__(self, fail_times):
        self.fail = fail_times['fail']
        self.exit = fail_times['exit']


# Data within beatmap data requested from api
class Beatmapset(RecentBeatmapset):
    def __init__(self, beatmapset_data):
        super().__init__(beatmapset_data)
        self.availability = Availability(beatmapset_data['availability'])
        self.bpm = beatmapset_data['bpm']
        self.can_be_hyped = beatmapset_data['can_be_hyped']
        self.discussion_enabled = beatmapset_data['discussion_enabled']
        self.discussion_locked = beatmapset_data['discussion_locked']
        self.is_scoreable = beatmapset_data['is_scoreable']
        self.last_updated = beatmapset_data['last_updated']
        self.legacy_thread_url = beatmapset_data['legacy_thread_url']
        self.nominations_summary = NominationsSummary(
            beatmapset_data['nominations_summary'])
        self.ranked = beatmapset_data['ranked']
        self.ranked_date = beatmapset_data['ranked_date']
        self.storyboard = beatmapset_data['storyboard']
        self.submitted_date = beatmapset_data['submitted_date']
        self.tags = beatmapset_data['tags']
        self.ratings = beatmapset_data['ratings']


class NominationsSummary():
    def __init__(self, nominations_summary):
        self.current = nominations_summary['current']
        self.required = nominations_summary['required']


class Availability():
    def __init__(self, availability):
        self.download_disabled = availability['download_disabled']
        self.more_information = availability['more_information']


class BeatmapStatistics:
    def __init__(self, statistics):
        self.count_100 = statistics['count_100']
        self.count_300 = statistics['count_300']
        self.count_50 = statistics['count_50']
        self.count_geki = statistics['count_geki']
        self.count_katu = statistics['count_katu']
        self.count_miss = statistics['count_miss']


class CurrentUserAttributes:
    def __init__(self, current_user_attributes):
        self.pin = current_user_attributes['pin']
