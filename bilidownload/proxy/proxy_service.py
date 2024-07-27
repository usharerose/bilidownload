"""
Bilibili official API proxy
"""
import copy
from enum import Enum
import json
from typing import Optional, Union
from urllib.parse import urlencode

import requests
from requests import Response

from .constants import (
    REQUEST_PGC_INFO_URL,
    REQUEST_PGC_STREAM_META_URL,
    REQUEST_PUGV_INFO_URL,
    REQUEST_PUGV_STREAM_META_URL,
    REQUEST_VIDEO_INFO_URL,
    REQUEST_VIDEO_STREAM_META_URL,
    REQUEST_WEB_CAPTCHA_URL,
    REQUEST_WEB_LOGIN_URL,
    REQUEST_WEB_PUBLIC_KEY_URL,
    REQUEST_WEB_SPI_URL,
    REQUEST_WEB_USER_INFO_URL
)
from .schemes import (
    GetBangumiDetailResponse,
    GetBangumiStreamMetaResponse,
    GetCheeseDetailResponse,
    GetCheeseStreamMetaResponse,
    GetUserInfoLoginResponse,
    GetUserInfoNotLoginResponse,
    GetWebCaptchaResponse,
    GetWebPublicKeyResponse,
    GetWebSPIResponse,
    GetVideoInfoResponse,
    GetVideoStreamMetaResponse,
    WebLoginResponse
)
from ..constants import HEADERS, TIMEOUT


VIDEO_FORMAT_DASH = 16


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
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        session_data: Optional[str] = None
    ) -> Response:
        """
        only need one of video's bvid or aid
        bvid is prior than aid if both exist
        """
        if all([id_value is None for id_value in (bvid, aid)]):
            raise

        session = requests.session()
        if session_data:
            session.cookies.set('SESSDATA', session_data)
        params = {}
        if bvid is not None:
            params.update({'bvid': bvid})
        else:
            params.update({'aid': aid})
        response = session.get(REQUEST_VIDEO_INFO_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_video_info_data(
        cls,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        session_data: Optional[str] = None
    ) -> GetVideoInfoResponse:
        response = cls.get_video_info(bvid, aid, session_data)
        data = json.loads(response.content.decode('utf-8'))
        return GetVideoInfoResponse.model_validate(data)

    @classmethod
    def get_video_stream_meta(
        cls,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        session_data: Optional[str] = None
    ) -> Response:
        """
        only need one of video's bvid or aid
        bvid is prior than aid if both exist
        """
        if all([id_value is None for id_value in (bvid, aid)]):
            raise

        session = requests.session()
        if session_data:
            session.cookies.set('SESSDATA', session_data)
        params = {}
        if bvid is not None:
            params.update({'bvid': bvid})
        else:
            params.update({'avid': aid})
        params.update({'cid': cid})
        response = session.get(REQUEST_VIDEO_STREAM_META_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_video_stream_meta_data(
        cls,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        session_data: Optional[str] = None
    ) -> GetVideoStreamMetaResponse:
        response = cls.get_video_stream_meta(cid, bvid, aid, session_data)
        data = json.loads(response.content.decode('utf-8'))
        return GetVideoStreamMetaResponse.model_validate(data)

    @classmethod
    def get_bangumi_info(
        cls,
        ssid: Optional[int] = None,
        epid: Optional[int] = None,
        session_data: Optional[str] = None
    ) -> Response:
        """
        only need one of bangumi's ssid or epid
        ssid is prior than epid if both exist
        """
        if all([id_value is None for id_value in (ssid, epid)]):
            raise

        session = requests.session()
        if session_data:
            session.cookies.set('SESSDATA', session_data)
        params = {}
        if ssid is not None:
            params.update({'season_id': ssid})
        else:
            params.update({'ep_id': epid})
        response = session.get(REQUEST_PGC_INFO_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_bangumi_info_data(
        cls,
        ssid: Optional[int] = None,
        epid: Optional[int] = None,
        session_data: Optional[str] = None
    ) -> GetBangumiDetailResponse:
        response = cls.get_bangumi_info(ssid, epid , session_data)
        data = json.loads(response.content.decode('utf-8'))
        return GetBangumiDetailResponse.model_validate(data)

    @classmethod
    def get_bangumi_stream_meta(
        cls,
        epid: int,
        session_data: Optional[str] = None
    ) -> Response:
        session = requests.session()
        if session_data:
            session.cookies.set('SESSDATA', session_data)
        params = {'ep_id': epid}
        response = session.get(REQUEST_PGC_STREAM_META_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_bangumi_stream_meta_data(
        cls,
        epid: int,
        session_data: Optional[str] = None
    ) -> GetBangumiStreamMetaResponse:
        response = cls.get_bangumi_stream_meta(epid, session_data)
        data = json.loads(response.content.decode('utf-8'))
        return GetBangumiStreamMetaResponse.model_validate(data)

    @classmethod
    def get_cheese_info(
        cls,
        ssid: Optional[int] = None,
        epid: Optional[int] = None,
        session_data: Optional[str] = None
    ) -> Response:
        """
        only need one of cheese's ssid or epid
        ssid is prior than epid if both exist

        and it is different from ssid and epid of bangumi
        """
        if all([id_value is None for id_value in (ssid, epid)]):
            raise

        session = requests.session()
        if session_data:
            session.cookies.set('SESSDATA', session_data)
        params = {}
        if ssid is not None:
            params.update({'season_id': ssid})
        else:
            params.update({'ep_id': epid})
        response = session.get(REQUEST_PUGV_INFO_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_cheese_info_data(
        cls,
        ssid: Optional[int] = None,
        epid: Optional[int] = None,
        session_data: Optional[str] = None
    ) -> GetCheeseDetailResponse:
        response = cls.get_cheese_info(ssid, epid , session_data)
        data = json.loads(response.content.decode('utf-8'))
        return GetCheeseDetailResponse.model_validate(data)

    @classmethod
    def get_cheese_stream_meta(
        cls,
        aid: int,
        epid: int,
        cid: int,
        session_data: Optional[str] = None
    ) -> Response:
        session = requests.session()
        if session_data:
            session.cookies.set('SESSDATA', session_data)
        params = {
            'avid': aid,
            'ep_id': epid,
            'cid': cid,
            'fnval': VIDEO_FORMAT_DASH
        }
        response = session.get(REQUEST_PUGV_STREAM_META_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        return response

    @classmethod
    def get_cheese_stream_meta_data(
        cls,
        aid: int,
        epid: int,
        cid: int,
        session_data: Optional[str] = None
    ) -> GetCheeseStreamMetaResponse:
        response = cls.get_cheese_stream_meta(aid, epid, cid, session_data)
        data = json.loads(response.content.decode('utf-8'))
        return GetCheeseStreamMetaResponse.model_validate(data)
