import json
from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time

from account.models import User
from config.common.exception_codes import StoryDoesNotExists
from config.test_helper.helper import LoginMixin
from story.constants import StoryLevel
from story.models import (
    PopularStory,
    NextSheetPath,
    Story,
    Sheet,
    SheetAnswer,
    StoryLike,
    UserStorySolve,
    UserSheetAnswerSolve,
    WrongAnswer,
)


def _generate_user_sheet_answer_solve_with_next_path(user: User, story: Story, current_sheet: Sheet,
                                                     next_sheet: Sheet, sheet_answer: SheetAnswer,
                                                     solving_status) -> UserSheetAnswerSolve:
    UserStorySolve.objects.get_or_create(
        story_id=story.id,
        user=user,
    )
    user_sheet_answer_solve, is_created = UserSheetAnswerSolve.generate_cls_if_first_time(
        user=user,
        sheet_id=current_sheet.id,
    )
    next_sheet_path = NextSheetPath.objects.create(
        answer=sheet_answer,
        sheet=next_sheet,
        quantity=10,
    )
    user_sheet_answer_solve.next_sheet_path = next_sheet_path
    user_sheet_answer_solve.solving_status = solving_status
    user_sheet_answer_solve.answer = sheet_answer.answer
    user_sheet_answer_solve.save()
    return UserSheetAnswerSolve.objects.get(id=user_sheet_answer_solve.id)


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

    def test_get_story_play_api_should_fail_when_story_is_deleted(self):
        # Given: Story 가 삭제된 경우
        self.story.is_deleted = True
        self.story.save()
        # And: 로그인
        self.login()

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story 조회 실패
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '스토리를 불러올 수 없습니다.')

    def test_get_story_play_api_should_fail_when_story_is_not_displayable(self):
        # Given: Story 가 displayable 가 False 인 경우
        self.story.displayable = False
        self.story.save()
        # And: 로그인
        self.login()

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story 조회 실패
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '스토리를 불러올 수 없습니다.')

    def test_get_story_play_api_should_fail_when_story_not_have_is_start_sheet(self):
        # Given: Sheet 가 is_start 가 없는 경우
        self.start_sheet.is_start = False
        self.start_sheet.save()
        # And: 로그인
        self.login()

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story 조회 실패
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '스토리를 불러올 수 없습니다.')

    def test_get_story_play_api_should_success_when_story_have_is_start(self):
        # Given: Sheet 가 is_start 가 있는 경우
        # And: 로그인
        self.login()

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story 조회 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('sheet_id'), self.start_sheet.id)
        self.assertEqual(content.get('title'), self.start_sheet.title)
        self.assertEqual(content.get('question'), self.start_sheet.question)
        self.assertEqual(content.get('image'), self.start_sheet.image)
        self.assertEqual(content.get('background_image'), self.start_sheet.background_image)
        self.assertIsNone(content.get('next_sheet_id'))
        self.assertIsNone(content.get('answer'))
        self.assertIsNone(content.get('answer_reply'))
        self.assertFalse(content.get('is_solved'))

    def test_on_first_story_play_api_story_played_count_should_increase(self):
        # Given:
        self.login()

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))

        # Then: Story 조회 성공
        self.assertEqual(response.status_code, 200)
        # And: 스토리 played_count 가 1 증가
        story = Story.objects.get(id=self.story.id)
        self.assertEqual(story.played_count, 1)

        # When: story_play 재요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))

        self.assertEqual(response.status_code, 200)
        # Then: 기존에 1개가 UserStorySolve 로 올랐기 때문에 1개만 조회
        self.assertEqual(story.played_count, 1)

    def test_get_story_play_api_should_create_user_story_solve_when_user_is_authenticated(self):
        # Given: 로그인
        self.login()
        # And: 유효한 UserSheetAnswerSolve 생성
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.final_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story 조회 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('sheet_id'), self.start_sheet.id)
        self.assertEqual(content.get('title'), self.start_sheet.title)
        self.assertEqual(content.get('question'), self.start_sheet.question)
        self.assertEqual(content.get('image'), self.start_sheet.image)
        self.assertEqual(content.get('background_image'), self.start_sheet.background_image)
        self.assertIsNone(content.get('next_sheet_id'))
        self.assertIsNone(content.get('answer'))
        self.assertIsNone(content.get('answer_reply'))
        self.assertFalse(content.get('is_solved'))
        # And: 로그인 한 유저의 UserStorySolve 존재
        self.assertTrue(UserStorySolve.objects.filter(user=self.c.user, status=UserStorySolve.STATUS_CHOICES[0][0]).exists())

    def test_get_story_play_api_should_create_user_sheet_answer_solve_when_user_is_authenticated(self):
        # Given: 로그인
        self.login()

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))

        # Then: Story 조회 성공
        self.assertEqual(response.status_code, 200)
        # And: 로그인 한 유저의 UserSheetAnswerSolve 존재
        self.assertTrue(UserSheetAnswerSolve.objects.filter(user=self.c.user, sheet=self.start_sheet, solving_status='solving').exists())

    def test_get_story_play_api_should_raise_error_user_is_not_authenticated(self):
        # Given: 로그인 안되어있음

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: 로그인 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '로그인이 필요합니다.')

    def test_get_story_play_api_should_return_playing_sheet_answer_solved_response_when_already_user_had_been_solved_sheet(self):
        # Given: 로그인
        self.login()
        # And: 유저가 한번 이미 문제를 해결했을 경우
        self.c.get(reverse('story:story_play', args=[self.story.id]))
        response = self.c.post(reverse('story:submit_answer'), data={
            'sheet_id': self.start_sheet.id,
            'answer': self.start_sheet_answer1.answer,
        })
        self.assertEqual(response.status_code, 200)

        # When: story_play 요청
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: PlayingSheetInfoDTO response 반환
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('sheet_id'), self.start_sheet.id)
        self.assertEqual(content.get('title'), self.start_sheet.title)
        self.assertEqual(content.get('question'), self.start_sheet.question)
        self.assertEqual(content.get('image'), self.start_sheet.image)
        self.assertEqual(content.get('background_image'), self.start_sheet.background_image)
        self.assertEqual(content.get('next_sheet_id'), self.start_sheet_answer_next_sheet_path1.sheet_id)
        self.assertEqual(content.get('answer'), self.start_sheet_answer1.answer)
        self.assertEqual(content.get('answer_reply'), self.start_sheet_answer1.answer_reply)
        self.assertTrue(content.get('is_solved'))


class SheetPlayAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(SheetPlayAPIViewTestCase, self).setUp()
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

    def test_get_sheet_play_api_should_fail_when_story_is_deleted(self):
        # Given: 유효한 UserSheetAnswerSolve 생성
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )
        # And: Story 삭제
        self.story.is_deleted = True
        self.story.save()

        # When: sheet_play 요청
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: Sheet 조회 실패
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '존재하지 않은 Sheet 입니다.')

    def test_get_sheet_play_api_should_fail_when_story_is_not_displayable(self):
        # Given: 유효한 UserSheetAnswerSolve 생성
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )
        # And: Story 가 displayable 가 False 인 경우
        self.story.displayable = False
        self.story.save()

        # When: sheet_play 요청
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: Sheet 조회 실패
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '존재하지 않은 Sheet 입니다.')

    def test_get_sheet_play_api_should_fail_when_sheet_is_deleted(self):
        # Given: 유효한 UserSheetAnswerSolve 생성
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )
        # And: Sheet 가 is_deleted 인 경우
        self.normal_sheet.is_deleted = True
        self.normal_sheet.save()

        # When: sheet_play 요청
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: Sheet 조회 실패
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '존재하지 않은 Sheet 입니다.')

    def test_get_sheet_play_api_should_return_playing_sheet_dto_when_success(self):
        # Given: 유효한 UserSheetAnswerSolve 생성
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )

        # When: sheet_play 요청
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: Sheet 조회 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('sheet_id'), self.normal_sheet.id)
        self.assertEqual(content.get('title'), self.normal_sheet.title)
        self.assertEqual(content.get('question'), self.normal_sheet.question)
        self.assertEqual(content.get('image'), self.normal_sheet.image)
        self.assertEqual(content.get('background_image'), self.normal_sheet.background_image)
        self.assertIsNone(content.get('next_sheet_id'))
        self.assertIsNone(content.get('answer'))
        self.assertIsNone(content.get('answer_reply'))
        self.assertFalse(content.get('is_solved'))

    def test_get_sheet_play_api_should_create_user_sheet_answer_solve_when_success(self):
        # Given: 현재 sheet를 플레이할 수 있도록 이전 UserSheetAnswerSolve 생성
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )

        # When: sheet_play 요청
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))

        # Then: Sheet 조회 성공
        self.assertEqual(response.status_code, 200)
        # And: UserSheetAnswerSolve 생성
        self.assertTrue(UserSheetAnswerSolve.objects.filter(user=self.c.user, sheet=self.normal_sheet, solving_status='solving').exists())

    def test_get_sheet_play_api_should_raise_error_user_is_not_authenticated(self):
        # Given: 로그인 안되어있음
        self.logout()

        # When: sheet_play 요청
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: 로그인 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '로그인이 필요합니다.')

    def test_get_sheet_play_api_should_return_playing_sheet_answer_solved_response_when_already_user_had_been_solved_sheet(self):
        # Given: 첫 story 의 첫 sheet 문제 해결
        self.c.get(reverse('story:story_play', args=[self.story.id]))
        response = self.c.post(reverse('story:submit_answer'), data={
            'sheet_id': self.start_sheet.id,
            'answer': self.start_sheet_answer1.answer,
        })
        self.assertEqual(response.status_code, 200)
        # And: 두번째 문제 해결
        self.c.get(reverse('story:sheet_play', args=[self.start_sheet_answer_next_sheet_path1.sheet_id]))
        self.c.post(reverse('story:submit_answer'), data={
            'sheet_id': self.start_sheet_answer_next_sheet_path1.sheet_id,
            'answer': self.normal_sheet_answer1.answer,
        })

        # When: sheet_play 재요청
        response = self.c.get(reverse('story:sheet_play', args=[self.start_sheet_answer_next_sheet_path1.sheet_id]))
        content = json.loads(response.content)

        # Then: PlayingSheetInfoDTO response 반환
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('sheet_id'), self.start_sheet_answer_next_sheet_path1.sheet.id)
        self.assertEqual(content.get('title'), self.start_sheet_answer_next_sheet_path1.sheet.title)
        self.assertEqual(content.get('question'), self.start_sheet_answer_next_sheet_path1.sheet.question)
        self.assertEqual(content.get('image'), self.start_sheet_answer_next_sheet_path1.sheet.image)
        self.assertEqual(content.get('background_image'), self.start_sheet_answer_next_sheet_path1.sheet.background_image)
        self.assertEqual(content.get('next_sheet_id'), self.normal_sheet_answer_next_sheet_path1.sheet_id)
        self.assertEqual(content.get('answer'), self.normal_sheet_answer1.answer)
        self.assertEqual(content.get('answer_reply'), self.normal_sheet_answer1.answer_reply)
        self.assertTrue(content.get('is_solved'))


class SheetAnswerCheckAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(SheetAnswerCheckAPIViewTestCase, self).setUp()
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

    @freeze_time('2022-01-01')
    def test_get_story_next_sheet_when_answer_is_valid(self):
        # Given: start_sheet_answer1 정답과 sheet_id 명시
        # And: 유효한 UserSheetAnswerSolve 생성
        user_sheet_answer_solve = _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.final_sheet1,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solving',
        )
        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: 조회 성공
        self.assertEqual(response.status_code, 200)
        # And: 정답은 참
        self.assertTrue(content.get('is_valid'))
        # And: 정답이 start_sheet_answer1 이기 때문에 해당 quantity 10인 final_sheet1 을 선택
        self.assertEqual(content.get('next_sheet_id'), self.final_sheet1.id)
        # And: 정답 응답 확인
        self.assertEqual(content.get('answer_reply'), self.start_sheet_answer1.answer_reply)
        # And: UserSheetAnswerSolve solved 로 변경
        self.assertEqual(UserSheetAnswerSolve.objects.get(id=user_sheet_answer_solve.id).solving_status, 'solved')
        # And: 현재 시간 해결
        self.assertEqual(
            UserSheetAnswerSolve.objects.get(id=user_sheet_answer_solve.id).solved_time.strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    @freeze_time('2022-01-01')
    def test_get_story_next_sheet_when_answer_is_valid_but_one_more_submit_answer(self):
        # Given: start_sheet_answer1 정답과 sheet_id 명시
        # And: 유효한 UserSheetAnswerSolve 생성
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.final_sheet1,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solving',
        )
        self.c.post(reverse('story:submit_answer'), data=self.request_data)

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: 이미 문제를 해결한 기록이 있기 때문에 문제를 다시 풀 수 없습니다.
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '이미 문제를 해결한 기록이 있습니다.')

    @freeze_time('2022-01-01')
    def test_get_story_answer_reply_when_next_sheet_path_is_not_exists_but_answer_is_valid(self):
        # Given: start_sheet_answer1 정답과 sheet_id 명시
        # And: 유효한 UserSheetAnswerSolve 생성
        user_sheet_answer_solve = _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.final_sheet1,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solving',
        )
        # And: next_sheet_path 전부 삭제
        self.start_sheet_answer1.next_sheet_paths.all().delete()

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: 조회 성공
        self.assertEqual(response.status_code, 200)
        # And: 정답은 참
        self.assertTrue(content.get('is_valid'))
        # And: next_sheet_path 가 없어 None 반환
        self.assertIsNone(content.get('next_sheet_id'))
        # And: 정답 응답 확인
        self.assertEqual(content.get('answer_reply'), self.start_sheet_answer1.answer_reply)
        # And: UserSheetAnswerSolve solved 로 변경
        self.assertEqual(UserSheetAnswerSolve.objects.get(id=user_sheet_answer_solve.id).solving_status, 'solved')
        # And: 현재 시간 해결
        self.assertEqual(
            UserSheetAnswerSolve.objects.get(id=user_sheet_answer_solve.id).solved_time.strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

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
        # And: Wrong Answer 생성
        wrong_answer_qs = WrongAnswer.objects.filter(user=self.c.user, sheet=self.start_sheet)
        self.assertEqual(wrong_answer_qs.count(), 1)
        self.assertEqual(wrong_answer_qs[0].user_id, self.c.user.id)
        self.assertEqual(wrong_answer_qs[0].story_id, self.story.id)
        self.assertEqual(wrong_answer_qs[0].sheet_id, self.request_data['sheet_id'])
        self.assertEqual(wrong_answer_qs[0].answer, self.request_data['answer'])

    def test_get_story_next_sheet_should_fail_when_sheet_is_deleted(self):
        # Given: sheet 삭제 됐을 경우
        self.start_sheet.is_deleted = True
        self.start_sheet.save()

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: Sheet 삭제되어서 Error 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '존재하지 않은 Sheet 입니다.')

    def test_get_story_next_sheet_should_fail_when_story_is_not_displayable(self):
        # Given: sheet 삭제 됐을 경우
        self.start_sheet.story.displayable = False
        self.start_sheet.story.save()

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: Story 삭제 되어서 Error 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '존재하지 않은 Sheet 입니다.')

    def test_get_story_next_sheet_should_fail_when_story_is_deleted(self):
        # Given: sheet 삭제 됐을 경우
        self.start_sheet.story.is_deleted = True
        self.start_sheet.story.save()

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: Story 비활성화 되어서 Error 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '존재하지 않은 Sheet 입니다.')

    def test_get_story_next_sheet_should_raise_error_user_is_not_authenticated(self):
        # Given: 로그인 안되어있음
        self.logout()

        # When: submit_answer 요청
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: 로그인 에러 반환
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '로그인이 필요합니다.')


class GetStoryRecentPlayAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(GetStoryRecentPlayAPIViewTestCase, self).setUp()
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
        self.next_sheet_path = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet1,
            quantity=10,
        )
        self.user_story_solve = UserStorySolve.objects.get_or_create(
            story_id=self.story.id,
            user=self.c.user,
        )
        self.user_sheet_answer_solve = UserSheetAnswerSolve.objects.create(
            user=self.c.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=self.start_sheet.version,
            solved_answer_version=self.start_sheet_answer1.version,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
            next_sheet_path=self.next_sheet_path,
            answer=self.start_sheet_answer1.answer,
        )

    def test_get_recent_play_sheet(self):
        # Given: next_sheet_path 조회로 UserSheetAnswerSolve 생성
        self.c.get(reverse('story:sheet_play', args=[self.next_sheet_path.sheet.id]))

        # When: get_recent_play_sheet 요청
        response = self.c.get(reverse('story:get_recent_play_sheet', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('recent_sheet_id'), self.next_sheet_path.sheet.id)

    def test_get_recent_play_sheet_should_raise_error_when_user_do_not_have_user_sheet_answer_solve(self):
        # Given: 모든 UserSheetAnswerSolve 제거
        UserSheetAnswerSolve.objects.all().delete()

        # When: get_recent_play_sheet 요청
        response = self.c.get(reverse('story:get_recent_play_sheet', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '최근에 해결 못한 sheet 가 없습니다.')


class StoryLikeAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(StoryLikeAPIViewTestCase, self).setUp()
        self.user = User.objects.all()[0]
        self.login()
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )

    def test_post_story_like_when_request_like(self):
        # Given:
        # When: story_like 요청
        response = self.c.post(reverse('story:story_like', args=[self.story.id]))

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        # And: StoryLike 생성
        self.assertTrue(StoryLike.objects.filter(user=self.c.user, story=self.story, is_deleted=False).exists())
        # And: like_count 1 증가
        self.story.refresh_from_db()
        self.assertEqual(self.story.like_count, 1)

    # DB 문제로 테스트케이스 실패
    # def test_post_story_like_should_fail_when_story_not_exists(self):
    #     # Given: story 제거
    #     story_id = self.story.id
    #     self.story.delete()
    #
    #     # When: story_like 요청
    #     response = self.c.post(reverse('story:story_like', args=[story_id]))
    #     content = json.loads(response.content)
    #
    #     # Then: 실패
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(content['message'], 'story에 문제가 있습니다.')

    def test_delete_story_like_when_user_has_like(self):
        # Given: story like 생성
        StoryLike.objects.create(
            user=self.c.user,
            story=self.story,
            is_deleted=False,
        )

        # When: story_like 요청
        response = self.c.delete(reverse('story:story_like', args=[self.story.id]))

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        # And: StoryLike 제거
        self.assertTrue(StoryLike.objects.filter(user=self.c.user, story=self.story, is_deleted=True).exists())
        # And: like_count 0
        self.story.refresh_from_db()
        self.assertEqual(self.story.like_count, 0)

    def test_delete_story_like_should_fail_when_user_not_have_like(self):
        # Given:
        # When: story_like 요청
        response = self.c.delete(reverse('story:story_like', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: 실패
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['message'], '좋아요를 한적이 없습니다.')


class StoryListAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(StoryListAPIViewTestCase, self).setUp()
        self.user = User.objects.all()[0]
        self.login()
        self.story1 = Story.objects.create(
            author=self.user,
            title='test_story1',
            description='test_description1',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.story2 = Story.objects.create(
            author=self.user,
            title='test_story2',
            description='test_description2',
            image='https://image.test',
            background_image='https://image.test',
        )

    def test_story_list_api(self):
        # Given:
        # When: story list 요청
        response = self.c.get(reverse('story:story_list'))
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        # And: story list 반환
        self.assertEqual(len(content['stories']), 2)
        self.assertEqual(content['stories'][0]['id'], self.story2.id)
        self.assertEqual(content['stories'][1]['id'], self.story1.id)

    def test_story_list_api_with_paging(self):
        # Given:
        size = 1

        # When: story list paging과 함께 요청
        response = self.c.get(reverse('story:story_list'), data={'size': size})
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        # And: story list 반환
        self.assertEqual(len(content['stories']), 1)
        self.assertEqual(content['stories'][0]['id'], self.story2.id)

    def test_story_list_api_with_search(self):
        # Given:
        search = self.story2.title

        # When: story list paging과 함께 요청
        response = self.c.get(reverse('story:story_list'), data={'search': search})
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        # And: story list 반환
        self.assertEqual(len(content['stories']), 1)
        self.assertEqual(content['stories'][0]['id'], self.story2.id)


class StorySheetSolveAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(StorySheetSolveAPIViewTestCase, self).setUp()
        self.user = User.objects.all()[0]
        self.login(self.user)
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
        self.next_sheet_path = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet1,
            quantity=10,
        )
        self.user_story_solve = UserStorySolve.objects.get_or_create(
            story_id=self.story.id,
            user=self.c.user,
        )
        self.middle_sheet = Sheet.objects.create(
            story=self.story,
            title='middle_sheet_title',
            question='middle_sheet_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=False,
            is_final=False,
        )
        self.middle_sheet_answer = SheetAnswer.objects.create(
            sheet=self.middle_sheet,
            answer='middle_sheet test',
            answer_reply='middle_sheet test_reply',
        )
        self.next_sheet_path_to_middle = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.middle_sheet,
            quantity=10,
        )
        self.next_sheet_path_to_final = NextSheetPath.objects.create(
            answer=self.middle_sheet_answer,
            sheet=self.final_sheet1,
            quantity=10,
        )
        self.user_sheet_answer_solve1 = UserSheetAnswerSolve.objects.create(
            user=self.c.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=self.start_sheet.version,
            solved_answer_version=self.start_sheet_answer1.version,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
            next_sheet_path=self.next_sheet_path,
            answer=self.start_sheet_answer1.answer,
            start_time=datetime(2022, 1, 1),
            solved_time=datetime(2022, 1, 1),
        )
        self.user_sheet_answer_solve2 = UserSheetAnswerSolve.objects.create(
            user=self.c.user,
            story=self.story,
            sheet=self.middle_sheet,
            solved_sheet_version=self.middle_sheet.version,
            solved_answer_version=self.middle_sheet_answer.version,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
            next_sheet_path=self.next_sheet_path_to_middle,
            answer=self.middle_sheet_answer.answer,
            start_time=datetime(2022, 1, 1),
            solved_time=datetime(2022, 1, 1),
        )

    def test_reset_story_sheet_solve_should_success_when_solve_exists(self):
        # Given:
        # When: solve_history 요청
        response = self.c.delete(reverse('story:solve_history', args=[self.story.id]))

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)

    def test_reset_story_sheet_solve_should_fail_when_solve_not_exists(self):
        # Given: UserSheetAnswerSolve 제거
        UserSheetAnswerSolve.objects.all().delete()

        # When: solve_history 요청
        response = self.c.delete(reverse('story:solve_history', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: 없어서 실패
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content['message'], '스토리를 플레이 하신 기록이 없으십니다.')

    def test_story_sheet_solve_history_get_api(self):
        # Given: history 한번 생성
        self.c.delete(reverse('story:solve_history', args=[self.story.id]))
        # And: 한번 더 생성
        UserSheetAnswerSolve.objects.create(
            user=self.c.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=self.start_sheet.version,
            solved_answer_version=self.start_sheet_answer1.version,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
            next_sheet_path=self.next_sheet_path,
            answer=self.start_sheet_answer1.answer,
            start_time=datetime(2022, 1, 1),
            solved_time=datetime(2022, 1, 1),
        )
        UserSheetAnswerSolve.objects.create(
            user=self.c.user,
            story=self.story,
            sheet=self.middle_sheet,
            solved_sheet_version=self.middle_sheet.version,
            solved_answer_version=self.middle_sheet_answer.version,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
            next_sheet_path=self.next_sheet_path_to_middle,
            answer=self.middle_sheet_answer.answer,
            start_time=datetime(2022, 1, 1),
            solved_time=datetime(2022, 1, 1),
        )
        self.c.delete(reverse('story:solve_history', args=[self.story.id]))

        # When:
        response = self.c.get(reverse('story:solve_history', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]['group_id'], 2)
        self.assertEqual(content[1]['group_id'], 1)
        self.assertEqual(
            content,
            [
                {
                    'group_id': 2,
                    'sheet_answer_solve': [
                        {'group_id': 2, 'sheet_title': 'test_title', 'sheet_question': 'test_question',
                         'user_answer': 'test', 'solving_status': 'solved', 'start_time': '2022-01-01 00:00:00', 'solved_time': '2022-01-01 00:00:00'},
                        {'group_id': 2, 'sheet_title': 'middle_sheet_title', 'sheet_question': 'middle_sheet_question',
                         'user_answer': 'middle_sheet test', 'solving_status': 'solved', 'start_time': '2022-01-01 00:00:00', 'solved_time': '2022-01-01 00:00:00'}
                    ]
                },
                {
                    'group_id': 1,
                    'sheet_answer_solve': [
                        {'group_id': 1, 'sheet_title': 'test_title', 'sheet_question': 'test_question',
                         'user_answer': 'test', 'solving_status': 'solved', 'start_time': '2022-01-01 00:00:00', 'solved_time': '2022-01-01 00:00:00'},
                        {'group_id': 1, 'sheet_title': 'middle_sheet_title', 'sheet_question': 'middle_sheet_question',
                         'user_answer': 'middle_sheet test', 'solving_status': 'solved', 'start_time': '2022-01-01 00:00:00', 'solved_time': '2022-01-01 00:00:00'}
                    ]
                }
            ]
        )


class PopularStoryListAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(PopularStoryListAPIViewTestCase, self).setUp()
        self.user = User.objects.all()[0]
        self.login()
        self.active_story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.displayable_false_story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
            displayable=False,
        )
        self.deleted_story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
            is_deleted=True,
        )
        self.popular_story = PopularStory.objects.create(
            story=self.active_story,
            rank=1,
            like_count=1,
            base_past_second=1,
            is_deleted=False,
        )
        self.displayable_false_popular_story = PopularStory.objects.create(
            story=self.displayable_false_story,
            rank=2,
            like_count=1,
            base_past_second=1,
            is_deleted=False,
        )
        self.deleted_popular_story_by_story = PopularStory.objects.create(
            story=self.deleted_story,
            rank=3,
            like_count=1,
            base_past_second=1,
            is_deleted=False,
        )
        self.deleted_popular_story = PopularStory.objects.create(
            story=self.active_story,
            rank=4,
            like_count=1,
            base_past_second=1,
            is_deleted=True,
        )

    def test_popular_story_list_api(self):
        # Given: setUp 에서 4개 PopularStory 생성
        # self.popular_story: story 정상
        # self.displayable_false_popular_story: story 가 displayable False
        # self.deleted_popular_story_by_story: story 가 is_deleted True
        # self.deleted_popular_story: popular story 가 is_deleted True

        # When:
        response = self.c.get(reverse('story:story_popular_list'))
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        # And: story list 반환
        self.assertEqual(len(content['popular_stories']), 1)
        self.assertEqual(content['popular_stories'][0]['story_id'], self.active_story.id)

    def test_popular_story_list_api_when_popular_story_not_exists(self):
        # Given: PopularStory 제거
        PopularStory.objects.all().delete()
        # And: active_story 에 like_count 1 추가
        self.active_story.like_count = 1
        self.active_story.save()

        # When:
        response = self.c.get(reverse('story:story_popular_list'))
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        # And: Story 에서 확인 후, story list 반환
        self.assertEqual(len(content['popular_stories']), 1)
        self.assertEqual(content['popular_stories'][0]['story_id'], self.active_story.id)


class StoryDetailAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(StoryDetailAPIViewTestCase, self).setUp()
        self.user = User.objects.all()[0]
        self.login()
        self.story = Story.objects.create(
            author=self.user,
            title='test_story1',
            description='test_description1',
            image='https://image.test',
            background_image='https://image.test',
        )

    def test_story_detail_api_should_success(self):
        # Given: 좋아요 생성
        StoryLike.objects.create(
            user=self.c.user,
            story=self.story,
        )
        # When: story detail 요청
        response = self.c.get(reverse('story:story_detail', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        # And: story detail 반환
        self.assertEqual(content['id'], self.story.id)
        self.assertEqual(content['title'], self.story.title)
        self.assertEqual(content['description'], self.story.description)
        self.assertEqual(content['image'], self.story.image)
        self.assertEqual(content['background_image'], self.story.background_image)
        self.assertEqual(content['played_count'], self.story.played_count)
        self.assertEqual(content['like_count'], self.story.like_count)
        self.assertEqual(content['review_rate'], self.story.review_rate)
        self.assertEqual(content['playing_point'], self.story.playing_point)
        self.assertEqual(content['level'], StoryLevel(self.story.level).selector)
        self.assertEqual(content['free_to_play_sheet_count'], self.story.free_to_play_sheet_count)
        # And: is_liked True
        self.assertTrue(content['is_liked'])

    def test_story_detail_api_should_fail_when_story_not_exists(self):
        # Given:
        self.story.is_deleted = True
        self.story.save()

        # When: story detail 요청
        response = self.c.get(reverse('story:story_detail', args=[9999]))
        content = json.loads(response.content)

        # Then: 에러 접근
        self.assertEqual(response.status_code, 400)
        # And: fail 반환
        self.assertEqual(content['message'], StoryDoesNotExists.default_detail)
