"""
Components on Bilibili videos
"""
from enum import Enum
import re
from typing import Optional

from .proxy import (
    GetBangumiDetailResponse,
    GetVideoInfoResponse,
    ProxyService
)


class VideoType(Enum):

    VIDEO = 'video'
    BANGUMI = 'bangumi'


BVID_LENGTH = 9
VIDEO_URL_BV_PATTERN = re.compile(fr'/video/(BV1[a-zA-Z0-9]{{{BVID_LENGTH}}})')
VIDEO_URL_AV_PATTERN = re.compile(r'/video/av(\d+)')
VIDEO_URL_EP_PATTERN_STRING = r'/play/ep(\d+)'
VIDEO_URL_EP_PATTERN = re.compile(VIDEO_URL_EP_PATTERN_STRING)
VIDEO_URL_BANGUMI_EP_PATTERN = re.compile(r'/bangumi' + VIDEO_URL_EP_PATTERN_STRING)


VIDEO_TYPE_MAPPING = {
    VIDEO_URL_BV_PATTERN: VideoType.VIDEO,
    VIDEO_URL_AV_PATTERN: VideoType.VIDEO,
    VIDEO_URL_BANGUMI_EP_PATTERN: VideoType.BANGUMI
}


GET_VIDEO_INFO_FUNC_TEMPLATE = '_get_{video_type}_video_info'


class VideoService:

    @classmethod
    def get_video_type(cls, url: str):
        for pattern, video_type in VIDEO_TYPE_MAPPING.items():
            search_result = pattern.search(url)
            if search_result:
                return video_type
        return None

    @classmethod
    def get_bvid(cls, url: str) -> Optional[str]:
        search_result = VIDEO_URL_BV_PATTERN.search(url)
        if search_result is None:
            return None
        return search_result.group(1)

    @classmethod
    def get_aid(cls, url: str) -> Optional[int]:
        search_result = VIDEO_URL_AV_PATTERN.search(url)
        if search_result is None:
            return None
        return int(search_result.group(1))

    @classmethod
    def get_epid(cls, url: str) -> Optional[int]:
        search_result = VIDEO_URL_EP_PATTERN.search(url)
        if search_result is None:
            return None
        return int(search_result.group(1))

    @classmethod
    def get_video_info(cls, url: str, session_data: Optional[str] = None) -> GetVideoInfoResponse:
        video_type = cls.get_video_type(url)
        if video_type is None:
            raise

        func = getattr(cls, GET_VIDEO_INFO_FUNC_TEMPLATE.format(video_type=video_type.name.lower()))
        return func(url, session_data)

    @classmethod
    def _get_video_video_info(
        cls, url: str,
        session_data: Optional[str] = None
    ) -> GetVideoInfoResponse:
        params = {}
        aid = cls.get_aid(url)
        if aid is None:
            bvid = cls.get_bvid(url)
            params.update({'bvid': bvid})
        else:
            params.update({'aid': aid})
        video_info_response_dm = ProxyService.get_video_info_data(session_data=session_data, **params)
        return video_info_response_dm

    @classmethod
    def _get_bangumi_video_info(
        cls,
        url: str,
        session_data: Optional[str] = None
    ) -> GetBangumiDetailResponse:
        params = {}
        epid = cls.get_epid(url)
        params.update({'epid': epid})
        bangumi_response_dm = ProxyService.get_bangumi_info_data(session_data=session_data, **params)
        return bangumi_response_dm
