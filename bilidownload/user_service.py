"""
Components on login Bilibili
"""
import base64
from collections import namedtuple
import copy
import json
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


class LoginBaseModel(BaseModel):

    code: int = 0
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
