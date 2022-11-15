import json

from django.test import Client, TestCase
from django.urls import reverse

from rest_framework.exceptions import APIException

from account.models import User
from story.models import Story, Sheet
from story.services import get_running_start_sheet_by_story


class StoryPlayAPIViewTestCase(TestCase):
    def setUp(self):
        self.c = Client()
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

    def test_get_story_play_api_should_fail_when_story_is_deleted(self):
        # Given: Story 가 삭제된 경우
        self.story.is_deleted = True
        self.story.save()

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story 조회 실패
        self.assertTrue(response.status_code, 400)
        self.assertTrue(content.get('error'), '스토리를 불러올 수 없습니다.')

    def test_get_story_play_api_should_fail_when_story_is_not_displayable(self):
        # Given: Story 가 displayable 가 False 인 경우
        self.story.displayable = False
        self.story.save()

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story 조회 실패
        self.assertTrue(response.status_code, 400)
        self.assertTrue(content.get('error'), '스토리를 불러올 수 없습니다.')

    def test_get_story_play_api_should_fail_when_story_not_have_is_start_sheet(self):
        # Given: Sheet 가 is_start 가 없는 경우
        self.start_sheet.is_start = False
        self.start_sheet.save()

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story 조회 실패
        self.assertTrue(response.status_code, 400)
        self.assertTrue(content.get('error'), '스토리를 불러올 수 없습니다.')

    def test_get_story_play_api_should_success_when_story_have_is_start(self):
        # Given: Sheet 가 is_start 가 있는 경우

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story 조회 성공
        self.assertTrue(response.status_code, 200)
        self.assertTrue(content.get('id'), self.start_sheet.id)
        self.assertTrue(content.get('title'), self.start_sheet.title)
        self.assertTrue(content.get('question'), self.start_sheet.question)
        self.assertTrue(content.get('image'), self.start_sheet.image)
        self.assertTrue(content.get('background_image'), self.start_sheet.background_image)
