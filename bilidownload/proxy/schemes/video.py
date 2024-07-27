"""
Response models of video related Bilibili API requests
"""
from typing import List, Optional

from pydantic import BaseModel, Field

from .base import (
    BaseResponseModel,
    UserOfficialInfoData,
    VideoDimensionData,
    VideoStreamMetaLiteSupportFormatItemData
)


__all__ = [
    'GetVideoInfoResponse',
    'GetVideoStreamMetaResponse'
]


class VideoDescriptionV2ItemData(BaseModel):

    raw_text: str    # description content
    type: int        # 1 when common, 2 when @other user
    biz_id: int = 0  # 0 when type is common, or user ID which is @


class VideoRightsData(BaseModel):

    bp: int               # allow contract or not
    elec: int             # allow charging or not
    download: int         # allow download or not
    movie: int            # whether is movie or not
    pay: int              # whether is PGC paid or not
    hd5: int              # whether it has high bit rate or not
    no_reprint: int       # whether it illustrates 'No Reprint' or not
    autoplay: int         # whether is auto-plays or not
    ugc_pay: int          # whether is UGC paid or not
    is_cooperation: int   # whether it is created by multiple creators or not
    ugc_pay_preview: int
    no_background: int
    clean_mode: int
    is_stein_gate: int    # whether it is interactive video or not
    is_360: int           # whether it is full view video or not
    no_share: int
    arc_pay: int
    free_watch: int


class VideoOwnerData(BaseModel):

    mid: int   # User ID
    name: str  # User name
    face: str  # Profile icon's source URL


class VideoStatusData(BaseModel):

    aid: int         # AV ID of video
    view: int        # Count of play times
    danmaku: int     # Count of danmu
    reply: int       # Count of comments
    favorite: int    # Count of collect
    coin: int        # Count of coins received
    share: int       # Count of sharing
    now_rank: int    # Current rank
    his_rank: int    # Historical highest rank
    like: int        # Count of like
    dislike: int     # Count of dislike
    evaluation: str  # Video evaluation
    vt: int = 0


class VideoPagesItemData(BaseModel):

    cid: int                                    # cid of this page
    page: int                                   # Serial num of this page
    from_field: str = Field(..., alias='from')  # Source of video, vupload, hunan or qq
    part: str                                   # Title of this page
    duration: int                               # Total seconds of this page
    vid: str                                    # Identifier of outside site video
    weblink: str                                # URL of outside site video
    dimension: VideoDimensionData
    first_frame: Optional[str] = None


class VideoSubtitleAuthorData(BaseModel):

    mid: int   # Identifier of user who uploads the subtitle
    name: str  # Nickname of user
    sex: str   # gender of user, 男, 女 and 保密
    face: str  # Profile icon's source URL
    sign: str  # Sign of user who uploads the subtitle
    rank: int
    birthday: int
    is_fake_account: int
    is_deleted: int


class VideoSubtitleItemData(BaseModel):

    id: int                          # identifier of subtitle
    lan: str                         # Language
    lan_doc: str                     # Language name of subtitle language
    is_lock: bool                    # Whether the subtitle is locked or not
    author_mid: int                  # Identifier of user who uploads the subtitle
    subtitle_url: str                # URL of subtitle JSON file
    author: VideoSubtitleAuthorData


class VideoSubtitleData(BaseModel):

    allow_submit: bool  # Whether allow to submit subtitle or not
    list_field: List[VideoSubtitleItemData] = Field(
        ...,
        alias='list'
    )                   # Source of video, vupload, hunan or qq


class VideoStaffVipInfoData(BaseModel):

    vip_type: int = Field(..., alias='type')  # 0: No VIP; 1：Monthly VIP; 2: Yearly or superior VIP
    status: int  # 0: No VIP; 1: Has VIP
    theme_type: int


class VideoStaffItemData(BaseModel):

    mid: int                        # Identifier of user
    title: str                      # Name of user
    name: str                       # Nickname of user
    face: str                       # Profile icon's source URL
    vip: VideoStaffVipInfoData
    official: UserOfficialInfoData
    follower: int                   # Count of followers
    label_style: int


class VideoUserGrabData(BaseModel):

    url_image_ani_cut: str


class VideoHonorItemData(BaseModel):

    aid: int  # AV ID of current video
    # Enum of honor_type
    # 1: 入站必刷收录
    # 2：第n期每周必看
    # 3：全站排行榜最高第n名
    # 4: 热门
    honor_type: int = Field(..., alias='type')
    desc: str
    weekly_recommend_num: int


class VideoHonorReplyData(BaseModel):

    honor: Optional[List[VideoHonorItemData]] = None


class VideoArgueInfoData(BaseModel):

    argue_msg: str
    argue_type: int
    argue_link: str


class GetVideoInfoData(BaseModel):

    # BV ID of video, refer to https://www.bilibili.com/blackboard/activity-BV-PC.html
    bvid: str
    aid: int                                   # AV ID of video
    videos: int = 1                            # Count of pages
    tid: int                                   # ID of category
    tname: str                                 # Name of category
    copyright: int                             # 1 is original, 2 is relaid
    pic: str                                   # URL of video cover
    title: str                                 # Title of video
    pubdate: int                               # Unix timestamp when video published (audited)
    ctime: int                                 # Unix timestamp when video contributed
    desc: str                                  # legacy version video description
    desc_v2: Optional[List[VideoDescriptionV2ItemData]]
    state: int                                 # video attributes
    duration: int                              # Total seconds of video
    rights: VideoRightsData
    owner: VideoOwnerData
    stat: VideoStatusData
    forward: Optional[int] = None              # AV ID of redirect video when video is conflict
    mission_id: Optional[int] = None           # Identifier of mission which video participants
    redirect_url: Optional[str] = None         # AV/BV -> ep
    dynamic: str                               # Content of activity when video is published
    cid: int                                   # cid of video's 1P
    dimension: VideoDimensionData
    premiere: None
    teenage_mode: int
    is_chargeable_season: bool
    is_story: bool
    no_cache: bool
    pages: List[VideoPagesItemData]
    subtitle: VideoSubtitleData
    staff: Optional[List[VideoStaffItemData]] = None
    is_season_display: bool
    user_garb: VideoUserGrabData
    honor_reply: Optional[VideoHonorReplyData]
    like_icon: str
    argue_info: VideoArgueInfoData
    is_upower_exclusive: bool
    is_upower_play: bool
    is_upower_preview: bool
    enable_vt: int
    vt_display: str
    need_jump_bv: bool
    disable_show_up_info: bool
    is_story_play: int


class GetVideoInfoResponse(BaseResponseModel):
    """
    On 'code' field,

    0：success, and has 'data'
    -400：request error
    -403：authentication limit
    -404：video unavailable
    62002：video invisible
    62004：video in review
    """
    data: Optional[GetVideoInfoData] = None


class VideoStreamMetaDURLItemData(BaseModel):

    order: int
    length: int
    size: int
    ahead: str
    vhead: str
    url: str
    backup_url: List[str]


class VideoStreamMetaSupportFormatItemData(VideoStreamMetaLiteSupportFormatItemData):

    format_field: str = Field(..., alias='format')
    display_desc: str
    superscript: str
    codecs: Optional[List[str]]


class GetVideoStreamMetaData(BaseModel):

    from_field: str = Field(..., alias='from')
    result: str
    message: str
    quality: int
    format_field: str = Field(..., alias='format')
    timelength: int  # millisecond
    accept_format: str
    accept_description: List[str]
    accept_quality: List[int]
    video_codecid: int
    seek_param: str
    seek_type: str
    durl: List[VideoStreamMetaDURLItemData]
    support_formats: List[VideoStreamMetaSupportFormatItemData]
    high_format: None
    last_play_time: int
    last_play_cid: int
    view_info: None


class GetVideoStreamMetaResponse(BaseResponseModel):

    data: Optional[GetVideoStreamMetaData] = None
