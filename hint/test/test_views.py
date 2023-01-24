import json

from django.test import TestCase
from django.urls import reverse

from account.models import User
from config.common.exception_codes import SheetDoesNotExists
from config.test_helper.helper import LoginMixin
from hint.models import SheetHint, UserSheetHintHistory
from story.models import Story, Sheet, SheetAnswer, NextSheetPath


class SheetHintAPIViewViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(SheetHintAPIViewViewTestCase, self).setUp()
        self.user = User.objects.all()[0]
        self.login()
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
        self.start_sheet_answer1 = SheetAnswer.objects.create(
            sheet=self.start_sheet,
            answer='test',
            answer_reply='test_reply',
        )
        self.normal_sheet = Sheet.objects.create(
            story=self.story,
            title='normal sheet',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=False,
            is_final=False,
        )
        self.normal_sheet_answer1 = SheetAnswer.objects.create(
            sheet=self.normal_sheet,
            answer='normal_sheet_test',
            answer_reply='normal_sheet_test_reply',
        )
        self.final_sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=False,
            is_final=True,
        )
        self.start_sheet_answer_next_sheet_path1 = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.normal_sheet,
            quantity=10,
        )
        self.normal_sheet_answer_next_sheet_path1 = NextSheetPath.objects.create(
            answer=self.normal_sheet_answer1,
            sheet=self.final_sheet,
            quantity=10,
        )
        self.start_sheet_hint = SheetHint.objects.create(
            sheet=self.start_sheet,
            hint='test_hint',
            image='test_image',
            sequence=1,
            point=10,
        )

    def test_get_sheet_hint_infos_when_user_not_have_hint_history(self):
        # Given:
        # When: start_sheet hint 요청
        response = self.c.get(reverse('hint:sheet_hint', args=[self.start_sheet.id]))
        content = json.loads(response.content)

        # Then:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('user_sheet_hint_infos')[0]['id'], self.start_sheet_hint.id)
        self.assertEqual(content.get('user_sheet_hint_infos')[0]['point'], self.start_sheet_hint.point)
        self.assertEqual(content.get('user_sheet_hint_infos')[0]['hint'], '')
        self.assertEqual(content.get('user_sheet_hint_infos')[0]['image'], '')
        self.assertFalse(content.get('user_sheet_hint_infos')[0]['has_history'])

    def test_get_sheet_hint_infos_when_user_has_hint_history(self):
        # Given: 유저가 hint history 가 있을 경우
        self.user_sheet_hint_history = UserSheetHintHistory.objects.create(
            user=self.c.user,
            sheet_hint=self.start_sheet_hint,
        )

        # When: start_sheet hint 요청
        response = self.c.get(reverse('hint:sheet_hint', args=[self.start_sheet.id]))
        content = json.loads(response.content)

        # Then:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('user_sheet_hint_infos')[0]['id'], self.start_sheet_hint.id)
        self.assertEqual(content.get('user_sheet_hint_infos')[0]['point'], self.start_sheet_hint.point)
        self.assertEqual(content.get('user_sheet_hint_infos')[0]['hint'], self.start_sheet_hint.hint)
        self.assertEqual(content.get('user_sheet_hint_infos')[0]['image'], self.start_sheet_hint.image)
        self.assertTrue(content.get('user_sheet_hint_infos')[0]['has_history'])

    def test_get_sheet_hint_infos_should_raise_error_when_sheet_is_not_valid(self):
        # Given: Sheet 가 유효하지 않는 경우
        self.start_sheet.is_deleted = True
        self.start_sheet.save()

        # When: start_sheet hint 요청
        response = self.c.get(reverse('hint:sheet_hint', args=[self.start_sheet.id]))
        content = json.loads(response.content)

        # Then:
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), SheetDoesNotExists.default_detail)
