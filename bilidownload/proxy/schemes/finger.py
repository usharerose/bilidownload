"""
Response models of frontend finger Bilibili API requests
"""
from pydantic import BaseModel

from .base import BaseResponseModel


__all__ = ['GetWebSPIResponse']


class GetWebSPIData(BaseModel):

    b_3: str
    b_4: str


class GetWebSPIResponse(BaseResponseModel):
    """
    response from 'https://api.bilibili.com/x/frontend/finger/spi'
    which is for frontend finger SPI
    """
    data: GetWebSPIData
    message: str = 'ok'
