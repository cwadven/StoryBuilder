from django.test import TestCase

from account.models import User
from config.test_helper.helper import LoginMixin
from hint.models import SheetHint, UserSheetHintHistory
from hint.services import get_user_available_sheet_hints
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

    def test_get_user_available_sheet_hints_has_history(self):
        # Given: 유저가 hint history 가 있을 경우
        self.login()
        self.user_sheet_hint_history = UserSheetHintHistory.objects.create(
            user=self.c.user,
            sheet_hint=self.start_sheet_hint,
        )

        # When: get_user_available_sheet_hints 요청
        user_available_sheet_hints = get_user_available_sheet_hints(self.c.user, self.start_sheet.id)

        # Then: hint 내용 있음
        self.assertEqual(user_available_sheet_hints[0].get('id'), self.start_sheet_hint.id)
        self.assertEqual(user_available_sheet_hints[0].get('hint'), self.start_sheet_hint.hint)
        self.assertEqual(user_available_sheet_hints[0].get('image'), self.start_sheet_hint.image)
        self.assertTrue(user_available_sheet_hints[0].get('has_history'))

    def test_get_user_available_sheet_hints_not_have_history(self):
        # Given: 유저가 hint history 가 없을 경우
        self.login()
        UserSheetHintHistory.objects.filter(
            user=self.c.user,
        ).delete()

        # When: get_user_available_sheet_hints 요청
        user_available_sheet_hints = get_user_available_sheet_hints(self.c.user, self.start_sheet.id)

        # Then: hint 내용 없음
        self.assertEqual(user_available_sheet_hints[0].get('id'), self.start_sheet_hint.id)
        self.assertEqual(user_available_sheet_hints[0].get('hint'), '')
        self.assertEqual(user_available_sheet_hints[0].get('image'), '')
        self.assertFalse(user_available_sheet_hints[0].get('has_history'))
