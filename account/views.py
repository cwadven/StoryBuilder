from django.contrib.auth import login

from account.constants import UserCreationExceptionMessage, UserProviderEnum, UserTypeEnum
from account.models import User

from rest_framework.views import APIView
from rest_framework.response import Response

from account.services import is_username_exists, is_nickname_exists, is_email_exists
from common_decorator import mandatories
from common_library import get_login_token
from config.common.exception_codes import CannotCreateUserException


class SignUpView(APIView):
    @mandatories('username', 'email', 'nickname', 'password1', 'password2', 'one_time_token')
    def post(self, request, m):
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
