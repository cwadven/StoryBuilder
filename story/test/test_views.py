import json

from django.test import Client, TestCase
from django.urls import reverse

from account.models import User
from config.test_helper.helper import LoginMixin
from story.models import Story, Sheet, SheetAnswer, NextSheetPath, UserStorySolve


class StoryPlayAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(StoryPlayAPIViewTestCase, self).setUp()
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

    def test_get_story_play_api_should_create_user_story_solve_when_user_is_authenticated(self):
        # Given: 로그인
        self.login()

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
        # And: 로그인 한 유저의 UserStorySolve 존재
        self.assertTrue(UserStorySolve.objects.filter(user=self.c.user, status=UserStorySolve.STATUS_CHOICES[0][0]).exists())


class SheetAnswerCheckAPIViewViewTestCase(TestCase):
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
        self.start_sheet_answer1 = SheetAnswer.objects.create(
            sheet=self.start_sheet,
            answer='test',
            answer_reply='test_reply',
        )
        self.start_sheet_answer2 = SheetAnswer.objects.create(
            sheet=self.start_sheet,
            answer='test2',
            answer_reply='test_reply2',
        )
        self.final_sheet1 = Sheet.objects.create(
            story=self.story,
            title='test_title1',
            question='test_question1',
            image='https://image.test',
            background_image='https://image.test',
            is_start=False,
            is_final=True,
        )
        self.final_sheet2 = Sheet.objects.create(
            story=self.story,
            title='test_title2',
            question='test_question2',
            image='https://image.test',
            background_image='https://image.test',
            is_start=False,
            is_final=True,
        )
        self.start_sheet_answer_next_sheet_path1 = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet1,
            quantity=10,
        )
        self.start_sheet_answer_next_sheet_path2 = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet2,
            quantity=0,
        )
        self.request_data = {
            'sheet_id': self.start_sheet.id,
            'answer': self.start_sheet_answer1.answer,
        }

    def test_get_story_next_sheet_when_answer_is_valid(self):
        # Given: start_sheet_answer1 정답과 sheet_id 명시
        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: 조회 성공
        self.assertTrue(response.status_code, 200)
        # And: 정답은 참
        self.assertTrue(content.get('is_valid'))
        # And: 정답이 start_sheet_answer1 이기 때문에 해당 quantity 10인 final_sheet1 을 선택
        self.assertTrue(content.get('next_sheet_id'), self.final_sheet1.id)
        # And: 정답 응답 확인
        self.assertTrue(content.get('answer_reply'), self.start_sheet_answer1.answer_reply)

    def test_get_story_next_sheet_when_answer_is_invalid(self):
        # Given: sheet_id 에 대해 오답 명시
        self.request_data['answer'] = '오답'

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: 조회 성공
        self.assertTrue(response.status_code, 200)
        # And: 정답은 거짓
        self.assertFalse(content.get('is_valid'))
        # And: 정답이 아니어서 None 반환
        self.assertIsNone(content.get('next_sheet_id'))
        self.assertIsNone(content.get('answer_reply'))

    def test_get_story_next_sheet_should_fail_when_sheet_is_deleted(self):
        # Given: sheet 삭제 됐을 경우
        self.start_sheet.is_deleted = True
        self.start_sheet.save()

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: Sheet 삭제되어서 Error 반환
        self.assertTrue(response.status_code, 400)
        self.assertTrue(content.get('error'), '존재하지 않은 Sheet 입니다.')

    def test_get_story_next_sheet_should_fail_when_story_is_not_displayable(self):
        # Given: sheet 삭제 됐을 경우
        self.start_sheet.story.displayable = False
        self.start_sheet.story.save()

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: Story 삭제 되어서 Error 반환
        self.assertTrue(response.status_code, 400)
        self.assertTrue(content.get('error'), '존재하지 않은 Sheet 입니다.')

    def test_get_story_next_sheet_should_fail_when_story_is_deleted(self):
        # Given: sheet 삭제 됐을 경우
        self.start_sheet.story.is_deleted = True
        self.start_sheet.story.save()

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: Story 비활성화 되어서 Error 반환
        self.assertTrue(response.status_code, 400)
        self.assertTrue(content.get('error'), '존재하지 않은 Sheet 입니다.')
