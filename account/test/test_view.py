import json
from unittest.mock import patch, Mock

from django.urls import reverse
from django.test import TestCase, Client

from account.constants import (
    SocialTypeSelector,
    UserCreationExceptionMessage,
    SIGNUP_MACRO_COUNT,
)
from account.helpers.social_login_helpers import SocialLoginController
from account.models import User

from config.common.exception_codes import LoginFailedException, UnknownPlatformException, BlackUserException, \
    LeaveUserException, DormantUserException
from config.test_helper.helper import LoginMixin


class SocialLoginTestCase(TestCase):
    def setUp(self):
        self.c = Client()

    @patch('account.helpers.social_login_helpers.requests.post')
    def test_invalidate_kakao_token_social_login_should_fail(self, mock_post):
        # Given: 문제가 있는 토큰을 보냈을 경우 및 status_code 를 400 으로 설정
        res = mock_post.return_value
        res.status_code = 400
        wrong_token = 'dkdkdkdkdkkdkdkd'

        # When: 카카오톡으로 소셜 로그인을 접근할 경우
        login_exception = lambda: SocialLoginController(
            SocialTypeSelector(2).selector()
        ).validate(wrong_token)

        # Then: 로그인 실패
        self.assertRaises(LoginFailedException, login_exception)

    def test_invalidate_platform_social_login_should_fail(self):
        # Given: 이상한 플랫폼으로 접근 했을 경우
        platform_num = 123123123
        token = '9123912ujdalksjflkasld'

        # When: 소셜 로그인을 할 경우
        platform_exception = lambda: SocialLoginController(
            SocialTypeSelector(platform_num).selector()
        ).validate(token)

        # Then: 알 수 없는 플랫폼으로 접근 했습니다.
        self.assertRaises(UnknownPlatformException, platform_exception)

    @patch('account.helpers.social_login_helpers.requests.post')
    @patch('account.helpers.social_login_helpers.requests.get')
    def test_valid_kakao_social_login_should_success(self, mock_get, mock_post):
        # Given: 토큰을 가져오는 값과 정보를 가져오는 것을 mocking
        res = mock_post.return_value
        res.status_code = 200
        res.text = json.dumps({'access_token': 'hello_token'})

        res2 = mock_get.return_value
        res2.status_code = 200
        res2.text = json.dumps({
            'id': 12345,
            'kakao_account': {}
        })

        # When: 카카오톡으로 소셜 로그인
        data = SocialLoginController(
            SocialTypeSelector(2).selector()
        ).validate('hello_token')

        # actual / expect
        # Then: 결과 값을 가져옵니다.
        self.assertEqual(data, {
            'id': 12345,
            'gender': None,
            'phone': None,
            'birth': None,
            'email': None,
            'name': None,
        })

    @patch('account.helpers.social_login_helpers.requests.post')
    @patch('account.helpers.social_login_helpers.requests.get')
    def test_valid_naver_social_login_should_success(self, mock_get, mock_post):
        # Given: 토큰을 가져오는 값과 정보를 가져오는 것을 mocking
        res = mock_post.return_value
        res.status_code = 200
        res.text = json.dumps({'access_token': 'hello_token'})

        res2 = mock_get.return_value
        res2.status_code = 200
        res2.text = json.dumps({
            'response': {
                'id': 12345,
            }
        })

        # When: 네이버로 소셜 로그인
        data = SocialLoginController(
            SocialTypeSelector(3).selector()
        ).validate('hello_token')

        # actual / expect
        # Then: 결과 값을 가져옵니다.
        self.assertEqual(data.get('id'), 12345)
        self.assertEqual(data.get('gender'), None)
        self.assertEqual(data.get('phone'), None)
        self.assertEqual(data.get('birth'), None)
        self.assertEqual(data.get('email'), None)
        self.assertEqual(data.get('name'), None)

    @patch('account.helpers.social_login_helpers.requests.post')
    @patch('account.helpers.social_login_helpers.requests.get')
    def test_valid_google_social_login_should_success(self, mock_get, mock_post):
        # Given: 토큰을 가져오는 값과 정보를 가져오는 것을 mocking
        res = mock_post.return_value
        res.status_code = 200
        res.text = json.dumps({'access_token': 'hello_token'})

        res2 = mock_get.return_value
        res2.status_code = 200
        res2.text = json.dumps({
            'sub': 12345,
        })

        # When: 구글로 소셜 로그인
        data = SocialLoginController(
            SocialTypeSelector(4).selector()
        ).validate('hello_token')

        # actual / expect
        # Then: 결과 값을 가져옵니다.
        self.assertEqual(data.get('id'), 12345)
        self.assertEqual(data.get('gender'), None)
        self.assertEqual(data.get('phone'), None)
        self.assertEqual(data.get('birth'), None)
        self.assertEqual(data.get('email'), None)
        self.assertEqual(data.get('name'), None)

    def test_kakao_social_login_without_mandatory_key(self):
        # Given: 필수 항목을 보내지 않은 경우
        body = {}

        # When
        response = self.c.post(reverse('social_login'), body)
        response_data = json.loads(response.content.decode('utf-8'))

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data.get('error'), '입력값을 다시 확인해주세요.')

    @patch('account.helpers.social_login_helpers.requests.post')
    @patch('account.helpers.social_login_helpers.requests.get')
    def test_kakao_social_login_with_mandatory_key_when_user_create_scenario(self, mock_get, mock_post):
        # Given: 필수 항목을 보냈을 경우
        # kakao 계정으로 로그인 했을 경우
        res = mock_post.return_value
        res.status_code = 200
        res.text = json.dumps({'access_token': 'hello_token'})

        res2 = mock_get.return_value
        res2.status_code = 200
        res2.text = json.dumps({
            'id': 12345,
            'kakao_account': {}
        })
        provider = 2
        body = {
            'provider': provider,
            'token': 'test_token',
        }

        # When: 소셜로그인에 성공했을 경우
        response = self.c.post(reverse('social_login'), body)

        # Then: User 가 생성되어야합니다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='12345').exists())
        user = User.objects.get(username='12345')
        self.assertEqual(user.user_type.id, 3)
        self.assertEqual(user.user_status.id, 1)
        self.assertEqual(user.user_provider.id, provider)

    @patch('account.helpers.social_login_helpers.requests.post')
    @patch('account.helpers.social_login_helpers.requests.get')
    def test_naver_social_login_with_mandatory_key_when_user_create_scenario(self, mock_get, mock_post):
        # Given: 필수 항목을 보냈을 경우
        # naver 계정으로 로그인 했을 경우
        res = mock_post.return_value
        res.status_code = 200
        res.text = json.dumps({'access_token': 'hello_token'})

        res = mock_post.return_value
        res.status_code = 200
        res.text = json.dumps({'access_token': 'hello_token'})

        res2 = mock_get.return_value
        res2.status_code = 200
        res2.text = json.dumps({
            'response': {
                'id': 12345,
            }
        })
        provider = 3
        body = {
            'provider': provider,
            'token': 'test_token',
        }

        # When: 소셜로그인에 성공했을 경우
        response = self.c.post(reverse('social_login'), body)

        # Then: User 가 생성되어야합니다.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='12345').exists())
        user = User.objects.get(username='12345')
        self.assertEqual(user.user_type.id, 3)
        self.assertEqual(user.user_status.id, 1)
        self.assertEqual(user.user_provider.id, provider)

    @patch('account.helpers.social_login_helpers.requests.post')
    @patch('account.helpers.social_login_helpers.requests.get')
    def test_kakao_social_login_with_when_user_is_black_user(self, mock_get, mock_post):
        # Given: 필수 항목을 보냈을 경우
        # kakao 계정으로 로그인 했을 경우
        # 계정을 생성합니다.
        # 생성한 계정을 정지 계정으로 만듭니다.
        res = mock_post.return_value
        res.status_code = 200
        res.text = json.dumps({'access_token': 'hello_token'})

        res2 = mock_get.return_value
        res2.status_code = 200
        res2.text = json.dumps({
            'id': 12345,
            'kakao_account': {}
        })
        provider = 2
        body = {
            'provider': provider,
            'token': 'test_token',
        }
        self.c.post(reverse('social_login'), body)
        self.assertTrue(User.objects.filter(username='12345').exists())
        user = User.objects.get(username='12345')
        user.user_status_id = 3
        user.save()

        # When: 계정을 생성합니다
        response = self.c.post(reverse('social_login'), body)
        response_data = json.loads(response.content.decode('utf-8'))

        # Then: 정지된 계정이라는 에러가 나와야합니다.
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data.get('error'), BlackUserException.default_detail)

    @patch('account.helpers.social_login_helpers.requests.post')
    @patch('account.helpers.social_login_helpers.requests.get')
    def test_kakao_social_login_with_when_user_is_deactivated_user(self, mock_get, mock_post):
        # Given: 필수 항목을 보냈을 경우
        # kakao 계정으로 로그인 했을 경우
        # 계정을 생성합니다.
        # 생성한 계정을 탈퇴 계정으로 만듭니다.
        res = mock_post.return_value
        res.status_code = 200
        res.text = json.dumps({'access_token': 'hello_token'})

        res2 = mock_get.return_value
        res2.status_code = 200
        res2.text = json.dumps({
            'id': 12345,
            'kakao_account': {}
        })
        provider = 2
        body = {
            'provider': provider,
            'token': 'test_token',
        }
        self.c.post(reverse('social_login'), data=body)
        self.assertTrue(User.objects.filter(username='12345').exists())
        user = User.objects.get(username='12345')
        user.user_status_id = 2
        user.save()

        # When: 계정을 생성합니다
        response = self.c.post(reverse('social_login'), body)
        response_data = json.loads(response.content.decode('utf-8'))

        # Then: 탈퇴된 계정이라는 에러가 나와야합니다.
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data.get('error'), LeaveUserException.default_detail)

    @patch('account.helpers.social_login_helpers.requests.post')
    @patch('account.helpers.social_login_helpers.requests.get')
    def test_kakao_social_login_with_when_user_is_dormant_user(self, mock_get, mock_post):
        # Given: 필수 항목을 보냈을 경우
        # kakao 계정으로 로그인 했을 경우
        # 계정을 생성합니다.
        # 생성한 계정을 휴면 계정으로 만듭니다.
        res = mock_post.return_value
        res.status_code = 200
        res.text = json.dumps({'access_token': 'hello_token'})

        res2 = mock_get.return_value
        res2.status_code = 200
        res2.text = json.dumps({
            'id': 12345,
            'kakao_account': {}
        })
        provider = 2
        body = {
            'provider': provider,
            'token': 'test_token',
        }
        self.c.post(reverse('social_login'), body)
        self.assertTrue(User.objects.filter(username='12345').exists())
        user = User.objects.get(username='12345')
        user.user_status_id = 4
        user.save()

        # When: 계정을 생성합니다
        response = self.c.post(reverse('social_login'), body)
        response_data = json.loads(response.content.decode('utf-8'))

        # Then: 휴면 계정이라는 에러가 나와야합니다.
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data.get('error'), DormantUserException.default_detail)


class SignUpValidationTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(SignUpValidationTestCase, self).setUp()
        self.body = {
            'username': 'test',
            'nickname': 'test_token',
            'password1': '12341234123412341234',
            'password2': '12341234123412341234',
            'email': 'aaaa@naver.com',
            'one_time_token': '1234',
        }

    def test_sign_up_validation_success(self):
        # When: 회원가입 검증 요청
        response = self.c.post(reverse('sign_up_validation'), self.body)
        content = json.loads(response.content)

        # Then: 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['result'], 'success')

    def test_sign_up_validation_should_fail_when_username_already_exists(self):
        # Given: 유저를 생성
        User.objects.create_user(username='test')
        # And: username 중복 설정
        self.body['username'] = 'test'

        # When: 회원가입 검증 요청
        response = self.c.post(reverse('sign_up_validation'), self.body)
        content = json.loads(response.content)

        # Then: username 중복 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['username'][0], UserCreationExceptionMessage.USERNAME_EXISTS.label)

    def test_sign_up_validation_should_fail_when_nickname_already_exists(self):
        # Given: 유저를 생성
        User.objects.create_user(username='test2', nickname='test_token')
        # And: nickname 중복 설정
        self.body['nickname'] = 'test_token'

        # When: 회원가입 검증 요청
        response = self.c.post(reverse('sign_up_validation'), self.body)
        content = json.loads(response.content)

        # Then: nickname 중복 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['nickname'][0], UserCreationExceptionMessage.NICKNAME_EXISTS.label)

    def test_sign_up_validation_should_fail_when_email_already_exists(self):
        # Given: 유저를 생성
        User.objects.create_user(username='test3', nickname='tes2t_token22', email='aaaa@naver.com')
        # And: 중복 닉네임 설정
        self.body['email'] = 'aaaa@naver.com'

        # When: 회원가입 검증 요청
        response = self.c.post(reverse('sign_up_validation'), self.body)
        content = json.loads(response.content)

        # Then: nickname 중복 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['email'][0], UserCreationExceptionMessage.EMAIL_EXISTS.label)

    def test_sign_up_validation_should_fail_when_password_wrong(self):
        # Given: 비밀번호 다르게 설정
        self.body['password2'] = '12312312'

        # When: 회원가입 검증 요청
        response = self.c.post(reverse('sign_up_validation'), self.body)
        content = json.loads(response.content)

        # Then: password 확인 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['password2'][0], UserCreationExceptionMessage.CHECK_PASSWORD.label)


class SignUpEmailTokenSendTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(SignUpEmailTokenSendTestCase, self).setUp()
        self.body = {
            'username': 'test',
            'nickname': 'test_token',
            'password2': '12341234123412341234',
            'email': 'aaaa@naver.com',
        }

    @patch('account.views.generate_dict_value_by_key_to_cache', Mock())
    @patch('account.views.send_one_time_token_email', Mock())
    @patch('account.views.get_cache_value_by_key')
    def test_email_token_create_when_token_create_successful(self, mock_get_cache_value_by_key):
        # Given:
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1234',
            'email': self.body['email'],
            'username': self.body['username'],
            'nickname': self.body['nickname'],
            'password2': self.body['password2'],
        }

        # When:
        response = self.c.post(reverse('sign_up_check'), self.body)
        content = json.loads(response.content)

        # Then: 성공 했다는 메시지 반환
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message'], '인증번호를 이메일로 전송했습니다.')

    @patch('account.views.generate_dict_value_by_key_to_cache', Mock())
    @patch('account.views.send_one_time_token_email', Mock())
    @patch('account.views.get_cache_value_by_key')
    def test_email_token_create_when_token_create_failed(self, mock_get_cache_value_by_key):
        # Given:
        mock_get_cache_value_by_key.return_value = None

        # When:
        response = self.c.post(reverse('sign_up_check'), self.body)
        content = json.loads(response.content)

        # Then: 성공 했다는 메시지 반환
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message'], '인증번호를 이메일로 전송했습니다.')


class SignUpEmailTokenValidationEndViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(SignUpEmailTokenValidationEndViewTestCase, self).setUp()
        self.body = {
            'email': 'aaaa@naver.com',
            'one_time_token': '1234',
        }

    @patch('account.views.increase_cache_int_value_by_key')
    def test_email_token_validate_should_return_fail_when_macro_count_is_30_times(self, mock_increase_cache_int_value_by_key):
        # Given: 30 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 30

        # When:
        response = self.c.post(reverse('sign_up_one_time_token'), self.body)
        content = json.loads(response.content)

        # Then: 메크로 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content['message'],
            '{}회 이상 인증번호를 틀리셨습니다. 현 이메일은 {}시간 동안 인증할 수 없습니다.'.format(SIGNUP_MACRO_COUNT, 24)
        )

    @patch('account.views.increase_cache_int_value_by_key')
    @patch('account.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_email_key_not_exists(self,
                                                                                  mock_get_cache_value_by_key,
                                                                                  mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        # And: 인증한 이메일이 없는 경우
        mock_get_cache_value_by_key.return_value = None

        # When:
        response = self.c.post(reverse('sign_up_one_time_token'), self.body)
        content = json.loads(response.content)

        # Then: 이메일 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content['message'],
            '이메일 인증번호를 다시 요청하세요.',
        )

    @patch('account.views.increase_cache_int_value_by_key')
    @patch('account.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_one_time_token_not_exists(self,
                                                                               mock_get_cache_value_by_key,
                                                                               mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        # And: one time token 이 없는 경우
        mock_get_cache_value_by_key.return_value = {
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }

        # When:
        response = self.c.post(reverse('sign_up_one_time_token'), self.body)
        content = json.loads(response.content)

        # Then: 인증번호 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content['message'],
            '인증번호가 다릅니다.',
        )

    @patch('account.views.increase_cache_int_value_by_key')
    @patch('account.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_one_time_token_is_different(self,
                                                                                    mock_get_cache_value_by_key,
                                                                                    mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        # And: one time token 다르게 설정
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1233',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }
        # And: one time token 다르게 설정
        self.body['one_time_token'] = '1234'

        # When:
        response = self.c.post(reverse('sign_up_one_time_token'), self.body)
        content = json.loads(response.content)

        # Then: 인증번호 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content['message'],
            '인증번호가 다릅니다.',
        )

    @patch('account.views.increase_cache_int_value_by_key')
    @patch('account.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_username_user_already_exists(self,
                                                                                      mock_get_cache_value_by_key,
                                                                                      mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1234',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }
        # And: 이미 username mocking 한 데이터의 계정이 있는 경우
        User.objects.create_user(username='test')

        # When:
        response = self.c.post(reverse('sign_up_one_time_token'), self.body)
        content = json.loads(response.content)

        # Then: username 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content['message'],
            UserCreationExceptionMessage.USERNAME_EXISTS.label,
        )

    @patch('account.views.increase_cache_int_value_by_key')
    @patch('account.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_nickname_user_already_exists(self,
                                                                                       mock_get_cache_value_by_key,
                                                                                       mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1234',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }
        # And: 이미 nickname mocking 한 데이터의 계정이 있는 경우
        User.objects.create_user(username='test2', nickname='test')

        # When:
        response = self.c.post(reverse('sign_up_one_time_token'), self.body)
        content = json.loads(response.content)

        # Then: 닉네임 중복 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content['message'],
            UserCreationExceptionMessage.NICKNAME_EXISTS.label,
        )

    @patch('account.views.increase_cache_int_value_by_key')
    @patch('account.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_fail_when_email_user_already_exists(self,
                                                                                       mock_get_cache_value_by_key,
                                                                                       mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1234',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }
        # And: 이미 email mocking 한 데이터의 계정이 있는 경우
        User.objects.create_user(username='test2', nickname='test2', email='test@test.com')

        # When:
        response = self.c.post(reverse('sign_up_one_time_token'), self.body)
        content = json.loads(response.content)

        # Then: email 중복 에러
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            content['message'],
            UserCreationExceptionMessage.EMAIL_EXISTS.label,
        )

    @patch('account.views.delete_cache_value_by_key', Mock())
    @patch('account.views.increase_cache_int_value_by_key')
    @patch('account.views.get_cache_value_by_key')
    def test_email_token_validate_should_return_success(self,
                                                        mock_get_cache_value_by_key,
                                                        mock_increase_cache_int_value_by_key):
        # Given: 0 번 메크로를 했을 경우
        mock_increase_cache_int_value_by_key.return_value = 0
        mock_get_cache_value_by_key.return_value = {
            'one_time_token': '1234',
            'email': 'test@test.com',
            'username': 'test',
            'nickname': 'test',
            'password2': 'test',
        }

        # When:
        response = self.c.post(reverse('sign_up_one_time_token'), self.body)
        content = json.loads(response.content)

        # Then: 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content['message'],
            '회원가입에 성공했습니다.',
        )


class LoginTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(LoginTestCase, self).setUp()
        self.user = User.objects.create_user(
            username='test',
            password='12341234'
        )
        self.body = {
            'username': 'test',
            'password': '12341234',
        }

    def test_login_user_should_success_when_username_and_password_exists(self):
        # Given:
        # When:
        response = self.c.post(reverse('normal_login'), self.body)

        # Then: 로그인 성공
        self.assertEqual(response.status_code, 200)

    def test_login_user_should_fail_when_username_and_password_different(self):
        # Given:
        self.body['password'] = 'wrong_password'
        
        # When:
        response = self.c.post(reverse('normal_login'), self.body)
        content = json.loads(response.content)

        # Then: 로그인 실패
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['result'], '이이디/비밀번호 문제가 발생했습니다.')
