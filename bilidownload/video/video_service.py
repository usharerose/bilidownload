"""
Components on Bilibili videos
"""
from typing import Optional, Type

from .base import REGISTERED_TYPE_VIDEO_COMPONENT, VideoComponentType
from .constants import VIDEO_TYPE_MAPPING, VideoQualityNumber
from .schemes import VideoMetaModel


class VideoService:

    @classmethod
    def _get_video_type(cls, url: str):
        for pattern, video_type in VIDEO_TYPE_MAPPING.items():
            search_result = pattern.search(url)
            if search_result:
                return video_type
        return None

    @classmethod
    def _get_video_component(
        cls,
        video_type_name: Optional[str] = None
    ) -> Type[VideoComponentType]:
        if video_type_name is None:
            raise
        return REGISTERED_TYPE_VIDEO_COMPONENT[video_type_name]

    @classmethod
    def get_video_meta(
        cls,
        url: str,
        session_data: Optional[str] = None
    ) -> VideoMetaModel:
        video_type = cls._get_video_type(url)
        component_kls = cls._get_video_component(video_type.name.lower())
        return component_kls.get_video_meta(url, session_data)

    @classmethod
    def download_data(
        cls,
        location_path: str,
        video_type_name: str,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        epid: Optional[int] = None,
        qn: int = VideoQualityNumber.P480.value,
        is_hires_audio: bool = False,
        title: str = '',
        session_data: Optional[str] = None
    ) -> None:
        component_kls = cls._get_video_component(video_type_name)
        component_kls.download_data(
            location_path=location_path,
            cid=cid,
            bvid=bvid,
            aid=aid,
            epid=epid,
            title=title,
            qn=qn,
            is_hires_audio=is_hires_audio,
            session_data=session_data
        )
