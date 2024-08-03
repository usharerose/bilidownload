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


class VideoDashVideoSegmentBaseData(BaseModel):

    Initialization: int
    indexRange: str


class VideoDashAudioSegmentBaseData(BaseModel):

    initialization: int
    index_range: str


class VideoDashMediaItemData(BaseModel):

    SegmentBase: Union[VideoDashVideoSegmentBaseData, VideoDashAudioSegmentBaseData]
    backupUrl: List[str]
    backup_url: List[str]
    bandwidth: int
    baseUrl: str
    base_url: str
    codecid: int  # 7 is AVC, 12 is HEVC, and 13 is AV1
    codecs: str
    frameRate: Optional[str] = None
    frame_rate: Optional[str] = None
    height: int
    id_field: int = Field(..., alias='id')
    mimeType: str
    mime_type: str
    sar: str
    segment_base: Union[VideoDashVideoSegmentBaseData, VideoDashAudioSegmentBaseData]
    startWithSAP: Optional[int] = None
    startWithSap: Optional[int] = None
    start_with_sap: int
    width: int


class VideoDashDolbyData(BaseModel):

    type_field: int = Field(..., alias='type')  # 1 is normal, 2 is panoramic
    audio: Optional[List[VideoDashMediaItemData]] = None


class VideoDashFlacData(BaseModel):

    display: bool  # illustrate Hi-Res or not
    audio: Optional[VideoDashMediaItemData] = None


class VideoDashData(BaseModel):

    audio: Optional[List[VideoDashMediaItemData]] = None  # null when video has no audio
    dolby: VideoDashDolbyData
    duration: int  # second
    flac: Optional[VideoDashFlacData] = None
    minBufferTime: float
    min_buffer_time: float
    video: List[VideoDashMediaItemData]
