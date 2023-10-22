import json

from django.test import TestCase
from django.urls import reverse

from account.models import User
from config.test_helper.helper import LoginMixin
from story.models import (
    Story,
    Sheet,
    SheetAnswer,
    NextSheetPath,
)


class CMSStoryListAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(CMSStoryListAPIViewTestCase, self).setUp()
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
        self.start_sheet_answer1 = SheetAnswer.objects.create(
            sheet=self.start_sheet,
            answer='test',
            answer_reply='test_reply',
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
            sheet=self.final_sheet,
            quantity=10,
        )

    def test_get_cms_story_api_should_success(self):
        # Given: 관리자 로그인
        self.cms_login()

        # When: cms 요청
        response = self.c.get(reverse('cms_story:story_cms'))
        content = json.loads(response.content)

        # Then: Story 조회 성공
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_count', content)
        self.assertIn('stories', content)
        self.assertEqual(content['total_count'], 1)
        self.assertEqual(len(content['stories']), 1)
        story = content['stories'][0]
        self.assertEqual(story['id'], self.story.id)

    def test_get_cms_story_api_should_fail_when_not_admin_user(self):
        # Given: 일반 로그인
        self.login()

        # When: cms 요청
        response = self.c.get(reverse('cms_story:story_cms'))
        content = json.loads(response.content)

        # Then: 403 반환
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content['message'], 'No Auth')

    def test_get_cms_story_api_should_fail_when_not_login(self):
        # Given: 로그인 안함
        self.logout()

        # When: cms 요청
        response = self.c.get(reverse('cms_story:story_cms'))
        content = json.loads(response.content)

        # Then: 401 반환
        self.assertEqual(response.status_code, 401)
        self.assertEqual(content['message'], 'No Auth')


class CMSStorySheetMapAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(CMSStorySheetMapAPIViewTestCase, self).setUp()
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
        self.start_sheet_answer1 = SheetAnswer.objects.create(
            sheet=self.start_sheet,
            answer='test',
            answer_reply='test_reply',
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
            sheet=self.final_sheet,
            quantity=10,
        )

    def test_get_cms_story_sheet_map_api_should_success(self):
        # Given: 관리자 로그인
        self.cms_login()

        # When: cms 요청
        response = self.c.get(reverse('cms_story:sheet_cms_map', kwargs={'story_id': self.story.id}))
        content = json.loads(response.content)

        # Then: Sheets 조회 성공
        self.assertEqual(response.status_code, 200)
        self.assertIn('sheets', content)

    def test_get_cms_story_sheet_map_api_should_fail_when_not_admin_user(self):
        # Given: 일반 로그인
        self.login()

        # When: cms 요청
        response = self.c.get(reverse('cms_story:sheet_cms_map', kwargs={'story_id': self.story.id}))
        content = json.loads(response.content)

        # Then: 403 반환
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content['message'], 'No Auth')

    def test_get_cms_story_sheet_map_api_should_fail_when_not_login(self):
        # Given: 로그인 안함
        self.logout()

        # When: cms 요청
        response = self.c.get(reverse('cms_story:sheet_cms_map', kwargs={'story_id': self.story.id}))
        content = json.loads(response.content)

        # Then: 401 반환
        self.assertEqual(response.status_code, 401)
        self.assertEqual(content['message'], 'No Auth')


class CMSStorySheetAnswerMapAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(CMSStorySheetAnswerMapAPIViewTestCase, self).setUp()
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
        self.start_sheet_answer1 = SheetAnswer.objects.create(
            sheet=self.start_sheet,
            answer='test',
            answer_reply='test_reply',
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
            sheet=self.final_sheet,
            quantity=10,
        )

    def test_get_cms_story_answer_map_api_should_success(self):
        # Given: 관리자 로그인
        self.cms_login()

        # When: cms 요청
        response = self.c.get(reverse('cms_story:answer_cms_map', kwargs={'story_id': self.story.id}))
        content = json.loads(response.content)

        # Then: Sheets 조회 성공
        self.assertEqual(response.status_code, 200)
        self.assertIn('answers', content)

    def test_get_cms_story_answer_map_api_should_fail_when_not_admin_user(self):
        # Given: 일반 로그인
        self.login()

        # When: cms 요청
        response = self.c.get(reverse('cms_story:answer_cms_map', kwargs={'story_id': self.story.id}))
        content = json.loads(response.content)

        # Then: 403 반환
        self.assertEqual(response.status_code, 403)
        self.assertEqual(content['message'], 'No Auth')

    def test_get_cms_story_answer_map_api_should_fail_when_not_login(self):
        # Given: 로그인 안함
        self.logout()

        # When: cms 요청
        response = self.c.get(reverse('cms_story:answer_cms_map', kwargs={'story_id': self.story.id}))
        content = json.loads(response.content)

        # Then: 401 반환
        self.assertEqual(response.status_code, 401)
        self.assertEqual(content['message'], 'No Auth')
