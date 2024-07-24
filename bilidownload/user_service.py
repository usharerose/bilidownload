"""
Components on Bilibili User actions
"""
import base64
from collections import namedtuple
import json
from typing import Optional, Tuple, Union

from requests.cookies import RequestsCookieJar
import rsa

from .proxy import (
    ProxyService,
    GetUserInfoLoginData,
    GetUserInfoNotLoginData,
    WebLoginResponse
)

CaptchaParams = namedtuple('CaptchaParams', ['token', 'gt', 'challenge'])


class UserService:

    @staticmethod
    def _encrypt_password(password: str) -> str:
        pubkey_response_dm = ProxyService.get_web_public_key_data()
        pubkey_data = pubkey_response_dm.data
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
        captcha_response_dm = ProxyService.get_web_captcha_meta_data()
        captcha_data = captcha_response_dm.data

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
    ) -> Tuple[WebLoginResponse, RequestsCookieJar]:
        if is_plaintext_pwd:
            password = self._encrypt_password(password)
        response = ProxyService.login(
            username, password, token, challenge, validate, seccode
        )
        data = json.loads(response.content.decode('utf-8'))
        login_response_dm = WebLoginResponse.model_validate(data)
        return login_response_dm, response.cookies

    @staticmethod
    def is_login(session_data: Optional[str] = None) -> bool:
        login_response_dm = ProxyService.get_web_user_info_data(session_data)
        return login_response_dm.data.isLogin

    @staticmethod
    def get_user_info(
        session_data: str
    ) -> Union[GetUserInfoLoginData, GetUserInfoNotLoginData]:
        login_response_dm = ProxyService.get_web_user_info_data(session_data)
        return login_response_dm.data
