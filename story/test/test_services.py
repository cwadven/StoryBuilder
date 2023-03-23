from unittest.mock import MagicMock

from django.test import TestCase

from account.models import User
from config.common.exception_codes import StartingSheetDoesNotExists, SheetDoesNotExists, SheetNotAccessibleException, \
    StoryDoesNotExists
from config.test_helper.helper import LoginMixin
from story.models import Story, Sheet, SheetAnswer, NextSheetPath, UserSheetAnswerSolve, UserStorySolve, \
    StoryEmailSubscription, StoryLike, PopularStory
from story.services import (
    get_running_start_sheet_by_story,
    get_sheet_answers,
    get_valid_answer_info_with_random_quantity,
    get_sheet_answer_with_next_path_responses, get_running_sheet, validate_user_playing_sheet,
    get_sheet_solved_user_sheet_answer, get_recent_played_sheet_by_story_id, get_story_email_subscription_emails,
    create_story_like, update_story_total_like_count, delete_story_like, get_active_stories, get_active_story_by_id,
    get_active_popular_stories,
)


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

    def test_get_running_sheet_should_fail_when_story_is_deleted(self):
        # Given: Story 가 삭제된 경우
        self.story.is_deleted = True
        self.story.save()

        # When: get_running_sheet 요청
        # Then: Sheet 조회 실패
        with self.assertRaises(SheetDoesNotExists):
            get_running_sheet(self.story.sheet_set.all()[0].id)

    def test_get_running_sheet_should_fail_when_story_is_not_displayable(self):
        # Given: Story 가 displayable 가 False 인 경우
        self.story.displayable = False
        self.story.save()

        # When: get_running_sheet 요청
        # Then: Sheet 조회 실패
        with self.assertRaises(SheetDoesNotExists):
            get_running_sheet(self.story.sheet_set.all()[0].id)

    def test_get_running_sheet_should_fail_when_sheet_is_deleted(self):
        # Given: Sheet 가 is_deleted 가 True 인 경우
        sheet = Sheet.objects.get(id=self.story.sheet_set.all()[0].id)
        sheet.is_deleted = True
        sheet.save()

        # When: get_running_sheet 요청
        # Then: Sheet 조회 실패
        with self.assertRaises(SheetDoesNotExists):
            get_running_sheet(self.story.sheet_set.all()[0].id)

    def test_get_running_sheet_should_success(self):
        # When: get_running_sheet 요청
        sheet = get_running_sheet(self.story.sheet_set.all()[0].id)

        # Then: Sheet 조회 성공
        self.assertEqual(sheet.id, self.story.sheet_set.all()[0].id)


class GetSheetAnswerTestCase(TestCase):
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
        self.final_sheet1_answer1 = SheetAnswer.objects.create(
            sheet=self.final_sheet1,
            answer='final_sheet_answer1',
            answer_reply='final_sheet_answer1',
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

    def test_get_sheet_answers(self):
        # Given:
        # When: Sheet의 정답을 가져옵니다.
        answers = get_sheet_answers(self.start_sheet.id)

        # Then: start_sheet_answer1 와 start_sheet_answer2 의 answer 값이 있습니다.
        self.assertTrue(self.start_sheet_answer1.answer in answers)
        self.assertTrue(self.start_sheet_answer2.answer in answers)

    def test_get_sheet_answer_with_next_path_responses_should_success(self):
        # Given:
        # When: Sheet의 정답을 SheetAnswerResponse 형태로 가져옵니다.
        sheet_answer_responses = get_sheet_answer_with_next_path_responses(self.start_sheet.id)

        # When: Sheet의 정답을 SheetAnswerResponse 형태로 요청합니다.
        self.assertEqual(sheet_answer_responses[0].id, self.start_sheet_answer1.id)
        self.assertEqual(sheet_answer_responses[1].id, self.start_sheet_answer2.id)

    def test_get_sheet_answer_with_next_path_responses_should_fail_when_sheet_is_deleted(self):
        # Given: Sheet 가 삭제됐을 경우
        self.start_sheet.is_deleted = True
        self.start_sheet.save()

        # When: Sheet의 정답을 SheetAnswerResponse 형태로 요청합니다.
        # Then: Sheet 삭제되어서 Error 반환
        with self.assertRaises(SheetDoesNotExists):
            get_sheet_answer_with_next_path_responses(self.start_sheet.id)

    def test_get_sheet_answer_with_next_path_responses_should_fail_when_story_is_deleted(self):
        # Given:
        self.start_sheet.story.is_deleted = True
        self.start_sheet.story.save()

        # When: Sheet의 정답을 SheetAnswerResponse 형태로 요청합니다.
        # Then: Story 삭제되어서 Error 반환
        with self.assertRaises(SheetDoesNotExists):
            get_sheet_answer_with_next_path_responses(self.start_sheet.id)

    def test_get_sheet_answer_with_next_path_responses_should_fail_when_story_not_displayable(self):
        # Given:
        self.start_sheet.story.displayable = False
        self.start_sheet.story.save()

        # When: Sheet의 정답을 SheetAnswerResponse 형태로 요청합니다.
        # Then: Story 삭제되어서 Error 반환
        with self.assertRaises(SheetDoesNotExists):
            get_sheet_answer_with_next_path_responses(self.start_sheet.id)

    def test_get_valid_answer_info_with_random_quantity_should_success_when_answer_is_valid(self):
        # Given: SheetAnswer 에 final_sheet1 을 바라보는 NextSheetPath 를 추가합니다. quantity 10
        possible_next_sheet_path = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet1,
            quantity=10,
        )
        # And: SheetAnswer 에 final_sheet2 을 바라보는 NextSheetPath 를 추가합니다. quantity 0
        NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet2,
            quantity=0,
        )
        # And: sheet answer response 를 가져옵니다.
        sheet_answer_response = get_sheet_answer_with_next_path_responses(self.start_sheet.id)

        # When: 정답 및 랜덤 값들을 가져옵니다.
        is_valid, sheet_answer_id, next_sheet_path_id, next_sheet_id = get_valid_answer_info_with_random_quantity(
            answer=self.start_sheet_answer1.answer,
            answer_responses=sheet_answer_response,
        )

        # Then: 정답이 맞습니다.
        self.assertTrue(is_valid)
        # And: 맞춘 정답의 id 를 가져옵니다.
        self.assertEqual(sheet_answer_id, self.start_sheet_answer1.id)
        # And: quantity 가 10 인 next_sheet_id 를 가져옵니다
        # 0 은 가능성 이 없기 때문에 랜덤으로 안가져와 집니다.
        self.assertEqual(next_sheet_id, possible_next_sheet_path.sheet_id)
        # And: next_sheet_path id 를 가져옵니다
        self.assertEqual(next_sheet_path_id, possible_next_sheet_path.id)

    def test_get_valid_answer_info_with_random_quantity_should_success_when_answer_is_valid_but_next_path_is_not_exists(self):
        # Given: NextSheetPath 가 없는 sheet 문제를 해결했을 경우
        sheet_answer_response = get_sheet_answer_with_next_path_responses(self.final_sheet1.id)

        # When: 정답 및 랜덤 값들을 가져옵니다.
        is_valid, sheet_answer_id, next_sheet_path_id, next_sheet_id = get_valid_answer_info_with_random_quantity(
            answer=self.final_sheet1_answer1.answer,
            answer_responses=sheet_answer_response,
        )

        # Then: 정답이 맞습니다.
        self.assertTrue(is_valid)
        # And: NextSheetPaht는 없지만 정답을 가지고 있기 때문에 정답 반환
        self.assertEqual(sheet_answer_id, self.final_sheet1_answer1.id)
        # And: None 을 반환합니다.
        self.assertIsNone(next_sheet_id)
        # And: None 을 반환합니다.
        self.assertIsNone(next_sheet_path_id)

    def test_get_valid_answer_info_with_random_quantity_should_fail_when_answer_is_invalid(self):
        # Given: SheetAnswer 에 final_sheet1 을 바라보는 NextSheetPath 를 추가합니다. quantity 10
        NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet1,
            quantity=10,
        )
        # And: SheetAnswer 에 final_sheet2 을 바라보는 NextSheetPath 를 추가합니다. quantity 0
        NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet2,
            quantity=0,
        )
        # And: sheet answer response 를 가져옵니다.
        sheet_answer_response = get_sheet_answer_with_next_path_responses(self.start_sheet.id)

        # When: 없는 정답으로 정답 및 랜덤 값들을 가져옵니다.
        is_valid, sheet_answer_id, next_sheet_path_id, next_sheet_id = get_valid_answer_info_with_random_quantity(
            answer='wrong_answer',
            answer_responses=sheet_answer_response,
        )

        # Then: 정답이 틀렸습니다
        self.assertFalse(is_valid)
        # And: 정답을 맞추지 못해 None 입니다.
        self.assertIsNone(sheet_answer_id)
        # And: 정답을 맞추지 못해 None 입니다.
        self.assertIsNone(next_sheet_id)
        # And: 정답을 맞추지 못해 None 입니다.
        self.assertIsNone(next_sheet_path_id)


class ValidateUserPlayingSheetTestCase(LoginMixin, TestCase):
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

    def test_validate_user_playing_sheet_should_not_raise_error_when_user_solved_before_answer(self):
        # Given: final_sheet1 으로 가기 위해서 문제 해결을 한 것 처럼 UserSheetAnswerSolve 생성
        UserSheetAnswerSolve.objects.create(
            user=self.user,
            story=self.story,
            sheet=self.start_sheet,
            next_sheet_path=self.next_sheet_path,
            solved_sheet_version=1,
            solved_answer_version=1,
            solving_status='solved',
            answer=self.start_sheet_answer1.answer
        )

        # Expected: 에러 없이 성공
        validate_user_playing_sheet(self.user.id, self.final_sheet1)
        
    def test_validate_user_playing_sheet_should_raise_error_when_answer_has_been_modify(self):
        # Given: final_sheet1 으로 가기 위해서 문제 해결을 한 것 처럼 UserSheetAnswerSolve 생성
        UserSheetAnswerSolve.objects.create(
            user=self.user,
            story=self.story,
            sheet=self.start_sheet,
            next_sheet_path=self.next_sheet_path,
            solved_sheet_version=1,
            solved_answer_version=1,
            solving_status='solving',
            answer=self.start_sheet_answer1.answer
        )
        # And: 문제의 답이 달라졌을 경우
        self.start_sheet_answer1.answer = 'change'
        self.start_sheet_answer1.save()

        # Expected: 에러 반환
        with self.assertRaises(SheetNotAccessibleException):
            validate_user_playing_sheet(self.user.id, self.final_sheet1)

    def test_validate_user_playing_sheet_should_raise_error_when_user_not_solved(self):
        # Expected: 사용자가 final_sheet1 로 가는 문제를 풀적이 없기 때문에 에러 반환
        with self.assertRaises(SheetNotAccessibleException):
            validate_user_playing_sheet(self.user.id, self.final_sheet1)


class GetSheetSolvedUserSheetAnswerTestCase(LoginMixin, TestCase):
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
        self.final_sheet1 = Sheet.objects.create(
            story=self.story,
            title='test_title1',
            question='test_question1',
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
        self.user_sheet_answer_solve = UserSheetAnswerSolve.objects.create(
            user=self.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=self.start_sheet.version,
            solved_answer_version=self.start_sheet_answer1.version,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
            next_sheet_path=self.next_sheet_path,
            answer=self.start_sheet_answer1,
        )
        self.user_story_solve = UserStorySolve.objects.get_or_create(
            story_id=self.story.id,
            user=self.user,
        )

    def test_get_sheet_solved_user_sheet_answer_should_return_none_when_sheet_is_solved_but_sheet_version_is_changed(self):
        # Given: sheet version 변경
        self.start_sheet.version = 9
        self.start_sheet.save()

        # When: 함수 실행
        sheet_solved_user_sheet_answer = get_sheet_solved_user_sheet_answer(self.user.id, self.start_sheet.id)
        # Then:
        self.assertIsNone(sheet_solved_user_sheet_answer)

    def test_get_sheet_solved_user_sheet_answer_should_return_user_sheet_answer_when_sheet_has_been_solved(self):
        # Given: solved 생성
        # When: 함수 실행
        sheet_solved_user_sheet_answer = get_sheet_solved_user_sheet_answer(self.user.id, self.start_sheet.id)
        # Then:
        self.assertEqual(sheet_solved_user_sheet_answer.id, self.user_sheet_answer_solve.id)

    def test_get_sheet_solved_user_sheet_answer_should_return_none_when_sheet_is_not_solved(self):
        # Given: solving 으로 변경
        user_sheet_answer_solve = UserSheetAnswerSolve.objects.get(id=self.user_sheet_answer_solve.id)
        user_sheet_answer_solve.solving_status = UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[0][0]
        user_sheet_answer_solve.save()
        # When: 함수 실행
        sheet_solved_user_sheet_answer = get_sheet_solved_user_sheet_answer(self.user.id, self.start_sheet.id)
        # Then: 없기 때문에 None 반환
        self.assertIsNone(sheet_solved_user_sheet_answer)

    def test_get_recent_played_sheet_by_story_id(self):
        # Given: start_sheet 해결한 UserSheetAnswer 생성
        self.user_sheet_answer_solve = UserSheetAnswerSolve.objects.create(
            user=self.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=self.start_sheet.version,
            solved_answer_version=self.start_sheet_answer1.version,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
            next_sheet_path=self.next_sheet_path,
            answer=self.start_sheet_answer1,
        )
        # And: 다음 sheet path 를 생성
        user_sheet_answer_solve, _ = UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.next_sheet_path.sheet.id,
        )

        # When:
        recent_unsolved_sheet = get_recent_played_sheet_by_story_id(self.user.id, self.story.id)

        # Then: next_sheet_path 는 아직 풀지 못한 sheet 입니다.
        self.assertEqual(recent_unsolved_sheet.id, self.next_sheet_path.sheet.id)

    def test_get_recent_played_sheet_by_story_id_should_return_none_when_recent_sheet_has_been_deleted(self):
        # Given: start_sheet 해결한 UserSheetAnswer 생성
        self.user_sheet_answer_solve = UserSheetAnswerSolve.objects.create(
            user=self.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=self.start_sheet.version,
            solved_answer_version=self.start_sheet_answer1.version,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
            next_sheet_path=self.next_sheet_path,
            answer=self.start_sheet_answer1,
        )
        # And: 다음 sheet path 를 생성
        user_sheet_answer_solve, _ = UserSheetAnswerSolve.generate_cls_if_first_time(
            self.user,
            self.next_sheet_path.sheet.id,
        )
        # next_sheet_path 제거
        self.next_sheet_path.sheet.is_deleted = True
        self.next_sheet_path.sheet.save()

        # When:
        recent_unsolved_sheet = get_recent_played_sheet_by_story_id(self.user.id, self.story.id)

        # Then: next_sheet_path 는 아직 풀지 못한 sheet 입니다.
        self.assertIsNone(recent_unsolved_sheet)


class GetStoryEmailSubscriptionEmailsTestCase(LoginMixin, TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )

    def test_get_story_email_subscription_emails(self):
        # Given: StoryEmailSubscription 생성
        test_emails = ['test1@example.com', 'test2@example.com']
        for test_email in test_emails:
            StoryEmailSubscription.objects.create(
                story_id=self.story.id,
                respondent_user_id=self.user.id,
                email=test_email,
            )

        # When: 함수 실행
        story_email_subscription_emails = get_story_email_subscription_emails(self.story.id, self.user.id)

        # Then:
        self.assertEqual(len(story_email_subscription_emails), 2)
        self.assertIn(test_emails[0], story_email_subscription_emails)
        self.assertIn(test_emails[1], story_email_subscription_emails)


class CreateStoryLikeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )

    def test_create_story_like_when_first_creation(self):
        # Given: 처음 Like 생성
        self.assertEqual(self.story.like_count, 0)

        # When: 함수 실행
        story_like = create_story_like(self.story.id, self.user.id)

        # Then:
        self.story.refresh_from_db()
        self.assertTrue(StoryLike.objects.filter(id=story_like.id, is_deleted=False).exists())
        self.assertEqual(self.story.like_count, 1)
        self.assertEqual(story_like.user_id, self.user.id)
        self.assertEqual(story_like.story_id, self.story.id)

    def test_create_story_like_when_not_first_creation(self):
        # Given: 처음 Like 제거로 생성
        story_like = create_story_like(self.story.id, self.user.id)
        self.story.refresh_from_db()
        self.assertEqual(self.story.like_count, 1)
        story_like.is_deleted = True
        story_like.save()
        # And: 좋아요 개수 초기화
        self.story.like_count = 0
        self.story.save()

        # When: 함수 실행
        new_story_like = create_story_like(self.story.id, self.user.id)

        # Then:
        self.story.refresh_from_db()
        self.assertTrue(StoryLike.objects.filter(id=new_story_like.id, is_deleted=False).exists())
        self.assertEqual(self.story.like_count, 1)
        self.assertEqual(story_like.user_id, self.user.id)
        self.assertEqual(story_like.story_id, self.story.id)


class DeleteStoryLikeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )

    def test_delete_story_like(self):
        # Given: 처음 Like 생성
        create_story_like(self.story.id, self.user.id)
        self.story.refresh_from_db()
        self.assertEqual(self.story.like_count, 1)

        # When: 함수 실행
        story_like = delete_story_like(self.story.id, self.user.id)

        # Then:
        self.story.refresh_from_db()
        self.assertTrue(StoryLike.objects.filter(id=story_like.id, is_deleted=True).exists())
        self.assertEqual(self.story.like_count, 0)
        self.assertEqual(story_like.user_id, self.user.id)
        self.assertEqual(story_like.story_id, self.story.id)


class UpdateStoryLikeCountTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )

    def test_update_story_total_like_count(self):
        # Given: StoryLike 생성
        StoryLike.objects.create(
            user=self.user,
            story=self.story,
        )
        # And: like_count 가 0
        self.assertEqual(self.story.like_count, 0)

        # When: 함수 실행
        update_story_total_like_count(self.story.id)

        # Then: 개수 1 증가
        self.story.refresh_from_db()
        self.assertEqual(self.story.like_count, 1)


class GetActiveStoriesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
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

    def test_get_active_stories(self):
        # Given: setUp 에서 3개 Story 생성
        active_stories = get_active_stories()

        # Expect: 1개만 active
        self.assertIsInstance(active_stories, list)
        self.assertTrue(len(active_stories) == 1)
        self.assertTrue(active_stories[0].id, self.active_story.id)

    def test_get_active_stories_by_search(self):
        # Given: active_story 생성
        active_story2 = Story.objects.create(
            author=self.user,
            title='test_aa',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )

        # When:
        active_stories = get_active_stories(search='test_a')

        # Then: 1개 조회
        self.assertIsInstance(active_stories, list)
        self.assertTrue(len(active_stories) == 1)
        self.assertTrue(active_stories[0].id, active_story2.id)

        # When:
        active_stories = get_active_stories(search='description')

        # Then: 2개 조회
        self.assertIsInstance(active_stories, list)
        self.assertTrue(len(active_stories) == 2)
        self.assertTrue(active_stories[0].id, active_story2.id)
        self.assertTrue(active_stories[1].id, self.active_story.id)


class TestGetActiveStoryById(TestCase):
    def setUp(self):
        self.story1 = Story.objects.create(is_deleted=False, displayable=True)
        self.story2 = Story.objects.create(is_deleted=True, displayable=True)
        self.story3 = Story.objects.create(is_deleted=False, displayable=False)
        self.story4 = Story.objects.create(is_deleted=True, displayable=False)

    def test_get_active_story_by_id(self):
        # Given:
        # When: 조회
        active_story = get_active_story_by_id(self.story1.id)

        # Then: 1번 story 조회
        self.assertEqual(active_story, self.story1)

    def test_story_does_not_exist(self):
        # Given:
        # Expect: is_deleted True
        with self.assertRaises(StoryDoesNotExists):
            get_active_story_by_id(self.story2.id)
        # Expect: displayable False
        with self.assertRaises(StoryDoesNotExists):
            get_active_story_by_id(self.story3.id)
        # Expect: is_deleted True
        with self.assertRaises(StoryDoesNotExists):
            get_active_story_by_id(self.story4.id)


class GetActivePopularStoriesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
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

    def test_get_active_popular_stories(self):
        # Given: setUp 에서 4개 PopularStory 생성
        # self.popular_story: story 정상
        # self.displayable_false_popular_story: story 가 displayable False
        # self.deleted_popular_story_by_story: story 가 is_deleted True
        # self.deleted_popular_story: popular story 가 is_deleted True
        active_popular_stories = get_active_popular_stories()

        # Expect: 1개만 active
        self.assertIsInstance(active_popular_stories, list)
        self.assertTrue(len(active_popular_stories) == 1)
        self.assertTrue(active_popular_stories[0].id, self.popular_story.id)
