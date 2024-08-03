"""
Base models of Bilibili API requests
"""
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class BaseResponseModel(BaseModel):

    code: int = 0
    message: str = '0'
    ttl: Optional[int] = None


class UserOfficialVerifyData(BaseModel):

    type: int       # -1 as unverified, 0 as verified
    desc: str = ''  # Verification description


class UserOfficialInfoData(UserOfficialVerifyData):

    # 0: unverified
    # 1: personal verified, famous UP
    # 2: personal verified, V
    # 3: organization verified, enterprise
    # 4: organization verified, organization
    # 5: organization verified, media
    # 6: organization verified, government
    # 7: personal verified, Live show host
    # 9: personal verified, Social KOL
    role: int
    title: str  # Title of role


class VideoDimensionData(BaseModel):

    width: int   # Video width of current page
    height: int  # Video height of current page
    rotate: int  # 1 when exchange width and height, 0 not


class PendantData(BaseModel):

    pid: int = 0                   # Identifier of pendant
    name: str = ''                 # Name of pendant
    image: str = ''                # URL of pendant image


class VideoStreamMetaLiteSupportFormatItemData(BaseModel):

    quality: int  # qn
    new_description: str


class VideoDashSegmentBaseData(BaseModel):

    # for audio
    initialization: Optional[int] = None
    index_range: Optional[str] = None
    # for video
    Initialization: Optional[int] = None
    indexRange: Optional[str] = None


class VideoDashMediaItemData(BaseModel):

    SegmentBase: Optional[VideoDashSegmentBaseData] = None
    backupUrl: Optional[List[str]] = None
    backup_url: List[str]
    bandwidth: int
    baseUrl: Optional[str] = None
    base_url: str
    codecid: int  # 7 is AVC, 12 is HEVC, and 13 is AV1
    codecs: str
    frameRate: Optional[str] = None
    frame_rate: Optional[str] = None
    height: int
    id_field: int = Field(..., alias='id')
    mimeType: Optional[str] = None
    mime_type: str
    sar: str
    segment_base: VideoDashSegmentBaseData
    startWithSAP: Optional[int] = None
    startWithSap: Optional[int] = None
    start_with_sap: int
    width: int


class VideoDashDolbyData(BaseModel):

    # 1 is normal, 2 is panoramic
    # for cheese, could be 'NONE'
    type_field: Union[int, str] = Field(..., alias='type')
    audio: Optional[List[VideoDashMediaItemData]] = None


class VideoDashFlacData(BaseModel):

    display: bool  # illustrate Hi-Res or not
    audio: Optional[VideoDashMediaItemData] = None


class VideoDashData(BaseModel):

    audio: Optional[List[VideoDashMediaItemData]] = None  # null when video has no audio
    dolby: VideoDashDolbyData
    duration: int  # second
    flac: Optional[VideoDashFlacData] = None
    minBufferTime: Optional[float] = None
    min_buffer_time: Optional[float] = None
    video: List[VideoDashMediaItemData]
