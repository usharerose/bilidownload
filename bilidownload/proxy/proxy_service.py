"""
Bilibili official API proxy
"""
import copy
import json
from typing import Optional, Union
from urllib.parse import urlencode

import requests
from requests import Response

from .constants import (
    REQUEST_VIDEO_INFO_URL,
    REQUEST_WEB_CAPTCHA_URL,
    REQUEST_WEB_LOGIN_URL,
    REQUEST_WEB_PUBLIC_KEY_URL,
    REQUEST_WEB_SPI_URL,
    REQUEST_WEB_USER_INFO_URL
)
from .schemes import (
    GetUserInfoLoginResponse,
    GetUserInfoNotLoginResponse,
    GetWebCaptchaResponse,
    GetWebPublicKeyResponse,
    GetWebSPIResponse,
    GetVideoInfoResponse,
    WebLoginResponse
)
from ..constants import HEADERS, TIMEOUT


class ProxyService:

    @classmethod
    def get_web_captcha_meta(cls) -> Response:
        response = requests.get(REQUEST_WEB_CAPTCHA_URL, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_web_captcha_meta_data(cls) -> GetWebCaptchaResponse:
        response = cls.get_web_captcha_meta()
        data = json.loads(response.content.decode('utf-8'))
        return GetWebCaptchaResponse.model_validate(data)

    @classmethod
    def get_web_public_key(cls) -> Response:
        response = requests.get(REQUEST_WEB_PUBLIC_KEY_URL, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_web_public_key_data(cls) -> GetWebPublicKeyResponse:
        response = cls.get_web_public_key()
        data = json.loads(response.content.decode('utf-8'))
        return GetWebPublicKeyResponse.model_validate(data)

    @classmethod
    def get_web_spi(cls) -> Response:
        response = requests.get(REQUEST_WEB_SPI_URL, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_web_spi_data(cls) -> GetWebSPIResponse:
        response = cls.get_web_spi()
        data = json.loads(response.content.decode('utf-8'))
        return GetWebSPIResponse.model_validate(data)

    @classmethod
    def get_web_user_info(
        cls,
        session_data: Optional[str] = None
    ) -> Response:
        session = requests.session()
        if session_data:
            session.cookies.set('SESSDATA', session_data)
        response = session.get(REQUEST_WEB_USER_INFO_URL, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_web_user_info_data(
        cls,
        session_data: Optional[str] = None
    ) -> Union[GetUserInfoLoginResponse, GetUserInfoNotLoginResponse]:
        response = cls.get_web_user_info(session_data)
        data = json.loads(response.content.decode('utf-8'))
        model = GetUserInfoLoginResponse
        if data['code'] != 0:
            model = GetUserInfoNotLoginResponse
        return model.model_validate(data)

    @classmethod
    def login(
        cls,
        username: str,
        encrypted_password: str,
        token: str,
        challenge: str,
        validate: str,
        seccode: str
    ):
        session = requests.session()
        spi_response_dm = ProxyService.get_web_spi_data()
        session.cookies.set('buvid3', spi_response_dm.data.b_3)
        session.cookies.set('buvid4', spi_response_dm.data.b_4)

        data = {
            'source': 'main-fe-header',
            'username': username,
            'password': encrypted_password,
            'keep': 0,
            'token': token,
            'challenge': challenge,
            'validate': validate,
            'seccode': seccode,
            'go_url': 'https://www.bilibili.com/'
        }
        encoded_data = urlencode(data)
        headers = copy.deepcopy(HEADERS)
        headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        response = session.post(
            REQUEST_WEB_LOGIN_URL,
            headers=headers,
            data=encoded_data,
            timeout=TIMEOUT
        )
        return response

    @classmethod
    def login_data(
        cls,
        username: str,
        encrypted_password: str,
        token: str,
        challenge: str,
        validate: str,
        seccode: str
    ) -> WebLoginResponse:
        response = cls.login(
            username, encrypted_password, token, challenge, validate, seccode
        )
        data = json.loads(response.content.decode('utf-8'))
        return WebLoginResponse.model_validate(data)

    @classmethod
    def get_video_info(
        cls,
        bvid: str,
        session_data: Optional[str] = None
    ) -> Response:
        session = requests.session()
        if session_data:
            session.cookies.set('SESSDATA', session_data)
        params = {
            'bvid': bvid
        }
        response = session.get(REQUEST_VIDEO_INFO_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_video_info_data(
        cls,
        bvid: str,
        session_data: Optional[str] = None
    ) -> GetVideoInfoResponse:
        response = cls.get_video_info(bvid, session_data)
        data = json.loads(response.content.decode('utf-8'))
        return GetVideoInfoResponse.model_validate(data)
