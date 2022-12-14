import json
from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time

from account.models import User
from config.test_helper.helper import LoginMixin
from story.models import Story, Sheet, SheetAnswer, NextSheetPath, UserStorySolve, UserSheetAnswerSolve


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
        # Given: Story ??? ????????? ??????
        self.story.is_deleted = True
        self.story.save()
        # And: ?????????
        self.login()

        # When: story_play ??????
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story ?????? ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ????????? ??? ????????????.')

    def test_get_story_play_api_should_fail_when_story_is_not_displayable(self):
        # Given: Story ??? displayable ??? False ??? ??????
        self.story.displayable = False
        self.story.save()
        # And: ?????????
        self.login()

        # When: story_play ??????
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story ?????? ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ????????? ??? ????????????.')

    def test_get_story_play_api_should_fail_when_story_not_have_is_start_sheet(self):
        # Given: Sheet ??? is_start ??? ?????? ??????
        self.start_sheet.is_start = False
        self.start_sheet.save()
        # And: ?????????
        self.login()

        # When: story_play ??????
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story ?????? ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ????????? ??? ????????????.')

    def test_get_story_play_api_should_success_when_story_have_is_start(self):
        # Given: Sheet ??? is_start ??? ?????? ??????
        # And: ?????????
        self.login()

        # When: story_play ??????
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story ?????? ??????
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('sheet_id'), self.start_sheet.id)
        self.assertEqual(content.get('title'), self.start_sheet.title)
        self.assertEqual(content.get('question'), self.start_sheet.question)
        self.assertEqual(content.get('image'), self.start_sheet.image)
        self.assertEqual(content.get('background_image'), self.start_sheet.background_image)

    def test_get_story_play_api_should_create_user_story_solve_when_user_is_authenticated(self):
        # Given: ?????????
        self.login()
        # And: ????????? UserSheetAnswerSolve ??????
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.final_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )

        # When: story_play ??????
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: Story ?????? ??????
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('sheet_id'), self.start_sheet.id)
        self.assertEqual(content.get('title'), self.start_sheet.title)
        self.assertEqual(content.get('question'), self.start_sheet.question)
        self.assertEqual(content.get('image'), self.start_sheet.image)
        self.assertEqual(content.get('background_image'), self.start_sheet.background_image)
        # And: ????????? ??? ????????? UserStorySolve ??????
        self.assertTrue(UserStorySolve.objects.filter(user=self.c.user, status=UserStorySolve.STATUS_CHOICES[0][0]).exists())

    def test_get_story_play_api_should_create_user_sheet_answer_solve_when_user_is_authenticated(self):
        # Given: ?????????
        self.login()

        # When: story_play ??????
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))

        # Then: Story ?????? ??????
        self.assertEqual(response.status_code, 200)
        # And: ????????? ??? ????????? UserSheetAnswerSolve ??????
        self.assertTrue(UserSheetAnswerSolve.objects.filter(user=self.c.user, sheet=self.start_sheet, solving_status='solving').exists())

    def test_get_story_play_api_should_raise_error_user_is_not_authenticated(self):
        # Given: ????????? ???????????????

        # When: story_play ??????
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: ????????? ?????? ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ???????????????.')

    def test_get_story_play_api_should_return_playing_sheet_answer_solved_response_when_already_user_had_been_solved_sheet(self):
        # Given: ?????????
        self.login()
        # And: ????????? ?????? ?????? ????????? ???????????? ??????
        self.c.get(reverse('story:story_play', args=[self.story.id]))
        response = self.c.post(reverse('story:submit_answer'), data={
            'sheet_id': self.start_sheet.id,
            'answer': self.start_sheet_answer1.answer,
        })
        self.assertEqual(response.status_code, 200)

        # When: story_play ??????
        response = self.c.get(reverse('story:story_play', args=[self.story.id]))
        content = json.loads(response.content)

        # Then: PlayingSheetAnswerSolvedDTO response ??????
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
        # Given: ????????? UserSheetAnswerSolve ??????
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )
        # And: Story ??????
        self.story.is_deleted = True
        self.story.save()

        # When: sheet_play ??????
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: Sheet ?????? ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ?????? Sheet ?????????.')

    def test_get_sheet_play_api_should_fail_when_story_is_not_displayable(self):
        # Given: ????????? UserSheetAnswerSolve ??????
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )
        # And: Story ??? displayable ??? False ??? ??????
        self.story.displayable = False
        self.story.save()

        # When: sheet_play ??????
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: Sheet ?????? ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ?????? Sheet ?????????.')

    def test_get_sheet_play_api_should_fail_when_sheet_is_deleted(self):
        # Given: ????????? UserSheetAnswerSolve ??????
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )
        # And: Sheet ??? is_deleted ??? ??????
        self.normal_sheet.is_deleted = True
        self.normal_sheet.save()

        # When: sheet_play ??????
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: Sheet ?????? ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ?????? Sheet ?????????.')

    def test_get_sheet_play_api_should_return_playing_sheet_dto_when_success(self):
        # Given: ????????? UserSheetAnswerSolve ??????
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )

        # When: sheet_play ??????
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: Sheet ?????? ??????
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('sheet_id'), self.normal_sheet.id)
        self.assertEqual(content.get('title'), self.normal_sheet.title)
        self.assertEqual(content.get('question'), self.normal_sheet.question)
        self.assertEqual(content.get('image'), self.normal_sheet.image)
        self.assertEqual(content.get('background_image'), self.normal_sheet.background_image)
        
    def test_get_sheet_play_api_should_create_user_sheet_answer_solve_when_success(self):
        # Given: ?????? sheet??? ???????????? ??? ????????? ?????? UserSheetAnswerSolve ??????
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.normal_sheet,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solved',
        )

        # When: sheet_play ??????
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))

        # Then: Sheet ?????? ??????
        self.assertEqual(response.status_code, 200)
        # And: UserSheetAnswerSolve ??????
        self.assertTrue(UserSheetAnswerSolve.objects.filter(user=self.c.user, sheet=self.normal_sheet, solving_status='solving').exists())

    def test_get_sheet_play_api_should_raise_error_user_is_not_authenticated(self):
        # Given: ????????? ???????????????
        self.logout()

        # When: sheet_play ??????
        response = self.c.get(reverse('story:sheet_play', args=[self.normal_sheet.id]))
        content = json.loads(response.content)

        # Then: ????????? ?????? ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ???????????????.')

    def test_get_sheet_play_api_should_return_playing_sheet_answer_solved_response_when_already_user_had_been_solved_sheet(self):
        # Given: ??? story ??? ??? sheet ?????? ??????
        self.c.get(reverse('story:story_play', args=[self.story.id]))
        response = self.c.post(reverse('story:submit_answer'), data={
            'sheet_id': self.start_sheet.id,
            'answer': self.start_sheet_answer1.answer,
        })
        self.assertEqual(response.status_code, 200)
        # And: ????????? ?????? ??????
        self.c.get(reverse('story:sheet_play', args=[self.start_sheet_answer_next_sheet_path1.sheet_id]))
        self.c.post(reverse('story:submit_answer'), data={
            'sheet_id': self.start_sheet_answer_next_sheet_path1.sheet_id,
            'answer': self.normal_sheet_answer1.answer,
        })

        # When: sheet_play ?????????
        response = self.c.get(reverse('story:sheet_play', args=[self.start_sheet_answer_next_sheet_path1.sheet_id]))
        content = json.loads(response.content)

        # Then: PlayingSheetAnswerSolvedDTO response ??????
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
        # Given: start_sheet_answer1 ????????? sheet_id ??????
        # And: ????????? UserSheetAnswerSolve ??????
        user_sheet_answer_solve = _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.final_sheet1,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solving',
        )
        # When: submit_answer ??????
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: ?????? ??????
        self.assertEqual(response.status_code, 200)
        # And: ????????? ???
        self.assertTrue(content.get('is_valid'))
        # And: ????????? start_sheet_answer1 ?????? ????????? ?????? quantity 10??? final_sheet1 ??? ??????
        self.assertEqual(content.get('next_sheet_id'), self.final_sheet1.id)
        # And: ?????? ?????? ??????
        self.assertEqual(content.get('answer_reply'), self.start_sheet_answer1.answer_reply)
        # And: UserSheetAnswerSolve solved ??? ??????
        self.assertEqual(UserSheetAnswerSolve.objects.get(id=user_sheet_answer_solve.id).solving_status, 'solved')
        # And: ?????? ?????? ??????
        self.assertEqual(
            UserSheetAnswerSolve.objects.get(id=user_sheet_answer_solve.id).solved_time.strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    @freeze_time('2022-01-01')
    def test_get_story_next_sheet_when_answer_is_valid_but_one_more_submit_answer(self):
        # Given: start_sheet_answer1 ????????? sheet_id ??????
        # And: ????????? UserSheetAnswerSolve ??????
        _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.final_sheet1,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solving',
        )
        self.c.post(reverse('story:submit_answer'), data=self.request_data)

        # When: submit_answer ??????
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: ?????? ????????? ????????? ????????? ?????? ????????? ????????? ?????? ??? ??? ????????????.
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('message'), '?????? ????????? ????????? ????????? ????????????.')

    @freeze_time('2022-01-01')
    def test_get_story_answer_reply_when_next_sheet_path_is_not_exists_but_answer_is_valid(self):
        # Given: start_sheet_answer1 ????????? sheet_id ??????
        # And: ????????? UserSheetAnswerSolve ??????
        user_sheet_answer_solve = _generate_user_sheet_answer_solve_with_next_path(
            user=self.c.user,
            story=self.story,
            current_sheet=self.start_sheet,
            next_sheet=self.final_sheet1,
            sheet_answer=self.start_sheet_answer1,
            solving_status='solving',
        )
        # And: next_sheet_path ?????? ??????
        self.start_sheet_answer1.next_sheet_paths.all().delete()
        
        # When: submit_answer ??????
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: ?????? ??????
        self.assertEqual(response.status_code, 200)
        # And: ????????? ???
        self.assertTrue(content.get('is_valid'))
        # And: next_sheet_path ??? ?????? None ??????
        self.assertIsNone(content.get('next_sheet_id'))
        # And: ?????? ?????? ??????
        self.assertEqual(content.get('answer_reply'), self.start_sheet_answer1.answer_reply)
        # And: UserSheetAnswerSolve solved ??? ??????
        self.assertEqual(UserSheetAnswerSolve.objects.get(id=user_sheet_answer_solve.id).solving_status, 'solved')
        # And: ?????? ?????? ??????
        self.assertEqual(
            UserSheetAnswerSolve.objects.get(id=user_sheet_answer_solve.id).solved_time.strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def test_get_story_next_sheet_when_answer_is_invalid(self):
        # Given: sheet_id ??? ?????? ?????? ??????
        self.request_data['answer'] = '??????'

        # When: submit_answer ??????
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: ?????? ??????
        self.assertTrue(response.status_code, 200)
        # And: ????????? ??????
        self.assertFalse(content.get('is_valid'))
        # And: ????????? ???????????? None ??????
        self.assertIsNone(content.get('next_sheet_id'))
        self.assertIsNone(content.get('answer_reply'))

    def test_get_story_next_sheet_should_fail_when_sheet_is_deleted(self):
        # Given: sheet ?????? ?????? ??????
        self.start_sheet.is_deleted = True
        self.start_sheet.save()

        # When: submit_answer ??????
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: Sheet ??????????????? Error ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ?????? Sheet ?????????.')

    def test_get_story_next_sheet_should_fail_when_story_is_not_displayable(self):
        # Given: sheet ?????? ?????? ??????
        self.start_sheet.story.displayable = False
        self.start_sheet.story.save()

        # When: submit_answer ??????
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: Story ?????? ????????? Error ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ?????? Sheet ?????????.')

    def test_get_story_next_sheet_should_fail_when_story_is_deleted(self):
        # Given: sheet ?????? ?????? ??????
        self.start_sheet.story.is_deleted = True
        self.start_sheet.story.save()

        # When: submit_answer ??????
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: Story ???????????? ????????? Error ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ?????? Sheet ?????????.')

    def test_get_story_next_sheet_should_raise_error_user_is_not_authenticated(self):
        # Given: ????????? ???????????????
        self.logout()

        # When: submit_answer ??????
        response = self.c.post(reverse('story:submit_answer'), data=self.request_data)
        content = json.loads(response.content)

        # Then: ????????? ?????? ??????
        self.assertEqual(response.status_code, 400)
        self.assertEqual(content.get('error'), '???????????? ???????????????.')
