"""
Response models of bangumi video related Bilibili API requests
"""
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .base import (
    BaseResponseModel,
    PendantData,
    VideoDashData,
    VideoDimensionData,
    VideoStreamMetaLiteSupportFormatItemData
)


__all__ = ['GetBangumiDetailResponse', 'GetBangumiStreamMetaResponse']


class BangumiActivity(BaseModel):

    head_bg_url: str
    id: int
    title: str


class BadgeInfoData(BaseModel):

    bg_color: str
    bg_color_night: str
    text: str


class BangumiRightsLiteData(BaseModel):

    allow_demand: int
    allow_dm: int
    allow_download: int
    area_limit: int


class BangumiRightsData(BaseModel):

    allow_bp: int
    allow_bp_rank: int
    allow_download: int
    allow_review: int
    area_limit: int
    ban_area_show: int
    can_watch: int
    copyright: str
    forbid_pre: int
    is_cover_show: int
    is_preview: int
    only_vip_download: int
    resource: str
    watch_platform: int


class BangumiEpisodeItemData(BaseModel):

    aid: int
    badge: str
    badge_info: BadgeInfoData
    badge_type: int
    bvid: str
    cid: int
    cover: str
    dimension: VideoDimensionData
    from_field: str = Field(..., alias='from')
    id_field: int = Field(..., alias='id')  # epid
    link: str  # URL of the single episode
    long_title: str
    pub_time: int  # Unix timestamp when video published
    pv: int
    release_date: str
    rights: BangumiRightsLiteData
    share_copy: str
    share_url: str
    short_link: str
    status: int
    subtitle: str
    title: str
    vid: str


class BangumiNewEpData(BaseModel):

    desc: str
    id_field: int = Field(..., alias='id')  # Latest episode's epid
    is_new: int  # 0 if not latest publish else 1
    title: str  # Title of latest episode


class BangumiPaymentTypeData(BaseModel):
    """
    0 is disable, 1 is enable
    """
    allow_discount: int
    allow_pack: int
    allow_ticket: int
    allow_time_limit: int
    allow_vip_discount: int
    forbid_bb: int


class BangumiPaymentData(BaseModel):

    discount: int  # 0 - 100, 100 is original
    pay_type: BangumiPaymentTypeData
    price: str
    promotion: str
    vip_discount: int
    vip_first_promotion: str
    vip_price: str
    vip_promotion: str


class BangumiPositiveData(BaseModel):

    id_field: int = Field(..., alias='id')
    title: str


class BangumiPublishData(BaseModel):

    is_finish: int
    is_started: int
    pub_time: str       # Publish time with 'YYYY-MM-DD HH:MM:SS' pattern
    pub_time_show: str  # semantic publish time
    unknow_pub_date: int
    weekday: int


class BangumiRatingData(BaseModel):

    count: int  # amount of the people who participant in the rating
    score: float


class BangumiSeasonItemStatData(BaseModel):

    favorites: int
    series_follow: int
    views: int
    vt: int


class BangumiSeasonItemNewEpisodeData(BaseModel):

    cover: str
    id_field: int = Field(..., alias='id')
    index_show: str


class BangumiSeasonItemData(BaseModel):

    badge: str
    badge_info: BadgeInfoData
    badge_type: int
    cover: str
    media_id: int
    new_ep: BangumiSeasonItemNewEpisodeData
    season_id: int
    season_title: str
    season_type: int
    stat: BangumiSeasonItemStatData


class BangumiSectionItemEpisodeItemIconFontData(BaseModel):

    name: str
    text: str


class SkipData(BaseModel):

    end: int
    start: int


class BangumiSectionItemEpisodeItemSkipData(BaseModel):

    ed: SkipData
    op: SkipData


class BangumiSectionItemEpisodeItemStatData(BaseModel):

    coin: int
    danmakus: int
    likes: int
    play: int
    reply: int
    vt: int


class DanmakuData(BaseModel):

    icon: str
    pure_text: str
    text: str
    value: int


class BangumiSectionItemEpisodeItemStatForUnityData(BaseModel):

    coin: int
    danmaku: DanmakuData
    likes: int
    reply: int
    vt: DanmakuData


class BangumiSectionItemEpisodeItemData(BangumiEpisodeItemData):

    duration: int    # seconds
    enable_vt: bool
    ep_id: int
    icon_font: BangumiSectionItemEpisodeItemIconFontData
    is_view_hide: bool
    showDrmLoginDialog: bool
    skip: Optional[BangumiSectionItemEpisodeItemSkipData] = None
    stat: BangumiSectionItemEpisodeItemStatData
    stat_for_unity: BangumiSectionItemEpisodeItemStatForUnityData


class BangumiSectionItemData(BaseModel):

    attr: int
    episode_id: int
    episode_ids: List[int]
    episodes: List[BangumiSectionItemEpisodeItemData]
    id: int
    title: str
    type_field: int = Field(..., alias='type')
    type2: int


class BangumiSeriesData(BaseModel):

    series_id: int
    series_title: str


class BangumiShowData(BaseModel):

    wide_screen: int  # 0 is normal, 1 is full screen


class BangumiStatData(BaseModel):

    coins: int
    danmakus: int
    favorites: int
    likes: int
    reply: int
    share: int
    views: int


class BangumiUpInfoData(BaseModel):

    avatar: str
    follower: int
    is_follow: int
    mid: int
    pendant: PendantData
    theme_type: int
    uname: str
    verify_type: int
    vip_status: int
    vip_type: int


class GetBangumiDetailResult(BaseModel):

    activity: BangumiActivity
    alias: str
    bkg_cover: str
    cover: str
    episodes: List[BangumiEpisodeItemData]
    evaluate: str
    jp_title: str
    link: str
    media_id: int
    mode: int
    new_ep: BangumiNewEpData
    payment: BangumiPaymentData
    positive: BangumiPositiveData
    publish: BangumiPublishData
    rating: BangumiRatingData
    record: Optional[str] = None
    rights: BangumiRightsData
    season_id: int
    season_title: str
    seasons: List[BangumiSeasonItemData]
    section: Optional[List[BangumiSectionItemData]] = None
    series: BangumiSeriesData
    share_copy: str
    share_sub_title: str
    share_url: str
    show: BangumiShowData
    square_cover: str
    stat: BangumiStatData
    status: int
    subtitle: str
    title: str
    total: int  # -1 if not finished
    # 1: bangumi
    # 2: film
    # 3. documentary
    # 4. Chinese cartoon
    # 5. TV Play
    # 7. Variety Show
    type_field: int = Field(..., alias='type')
    up_info: BangumiUpInfoData


class GetBangumiDetailResponse(BaseResponseModel):
    """
    On 'code' field,

    0：success, and has 'data'
    -404：video unavailable
    """
    result: Optional[GetBangumiDetailResult] = None


class BangumiStreamMetaRecordInfoData(BaseModel):

    record_icon: str
    record: str


class BangumiStreamMetaDURLItemData(BaseModel):

    order: int
    length: int
    size: int
    ahead: str
    vhead: str
    url: str
    backup_url: List[str]
    md5: str


class BangumiStreamMetaSupportFormatItemData(VideoStreamMetaLiteSupportFormatItemData):

    codecs: Optional[List[str]]
    description: str
    display_desc: str
    format_field: str = Field(..., alias='format')
    has_preview: bool
    need_login: Optional[bool] = None
    sub_description: str
    superscript: str


class BangumiStreamMetaClipInfoListItemData(BaseModel):

    clipType: str
    end: int
    materialNo: int
    start: int
    toastText: str


class GetBangumiStreamMetaResult(BaseModel):

    accept_description: List[str]
    accept_format: str
    accept_quality: List[int]
    bp: int
    clip_info_list: List[BangumiStreamMetaClipInfoListItemData]
    code: int
    dash: Optional[VideoDashData] = None
    durl: Optional[List[BangumiStreamMetaDURLItemData]] = None
    # TODO: determine the type of durls' item
    durls: List[Any]
    fnval: int
    fnver: int
    format_field: str = Field(..., alias='format')
    from_field: str = Field(..., alias='from')
    has_paid: bool
    is_drm: bool
    is_preview: int
    message: str
    no_rexcode: int
    quality: int
    record_info: Optional[BangumiStreamMetaRecordInfoData] = None
    result: str
    status: int
    support_formats: List[BangumiStreamMetaSupportFormatItemData]
    timelength: int  # millisecond
    type_field: str = Field(..., alias='type')
    seek_param: str
    seek_type: str
    video_codecid: int
    video_project: bool


class GetBangumiStreamMetaResponse(BaseResponseModel):

    result: Optional[GetBangumiStreamMetaResult] = None
