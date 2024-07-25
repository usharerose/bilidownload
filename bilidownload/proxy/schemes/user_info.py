"""
Response models of user info related Bilibili API requests
"""
from typing import List, Optional

from pydantic import BaseModel, Field

from .base import (
    BaseResponseWithTTLModel,
    UserOfficialInfoData,
    UserOfficialVerifyData
)


__all__ = [
    'GetUserInfoNotLoginData',
    'GetUserInfoLoginData',
    'GetUserInfoNotLoginResponse',
    'GetUserInfoLoginResponse'
]


class UserLevelInfoData(BaseModel):

    current_level: int  # User level, 0 ~ 6
    current_min: int    # minimum experience value of current level
    current_exp: int    # experience value
    next_exp: int       # minimum experience value of next level


class ColorItemData(BaseModel):

    color_day: str    # hex color code when day mode
    color_night: str  # hex color code when night mode


class ColorsInfoData(BaseModel):

    color: List[ColorItemData]
    color_ids: List[str]        # ["6"]


class UserNameRenderInfoData(BaseModel):

    colors_info: ColorsInfoData
    render_scheme: str           # "Default" or "Colorful"


class UserPendantData(BaseModel):

    pid: int = 0                   # Identifier of pendant
    name: str = ''                 # Name of pendant
    image: str = ''                # URL of pendant image
    expire: int = 0                # Unix timestamp when pendant expired
    image_enhance: str = ''
    image_enhance_frame: str = ''
    n_pid: int = 0


class VipLabelInfoData(BaseModel):

    bg_color: str                    # hex code
    bg_style: int
    border_color: str
    img_label_uri_hans: str          # URL of VIP hans label gif
    img_label_uri_hans_static: str   # URL of VIP hans label png
    img_label_uri_hant: str          # URL of VIP hant label gif
    img_label_uri_hant_static: str   # URL of VIP hant label png
    label_theme: str
    path: str
    text: str
    text_color: str                  # hex code
    use_img_label: bool


class NavVipInfoData(BaseModel):

    avatar_icon: dict
    avatar_subscript: int
    avatar_subscript_url: str = ''
    due_date: int                   # Unix timestamp when VIP expired
    label: VipLabelInfoData
    nickname_color: str             # hex code
    role: int                       # 1：Monthly VIP; 3：Yearly VIP; 7：Decade VIP; 15: Century VIP
    status: int                     # 0: No VIP; 1: Has VIP
    theme_type: int
    tv_due_date: int                # Unix timestamp when TV VIP expired
    tv_vip_pay_type: int            # 0 is TV VIP unpaid, 1 is paid
    tv_vip_status: int              # 0 has no TV VIP, 1 has TV VIP
    vip_type: int = Field(..., alias='type')  # 0: No VIP; 1：Monthly VIP; 2: Yearly or superior VIP
    vip_pay_type: int               # 0 is VIP unpaid, 1 is paid


class UserWalletInfoData(BaseModel):

    mid: int              # User ID
    bcoin_balance: int    # Amount of B coins
    coupon_balance: int   # Monthly B coins coupon
    coupon_due_time: int  # Unix timestamp when B coins coupon expired


class UserWbiImageInfoData(BaseModel):

    img_url: str  # Wbi signed parameter 'imgKey'
    sub_url: str  # Wbi signed parameter 'subKey'


class GetUserInfoNotLoginData(BaseModel):

    isLogin: bool              # True when login, else False
    wbi_img: UserWbiImageInfoData


class GetUserInfoLoginData(GetUserInfoNotLoginData):

    allowance_count: int
    answer_status: int
    email_verified: int                            # 1 as true and 0 as false
    face: str                                      # Profile icon's source URL
    face_nft: int                                  # 1 as NFT profile icon, 0 as non-NFT
    face_nft_type: int
    has_shop: bool                                 # True when has promoted goods, else False
    is_jury: bool                                  # Whether the user is jury or not
    is_senior_member: int                          # 1 as senior member, else 0
    level_info: UserLevelInfoData
    mid: int                                       # User ID
    mobile_verified: int                           # 1 as true and 0 as false
    money: int                                     # Amount of money/coins
    moral: int                                     # Value of moral, maximum is 70
    name_render: Optional[UserNameRenderInfoData]
    official: UserOfficialInfoData
    officialVerify: UserOfficialVerifyData
    pendant: UserPendantData
    scores: int = 0
    shop_url: str = ""                             # URL of promoted goods
    uname: str                                     # User name
    vip: NavVipInfoData
    vipDueDate: int                                # Unix timestamp when VIP expired
    vipStatus: int                                 # 0: No VIP; 1: Has VIP
    vipType: int                                   # 0: No VIP; 1：Monthly VIP; 2: Yearly or superior VIP
    vip_avatar_subscript: int
    vip_label: VipLabelInfoData
    vip_nickname_color: str                        # hex code
    vip_pay_type: int                              # 0 is VIP unpaid, 1 is paid
    vip_theme_type: int
    wallet: UserWalletInfoData


class GetUserInfoLoginResponse(BaseResponseWithTTLModel):

    data: GetUserInfoLoginData


class GetUserInfoNotLoginResponse(BaseResponseWithTTLModel):

    data: GetUserInfoNotLoginData
