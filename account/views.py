from django.contrib.auth import login

from account.constants import UserCreationExceptionMessage
from account.models import User

from rest_framework.views import APIView
from rest_framework.response import Response

from account.services import is_username_exists, is_nickname_exists
from common_decorator import mandatories
from common_library import get_login_token
from config.common.exception_codes import CannotCreateUserException


class SignUpView(APIView):
    @mandatories('username', 'nickname', 'password1', 'password2')
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
        created_user = User.objects.create_user(
            username=m['username'],
            nickname=m['nickname'],
            user_type_id=3,
            password=m['password1'],
            user_provider_id=1,
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
