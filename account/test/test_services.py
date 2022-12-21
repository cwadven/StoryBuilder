from account.models import User
from django.test import TestCase

from account.services import is_username_exists


class AccountServiceTestCase(TestCase):
    def setUp(self):
        pass

    def test_is_username_exists_should_return_true_when_username_exists(self):
        # Given: test 라는 이름을 가진 User 생성
        User.objects.create_user(username='test')

        # Expected:
        self.assertTrue(is_username_exists('test'))

    def test_is_username_exists_should_return_false_when_username_not_exists(self):
        # Expected:
        self.assertFalse(is_username_exists('test'))
