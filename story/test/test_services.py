from django.test import TestCase
from rest_framework.exceptions import APIException

from account.models import User
from config.common.exception_codes import StartingSheetDoesNotExists
from story.models import Story, Sheet
from story.services import get_running_start_sheet_by_story


class GetSheetStoryTestCase(TestCase):
    def setUp(self):
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
        self.final_sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=False,
            is_final=True,
        )

    def test_get_running_start_sheet_by_story_should_fail_when_story_is_deleted(self):
        # Given: Story 가 삭제된 경우
        self.story.is_deleted = True
        self.story.save()

        # When: get_running_start_sheet_by_story 요청
        # Then: Story 조회 실패
        with self.assertRaises(StartingSheetDoesNotExists):
            get_running_start_sheet_by_story(self.story.id)

    def test_get_running_start_sheet_by_story_should_fail_when_story_is_not_displayable(self):
        # Given: Story 가 displayable 가 False 인 경우
        self.story.displayable = False
        self.story.save()

        # When: get_running_start_sheet_by_story 요청
        # Then: Story 조회 실패
        with self.assertRaises(StartingSheetDoesNotExists):
            get_running_start_sheet_by_story(self.story.id)

    def test_get_running_start_sheet_by_story_should_fail_when_story_not_have_is_start_sheet(self):
        # Given: Sheet 가 is_start 가 없는 경우
        self.start_sheet.is_start = False
        self.start_sheet.save()

        # When: get_running_start_sheet_by_story 요청
        # Then: Sheet 조회 실패
        with self.assertRaises(StartingSheetDoesNotExists):
            get_running_start_sheet_by_story(self.story.id)

    def test_get_running_start_sheet_by_story_should_success_when_story_have_is_start(self):
        # Given: Sheet 가 is_start 가 있는 경우

        # When: get_running_start_sheet_by_story 요청
        sheet = get_running_start_sheet_by_story(self.story.id)

        # Then: Sheet 조회 성공
        self.assertEqual(sheet.id, self.start_sheet.id)
