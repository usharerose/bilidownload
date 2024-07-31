"""
Component on Bangumi video
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
    VideoMetaModel,
    VideoMetaStaffItem,
    VideoPageLiteItemData
)
from ..proxy import (
    GetBangumiDetailResponse,
    GetBangumiStreamMetaResponse,
    PGC_AVAILABLE_EPISODE_STATUS_CODE,
    ProxyService,
    VideoStreamMetaLiteSupportFormatItemData
)


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
    def get_video_stream_meta(
        cls,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        epid: Optional[int] = None,
        qn: int = VideoQualityNumber.P480.value,
        fnval: int = VideoFormatNumber.DASH.value,
        session_data: Optional[str] = None,
    ) -> GetBangumiStreamMetaResponse:
        params = {'epid': epid}
        params.update({
            'qn': qn,
            'fnval': fnval
        })
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
                duration=None,
                video_type=VideoType.BANGUMI.name.lower()
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
                        duration=episode.duration // 1000,  # source's unit is millisecond
                        video_type=VideoType.BANGUMI.name.lower()
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

        video_stream_meta = cls.get_video_stream_meta(
            cid=sample_episode.cid,
            bvid=sample_episode.bvid,
            aid=sample_episode.aid,
            session_data=session_data
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
            for durl_item in video_stream_meta.result.durl:
                with ProxyService.get_video_stream_response(durl_item.url) as response:
                    for chunk in response.iter_content(chunk_size=UNIT_CHUNK):
                        f.write(chunk)
