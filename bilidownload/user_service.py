"""
Components on login Bilibili
"""
import base64
from collections import namedtuple
import copy
import json
from typing import List, Optional, Union
from urllib.parse import urlencode

from pydantic import BaseModel
import requests
import rsa


HEADERS = {
    'origin': 'https://www.bilibili.com',
    'referer': 'https://www.bilibili.com/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site'
}


REQUEST_WEB_CAPTCHA_URL = \
    'https://passport.bilibili.com/x/passport-login/captcha?source=main_web'
REQUEST_WEB_LOGIN_URL = 'https://passport.bilibili.com/x/passport-login/web/login'
REQUEST_WEB_PUBLIC_KEY_URL = \
    'https://passport.bilibili.com/x/passport-login/web/key'
REQUEST_WEB_SPI_URL = 'https://api.bilibili.com/x/frontend/finger/spi'
REQUEST_WEB_USER_INFO_URL = 'https://api.bilibili.com/x/web-interface/nav'


class LoginBaseModel(BaseModel):

    code: int = 0       # 0 is login, -101 is not login
    message: str = '0'
    ttl: int = 1


class GetWebCaptchaGeetestMeta(BaseModel):

    challenge: str
    gt: str


class GetWebCaptchaTencentMeta(BaseModel):

    appid: str


class GetWebCaptchaData(BaseModel):

    type: str = 'geetest'
    token: str
    geetest: GetWebCaptchaGeetestMeta
    tencent: GetWebCaptchaTencentMeta


class GetWebCaptchaResponse(LoginBaseModel):

    data: GetWebCaptchaData


class GetWebPublicKeyData(BaseModel):
    """
    hash: salt on login password
    key: rsa public key, used when encrypt login password
    """
    hash: str
    key: str


class GetWebPublicKeyResponse(LoginBaseModel):

    data: GetWebPublicKeyData


class GetWebSPIData(BaseModel):

    b_3: str
    b_4: str


class GetWebSPIResponse(BaseModel):

    code: int = 0
    data: GetWebSPIData
    message: str = 'ok'


class UserLevelInfo(BaseModel):

    current_level: int  # User level, 0 ~ 6
    current_min: int    # minimum experience value of current level
    current_exp: int    # experience value
    next_exp: int       # minimum experience value of next level


class ColorItem(BaseModel):

    color_day: str    # hex color code when day mode
    color_night: str  # hex color code when night mode


class ColorsInfo(BaseModel):

    color: List[ColorItem]
    color_ids: List[str]    # ["6"]


class UserNameRenderInfo(BaseModel):

    colors_info: ColorsInfo
    render_scheme: str  # "Default" or "Colorful"


class UserOfficialVerify(BaseModel):

    type: int       # -1 as unverified, 0 as verified
    desc: str = ''  # Verification description


class UserOfficialInfo(UserOfficialVerify):

    # 0: unverified
    # 1: personal verified, famous UP
    # 2: personal verified, V
    # 3: organization verified, enterprise
    # 4: organization verified, organization
    # 5: organization verified, media
    # 6: organization verified, government
    # 7: personal verified, Live show host
    # 9: personal verified, Social KOL
    role: int
    title: str  # Title of role


class UserPendant(BaseModel):

    pid: int = 0                   # Identifier of pendant
    name: str = ''                 # Name of pendant
    image: str = ''                # URL of pendant image
    expire: int = 0                # Unix timestamp when pendant expired
    image_enhance: str = ''
    image_enhance_frame: str = ''
    n_pid: int = 0


class VipLabelInfo(BaseModel):

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


class NavVipInfo(BaseModel):

    avatar_icon: dict
    avatar_subscript: int
    avatar_subscript_url: str = ''
    due_date: int                   # Unix timestamp when VIP expired
    label: VipLabelInfo
    nickname_color: str             # hex code
    role: int                       # 1：Monthly VIP; 3：Yearly VIP; 7：Decade VIP; 15: Century VIP
    status: int                     # 0: No VIP; 1: Has VIP
    theme_type: int
    tv_due_date: int                # Unix timestamp when TV VIP expired
    tv_vip_pay_type: int            # 0 is TV VIP unpaid, 1 is paid
    tv_vip_status: int              # 0 has no TV VIP, 1 has TV VIP
    type: int                       # 0: No VIP; 1：Monthly VIP; 2: Yearly or superior VIP
    vip_pay_type: int               # 0 is VIP unpaid, 1 is paid


class UserWalletInfo(BaseModel):

    mid: int              # User ID
    bcoin_balance: int    # Amount of B coins
    coupon_balance: int   # Monthly B coins coupon
    coupon_due_time: int  # Unix timestamp when B coins coupon expired


class UserWbiImageInfo(BaseModel):

    img_url: str  # Wbi signed parameter 'imgKey'
    sub_url: str  # Wbi signed parameter 'subKey'


class GetUserInfoNotLoginData(BaseModel):

    isLogin: bool              # True when login, else False
    wbi_img: UserWbiImageInfo


class GetUserInfoLoginData(GetUserInfoNotLoginData):

    allowance_count: int
    answer_status: int
    email_verified: int                        # 1 as true and 0 as false
    face: str                                  # Profile icon's source URL
    face_nft: int                              # 1 as NFT profile icon, 0 as non-NFT
    face_nft_type: int
    has_shop: bool                             # True when has promoted goods, else False
    is_jury: bool                              # Whether the user is jury or not
    is_senior_member: int                      # 1 as senior member, else 0
    level_info: UserLevelInfo
    mid: int                                   # User ID
    mobile_verified: int                       # 1 as true and 0 as false
    money: int                                 # Amount of money/coins
    moral: int                                 # Value of moral, maximum is 70
    name_render: Optional[UserNameRenderInfo]
    official: UserOfficialInfo
    officialVerify: UserOfficialVerify
    pendant: UserPendant
    scores: int = 0
    shop_url: str = ""                         # URL of promoted goods
    uname: str                                 # User name
    vip: NavVipInfo
    vipDueDate: int                            # Unix timestamp when VIP expired
    vipStatus: int                             # 0: No VIP; 1: Has VIP
    vipType: int                               # 0: No VIP; 1：Monthly VIP; 2: Yearly or superior VIP
    vip_avatar_subscript: int
    vip_label: VipLabelInfo
    vip_nickname_color: str                    # hex code
    vip_pay_type: int                          # 0 is VIP unpaid, 1 is paid
    vip_theme_type: int
    wallet: UserWalletInfo


class GetUserInfoLoginResponse(LoginBaseModel):

    data: GetUserInfoLoginData


class GetUserInfoNotLoginResponse(LoginBaseModel):

    data: GetUserInfoNotLoginData


def get_web_captcha_meta() -> GetWebCaptchaResponse:
    r = requests.get(REQUEST_WEB_CAPTCHA_URL, headers=HEADERS)
    data = json.loads(r.content.decode('utf-8'))
    return GetWebCaptchaResponse.model_validate(data)


def get_web_public_key() -> GetWebPublicKeyResponse:
    r = requests.get(REQUEST_WEB_PUBLIC_KEY_URL, headers=HEADERS)
    data = json.loads(r.content.decode('utf-8'))
    return GetWebPublicKeyResponse.model_validate(data)


def get_web_spi() -> GetWebSPIResponse:
    r = requests.get(REQUEST_WEB_SPI_URL, headers=HEADERS)
    data = json.loads(r.content.decode('utf-8'))
    return GetWebSPIResponse.model_validate(data)


def get_web_user_info(
    session_data: Optional[str] = None
) -> Union[GetUserInfoLoginResponse, GetUserInfoNotLoginResponse]:
    session = requests.session()
    if session_data:
        session.cookies.set('SESSDATA', session_data)
    r = session.get(REQUEST_WEB_USER_INFO_URL, headers=HEADERS)
    data = json.loads(r.content.decode('utf-8'))
    model = GetUserInfoLoginResponse
    if data['code'] != 0:
        model = GetUserInfoNotLoginResponse
    return model.model_validate(data)


CaptchaParams = namedtuple('CaptchaParams', ['token', 'gt', 'challenge'])


class UserService:

    @staticmethod
    def _encrypt_password(password: str) -> str:
        pubkey_response = get_web_public_key()
        pubkey_data = pubkey_response.data
        pubkey_string, salt_string = pubkey_data.key, pubkey_data.hash

        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(pubkey_string.encode('utf-8'))
        salted_password = salt_string + password

        encrypted_pwd = rsa.encrypt(
            salted_password.encode('utf-8'),
            pubkey
        )
        return base64.b64encode(encrypted_pwd).decode('utf-8')

    @staticmethod
    def get_captcha_params() -> CaptchaParams:
        captcha_response = get_web_captcha_meta()
        captcha_data = captcha_response.data

        return CaptchaParams(
            token=captcha_data.token,
            gt=captcha_data.geetest.gt,
            challenge=captcha_data.geetest.challenge
        )

    def login(
        self,
        username: str,
        password: str,
        token: str,
        challenge: str,
        validate: str,
        seccode: str,
        is_plaintext_pwd: bool = False,
    ):
        session = requests.session()
        spi_res = get_web_spi()
        session.cookies.set('buvid3', spi_res.data.b_3)
        session.cookies.set('buvid4', spi_res.data.b_4)

        data = {
            'source': 'main-fe-header',
            'username': username,
            'password': self._encrypt_password(password) if is_plaintext_pwd else password,
            'keep': 0,
            'token': token,
            'challenge': challenge,
            'validate': validate,
            'seccode': seccode,
            'go_url': 'https://www.bilibili.com/'
        }
        encoded_data = urlencode(data)
        headers = copy.deepcopy(HEADERS)
        headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        session.post(
            REQUEST_WEB_LOGIN_URL,
            headers=headers,
            data=encoded_data,
            timeout=5
        )
        session_data = session.cookies.get('SESSDATA')
        return session_data

    @staticmethod
    def is_login(session_data: Optional[str] = None) -> bool:
        login_data = get_web_user_info(session_data)
        return login_data.data.isLogin

    @staticmethod
    def get_user_info(
        session_data: str
    ) -> Union[GetUserInfoLoginData, GetUserInfoNotLoginData]:
        login_data = get_web_user_info(session_data)
        return login_data.data
