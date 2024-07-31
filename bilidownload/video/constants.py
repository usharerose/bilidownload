"""
Constants on Video
"""
from enum import Enum, IntEnum
from functools import reduce
import re
from typing import (
    Type,
    TypeVar
)


VideoQN = TypeVar('VideoQN', bound='VideoQualityNumber')


class VideoType(Enum):

    VIDEO = 'video'
    BANGUMI = 'bangumi'
    CHEESE = 'cheese'


class VideoQualityNumber(IntEnum):

    P240 = 6          # Only support MP4
    P360 = 16
    P480 = 32
    P720 = 64         # Web default, from this level, need login
    P720_60 = 74
    P1080 = 80        # from this level, need VIP
    PPLUS_1080 = 112
    P1080_60 = 116
    FOUR_K = 120
    HDR = 125
    DOLBY = 126
    EIGHT_K = 127

    @property
    def is_login_needed(self) -> bool:
        return self.value >= self.P720.value

    @property
    def is_vip_needed(self) -> bool:
        return self.value > self.P1080.value

    @classmethod
    def from_value(cls, qn: int) -> VideoQN:
        for item in cls:
            if item == qn:
                return item
        raise


class VideoFormatNumber(IntEnum):

    # FLV = 0  deprecated
    # MP4 = 1  not support in this project
    DASH = 16
    HDR = 64
    FOUR_K = 128
    DOLBY_AUDIO = 256
    DOLBY_VISION = 512
    EIGHT_K = 1024
    # AV1_ENCODE = 2048  not supported in this project

    @classmethod
    def full_format(cls) -> int:
        return reduce(lambda prev, cur: prev | cur, [item.value for item in cls])

    @classmethod
    def get_format(cls, qn: int, is_dolby_audio: bool = False) -> int:
        result = cls.DASH.value
        if qn == VideoFormatNumber.HDR:
            result = result | cls.HDR
        if qn >= VideoQualityNumber.FOUR_K:
            result = result | cls.FOUR_K
        if is_dolby_audio:
            result = result | cls.DOLBY_AUDIO
        if qn == VideoQualityNumber.DOLBY:
            result = result | cls.DOLBY_VISION
        if qn == VideoQualityNumber.EIGHT_K:
            result = result | cls.EIGHT_K
        return result


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
