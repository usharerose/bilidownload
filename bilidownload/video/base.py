"""
Base of Video component
"""
from abc import ABC, abstractmethod
from typing import Optional, TypeVar

from .constants import (
    VideoType,
    VideoQualityNumber,
    VideoFormatNumber,
    VIDEO_URL_AV_PATTERN,
    VIDEO_URL_BV_PATTERN,
    VIDEO_URL_EP_PATTERN,
    VIDEO_URL_SS_PATTERN
)
from .schemes import VideoMetaModel
from ..constants import ModelType


__all__ = [
    'AbstractVideoComponent',
    'register_component',
    'REGISTERED_TYPE_VIDEO_COMPONENT',
    'VideoComponentType'
]


class AbstractVideoComponent(ABC):

    @classmethod
    @abstractmethod
    def get_video_meta(
        cls,
        url: str,
        session_data: Optional[str] = None
    ) -> VideoMetaModel:
        """
        get video's meta, including cover, link, staff, pages, etc
        """
        pass

    @classmethod
    @abstractmethod
    def get_video_stream_meta(
        cls,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        epid: Optional[int] = None,
        qn: int = VideoQualityNumber.P480.value,
        fnval: int = VideoFormatNumber.DASH.value,
        session_data: Optional[str] = None,
    ) -> ModelType:
        """
        get video's stream meta, including source url
        """
        pass

    @classmethod
    @abstractmethod
    def download_data(
        cls,
        location_path: str,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        epid: Optional[int] = None,
        title: str = '',
        qn: int = VideoQualityNumber.P480.value,
        is_hires_audio: bool = False,
        session_data: Optional[str] = None
    ) -> None:
        """
        Download data from remote source
        """
        pass

    @classmethod
    def _get_bvid(cls, url: str) -> Optional[str]:
        search_result = VIDEO_URL_BV_PATTERN.search(url)
        if search_result is None:
            return None
        return search_result.group(1)

    @classmethod
    def _get_aid(cls, url: str) -> Optional[int]:
        search_result = VIDEO_URL_AV_PATTERN.search(url)
        if search_result is None:
            return None
        return int(search_result.group(1))

    @classmethod
    def _get_epid(cls, url: str) -> Optional[int]:
        search_result = VIDEO_URL_EP_PATTERN.search(url)
        if search_result is None:
            return None
        return int(search_result.group(1))

    @classmethod
    def _get_ssid(cls, url: str) -> Optional[int]:
        search_result = VIDEO_URL_SS_PATTERN.search(url)
        if search_result is None:
            return None
        return int(search_result.group(1))


VideoComponentType = TypeVar('VideoComponentType', bound=AbstractVideoComponent)


REGISTERED_TYPE_VIDEO_COMPONENT = {}


def register_component(video_type: VideoType):

    def decorator(klass):
        video_type_name = video_type.name.lower()
        if video_type_name in REGISTERED_TYPE_VIDEO_COMPONENT:
            raise
        REGISTERED_TYPE_VIDEO_COMPONENT[video_type_name] = klass
        return klass

    return decorator
