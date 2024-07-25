"""
Base models of Bilibili API requests
"""
from pydantic import BaseModel


class BaseResponseModel(BaseModel):

    code: int = 0
    message: str = '0'


class BaseResponseWithTTLModel(BaseResponseModel):

    ttl: int = 1


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
