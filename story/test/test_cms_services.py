from django.test import TestCase
from django.db.models import Q

from account.models import User
from config.test_helper.helper import LoginMixin
from story.cms_services import (
    get_stories_qs,
    get_story_search_filter, get_active_sheets,
)
from story.models import Story, Sheet


class StoryFilterTestCase(TestCase):
    def test_get_stories_qs(self):
        # Given: No additional setup required for this test

        # When: Calling get_stories_qs function
        stories_qs = get_stories_qs()

        # Then: We should get a queryset of all stories
        self.assertEqual(stories_qs.count(), Story.objects.count())

    def test_get_story_search_filter(self):
        # Given: A search type and search value
        search_type = 'title'
        search_value = 'example'

        # When: Calling get_story_search_filter function
        search_filter = get_story_search_filter(search_type, search_value)

        # Then: We should get a valid Q object for title search
        self.assertIsInstance(search_filter, Q)
        self.assertEqual(search_filter, Q(title__icontains=search_value))

        # Given: A search type and search value for author
        search_type = 'author'
        search_value = 'admin'

        # When: Calling get_story_search_filter function
        search_filter = get_story_search_filter(search_type, search_value)

        # Then: We should get a valid Q object for author search
        self.assertIsInstance(search_filter, Q)
        self.assertEqual(search_filter, Q(author__nickname__icontains=search_value))

        # Given: An unsupported search type
        search_type = 'unsupported'
        search_value = 'example'

        # When: Calling get_story_search_filter function
        search_filter = get_story_search_filter(search_type, search_value)

        # Then: We should get an empty Q object
        self.assertIsInstance(search_filter, Q)
        self.assertEqual(search_filter, Q())


class GetActiveSheetsTest(LoginMixin, TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.active_sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=True,
            is_final=False,
        )
        self.deleted_sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_deleted=True,
            is_start=True,
            is_final=False,
        )

    def test_get_active_sheets(self):
        # When: 동작 실행
        active_sheets = get_active_sheets(self.story.id)

        # Then: 결과 확인
        self.assertEqual(len(active_sheets), 1)
        self.assertIn(self.active_sheet, active_sheets)
        self.assertNotIn(self.deleted_sheet, active_sheets)
