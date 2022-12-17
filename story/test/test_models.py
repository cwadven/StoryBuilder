from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time

from account.models import User
from story.models import Sheet, Story, SheetAnswer, NextSheetPath, UserSheetAnswerSolve


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
            answer=self.start_sheet_answer1.answer,
            solved_sheet_version=self.start_sheet.version,
            solved_answer_version=self.start_sheet_answer1.version,
            next_sheet_path=self.next_sheet_path,
        )

        # Then:
        self.assertEqual(user_sheet_answer_solve.solving_status, UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0])
        self.assertEqual(user_sheet_answer_solve.solved_time, datetime.now())
        self.assertEqual(user_sheet_answer_solve.answer, self.start_sheet_answer1.answer)
        self.assertEqual(user_sheet_answer_solve.solved_sheet_version, self.start_sheet.version)
        self.assertEqual(user_sheet_answer_solve.solved_answer_version, self.start_sheet_answer1.version)
        self.assertEqual(user_sheet_answer_solve.next_sheet_path, self.next_sheet_path)
