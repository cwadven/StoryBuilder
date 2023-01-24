from django.test import TestCase

from account.models import User
from config.common.exception_codes import UserSheetHintHistoryAlreadyExists, SheetHintDoesNotExists
from config.test_helper.helper import LoginMixin
from hint.models import SheetHint, UserSheetHintHistory
from hint.services import get_sheet_hint_infos, give_sheet_hint_information, get_available_sheet_hint
from story.models import Story, Sheet


class GetUserHistoryHintTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(GetUserHistoryHintTestCase, self).setUp()
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.start_sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=True,
            is_final=False,
        )
        self.start_sheet_hint = SheetHint.objects.create(
            sheet=self.start_sheet,
            hint='test_hint',
            image='test_image',
            sequence=1,
            point=10,
        )

    def test_get_sheet_hint_infos_has_history(self):
        # Given: 유저가 hint history 가 있을 경우
        self.login()
        self.user_sheet_hint_history = UserSheetHintHistory.objects.create(
            user=self.c.user,
            sheet_hint=self.start_sheet_hint,
        )

        # When: get_user_available_sheet_hints 요청
        user_available_sheet_hints = get_sheet_hint_infos(self.c.user.id, self.start_sheet.id)

        # Then: hint 내용 있음
        self.assertEqual(user_available_sheet_hints[0].get('id'), self.start_sheet_hint.id)
        self.assertEqual(user_available_sheet_hints[0].get('hint'), self.start_sheet_hint.hint)
        self.assertEqual(user_available_sheet_hints[0].get('image'), self.start_sheet_hint.image)
        self.assertTrue(user_available_sheet_hints[0].get('has_history'))

    def test_get_sheet_hint_infos_not_have_history(self):
        # Given: 유저가 hint history 가 없을 경우
        self.login()
        UserSheetHintHistory.objects.filter(
            user=self.c.user,
        ).delete()

        # When: get_user_available_sheet_hints 요청
        user_available_sheet_hints = get_sheet_hint_infos(self.c.user.id, self.start_sheet.id)

        # Then: hint 내용 없음
        self.assertEqual(user_available_sheet_hints[0].get('id'), self.start_sheet_hint.id)
        self.assertEqual(user_available_sheet_hints[0].get('hint'), '')
        self.assertEqual(user_available_sheet_hints[0].get('image'), '')
        self.assertFalse(user_available_sheet_hints[0].get('has_history'))

    def test_get_available_sheet_hint_should_raise_error_when_start_sheet_is_not_available_to_access(self):
        # Given: start_sheet_hint 가 제거된 경우
        self.start_sheet_hint.is_deleted = True
        self.start_sheet_hint.save()

        # Expect: 오류 반환
        with self.assertRaises(SheetHintDoesNotExists):
            get_available_sheet_hint(self.start_sheet_hint.id)

    def test_get_available_sheet_hint_should_return_sheet_hint(self):
        # Given:
        # When:
        available_sheet_hint = get_available_sheet_hint(self.start_sheet_hint.id)

        # Then:
        self.assertEqual(self.start_sheet_hint.id, available_sheet_hint.id)


class GiveUserHistoryHintTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(GiveUserHistoryHintTestCase, self).setUp()
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.start_sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=True,
            is_final=False,
        )
        self.start_sheet_hint = SheetHint.objects.create(
            sheet=self.start_sheet,
            hint='test_hint',
            image='test_image',
            sequence=1,
            point=10,
        )

    def test_give_sheet_hint_information_should_raise_error_when_user_already_has_sheet_hint(self):
        # Given: 유저가 hint history 가 있을 경우
        self.login()
        self.user_sheet_hint_history = UserSheetHintHistory.objects.create(
            user=self.c.user,
            sheet_hint=self.start_sheet_hint,
        )

        # Expect: give_sheet_hint_information 하지만 이미 받은 기록이 있을 경우
        with self.assertRaises(UserSheetHintHistoryAlreadyExists):
            give_sheet_hint_information(self.c.user.id, self.start_sheet_hint.id)

    def test_give_sheet_hint_information_should_return_sheet_hint(self):
        # Given:
        self.login()

        # When:
        start_sheet_hint = give_sheet_hint_information(self.c.user.id, self.start_sheet_hint.id)

        # Then: self.start_sheet_hint 와 반환된 같이 동일
        self.assertEqual(self.start_sheet_hint.id, start_sheet_hint.id)
        # And: UserSheetHintHistory 존재
        self.assertTrue(UserSheetHintHistory.objects.filter(sheet_hint_id=self.start_sheet_hint.id, user_id=self.c.user.id).exists())
