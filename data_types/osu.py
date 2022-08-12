class OsuScoreData():
    def __init__(self, recent_score_data):
        self.accuracy: float = recent_score_data['accuracy']
        self.best_id: int = recent_score_data['best_id']
        self.created_at: str = recent_score_data['created_at']
        self.id: int = recent_score_data['id']
        self.max_combo: int = recent_score_data['max_combo']
        self.mode: str = recent_score_data['mode']
        self.mode_int: int = recent_score_data['mode_int']
        self.mods: list = recent_score_data['mods']
        self.passed: bool = recent_score_data['passed']
        self.perfect: bool = recent_score_data['perfect']
        self.pp: float = recent_score_data['pp']
        self.rank: str = recent_score_data['rank']
        self.replay: bool = recent_score_data['replay']
        self.score: int = recent_score_data['score']
        self.statistics: BeatmapStatistics = BeatmapStatistics(recent_score_data['statistics'])
        self.user_id: int = recent_score_data['user_id']
        self.current_user_attributes: CurrentUserAttributes = CurrentUserAttributes(
            recent_score_data['current_user_attributes'])
        self.beatmap: RecentBeatmap = RecentBeatmap(recent_score_data['beatmap'])
        self.user: User = User(recent_score_data['user'])

# Api return for recent scores


class OsuRecentScore(OsuScoreData):
    def __init__(self, recent_score_data):
        super().__init__(recent_score_data)
        self.beatmapset: RecentBeatmapset = RecentBeatmapset(recent_score_data['beatmapset'])

# Api return for specific score on beatmap


class OsuScore():
    def __init__(self, osu_score_data):
        self.position: int = osu_score_data['position']
        self.score = OsuScoreData(osu_score_data['score'])


class BeatmapMods():
    def __init__(self, score_data_mods):
        self.attributes: Attributes = Attributes(score_data_mods['attributes'])


class Attributes():
    def __init__(self, attributes):
        self.star_rating: float = attributes['star_rating']
        self.max_combo: int = attributes['max_combo']
        self.aim_difficulty: float = attributes['aim_difficulty']
        self.speed_difficulty: float = attributes['speed_difficulty']
        self.flashlight_difficulty: float = attributes['flashlight_difficulty']
        self.slider_factor: float = attributes['slider_factor']
        self.approach_rate: float = attributes['approach_rate']
        self.overall_difficulty: float = attributes['overall_difficulty']


# User data within recent score api return
class User:
    def __init__(self, user):
        self.avatar_url: str = user['avatar_url']
        self.country_code: str = user['country_code']
        self.default_group: str = user['default_group']
        self.id: int = user['id']
        self.is_active: bool = user['is_active']
        self.is_bot: bool = user['is_bot']
        self.is_deleted: bool = user['is_deleted']
        self.is_online: bool = user['is_online']
        self.is_supporter: bool = user['is_supporter']
        self.last_visit: str = user['last_visit']
        self.pm_friends_only: bool = user['pm_friends_only']
        self.profile_colour = user['profile_colour'] # TODO: Type definition
        self.username: str = user['username']


# Api return for user data
class UserData(User):
    def __init__(self, user_data):
        super().__init__(user_data)
        self.cover_url: str = user_data['cover_url']
        self.discord: str = user_data['discord']
        self.has_supported: bool = user_data['has_supported']
        self.interests: str = user_data['interests']
        self.join_date: str = user_data['join_date']
        self.kudosu: Kudosu = Kudosu(user_data['kudosu'])
        self.location: str = user_data['location']
        self.max_blocks: int = user_data['max_blocks']
        self.max_friends: int = user_data['max_friends']
        self.occupation: str = user_data['occupation']
        self.playmode: str = user_data['playmode']
        self.playstyle: list = user_data['playstyle']
        self.post_count: int = user_data['post_count']
        self.profile_order: list = user_data['profile_order']
        self.title = user_data['title'] # TODO: Type definition
        self.title_url = user_data['title_url'] # TODO: Type definition
        self.twitter: str = user_data['twitter']
        self.website: str = user_data['website']
        self.country: Country = Country(user_data['country'])
        self.cover: Cover = Cover(user_data['cover'])
        self.account_history: list = user_data['account_history']
        self.active_tournament_banner = user_data['active_tournament_banner'] # TODO: Type definition
        self.badges: list = user_data['badges']
        self.beatmap_playcounts_count: int = user_data['beatmap_playcounts_count']
        self.comments_count: int = user_data['comments_count']
        self.favourite_beatmapset_count: int = user_data['favourite_beatmapset_count']
        self.follower_count: int = user_data['follower_count']
        self.graveyard_beatmapset_count: int = user_data['graveyard_beatmapset_count']
        self.groups: list = user_data['groups']
        self.guest_beatmapset_count: int = user_data['guest_beatmapset_count']
        self.loved_beatmapset_count: int = user_data['loved_beatmapset_count']
        self.mapping_follower_count: int = user_data['mapping_follower_count']
        self.monthly_playcounts: list = user_data['monthly_playcounts']
        self.page: Page = Page(user_data['page'])
        self.pending_beatmapset_count: int = user_data['pending_beatmapset_count']
        self.ranked_beatmapset_count: int = user_data['ranked_beatmapset_count']
        self.previous_usernames: list = user_data['previous_usernames']
        self.replays_watched_counts: list = user_data['replays_watched_counts']
        self.scores_best_count: int = user_data['scores_best_count']
        self.scores_first_count: int = user_data['scores_first_count']
        self.scores_pinned_count: int = user_data['scores_pinned_count']
        self.scores_recent_count: int = user_data['scores_recent_count']
        self.statistics: UserStatistics = UserStatistics(user_data['statistics'])
        self.support_level: int = user_data['support_level']
        self.user_achievements: list = user_data['user_achievements']
        self.rankHistory: dict = user_data['rankHistory']
        self.rank_history: dict = user_data['rank_history']
        self.ranked_and_approved_beatmapset_count: int = user_data['ranked_and_approved_beatmapset_count']
        self.unranked_beatmapset_count: int = user_data['unranked_beatmapset_count']


class RankHistory():
    def __init__(self, rank_history):
        self.mode: str = rank_history['mode']
        self.data: list = rank_history['data']


class UserStatistics():
    def __init__(self, statistics):
        self.level: Level = Level(statistics['level'])
        self.global_rank: int = statistics['global_rank']
        self.pp: float = statistics['pp']
        self.ranked_score: int = statistics['ranked_score']
        self.hit_accuracy: float = statistics['hit_accuracy']
        self.play_count: int = statistics['play_count']
        self.play_time: int = statistics['play_time']
        self.total_score: int = statistics['total_score']
        self.maximum_combo: int = statistics['maximum_combo']
        self.replays_watched_by_others: int = statistics['replays_watched_by_others']
        self.is_ranked: bool = statistics['is_ranked']
        self.grade_counts: GradeCounts = GradeCounts(statistics['grade_counts'])
        self.country_rank: int = statistics['country_rank']
        self.rank = Rank(statistics['rank'])


class Rank():
    def __init__(self, rank):
        self.country: int = rank['country']


class GradeCounts():
    def __init__(self, grade_counts):
        self.ss: int = grade_counts['ss']
        self.ssh: int = grade_counts['ssh']
        self.s: int = grade_counts['s']
        self.sh: int = grade_counts['sh']
        self.a: int = grade_counts['a']


class Level():
    def __init__(self, level):
        self.current: int = level['current']
        self.progress: int = level['progress']


class Page():
    def __init__(self, page):
        self.html: str = page['html']
        self.raw: str = page['raw']


class Cover:
    def __init__(self, cover):
        self.url: str = cover['url']
        self.custom_url: str = cover['custom_url']
        self.id = cover['id'] # TODO: Type definition


class Country:
    def __init__(self, country):
        self.code: str = country['code']
        self.name: str = country['name']


class Kudosu:
    def __init__(self, kudosu):
        self.total: int = kudosu['total']
        self.available: int = kudosu['available']


# Beatmapset data returned in recent score
class RecentBeatmapset:
    def __init__(self, beatmapset):
        self.artist: str = beatmapset['artist']
        self.artist_unicode: str = beatmapset['artist_unicode']
        self.covers: Covers = Covers(beatmapset['covers'])
        self.creator: str = beatmapset['creator']
        self.favourite_count: int = beatmapset['favourite_count']
        self.hype = beatmapset['hype'] # TODO: Type definition
        self.id: int = beatmapset['id']
        self.nsfw: bool = beatmapset['nsfw']
        self.offset = beatmapset['offset'] # TODO: Type definition (int or float)
        self.play_count: int = beatmapset['play_count']
        self.preview_url: str = beatmapset['preview_url']
        self.source: str = beatmapset['source']
        self.spotlight: bool = beatmapset['spotlight']
        self.status: str = beatmapset['status']
        self.title: str = beatmapset['title']
        self.title_unicode: str = beatmapset['title_unicode']
        self.track_id = beatmapset['track_id'] # TODO: Type definition
        self.user_id: int = beatmapset['user_id']
        self.video: bool = beatmapset['video']


class Covers:
    def __init__(self, covers):
        self.cover: str = covers['cover']
        self.cover2x: str = covers['cover@2x']
        self.card: str = covers['card']
        self.card2x: str = covers['card@2x']
        self.list: str = covers['list']
        self.list2x: str = covers['list@2x']
        self.slimcover: str = covers['slimcover']
        self.slimcover2x: str = covers['slimcover@2x']


# Beatmaps within recent scores
class RecentBeatmap:
    def __init__(self, beatmap):
        self.beatmapset_id: int = beatmap['beatmapset_id']
        self.difficulty_rating: float = beatmap['difficulty_rating']
        self.id: int = beatmap['id']
        self.mode: str = beatmap['mode']
        self.status: str = beatmap['status']
        self.total_length: int = beatmap['total_length']
        self.user_id: int = beatmap['user_id']
        self.version: str = beatmap['version']
        self.accuracy: float = beatmap['accuracy']
        self.ar: float = beatmap['ar']
        self.bpm: float = beatmap['bpm']
        self.convert: bool = beatmap['convert']
        self.count_circles: int = beatmap['count_circles']
        self.count_sliders: int = beatmap['count_sliders']
        self.count_spinners: int = beatmap['count_spinners']
        self.cs: float = beatmap['cs']
        self.deleted_at = beatmap['deleted_at'] # TODO: Type definition
        self.drain: float = beatmap['drain']
        self.hit_length: float = beatmap['hit_length']
        self.is_scoreable: bool = beatmap['is_scoreable']
        self.last_updated: str = beatmap['last_updated']
        self.mode_int: int = beatmap['mode_int']
        self.passcount: int = beatmap['passcount']
        self.playcount: int = beatmap['playcount']
        self.ranked: int = beatmap['ranked']
        self.url: str = beatmap['url']
        self.checksum: str = beatmap['checksum']


# Returned when requesting beatmap data from the api
class Beatmap(RecentBeatmap):
    def __init__(self, beatmap_data):
        super().__init__(beatmap_data)
        self.beatmapset: Beatmapset = Beatmapset(beatmap_data['beatmapset'])
        self.failtimes: FailTimes = FailTimes(beatmap_data['failtimes'])
        self.max_combo: int = beatmap_data['max_combo']


class FailTimes():
    def __init__(self, fail_times):
        self.fail: list = fail_times['fail']
        self.exit: list = fail_times['exit']


# Data within beatmap data requested from api
class Beatmapset(RecentBeatmapset):
    def __init__(self, beatmapset_data):
        super().__init__(beatmapset_data)
        self.availability: Availability = Availability(beatmapset_data['availability'])
        self.bpm: float = beatmapset_data['bpm']
        self.can_be_hyped: bool = beatmapset_data['can_be_hyped']
        self.discussion_enabled: bool = beatmapset_data['discussion_enabled']
        self.discussion_locked: bool = beatmapset_data['discussion_locked']
        self.is_scoreable: bool = beatmapset_data['is_scoreable']
        self.last_updated: str = beatmapset_data['last_updated']
        self.legacy_thread_url: str = beatmapset_data['legacy_thread_url']
        self.nominations_summary: NominationsSummary = NominationsSummary(
            beatmapset_data['nominations_summary'])
        self.ranked: int = beatmapset_data['ranked']
        self.ranked_date: str = beatmapset_data['ranked_date']
        self.storyboard: bool = beatmapset_data['storyboard']
        self.submitted_date: str = beatmapset_data['submitted_date']
        self.tags: str = beatmapset_data['tags']
        self.ratings: list = beatmapset_data['ratings']


class NominationsSummary():
    def __init__(self, nominations_summary):
        self.current: int = nominations_summary['current']
        self.required: int = nominations_summary['required']


class Availability():
    def __init__(self, availability):
        self.download_disabled: bool = availability['download_disabled']
        self.more_information = availability['more_information'] # TODO: Type definition


class BeatmapStatistics:
    def __init__(self, statistics):
        self.count_100: int = statistics['count_100']
        self.count_300: int = statistics['count_300']
        self.count_50: int = statistics['count_50']
        self.count_geki: int = statistics['count_geki']
        self.count_katu: int = statistics['count_katu']
        self.count_miss: int = statistics['count_miss']


class CurrentUserAttributes:
    def __init__(self, current_user_attributes):
        self.pin = current_user_attributes['pin'] # TODO: Type definition
