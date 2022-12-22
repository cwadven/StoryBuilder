from django.contrib.auth import login

from account.constants import UserCreationExceptionMessage, UserProviderEnum, UserTypeEnum
from account.models import User

from rest_framework.views import APIView
from rest_framework.response import Response

from account.services import is_username_exists, is_nickname_exists, is_email_exists
from common_decorator import mandatories
from common_library import (
    get_login_token,
    generate_value_by_key_to_cache,
    generate_random_string_digits,
    get_cache_value_by_key
)
from .task import send_one_time_token_email
from config.common.exception_codes import CannotCreateUserException


class SignUpEmailTokenSendView(APIView):
    @mandatories('email', 'username', 'nickname', 'password2')
    def post(self, request, m):
        generate_value_by_key_to_cache(
            key=m['email'],
            value={
                'one_time_token': generate_random_string_digits(),
                'email': m['email'],
                'username': m['username'],
                'nickname': m['nickname'],
                'password2': m['password2'],
            },
            expire_seconds=60 * 2
        )
        value = get_cache_value_by_key(m['email'])
        if value:
            send_one_time_token_email.apply_async(
                (
                    m['email'],
                    value['one_time_token'],
                )
            )
        return Response({'message': '인증번호를 이메일로 전송했습니다.'}, 200)


class SignUpView(APIView):
    @mandatories('username', 'email', 'nickname', 'password1', 'password2', 'one_time_token')
    def post(self, request, m):
        # 1. 정보들을 처음에 redis로 저장 합니다.
        # 2. 이메일 인증 성공하면 바로 해당 redis 안에 있는 데이터로 유저 생성
        if is_username_exists(m['username']):
            raise CannotCreateUserException(
                detail=UserCreationExceptionMessage.USERNAME_EXISTS.label,
                code=UserCreationExceptionMessage.USERNAME_EXISTS.value,
            )
        if is_nickname_exists(m['nickname']):
            raise CannotCreateUserException(
                detail=UserCreationExceptionMessage.NICKNAME_EXISTS.label,
                code=UserCreationExceptionMessage.NICKNAME_EXISTS.value,
            )
        if is_email_exists(m['email']):
            raise CannotCreateUserException(
                detail=UserCreationExceptionMessage.EMAIL_EXISTS.label,
                code=UserCreationExceptionMessage.EMAIL_EXISTS.value,
            )

        created_user = User.objects.create_user(
            username=m['username'],
            nickname=m['nickname'],
            email=m['email'],
            user_type_id=UserTypeEnum.NORMAL_USER.value,
            password=m['password1'],
            user_provider_id=UserProviderEnum.EMAIL.value,
        )
        return Response({'message': f'{created_user.nickname} 님 환영합니다.'}, 200)


class SocialLoginView(APIView):
    @mandatories('provider', 'token')
    def post(self, request, m):
        user, is_created = User.objects.get_or_create_user_by_token(m['token'], m['provider'])
        user.raise_if_inaccessible()

        login(request, user)

        context = {
            'accessToken': get_login_token(user),
            'isCreated': is_created,
        }

        return Response(context, status=200)
