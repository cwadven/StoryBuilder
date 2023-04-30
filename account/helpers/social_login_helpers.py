import json
import requests
from datetime import datetime
from abc import ABC, abstractmethod

from django.conf import settings

from config.common.exception_codes import LoginFailedException


class SocialType(ABC):
    _request_access_token_path = None
    _request_user_info_path = None
    _client_id = None
    _secret = None
    _redirect_uri = None

    @property
    @abstractmethod
    def request_access_token_path(self):
        pass

    @property
    @abstractmethod
    def request_user_info_path(self):
        pass

    @property
    @abstractmethod
    def client_id(self):
        pass

    @property
    @abstractmethod
    def secret(self):
        pass

    @property
    @abstractmethod
    def redirect_uri(self):
        pass

    @abstractmethod
    def get_user_info_with_access_token(self, access_token: str) -> dict:
        pass

    def get_access_token_by_code(self, code: str) -> str:
        access_data = requests.post(
            self.request_access_token_path,
            data={
                'grant_type': 'authorization_code',
                "client_id": self.client_id,
                "client_secret": self.secret,
                "redirect_uri": self.redirect_uri,
                "code": code
            }
        )
        if access_data.status_code != 200:
            raise LoginFailedException()

        return json.loads(access_data.text)['access_token']


class KakaoSocialType(SocialType):
    def __init__(self):
        self._request_access_token_path = 'https://kauth.kakao.com/oauth/token'
        self._request_user_info_path = 'https://kapi.kakao.com/v2/user/me'
        self._client_id = settings.KAKAO_API_KEY
        self._secret = settings.KAKAO_SECRET_KEY
        self._redirect_uri = ''

    @property
    def request_access_token_path(self):
        return self._request_access_token_path

    @property
    def request_user_info_path(self):
        return self._request_user_info_path

    @property
    def client_id(self):
        return self._client_id

    @property
    def secret(self):
        return self._secret

    @property
    def redirect_uri(self):
        return self._redirect_uri

    @staticmethod
    def _get_birth_day(data: dict) -> datetime:
        birth = None
        if 'kakao_account' in data.keys():
            try:
                birth = data['kakao_account']['birthyear'] + data['kakao_account']['birthday']
                birth = datetime.strptime(birth, '%Y%m%d')
            except KeyError:
                pass
        return birth

    @staticmethod
    def _get_gender(data: dict):
        gender = None
        if 'kakao_account' in data.keys():
            try:
                gender = data['kakao_account']['gender']
            except KeyError:
                pass
        return gender

    @staticmethod
    def _get_phone(data: dict):
        phone = None
        if 'kakao_account' in data.keys():
            try:
                phone = data['kakao_account']['phone_number'].replace(
                    '+82 ',
                    '0'
                ).replace(
                    '-',
                    ''
                ).replace(
                    ' ',
                    '',
                )
            except KeyError:
                pass
        return phone

    @staticmethod
    def _get_email(data: dict):
        email = None
        if 'kakao_account' in data.keys():
            try:
                email = data['kakao_account']['email']
            except KeyError:
                pass
        return email

    @staticmethod
    def _get_name(data: dict):
        name = None
        if 'kakao_account' in data.keys():
            try:
                name = data['kakao_account']['profile']['nickname']
            except KeyError:
                pass
        return name

    def get_user_info_with_access_token(self, access_token: str) -> dict:
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        data = requests.get(
            self.request_user_info_path,
            headers=headers
        )
        if data.status_code != 200:
            raise LoginFailedException()
        else:
            data = json.loads(data.text)
            birth = self._get_birth_day(data)
            gender = self._get_gender(data)
            phone = self._get_phone(data)
            email = self._get_email(data)
            name = self._get_name(data)
            return {
                'id': data['id'],
                'gender': birth,
                'phone': gender,
                'birth': phone,
                'email': email,
                'name': name,
            }


class NaverSocialType(SocialType):
    def __init__(self):
        self._request_access_token_path = 'https://nid.naver.com/oauth2.0/token'
        self._request_user_info_path = 'https://openapi.naver.com/v1/nid/me'
        self._client_id = settings.NAVER_API_KEY
        self._secret = settings.NAVER_SECRET_KEY
        self._redirect_uri = ''

    @property
    def request_access_token_path(self):
        return self._request_access_token_path

    @property
    def request_user_info_path(self):
        return self._request_user_info_path

    @property
    def client_id(self):
        return self._client_id

    @property
    def secret(self):
        return self._secret

    @property
    def redirect_uri(self):
        return self._redirect_uri

    def get_user_info_with_access_token(self, access_token: str) -> dict:
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        data = requests.get(
            self.request_user_info_path,
            headers=headers
        )
        if data.status_code != 200:
            raise LoginFailedException()

        data = json.loads(data.text)['response']
        birth = None

        try:
            birth = data['birthyear'] + data['birthday']
            birth = datetime.strptime(birth, '%Y%m-%d')

            return_data = {
                'id': data['id'],
                'gender': data['gender'] if data['gender'] else None,
                'phone': data['phone_number'].replace('-', '').replace(' ', '') if data['phone_number'] else None,
                'birth': birth,
                'email': data['email'] if data['email'] else None,
                'name': data['name'] if data['name'] else None,
                'nickname': data['nickname'] if data['nickname'] else None,
            }
        except:
            return_data = {
                'id': data['id'],
                'gender': None,
                'phone': None,
                'birth': birth,
                'email': None,
                'name': None,
                'nickname': None,
            }

        return return_data


class GoogleSocialType(SocialType):
    def __init__(self):
        self._request_access_token_path = 'https://oauth2.googleapis.com/token'
        self._request_user_info_path = 'https://www.googleapis.com/oauth2/v3/userinfo'
        self._client_id = settings.GOOGLE_CLIENT_ID
        self._secret = settings.GOOGLE_SECRET_KEY
        self._redirect_uri = settings.GOOGLE_REDIRECT_URL

    @property
    def request_access_token_path(self):
        return self._request_access_token_path

    @property
    def request_user_info_path(self):
        return self._request_user_info_path

    @property
    def client_id(self):
        return self._client_id

    @property
    def secret(self):
        return self._secret

    @property
    def redirect_uri(self):
        return self._redirect_uri

    def get_user_info_with_access_token(self, access_token: str) -> dict:
        data = requests.get(
            self.request_user_info_path,
            params={
                'access_token': access_token
            }
        )
        if data.status_code != 200:
            raise LoginFailedException()

        data = json.loads(data.text)

        try:
            return_data = {
                'id': data.get('sub'),
                'gender': None,
                'phone': None,
                'birth': None,
                'email': None,
                'name': data.get('name') if data.get('name') else None,
                'nickname': None,
            }
        except:
            return_data = {
                'id': data.get('sub'),
                'gender': None,
                'phone': None,
                'birth': None,
                'email': None,
                'name': None,
                'nickname': None,
            }

        return return_data


class SocialLoginController:
    def __init__(self, social_type):
        self.social_type = social_type

    def validate(self, code):
        # access_token = self.social_type.get_access_token_by_code(code)
        return self.social_type.get_user_info_with_access_token(code)
