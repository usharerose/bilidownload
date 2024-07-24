"""
Base models of Bilibili API requests
"""
from pydantic import BaseModel


class BaseResponseModel(BaseModel):

    code: int = 0
    message: str = '0'


class BaseResponseWithTTLModel(BaseResponseModel):

    ttl: int = 1
