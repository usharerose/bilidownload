"""
Response models of cheese video related Bilibili API requests
"""
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .base import (
    BaseResponseModel,
    PendantData,
    VideoStreamMetaLiteSupportFormatItemData
)


__all__ = ['GetCheeseDetailResponse', 'GetCheeseStreamMetaResponse']


class CheeseAbtestInfo(BaseModel):

    style_abtest: int


class CheeseBriefImgItemData(BaseModel):

    aspect_ratio: float
    url: str


class CheeseBriefData(BaseModel):

    content: str
    img: List[CheeseBriefImgItemData]
    title: str
    type_field: int = Field(..., alias='type')


class CheeseConsultingData(BaseModel):

    consulting_flag: bool
    consulting_url: str


class CheeseCooperationData(BaseModel):

    link: str


class CheeseCouponData(BaseModel):

    amount: float
    coupon_type: int
    discount_amount: str
    expire_minute: str         # 'YYYY-MM-DD HH:MM'
    expire_time: str           # 'YYYY-MM-DD HH:MM:SS'
    receive_expire_time: int   # Unix timestamp
    scene_background_img: str
    scene_benefit_img: str
    scene_countdown: bool
    scene_mark: str
    short_title: str
    show_amount: str
    start_time: str            # 'YYYY-MM-DD HH:MM:SS'
    status: int
    title: str
    token: str
    use_expire_time: int       # Unix timestamp
    use_scope: str


class CheeseEpisodePageData(BaseModel):

    next_field: bool = Field(..., alias='next')
    num: int
    size: int
    total: int


class CheeseEpisodeItemData(BaseModel):

    aid: int                # different from common video's AV ID
    catalogue_index: int
    cid: int                # different from common video's cid
    cover: str
    duration: int           # Duration seconds
    ep_status: int
    episode_can_view: bool
    from_field: str = Field(..., alias='from')
    id_field: int = Field(..., alias='id')  # different from bangumi's EP ID
    index: int
    label: Optional[str] = None
    page: int
    play: int
    play_way: int
    playable: bool
    release_date: int       # Unix timestamp
    show_vt: bool
    status: int
    subtitle: str
    title: str
    watched: bool
    watchedHistory: int


class CheeseFAQData(BaseModel):

    content: str
    link: str
    title: str


class CheeseFAQPairItemData(BaseModel):

    question: str
    answer: str


class CheeseFAQPairData(BaseModel):

    items: List[CheeseFAQPairItemData]
    title: str


class CheesePackageInfoData(BaseModel):

    # TODO: determine the type of package item
    pack_item_list: List[Any]
    pack_notice2: str
    show_packs_right: bool
    title: str


class CheesePaidJumpData(BaseModel):

    jump_url_for_app: str
    url: str


class CheesePaymentData(BaseModel):
    bp_enough: int
    desc: str
    discount_desc: str
    my_bp: int
    pay_shade: str
    price: float
    price_format: str
    price_unit: str
    refresh_text: str
    select_text: str


class CheesePreviewedPurchaseNoteData(BaseModel):

    long_watch_text: str
    pay_text: str
    price_format: str
    watch_text: str
    watching_text: str


class CheesePurchaseFormatNoteContentItemData(BaseModel):

    bold: bool
    content: str
    number: str


class CheesePurchaseFormatNoteData(BaseModel):

    content_list: List[CheesePurchaseFormatNoteContentItemData]
    link: str
    title: str


class CheesePurchaseNoteData(BaseModel):

    content: str
    link: str
    title: str


class CheesePurchaseProtocolData(BaseModel):

    link: str
    title: str


class CheeseRecommendSeasonItemData(BaseModel):
    cover: str
    ep_count: str
    id_field: int = Field(..., alias='id')
    season_url: str
    subtitle: str
    title: str
    view: int


class CheeseStatData(BaseModel):

    play: int
    play_desc: str
    show_vt: bool


class CheeseUpInfoData(BaseModel):

    avatar: str
    brief: str
    follower: int
    is_follow: int
    is_living: bool
    link: str
    mid: int
    pendant: PendantData
    season_count: int
    uname: str


class CheeseProgressData(BaseModel):

    last_ep_id: int
    last_ep_index: str
    last_time: int


class CheeseUserStatusData(BaseModel):

    bp: int
    expire_at: int
    favored: int
    favored_count: int
    is_expired: bool
    is_first_paid: bool
    payed: int
    progress: Optional[CheeseProgressData] = None
    user_expiry_content: str


class GetCheeseDetailData(BaseModel):

    abtest_info: CheeseAbtestInfo
    active_market: List[int]
    # TODO: determine the type of activity list item
    activity_list: List[Any]
    be_subscription: bool
    brief: CheeseBriefData
    consulting: CheeseConsultingData
    cooperation: CheeseCooperationData
    # TODO: determine the type of cooperator item
    cooperators: List[Any]
    coupon: Optional[CheeseCouponData] = None
    course_content: str
    # TODO: determine the type of cooperator item
    courses: List[Any]
    cover: str
    # TODO: determine the type of episode catalogue item
    ep_catalogue: List[Any]
    ep_count: int
    episode_page: CheeseEpisodePageData
    episode_sort: int
    episodes: List[CheeseEpisodeItemData]
    expiry_day: int
    expiry_info_content: str
    faq: CheeseFAQData
    faq1: CheeseFAQPairData
    is_enable_cash: bool
    is_series: bool
    live_ep_count: int
    # TODO: determine the type of notice
    notice: Any
    opened_ep_count: int
    pack_info: CheesePackageInfoData
    paid_jump: CheesePaidJumpData
    payment: CheesePaymentData
    previewed_purchase_note: CheesePreviewedPurchaseNoteData
    purchase_format_note: CheesePurchaseFormatNoteData
    purchase_note: CheesePurchaseNoteData
    purchase_protocol: CheesePurchaseProtocolData
    recommend_seasons: List[CheeseRecommendSeasonItemData]
    release_bottom_info: str
    release_info: str
    release_info2: str
    release_status: str
    season_id: int
    season_tag: int
    share_url: str
    short_link: str
    show_watermark: bool
    stat: CheeseStatData
    status: int
    stop_sell: bool
    subscription_update_count_cycle_text: str
    subtitle: str
    title: str
    up_info: CheeseUpInfoData
    update_status: int
    user_status: CheeseUserStatusData
    watermark_interval: int


class GetCheeseDetailResponse(BaseResponseModel):
    """
    On 'code' field,

    0：success, and has 'data'
    -404：video unavailable
    """
    data: Optional[GetCheeseDetailData] = None


class CheeseStreamDashMediaSegmentBaseData(BaseModel):

    initialization: str
    index_range: str


class CheeseStreamMetaDashMediaItemData(BaseModel):

    backup_url: List[str]
    bandwidth: int
    base_url: str
    codecid: int
    codecs: str
    frame_rate: str
    height: int
    id_field: int = Field(..., alias='id')
    md5: str
    mime_type: str
    noRexcode: int
    sar: str
    segment_base: CheeseStreamDashMediaSegmentBaseData
    size: int
    start_with_sap: int
    width: int


class CheeseStreamDashDolbyData(BaseModel):

    # TODO: determine the type of audio's item
    audio: List[Any]
    type: str


class CheeseStreamDashLossLessAudioData(BaseModel):

    isLosslessAudio: bool


class CheeseStreamMetaDashData(BaseModel):

    audio: List[CheeseStreamMetaDashMediaItemData]
    dolby: CheeseStreamDashDolbyData
    duration: int
    losslessAudio: CheeseStreamDashLossLessAudioData
    min_buffer_time: float
    video: List[CheeseStreamMetaDashMediaItemData]


class BangumiStreamMetaSupportFormatItemData(VideoStreamMetaLiteSupportFormatItemData):

    codecs: Optional[List[str]]
    description: str
    display_desc: str
    format_field: str = Field(..., alias='format')
    need_login: Optional[bool] = None
    superscript: str


class GetCheeseStreamMetaData(BaseModel):

    accept_description: List[str]
    accept_format: str
    accept_quality: List[int]
    code: int
    dash: CheeseStreamMetaDashData
    fnval: int
    fnver: int
    format_field: str = Field(..., alias='format')
    from_field: str = Field(..., alias='from')
    has_paid: bool
    is_preview: int
    message: str
    no_rexcode: int
    quality: int
    result: str
    seek_param: str
    seek_type: str
    status: int
    support_formats: List[BangumiStreamMetaSupportFormatItemData]
    timelength: int
    type_field: str = Field(..., alias='type')
    video_codecid: int
    video_project: bool


class GetCheeseStreamMetaResponse(BaseResponseModel):

    data: Optional[GetCheeseStreamMetaData] = None
