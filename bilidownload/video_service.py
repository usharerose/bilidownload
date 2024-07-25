"""
Components on Bilibili videos
"""
import re
from typing import Optional

from .proxy import GetVideoInfoResponse, ProxyService


BVID_LENGTH = 9
VIDEO_URL_PATTERN = re.compile(fr'/video/(BV1[a-zA-Z0-9]{{{BVID_LENGTH}}})/')


class VideoService:

    @classmethod
    def is_valid_video_src(cls, url: str) -> bool:
        search_result = VIDEO_URL_PATTERN.search(url)
        if not search_result:
            return False
        return True

    @classmethod
    def get_bvid(cls, url: str) -> str:
        search_result = VIDEO_URL_PATTERN.search(url)
        return search_result.group(1)

    @classmethod
    def get_video_info(cls, url: str, session_data: Optional[str] = None) -> GetVideoInfoResponse:
        try:
            bvid = cls.get_bvid(url)
        except AttributeError:
            raise
        video_info_response_dm = ProxyService.get_video_info_data(bvid, session_data)
        return video_info_response_dm
