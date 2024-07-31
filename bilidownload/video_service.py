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
    GetCheeseStreamMetaResponse,
    GetVideoInfoResponse,
    GetVideoStreamMetaResponse,
    ProxyService,
    PGC_AVAILABLE_EPISODE_STATUS_CODE,
    PUGV_AVAILABLE_EPISODE_STATUS_CODE,
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


UNIT_CHUNK = 8192


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
    badge_text: str
    is_available: bool
    duration: Optional[int]     # unit is second


class VideoMetaModel(BaseModel):

    work_cover_url: str
    work_description: str
    work_url: str
    work_staff: List[VideoMetaStaffItem]
    work_title: str
    work_pages: List[VideoPageLiteItemData]
    work_formats: List[VideoStreamMetaLiteSupportFormatItemData]


REGISTERED_TYPE_VIDEO_COMPONENT = {}


class AbstractVideoComponent(ABC):

    @classmethod
    @abstractmethod
    def get_video_meta(cls, url: str, session_data: Optional[str] = None) -> VideoMetaModel:
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


def register_component(video_type: VideoType):

    def decorator(klass):
        if video_type in REGISTERED_TYPE_VIDEO_COMPONENT:
            raise
        REGISTERED_TYPE_VIDEO_COMPONENT[video_type] = klass
        return klass

    return decorator


@register_component(VideoType.VIDEO)
class CommonVideoComponent(AbstractVideoComponent):

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
                title=item.part,
                badge_text='',
                is_available=True,
                duration=item.duration
            ) for item in pages
        ]

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

    @classmethod
    def download_data(
        cls,
        location_path: str,
        cid: int,
        aid: Optional[str] = None,
        bvid: Optional[str] = None,
        title: str = '',
        session_data: Optional[str] = None
    ):
        video_stream_meta = cls._get_video_stream_meta(
            cid,
            bvid,
            aid,
            session_data
        )
        with open(location_path + title, 'wb') as f:
            for durl_item in video_stream_meta.data.durl:
                with ProxyService.get_video_stream_response(durl_item.url) as response:
                    for chunk in response.iter_content(chunk_size=UNIT_CHUNK):
                        f.write(chunk)


@register_component(VideoType.BANGUMI)
class BangumiVideoComponent(AbstractVideoComponent):

    @classmethod
    def _format_video_page_title(cls, title: str, long_title: str) -> str:
        if all([title, long_title]):
            return f'{title} {long_title}'
        return title if title else long_title

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
        result = [
            VideoPageLiteItemData(
                aid=item.aid,
                bvid=item.bvid,
                epid=item.id_field,
                cid=item.cid,
                title=cls._format_video_page_title(item.title, item.long_title),
                badge_text=item.badge_info.text,
                is_available=True if item.status == PGC_AVAILABLE_EPISODE_STATUS_CODE else False,
                duration=None
            ) for item in pages
        ]

        section = dm.result.section or []
        for sec_item in section:
            for episode in sec_item.episodes:
                result.append(
                    VideoPageLiteItemData(
                        aid=episode.aid,
                        bvid=episode.bvid,
                        epid=episode.ep_id,
                        cid=episode.cid,
                        title=cls._format_video_page_title(episode.title, episode.long_title),
                        badge_text=episode.badge_info.text,
                        is_available=True if episode.status == 2 else False,
                        duration=episode.duration // 1000  # source's unit is millisecond
                    )
                )
        return result

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


@register_component(VideoType.CHEESE)
class CheeseVideoComponent(AbstractVideoComponent):

    @classmethod
    def _get_video_info(
        cls,
        url: str,
        session_data: Optional[str] = None
    ) -> GetCheeseDetailResponse:
        params = {}
        ssid = cls._get_ssid(url)
        if ssid is None:
            epid = cls._get_epid(url)
            params.update({'epid': epid})
        else:
            params.update({'ssid': ssid})
        res_dm = ProxyService.get_cheese_info_data(session_data=session_data, **params)
        return res_dm

    @classmethod
    def _get_video_stream_meta(
        cls,
        aid: int,
        epid: int,
        cid: int,
        session_data: Optional[str] = None
    ) -> GetCheeseStreamMetaResponse:
        params = {
            'aid': aid,
            'epid': epid,
            'cid': cid
        }
        res_dm = ProxyService.get_cheese_stream_meta_data(session_data=session_data, **params)
        return res_dm

    @classmethod
    def _parse_work_formats(
        cls,
        dm: GetCheeseStreamMetaResponse
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
        dm: GetCheeseDetailResponse
    ) -> List[VideoPageLiteItemData]:
        pages = dm.data.episodes
        return [
            VideoPageLiteItemData(
                aid=item.aid,
                epid=item.id_field,
                cid=item.cid,
                title=item.title,
                badge_text='',
                is_available=True if item.status == PUGV_AVAILABLE_EPISODE_STATUS_CODE else False,
                duration=item.duration
            ) for item in pages
        ]

    @classmethod
    def _parse_work_staff(
        cls,
        dm: GetCheeseDetailResponse
    ) -> List[VideoMetaStaffItem]:
        work_staff = [dm.data.up_info]
        return [
            VideoMetaStaffItem(
                avatar_url=item.avatar,
                mid=item.mid,
                name=item.uname,
                title=DEFAULT_STAFF_TITLE
            ) for item in work_staff
        ]

    @classmethod
    def get_video_meta(
        cls,
        url: str,
        session_data: Optional[str] = None
    ) -> VideoMetaModel:
        video_info = cls._get_video_info(url, session_data)
        sample_episode, *_ = video_info.data.episodes
        video_stream_meta = cls._get_video_stream_meta(
            sample_episode.aid,
            sample_episode.id_field,
            sample_episode.cid
        )
        return VideoMetaModel(
            work_cover_url=video_info.data.cover,
            work_description=video_info.data.subtitle,
            work_url=url,
            work_staff=cls._parse_work_staff(video_info),
            work_title=video_info.data.title,
            work_formats=cls._parse_work_formats(video_stream_meta),
            work_pages=cls._parse_work_pages(video_info)
        )


class VideoService:

    @classmethod
    def _get_video_type(cls, url: str):
        for pattern, video_type in VIDEO_TYPE_MAPPING.items():
            search_result = pattern.search(url)
            if search_result:
                return video_type
        return None

    @classmethod
    def get_video_meta(
        cls,
        url: str,
        session_data: Optional[str] = None
    ) -> VideoMetaModel:
        video_type = cls._get_video_type(url)
        if video_type is None:
            raise
        parser_kls = REGISTERED_TYPE_VIDEO_COMPONENT[video_type]
        return parser_kls.get_video_meta(url, session_data)
