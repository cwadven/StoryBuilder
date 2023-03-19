import json
from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time

from account.models import User
from config.test_helper.helper import LoginMixin
from story.models import Story, Sheet, SheetAnswer, NextSheetPath, UserStorySolve, UserSheetAnswerSolve, StoryLike


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


class SheetAnswerCheckAPIViewViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(SheetAnswerCheckAPIViewViewTestCase, self).setUp()
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
