from django.contrib.auth import login, authenticate

from account.constants import (
    UserProviderEnum,
    UserTypeEnum,
    UserCreationExceptionMessage,
    SIGNUP_MACRO_VALIDATION_KEY,
    SIGNUP_MACRO_COUNT,
)
from account.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from common_decorator import mandatories
from common_library import (
    get_login_token,
    generate_dict_value_by_key_to_cache,
    generate_random_string_digits,
    get_cache_value_by_key, delete_cache_value_by_key,
    increase_cache_int_value_by_key
)
from .helpers.payload_validator_helpers import SignUpPayloadValidator
from .services import is_username_exists, is_nickname_exists, is_email_exists
from .task import send_one_time_token_email


class SignUpEmailTokenSendView(APIView):
    @mandatories('email', 'username', 'nickname', 'password2')
    def post(self, request, m):
        generate_dict_value_by_key_to_cache(
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


class SignUpValidationView(APIView):
    @mandatories('username', 'email', 'nickname', 'password1', 'password2')
    def post(self, request, m):
        payload_validator = SignUpPayloadValidator(m)
        try:
            payload_validator.validate()
        except ValidationError as e:
            return Response(e.detail, 400)
        return Response({'result': f'success'}, 200)


class SignUpEmailTokenValidationEndView(APIView):
    @mandatories('email', 'one_time_token')
    def post(self, request, m):
        macro_count = increase_cache_int_value_by_key(
            key=SIGNUP_MACRO_VALIDATION_KEY.format(m['email']),
        )
        if macro_count >= SIGNUP_MACRO_COUNT:
            return Response(
                data={
                    'message': '{}회 이상 인증번호를 틀리셨습니다. 현 이메일은 {}시간 동안 인증할 수 없습니다.'.format(
                        SIGNUP_MACRO_COUNT,
                        24
                    )
                },
                status=400,
            )

        value = get_cache_value_by_key(m['email'])

        if not value:
            return Response({'message': '이메일 인증번호를 다시 요청하세요.'}, 400)

        if not value.get('one_time_token') or value.get('one_time_token') != m['one_time_token']:
            return Response({'message': '인증번호가 다릅니다.'}, 400)

        # 회원 가입 제약을 위해 더블 체킹 validation
        if is_username_exists(value['username']):
            return Response({'message': UserCreationExceptionMessage.USERNAME_EXISTS.label}, 400)
        if is_nickname_exists(value['nickname']):
            return Response({'message': UserCreationExceptionMessage.NICKNAME_EXISTS.label}, 400)
        if is_email_exists(value['email']):
            return Response({'message': UserCreationExceptionMessage.EMAIL_EXISTS.label}, 400)

        User.objects.create_user(
            username=value['username'],
            nickname=value['nickname'],
            email=value['email'],
            user_type_id=UserTypeEnum.NORMAL_USER.value,
            password=value['password2'],
            user_provider_id=UserProviderEnum.EMAIL.value,
        )

        # 캐시 서버 기록 삭제 (메크로 및 정보 보존용)
        delete_cache_value_by_key(value['email'])
        delete_cache_value_by_key(SIGNUP_MACRO_VALIDATION_KEY.format(m['email']))
        return Response({'message': f'회원가입에 성공했습니다.'}, 200)


class LoginView(APIView):
    @mandatories('username', 'password')
    def post(self, request, m):
        user = authenticate(request, username=m['username'], password=m['password'])
        if not user:
            return Response({'message': '아이디/비밀번호 정보가 일치하지 않습니다.'}, status=400)

        login(request, user)
        context = {
            'accessToken': get_login_token(user),
        }
        return Response(context, status=200)


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
