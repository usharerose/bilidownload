"""
Scheme of video data
"""
from typing import Optional, List

from pydantic import BaseModel

from ..proxy import VideoStreamMetaLiteSupportFormatItemData


class VideoMetaStaffItem(BaseModel):

    avatar_url: str  # Profile icon's source URL
    mid: int         # Identifier of user
    name: str        # Nickname of user
    title: str       # Name of user


class VideoPageLiteItemData(BaseModel):

    aid: Optional[int] = None
    bvid: Optional[str] = None
    epid: Optional[int] = None
    cid: int                    # cid of this page
    title: str                  # Title of this page
    badge_text: str
    is_available: bool
    duration: Optional[int]     # unit is second
    video_type: str


class VideoFormatItemData(VideoStreamMetaLiteSupportFormatItemData):

    is_login_needed: bool
    is_vip_needed: bool


class VideoMetaModel(BaseModel):

    work_cover_url: str
    work_description: str
    work_url: str
    work_staff: List[VideoMetaStaffItem]
    work_title: str
    work_pages: List[VideoPageLiteItemData]
    work_formats: List[VideoFormatItemData]
    has_dolby_audio: bool
