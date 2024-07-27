"""
Base models of Bilibili API requests
"""
from typing import Optional

from pydantic import BaseModel


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
