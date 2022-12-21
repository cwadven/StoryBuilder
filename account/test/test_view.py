import json
from unittest.mock import patch

from django.urls import reverse
from django.test import TestCase, Client

from account.constants import SocialTypeSelector, UserCreationExceptionMessage, UserTypeEnum, UserProviderEnum
from account.helpers.social_login_helpers import SocialLoginController
from account.models import User

from config.common.exception_codes import LoginFailedException, UnknownPlatformException, BlackUserException, \
    LeaveUserException, DormantUserException, CannotCreateUserException
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


class SignUpTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(SignUpTestCase, self).setUp()
        self.body = {
            'username': 'test',
            'nickname': 'test_token',
            'password1': '12341234123412341234',
            'password2': '12341234123412341234',
            'email': 'aaaa@naver.com',
            'one_time_token': '1234',
        }

    def test_sign_up_should_success(self):
        # When: 회원가입 요청 이미 있는 username 으로 요청
        response = self.c.post(reverse('sign_up'), self.body)
        content = json.loads(response.content)

        # Then: 유저 생성
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message'], f'test_token 님 환영합니다.')
        user = User.objects.get(username='test')
        self.assertEqual(user.user_type_id, UserTypeEnum.NORMAL_USER.value)
        self.assertEqual(user.user_provider_id, UserProviderEnum.EMAIL.value)

    def test_sign_up_should_fail_when_username_already_exists(self):
        # Given: 유저를 생성
        User.objects.create_user(username='test')
        # And: username 중복 설정
        self.body['username'] = 'test'

        # When: 회원가입 요청 이미 있는 username 으로 요청
        response = self.c.post(reverse('sign_up'), self.body)
        content = json.loads(response.content)

        # Then: username 중복 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['error'], UserCreationExceptionMessage.USERNAME_EXISTS.label)

    def test_sign_up_should_fail_when_nickname_already_exists(self):
        # Given: 유저를 생성
        User.objects.create_user(username='test2', nickname='test_token')
        # And: nickname 중복 설정
        self.body['nickname'] = 'test_token'

        # When: 회원가입 요청 이미 있는 nickname 으로 요청
        response = self.c.post(reverse('sign_up'), self.body)
        content = json.loads(response.content)

        # Then: nickname 중복 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['error'], UserCreationExceptionMessage.NICKNAME_EXISTS.label)

    def test_sign_up_should_fail_when_email_already_exists(self):
        # Given: 유저를 생성
        User.objects.create_user(username='test3', nickname='tes2t_token22', email='aaaa@naver.com')
        # And: 중복 닉네임 설정
        self.body['email'] = 'aaaa@naver.com'

        # When: 회원가입 요청 이미 있는 email 으로 요청
        response = self.c.post(reverse('sign_up'), self.body)
        content = json.loads(response.content)

        # Then: nickname 중복 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['error'], UserCreationExceptionMessage.EMAIL_EXISTS.label)
