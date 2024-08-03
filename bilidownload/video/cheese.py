"""
Component on Cheese video
"""
from typing import List, Optional

from .base import AbstractVideoComponent, register_component
from .constants import (
    DEFAULT_STAFF_TITLE,
    UNIT_CHUNK,
    VideoType,
    VideoFormatNumber,
    VideoQualityNumber
)
from .schemes import (
    VideoFormatItemData,
    VideoMetaModel,
    VideoMetaStaffItem,
    VideoPageLiteItemData
)
from ..proxy import (
    GetCheeseDetailResponse,
    GetCheeseStreamMetaResponse,
    PUGV_AVAILABLE_EPISODE_STATUS_CODE,
    ProxyService
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
    def get_video_stream_meta(
        cls,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        epid: Optional[int] = None,
        qn: int = VideoQualityNumber.P480.value,
        fnval: int = VideoFormatNumber.DASH.value,
        session_data: Optional[str] = None,
    ) -> GetCheeseStreamMetaResponse:
        if any([item is None for item in (aid, epid)]):
            raise
        params = {
            'aid': aid,
            'epid': epid,
            'cid': cid
        }
        params.update({
            'qn': qn,
            'fnval': fnval
        })
        res_dm = ProxyService.get_cheese_stream_meta_data(session_data=session_data, **params)
        return res_dm

    @classmethod
    def _parse_work_formats(
        cls,
        dm: GetCheeseStreamMetaResponse
    ) -> List[VideoFormatItemData]:
        work_formats = dm.data.support_formats
        return [
            VideoFormatItemData(
                quality=item.quality,
                new_description=item.new_description,
                is_login_needed=VideoQualityNumber.from_value(item.quality).is_login_needed,
                is_vip_needed=VideoQualityNumber.from_value(item.quality).is_vip_needed
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
                duration=item.duration,
                video_type=VideoType.CHEESE.name.lower()
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
        video_stream_meta = cls.get_video_stream_meta(
            cid=sample_episode.cid,
            aid=sample_episode.aid,
            epid=sample_episode.id_field
        )
        return VideoMetaModel(
            work_cover_url=video_info.data.cover,
            work_description=video_info.data.subtitle,
            work_url=url,
            work_staff=cls._parse_work_staff(video_info),
            work_title=video_info.data.title,
            work_formats=cls._parse_work_formats(video_stream_meta),
            work_pages=cls._parse_work_pages(video_info),
            work_has_hires_audio=True if video_stream_meta.data.dash.flac is not None else False
        )

    @classmethod
    def download_data(
        cls,
        location_path: str,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        epid: Optional[int] = None,
        title: str = '',
        qn: int = VideoQualityNumber.P480.value,
        is_dolby_audio: bool = False,
        session_data: Optional[str] = None
    ) -> None:
        video_stream_meta = cls.get_video_stream_meta(
            cid=cid,
            bvid=bvid,
            aid=aid,
            epid=epid,
            qn=qn,
            fnval=VideoFormatNumber.get_format(qn, is_dolby_audio),
            session_data=session_data
        )
        with open(location_path + title, 'wb') as f:
            for item in video_stream_meta.data.dash.video:
                with ProxyService.get_video_stream_response(item.base_url) as response:
                    for chunk in response.iter_content(chunk_size=UNIT_CHUNK):
                        f.write(chunk)
