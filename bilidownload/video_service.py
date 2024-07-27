"""
Components on Bilibili videos
"""
from abc import ABC, abstractmethod
from enum import Enum
import re
from typing import List, Optional

from pydantic import BaseModel

from .proxy import (
    GetBangumiDetailResponse,
    GetBangumiStreamMetaResponse,
    GetCheeseDetailResponse,
    GetVideoInfoResponse,
    GetVideoStreamMetaResponse,
    ProxyService,
    VideoStreamMetaLiteSupportFormatItemData
)


class VideoType(Enum):

    VIDEO = 'video'
    BANGUMI = 'bangumi'
    CHEESE = 'cheese'


BVID_LENGTH = 9
VIDEO_URL_BV_PATTERN = re.compile(fr'/video/(BV1[a-zA-Z0-9]{{{BVID_LENGTH}}})')
VIDEO_URL_AV_PATTERN = re.compile(r'/video/av(\d+)')
VIDEO_URL_EP_PATTERN_STRING = r'/play/ep(\d+)'
VIDEO_URL_EP_PATTERN = re.compile(VIDEO_URL_EP_PATTERN_STRING)
VIDEO_URL_SS_PATTERN_STRING = r'/play/ss(\d+)'
VIDEO_URL_SS_PATTERN = re.compile(VIDEO_URL_SS_PATTERN_STRING)
VIDEO_URL_BANGUMI_PREFIX = '/bangumi'
VIDEO_URL_BANGUMI_EP_PATTERN = re.compile(VIDEO_URL_BANGUMI_PREFIX + VIDEO_URL_EP_PATTERN_STRING)
VIDEO_URL_BANGUMI_SS_PATTERN = re.compile(VIDEO_URL_BANGUMI_PREFIX + VIDEO_URL_SS_PATTERN_STRING)
VIDEO_URL_CHEESE_PREFIX = '/cheese'
VIDEO_URL_CHEESE_EP_PATTERN = re.compile(VIDEO_URL_CHEESE_PREFIX + VIDEO_URL_EP_PATTERN_STRING)
VIDEO_URL_CHEESE_SS_PATTERN = re.compile(VIDEO_URL_CHEESE_PREFIX + VIDEO_URL_SS_PATTERN_STRING)


VIDEO_TYPE_MAPPING = {
    VIDEO_URL_BV_PATTERN: VideoType.VIDEO,
    VIDEO_URL_AV_PATTERN: VideoType.VIDEO,
    VIDEO_URL_BANGUMI_EP_PATTERN: VideoType.BANGUMI,
    VIDEO_URL_BANGUMI_SS_PATTERN: VideoType.BANGUMI,
    VIDEO_URL_CHEESE_EP_PATTERN: VideoType.CHEESE,
    VIDEO_URL_CHEESE_SS_PATTERN: VideoType.CHEESE
}


DEFAULT_STAFF_TITLE = 'UP主'


GET_VIDEO_INFO_FUNC_TEMPLATE = '_get_{video_type}_video_info'


class VideoMetaStaffItem(BaseModel):

    avatar_url: str  # Profile icon's source URL
    mid: int         # Identifier of user
    name: str        # Nickname of user
    title: str       # Name of user


class VideoPageLiteItemData(BaseModel):

    aid: Optional[int] = None
    bvid: Optional[str] = None
    epid: Optional[int] = None
    cid: int                    # cid of this page
    title: str                  # Title of this page


class VideoMetaModel(BaseModel):

    work_cover_url: str
    work_description: str
    work_url: str
    work_staff: List[VideoMetaStaffItem]
    work_title: str
    work_pages: List[VideoPageLiteItemData]


REGISTERED_TYPE_VIDEO_META_PARSER = {}


class AbstractVideoMetaParser(ABC):

    @classmethod
    @abstractmethod
    def get_video_meta(cls, url: str, session_data: Optional[str] = None) -> VideoMetaModel:
        pass


def register_parser(video_type: VideoType):

    def decorator(klass):
        if video_type in REGISTERED_TYPE_VIDEO_META_PARSER:
            raise
        REGISTERED_TYPE_VIDEO_META_PARSER[video_type] = klass
        return klass

    return decorator


@register_parser(VideoType.VIDEO)
class CommonVideoMetaParser(AbstractVideoMetaParser):

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
    def _parse_work_staff(cls, dm: GetVideoInfoResponse) -> List[VideoMetaStaffItem]:
        work_staff = dm.data.staff
        if work_staff is None:
            work_staff = [dm.data.owner]
        return [
            VideoMetaStaffItem(
                avatar_url=item.face,
                mid=item.mid,
                name=item.name,
                title=item.title if hasattr(item, 'title') else DEFAULT_STAFF_TITLE
            ) for item in work_staff
        ]

    @classmethod
    def _get_video_info(cls, url: str, session_data: Optional[str] = None) -> GetVideoInfoResponse:
        params = {}
        aid = cls._get_aid(url)
        if aid is None:
            bvid = cls._get_bvid(url)
            params.update({'bvid': bvid})
        else:
            params.update({'aid': aid})
        res_dm = ProxyService.get_video_info_data(session_data=session_data, **params)
        return res_dm

    @classmethod
    def _get_video_stream_meta(
        cls,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        session_data: Optional[str] = None
    ) -> GetVideoStreamMetaResponse:
        params = {}
        if aid is None:
            params.update({'bvid': bvid})
        else:
            params.update({'aid': aid})
        params.update({'cid': cid})
        res_dm = ProxyService.get_video_stream_meta_data(session_data=session_data, **params)
        return res_dm

    @classmethod
    def _parse_work_formats(
        cls,
        dm: GetVideoStreamMetaResponse
    ) -> List[VideoStreamMetaLiteSupportFormatItemData]:
        work_formats = dm.data.support_formats
        return [
            VideoStreamMetaLiteSupportFormatItemData(
                quality=item.quality,
                new_description=item.new_description
            ) for item in work_formats
        ]

    @classmethod
    def _parse_work_pages(
        cls,
        dm: GetVideoInfoResponse
    ) -> List[VideoPageLiteItemData]:
        pages = dm.data.pages
        return [
            VideoPageLiteItemData(
                aid=dm.data.aid,
                bvid=dm.data.bvid,
                cid=item.cid,
                title=item.part
            ) for item in pages
        ]

    @classmethod
    def get_video_meta(cls, url: str, session_data: Optional[str] = None) -> VideoMetaModel:
        video_info = cls._get_video_info(url, session_data)
        video_stream_meta = cls._get_video_stream_meta(
            video_info.data.cid,
            video_info.data.bvid,
            video_info.data.aid,
            session_data
        )
        return VideoMetaModel(
            work_cover_url=video_info.data.pic,
            work_description=video_info.data.desc,
            work_url=url,
            work_staff=cls._parse_work_staff(video_info),
            work_title=video_info.data.title,
            work_formats=cls._parse_work_formats(video_stream_meta),
            work_pages=cls._parse_work_pages(video_info)
        )


@register_parser(VideoType.BANGUMI)
class BangumiVideoMetaParser(AbstractVideoMetaParser):

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

    @classmethod
    def _get_video_info(
        cls,
        url: str,
        session_data: Optional[str] = None
    ) -> GetBangumiDetailResponse:
        params = {}
        ssid = cls._get_ssid(url)
        if ssid is None:
            epid = cls._get_epid(url)
            params.update({'epid': epid})
        else:
            params.update({'ssid': ssid})
        res_dm = ProxyService.get_bangumi_info_data(session_data=session_data, **params)
        return res_dm

    @classmethod
    def _get_video_stream_meta(
        cls,
        epid: int,
        session_data: Optional[str] = None
    ) -> GetBangumiStreamMetaResponse:
        params = {'epid': epid}
        res_dm = ProxyService.get_bangumi_stream_meta_data(session_data=session_data, **params)
        return res_dm

    @classmethod
    def _parse_work_staff(
        cls,
        dm: GetBangumiDetailResponse
    ) -> List[VideoMetaStaffItem]:
        work_staff = [dm.result.up_info]
        return [
            VideoMetaStaffItem(
                avatar_url=item.avatar,
                mid=item.mid,
                name=item.uname,
                title=DEFAULT_STAFF_TITLE
            ) for item in work_staff
        ]

    @classmethod
    def _parse_work_formats(
        cls,
        dm: GetBangumiStreamMetaResponse
    ) -> List[VideoStreamMetaLiteSupportFormatItemData]:
        work_formats = dm.result.support_formats
        return [
            VideoStreamMetaLiteSupportFormatItemData(
                quality=item.quality,
                new_description=item.new_description
            ) for item in work_formats
        ]

    @classmethod
    def _parse_work_pages(
        cls,
        dm: GetBangumiDetailResponse
    ) -> List[VideoPageLiteItemData]:
        pages = dm.result.episodes
        return [
            VideoPageLiteItemData(
                aid=item.aid,
                bvid=item.bvid,
                epid=item.id_field,
                cid=item.cid,
                title=item.long_title
            ) for item in pages
        ]

    @classmethod
    def get_video_meta(cls, url: str, session_data: Optional[str] = None) -> VideoMetaModel:
        video_info = cls._get_video_info(url, session_data)
        sample_episode, *_ = video_info.result.episodes

        video_stream_meta = cls._get_video_stream_meta(
            sample_episode.id_field,
            session_data
        )
        return VideoMetaModel(
            work_cover_url=video_info.result.cover,
            work_description=video_info.result.evaluate,
            work_url=url,
            work_staff=cls._parse_work_staff(video_info),
            work_title=video_info.result.title,
            work_formats=cls._parse_work_formats(video_stream_meta),
            work_pages=cls._parse_work_pages(video_info)
        )


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
    def get_ssid(cls, url: str) -> Optional[int]:
        search_result = VIDEO_URL_SS_PATTERN.search(url)
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
        ssid = cls.get_ssid(url)
        if ssid is None:
            epid = cls.get_epid(url)
            params.update({'epid': epid})
        else:
            params.update({'ssid': ssid})
        bangumi_response_dm = ProxyService.get_bangumi_info_data(session_data=session_data, **params)
        return bangumi_response_dm

    @classmethod
    def _get_cheese_video_info(
        cls,
        url: str,
        session_data: Optional[str] = None
    ) -> GetCheeseDetailResponse:
        params = {}
        ssid = cls.get_ssid(url)
        if ssid is None:
            epid = cls.get_epid(url)
            params.update({'epid': epid})
        else:
            params.update({'ssid': ssid})
        cheese_response_dm = ProxyService.get_cheese_info_data(session_data=session_data, **params)
        return cheese_response_dm
