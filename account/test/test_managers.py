from unittest.mock import patch

from django.test import TestCase

from account.constants import UserTypeEnum, UserStatusEnum
from account.models import User


class TestCustomUserManager(TestCase):
    def setUp(self):
        pass

    @patch('account.managers.SocialLoginController.validate')
    @patch('common_library.generate_random_string_digits')
    def test_get_or_create_user_by_token_when_create_user_email_and_nickname_not_exists(self, mock_random_string, mock_validate):
        # Given:
        token = 'test_token'
        provider = 3
        # And: validate 결과 값 모킹
        mock_validate.return_value = {
            'id': 'test_id',
            'email': None,
            'nickname': None,
        }
        # And: 닉네임 생성 모킹
        mock_random_string.return_value = '12345'

        # When: get_or_create_user_by_token
        user, is_created = User.objects.get_or_create_user_by_token(token, provider)

        # Then:
        self.assertTrue(is_created)
        self.assertEqual(user.username, 'test_id')
        self.assertEqual(user.user_provider_id, provider)
        self.assertEqual(user.user_type_id, UserTypeEnum.NORMAL_USER.value)
        self.assertEqual(user.user_status_id, UserStatusEnum.NORMAL_USER.value)
        self.assertEqual(user.email, '')
        self.assertEqual(user.nickname, 'Puzztory12345')

    @patch('account.managers.SocialLoginController.validate')
    def test_get_or_create_user_by_token_when_create_user_email_and_nickname_exists(self, mock_validate):
        # Given:
        token = 'test_token'
        provider = 3
        # And: validate 결과 값 모킹
        mock_validate.return_value = {
            'id': 'test_id',
            'email': 'test_email',
            'nickname': 'test_nickname',
        }

        # When: get_or_create_user_by_token
        user, is_created = User.objects.get_or_create_user_by_token(token, provider)

        # Then:
        self.assertTrue(is_created)
        self.assertEqual(user.username, 'test_id')
        self.assertEqual(user.user_provider_id, provider)
        self.assertEqual(user.user_type_id, UserTypeEnum.NORMAL_USER.value)
        self.assertEqual(user.user_status_id, UserStatusEnum.NORMAL_USER.value)
        self.assertEqual(user.email, 'test_email')
        self.assertEqual(user.nickname, 'test_nickname')

    @patch('account.managers.SocialLoginController.validate')
    def test_get_or_create_user_by_token_when_already_user_exists(self, mock_validate):
        # Given:
        token = 'test_token'
        provider = 3
        # And: validate 결과 값 모킹
        mock_validate.return_value = {
            'id': 'test_id',
            'email': 'test_email',
            'nickname': 'test_nickname',
        }
        # And: 1번 미리 생성 get_or_create_user_by_token
        User.objects.get_or_create_user_by_token(token, provider)

        # When: 2번째 email 과 nickname 기존과 다르게 하고 실행
        mock_validate.return_value = {
            'id': 'test_id',
            'email': 'test_email2',
            'nickname': 'test_nickname2',
        }
        user, is_created = User.objects.get_or_create_user_by_token(token, provider)

        # Then:
        self.assertFalse(is_created)
        self.assertEqual(user.username, 'test_id')
        self.assertEqual(user.user_provider_id, provider)
        self.assertEqual(user.user_type_id, UserTypeEnum.NORMAL_USER.value)
        self.assertEqual(user.user_status_id, UserStatusEnum.NORMAL_USER.value)
        # And: 처음에 만들었던 것으로 반환
        self.assertEqual(user.email, 'test_email')
        self.assertEqual(user.nickname, 'test_nickname')
