"""
Response models of login action related Bilibili API requests
"""
from typing import Optional

from pydantic import BaseModel

from .base import BaseResponseModel, BaseResponseModel


__all__ = [
    'GetWebCaptchaResponse',
    'GetWebPublicKeyResponse',
    'WebLoginResponse'
]


class GetWebCaptchaGeetestData(BaseModel):
    """
    Geetest captcha generation parameters
    """
    challenge: str
    gt: str


class GetWebCaptchaTencentData(BaseModel):

    appid: str


class GetWebCaptchaData(BaseModel):

    type: str = 'geetest'
    token: str
    geetest: GetWebCaptchaGeetestData
    tencent: GetWebCaptchaTencentData


class GetWebCaptchaResponse(BaseResponseModel):
    """
    response from 'https://passport.bilibili.com/x/passport-login/captcha?source=main_web'
    which is for Geetest captcha metadata
    """
    data: GetWebCaptchaData


class GetWebPublicKeyData(BaseModel):
    """
    hash: salt on login password
    key: rsa public key, used when encrypt login password
    """
    hash: str
    key: str


class GetWebPublicKeyResponse(BaseResponseModel):
    """
    response from 'https://passport.bilibili.com/x/passport-login/web/key'
    which is for RSA encrypt on password
    """
    data: GetWebPublicKeyData


class LoginData(BaseModel):

    message: str
    refresh_token: str
    status: int = 0
    timestamp: int      # Unix timestamp when login
    url: str


class WebLoginData(BaseModel):

    # 0: success
    # -105: captcha error
    # -400: request error
    # -629：username or password incorrect
    # -653：username or password is empty
    # -662：request timeout
    # -2001：lack of required parameters
    # -2100：need to verify mobile or email
    # 2400：secret key error
    # 2406: Geetest service error
    # 86000: RSA decrypt error
    code: int
    message: str
    data: Optional[LoginData]


class WebLoginResponse(BaseResponseModel):
    """
    response from 'https://passport.bilibili.com/x/passport-login/web/login'
    which is for web login action
    """
    data: WebLoginData
