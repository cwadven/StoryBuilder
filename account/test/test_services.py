from account.models import User
from django.test import TestCase

from account.services import is_username_exists, is_nickname_exists, is_email_exists, is_length_valid, \
    is_only_alphanumeric, is_only_korean_english_alphanumeric


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

    def test_is_nickname_exists_should_return_true_when_username_exists(self):
        # Given: test 라는 nickname 을 가진 User 생성
        User.objects.create_user(username='aaaa', nickname='test')

        # Expected:
        self.assertTrue(is_nickname_exists('test'))

    def test_is_nickname_exists_should_return_false_when_username_not_exists(self):
        # Expected:
        self.assertFalse(is_nickname_exists('test'))

    def test_is_email_exists_should_return_true_when_username_exists(self):
        # Given: test 라는 email 을 가진 User 생성
        User.objects.create_user(username='aaaa', email='test@naver.com')

        # Expected:
        self.assertTrue(is_email_exists('test@naver.com'))

    def test_is_email_exists_should_return_false_when_username_not_exists(self):
        # Expected:
        self.assertFalse(is_email_exists('test@naver.com'))

    def test_is_length_valid(self):
        self.assertTrue(is_length_valid("hello", 3, 10))
        self.assertFalse(is_length_valid("hello", 6, 10))
        self.assertFalse(is_length_valid("hello", 3, 4))

    def test_is_only_alphanumeric(self):
        self.assertTrue(is_only_alphanumeric("abc123"))
        self.assertFalse(is_only_alphanumeric("abc@123"))
        self.assertFalse(is_only_alphanumeric("한글123"))

    def test_is_only_korean_english_alphanumeric(self):
        self.assertTrue(is_only_korean_english_alphanumeric("안녕abc123"))
        self.assertFalse(is_only_korean_english_alphanumeric("안녕abc@123"))
        self.assertTrue(is_only_korean_english_alphanumeric("가나다ABC123"))
