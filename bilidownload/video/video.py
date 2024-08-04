"""
Component on common video
"""
import os
from typing import List, Optional

from .base import AbstractVideoComponent, register_component
from .constants import (
    DEFAULT_STAFF_TITLE,
    UNIT_CHUNK,
    RAW_FILE_EXT,
    VideoType,
    VideoQualityNumber,
    VideoFormatNumber
)
from .schemes import (
    VideoFormatItemData,
    VideoMetaModel,
    VideoMetaStaffItem,
    VideoPageLiteItemData
)
from ..proxy import (
    GetVideoInfoResponse,
    GetVideoStreamMetaResponse,
    ProxyService
)


@register_component(VideoType.VIDEO)
class CommonVideoComponent(AbstractVideoComponent):

    @classmethod
    def _get_video_info(
        cls,
        url: str,
        session_data: Optional[str] = None
    ) -> GetVideoInfoResponse:
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
    def get_video_stream_meta(
        cls,
        cid: int,
        bvid: Optional[str] = None,
        aid: Optional[int] = None,
        epid: Optional[int] = None,
        qn: int = VideoQualityNumber.P480.value,
        fnval: int = VideoFormatNumber.DASH.value,
        session_data: Optional[str] = None,
    ) -> GetVideoStreamMetaResponse:
        params = {}
        if aid is None:
            params.update({'bvid': bvid})
        else:
            params.update({'aid': aid})
        params.update({'cid': cid})

        params.update({
            'qn': qn,
            'fnval': fnval
        })

        res_dm = ProxyService.get_video_stream_meta_data(session_data=session_data, **params)
        return res_dm

    @classmethod
    def _parse_work_formats(
        cls,
        dm: GetVideoStreamMetaResponse
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
                duration=item.duration,
                video_type=VideoType.VIDEO.name.lower()
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
        video_stream_meta = cls.get_video_stream_meta(
            cid=video_info.data.cid,
            bvid=video_info.data.bvid,
            aid=video_info.data.aid,
            session_data=session_data
        )
        return VideoMetaModel(
            work_cover_url=video_info.data.pic,
            work_description=video_info.data.desc,
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
        is_hires_audio: bool = False,
        session_data: Optional[str] = None
    ) -> None:
        video_stream_meta = cls.get_video_stream_meta(
            cid=cid,
            bvid=bvid,
            aid=aid,
            epid=epid,
            qn=qn,
            fnval=VideoFormatNumber.get_format(qn, True),
            session_data=session_data
        )

        video_stocks = [item for item in video_stream_meta.data.dash.video if item.id_field <= qn]
        if not video_stocks:
            video_stocks = [video_stream_meta.data.dash.video[0]]
        video_src, *_ = video_stocks
        video_file_path = os.path.join(location_path, f'{title}_video{RAW_FILE_EXT}')
        with open(video_file_path, 'wb') as f:
            with ProxyService.get_video_stream_response(video_src.base_url) as response:
                for chunk in response.iter_content(chunk_size=UNIT_CHUNK):
                    f.write(chunk)

        if is_hires_audio:
            audio_src = video_stream_meta.data.dash.flac.audio
        else:
            dolby_audios = video_stream_meta.data.dash.dolby.audio
            if dolby_audios:
                audio_src, *_ = dolby_audios
            else:
                audio_src, *_ = video_stream_meta.data.dash.audio
        audio_file_path = os.path.join(location_path, f'{title}_audio{RAW_FILE_EXT}')
        with open(audio_file_path, 'wb') as f:
            with ProxyService.get_video_stream_response(audio_src.base_url) as response:
                for chunk in response.iter_content(chunk_size=UNIT_CHUNK):
                    f.write(chunk)
