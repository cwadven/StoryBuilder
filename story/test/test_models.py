from datetime import datetime

from django.test import TestCase
from unittest.mock import patch, Mock
from freezegun import freeze_time

from account.models import User
from story.models import Sheet, Story, SheetAnswer, NextSheetPath, UserSheetAnswerSolve, UserStorySolve, \
    StoryEmailSubscription


class UserSheetAnswerSolveTestCase(TestCase):
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
        self.next_sheet_path = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet1,
            quantity=10,
        )

    @freeze_time('2022-05-31')
    def test_solved_sheet_action(self):
        # Given: 해결하지 못한 UserSheetAnswerSolve 생성
        user_sheet_answer_solve = UserSheetAnswerSolve.objects.create(
            user=self.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=1,
            solved_answer_version=1,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[0][0],
        )

        # When: solved_sheet_action 실행
        user_sheet_answer_solve.solved_sheet_action(
            solved_sheet_answer=self.start_sheet_answer1,
            next_sheet_path=self.next_sheet_path,
        )

        # Then:
        self.assertEqual(user_sheet_answer_solve.solving_status, UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0])
        self.assertEqual(user_sheet_answer_solve.solved_time, datetime.now())
        self.assertEqual(user_sheet_answer_solve.answer, self.start_sheet_answer1.answer)
        self.assertEqual(user_sheet_answer_solve.sheet_question, self.start_sheet.question)
        self.assertEqual(user_sheet_answer_solve.solved_sheet_version, self.start_sheet.version)
        self.assertEqual(user_sheet_answer_solve.solved_answer_version, self.start_sheet_answer1.version)
        self.assertEqual(user_sheet_answer_solve.next_sheet_path, self.next_sheet_path)
        self.assertEqual(user_sheet_answer_solve.solved_sheet_answer, self.start_sheet_answer1)

    @freeze_time('2022-05-31')
    @patch('story.models.send_user_sheet_solved_email.apply_async')
    def test_solved_sheet_action_when_success_then_send_user_sheet_solved_email(self, mock_send_user_sheet_solved_email):
        # Given: 해결하지 못한 UserSheetAnswerSolve 생성
        user_sheet_answer_solve = UserSheetAnswerSolve.objects.create(
            user=self.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=1,
            solved_answer_version=1,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[0][0],
        )
        # And: StoryEmailSubscription 생성
        StoryEmailSubscription.objects.create(
            story_id=self.story.id,
            respondent_user_id=self.user.id,
            email='cwadven@kakao.com',
        )

        # When: solved_sheet_action 실행
        user_sheet_answer_solve.solved_sheet_action(
            solved_sheet_answer=self.start_sheet_answer1,
            next_sheet_path=self.next_sheet_path,
        )

        # Then: 호출이 됐는지 확인
        mock_send_user_sheet_solved_email.assert_called_once()

    @freeze_time('2022-05-31')
    def test_generate_cls_if_first_time_should_create_user_sheet_answer_solve_when_not_exists(self):
        # Given: UserStorySolve 생성
        user_story_solve = UserStorySolve.objects.create(
            story=self.story,
            user=self.user,
        )

        # When: generate_cls_if_first_time 실행
        user_sheet_answer_solve, is_created = UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.start_sheet.id,
        )

        # Then:
        self.assertTrue(is_created)
        self.assertEqual(user_sheet_answer_solve.user, self.user)
        self.assertEqual(user_sheet_answer_solve.story, self.story)
        self.assertEqual(user_sheet_answer_solve.user_story_solve, user_story_solve)
        self.assertEqual(user_sheet_answer_solve.sheet, self.start_sheet)
        self.assertEqual(user_sheet_answer_solve.start_time, datetime.now())

    @freeze_time('2022-05-31')
    def test_generate_cls_if_first_time_should_not_create_when_already_exists(self):
        # Given: UserStorySolve 생성
        UserStorySolve.objects.create(
            story=self.story,
            user=self.user,
        )
        # And: generate_cls_if_first_time 한번 실행
        UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.start_sheet.id,
        )

        # When: generate_cls_if_first_time 또 실행
        user_sheet_answer_solve, is_created = UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.start_sheet.id,
        )

        # Then: 생성 된게 아닙니다.
        self.assertFalse(is_created)

    @freeze_time('2022-05-31')
    def test_generate_cls_if_first_time_should_return_none_if_user_story_solve_not_exists(self):
        # Given: UserStorySolve 가 없은 경우
        # When: generate_cls_if_first_time 실행
        user_sheet_answer_solve, is_created = UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.start_sheet.id,
        )

        # Then:
        self.assertIsNone(user_sheet_answer_solve)
        self.assertIsNone(is_created)

    def test_get_solved_previous_sheet_with_current_sheet_id(self):
        # Given: UserStorySolve 생성
        UserStorySolve.objects.create(
            story=self.story,
            user=self.user,
        )
        # And: start_sheet generate_cls_if_first_time 실행으로 문제를 해결하기 위한 UserSheetAnswerSolve 생성
        user_sheet_answer_solve, _ = UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.start_sheet.id,
        )
        # And: solved_sheet_action 실행
        user_sheet_answer_solve.solved_sheet_action(
            solved_sheet_answer=self.start_sheet_answer1,
            next_sheet_path=self.next_sheet_path,
        )
        # And: final Sheet로 generate_cls_if_first_time 생성
        UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.final_sheet1.id,
        )

        # When: solved_sheet_action 실행
        previous_user_sheet_answer_solves = UserSheetAnswerSolve.get_previous_user_sheet_answer_solves_with_current_sheet_id(
            user_id=self.user.id,
            current_sheet_id=self.final_sheet1.id,
        )

        # Then: 이전에 푼 start_sheet 조회
        self.assertEqual(previous_user_sheet_answer_solves[0]['sheet_id'], self.start_sheet.id)

    def test_get_solved_previous_sheet_with_current_sheet_id_should_return_none_due_to_solved_sheet_deleted(self):
        # Given: UserStorySolve 생성
        UserStorySolve.objects.create(
            story=self.story,
            user=self.user,
        )
        # And: start_sheet generate_cls_if_first_time 실행으로 문제를 해결하기 위한 UserSheetAnswerSolve 생성
        user_sheet_answer_solve, _ = UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.start_sheet.id,
        )
        # And: solved_sheet_action 실행
        user_sheet_answer_solve.solved_sheet_action(
            solved_sheet_answer=self.start_sheet_answer1,
            next_sheet_path=self.next_sheet_path,
        )
        # And: start_sheet 제거
        self.start_sheet.is_deleted = True
        self.start_sheet.save()
        # And: final Sheet로 generate_cls_if_first_time 생성
        UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.final_sheet1.id,
        )

        # When: solved_sheet_action 실행
        previous_user_sheet_answer_solves = UserSheetAnswerSolve.get_previous_user_sheet_answer_solves_with_current_sheet_id(
            user_id=self.user.id,
            current_sheet_id=self.final_sheet1.id,
        )

        # Then: start_sheet 제거돼서 안보임
        self.assertEqual(list(previous_user_sheet_answer_solves), [])

    def test_get_solved_previous_sheet_with_current_sheet_id_should_return_none_due_to_not_exists(self):
        # Given: UserStorySolve 생성
        UserStorySolve.objects.create(
            story=self.story,
            user=self.user,
        )
        # And: start_sheet generate_cls_if_first_time 실행으로 문제를 해결하기 위한 UserSheetAnswerSolve 생성
        user_sheet_answer_solve, _ = UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.start_sheet.id,
        )

        # When: solved_sheet_action 실행
        previous_user_sheet_answer_solves = UserSheetAnswerSolve.get_previous_user_sheet_answer_solves_with_current_sheet_id(
            user_id=self.user.id,
            current_sheet_id=self.start_sheet.id,
        )

        # Then: start_sheet 에서 시작해서 이전에 푼 문제 자체가 없어서 None 반환
        self.assertEqual(list(previous_user_sheet_answer_solves), [])


class StoryEmailSubscriptionMethodTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )

    @freeze_time('2022-05-31')
    def test_has_respondent_user(self):
        # Given: StoryEmailSubscription 생성
        test_emails = ['test1@example.com', 'test2@example.com']
        for test_email in test_emails:
            StoryEmailSubscription.objects.create(
                story_id=self.story.id,
                respondent_user_id=self.user.id,
                email=test_email,
            )

        # Except: 있기 때문에 True 반환
        self.assertTrue(StoryEmailSubscription.has_respondent_user(self.story.id, self.user.id))
