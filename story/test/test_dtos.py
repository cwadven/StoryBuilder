from datetime import datetime

from django.test import TestCase

from account.models import User
from story.constants import StoryLevel
from story.dtos import SheetAnswerResponseDTO, PlayingSheetInfoDTO, PreviousSheetInfoDTO, StoryListItemDTO, \
    StoryDetailItemDTO, StoryPopularListItemDTO, UserSheetAnswerSolveHistoryItemDTO, GroupedSheetAnswerSolveDTO
from story.models import Sheet, Story, SheetAnswer, NextSheetPath, UserSheetAnswerSolve, PopularStory, \
    UserSheetAnswerSolveHistory


class DTOSheetAnswerResponseTestCase(TestCase):
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

    def test_sheet_answer_response_dto(self):
        # Given: SheetAnswerResponseDTO 에 맞는 타입 생성
        start_sheet_values = self.start_sheet.sheetanswer_set.all().values(
            'id',
            'answer',
            'answer_reply',
            'is_always_correct',
            'nextsheetpath',
            'next_sheet_paths__nextsheetpath__sheet_id',
            'next_sheet_paths__nextsheetpath__quantity',
        )

        # When: dto 객체 생성
        sheet_answer_response_dto = SheetAnswerResponseDTO.of(start_sheet_values[0])
        sheet_answer_response = sheet_answer_response_dto.to_dict()

        # Then: set dto
        self.assertEqual(sheet_answer_response.get('id'), start_sheet_values[0]['id'])
        self.assertEqual(sheet_answer_response.get('answer'), start_sheet_values[0]['answer'])
        self.assertEqual(sheet_answer_response.get('answer_reply'), start_sheet_values[0]['answer_reply'])
        self.assertEqual(sheet_answer_response.get('is_always_correct'), start_sheet_values[0]['is_always_correct'])
        self.assertEqual(sheet_answer_response.get('next_sheet_path_id'), start_sheet_values[0]['nextsheetpath'])
        self.assertEqual(sheet_answer_response.get('next_sheet_id'), start_sheet_values[0]['next_sheet_paths__nextsheetpath__sheet_id'])
        self.assertEqual(sheet_answer_response.get('next_sheet_quantity'), start_sheet_values[0]['next_sheet_paths__nextsheetpath__quantity'])


class DTOPlayingSheetInfoDTOTestCase(TestCase):
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
            solved_sheet_version=1,
            solved_answer_version=1,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[0][0],
            next_sheet_path=self.next_sheet_path,
            solved_sheet_answer=self.start_sheet_answer1,
            answer=self.start_sheet_answer1.answer,
        )

    def test_playing_sheet_answer_solved_dto(self):
        # Given:
        # When: dto 객체 생성
        playing_sheet_answer_solved_dto = PlayingSheetInfoDTO.of(
            self.start_sheet,
            self.user_sheet_answer_solve
        )
        playing_sheet_answer_solved = playing_sheet_answer_solved_dto.to_dict()

        # Then: set dto
        self.assertEqual(playing_sheet_answer_solved.get('next_sheet_id'), self.final_sheet1.id)
        self.assertEqual(playing_sheet_answer_solved.get('answer'), self.start_sheet_answer1.answer)
        self.assertEqual(playing_sheet_answer_solved.get('answer_reply'), self.start_sheet_answer1.answer_reply)
        self.assertEqual(playing_sheet_answer_solved.get('sheet_id'), self.start_sheet.id)
        self.assertEqual(playing_sheet_answer_solved.get('title'), self.start_sheet.title)
        self.assertEqual(playing_sheet_answer_solved.get('question'), self.start_sheet.question)
        self.assertEqual(playing_sheet_answer_solved.get('image'), self.start_sheet.image)
        self.assertEqual(playing_sheet_answer_solved.get('background_image'), self.start_sheet.background_image)
        self.assertTrue(playing_sheet_answer_solved.get('is_solved'))

    def test_playing_sheet_answer_solved_dto_with_previous_sheet_infos(self):
        # Given:
        previous_sheet_infos = [
            PreviousSheetInfoDTO(
                sheet_id=i,
                title='test_test',
            ) for i in range(3)
        ]
        # When: dto 객체 생성
        playing_sheet_answer_solved_dto = PlayingSheetInfoDTO.of(
            self.start_sheet,
            self.user_sheet_answer_solve,
            previous_sheet_infos,
        )
        playing_sheet_answer_solved = playing_sheet_answer_solved_dto.to_dict()

        # Then: set dto
        self.assertEqual(playing_sheet_answer_solved['next_sheet_id'], self.final_sheet1.id)
        self.assertEqual(playing_sheet_answer_solved['answer'], self.start_sheet_answer1.answer)
        self.assertEqual(playing_sheet_answer_solved['answer_reply'], self.start_sheet_answer1.answer_reply)
        self.assertEqual(playing_sheet_answer_solved['sheet_id'], self.start_sheet.id)
        self.assertEqual(playing_sheet_answer_solved['title'], self.start_sheet.title)
        self.assertEqual(playing_sheet_answer_solved['question'], self.start_sheet.question)
        self.assertEqual(playing_sheet_answer_solved['image'], self.start_sheet.image)
        self.assertEqual(playing_sheet_answer_solved['background_image'], self.start_sheet.background_image)
        self.assertTrue(playing_sheet_answer_solved['is_solved'])
        self.assertEqual(playing_sheet_answer_solved['previous_sheet_infos'][0], previous_sheet_infos[0].to_dict())
        self.assertEqual(playing_sheet_answer_solved['previous_sheet_infos'][1], previous_sheet_infos[1].to_dict())
        self.assertEqual(playing_sheet_answer_solved['previous_sheet_infos'][2], previous_sheet_infos[2].to_dict())


class PreviousSheetInfoDTOTestCase(TestCase):
    def test_previous_sheet_info_dto(self):
        # Given:
        # When: dto 객체 생성
        previous_sheet_info_dto = PreviousSheetInfoDTO(
            sheet_id=1,
            title='test'
        )
        previous_sheet_info = previous_sheet_info_dto.to_dict()

        # Then: set dto
        self.assertEqual(previous_sheet_info['sheet_id'], 1)
        self.assertEqual(previous_sheet_info['title'], 'test')


class StoryListItemDTOTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )

    def test_story_list_item_dto(self):
        # Given:
        # When: dto 객체 생성
        story_list_item_dto = StoryListItemDTO.of(self.story)
        story_list_item = story_list_item_dto.to_dict()

        # Then: set dto
        self.assertEqual(story_list_item['id'], self.story.id)
        self.assertEqual(story_list_item['title'], self.story.title)
        self.assertEqual(story_list_item['description'], self.story.description)
        self.assertEqual(story_list_item['image'], self.story.image)
        self.assertEqual(story_list_item['background_image'], self.story.background_image)


class StoryPopularListItemDTOTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.popular_story = PopularStory.objects.create(
            story=self.story,
            rank=1,
            like_count=1,
            base_past_second=1,
        )

    def test_popular_story_list_item_dto(self):
        # Given:
        # When: dto 객체 생성
        story_popular_list_item_dto = StoryPopularListItemDTO.of(self.popular_story)
        story_popular_list_item = story_popular_list_item_dto.to_dict()

        # Then: set dto
        self.assertEqual(story_popular_list_item['story_id'], self.story.id)
        self.assertEqual(story_popular_list_item['title'], self.story.title)
        self.assertEqual(story_popular_list_item['image'], self.story.image)

    def test_popular_story_list_item_dto_by_story(self):
        # Given:
        # When: dto 객체 생성
        story_popular_list_item_dto = StoryPopularListItemDTO.by_story(self.story)
        story_popular_list_item = story_popular_list_item_dto.to_dict()

        # Then: set dto
        self.assertEqual(story_popular_list_item['story_id'], self.story.id)
        self.assertEqual(story_popular_list_item['title'], self.story.title)
        self.assertEqual(story_popular_list_item['image'], self.story.image)


class StoryDetailItemDTOTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
            level=2,
        )

    def test_story_list_item_dto(self):
        # Given:
        is_liked = True

        # When: dto 객체 생성
        story_list_item_dto = StoryDetailItemDTO.of(self.story, is_liked=is_liked)
        story_list_item = story_list_item_dto.to_dict()

        # Then: set dto
        self.assertEqual(story_list_item['id'], self.story.id)
        self.assertEqual(story_list_item['title'], self.story.title)
        self.assertEqual(story_list_item['description'], self.story.description)
        self.assertEqual(story_list_item['image'], self.story.image)
        self.assertEqual(story_list_item['background_image'], self.story.background_image)
        self.assertEqual(story_list_item['played_count'], self.story.played_count)
        self.assertEqual(story_list_item['like_count'], self.story.like_count)
        self.assertEqual(story_list_item['review_rate'], self.story.review_rate)
        self.assertEqual(story_list_item['playing_point'], self.story.playing_point)
        self.assertEqual(story_list_item['free_to_play_sheet_count'], self.story.free_to_play_sheet_count)
        self.assertEqual(story_list_item['level'], StoryLevel(self.story.level).selector)
        self.assertEqual(story_list_item['is_liked'], is_liked)


class UserSheetAnswerSolveHistoryItemDTOTestCase(TestCase):
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
            solved_sheet_version=1,
            solved_answer_version=1,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[0][0],
            next_sheet_path=self.next_sheet_path,
            solved_sheet_answer=self.start_sheet_answer1,
            answer=self.start_sheet_answer1.answer,
        )
        self.user_sheet_answer_solve_history = UserSheetAnswerSolveHistory.objects.create(
            group_id=1,
            user=self.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=1,
            solved_answer_version=1,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[0][0],
            next_sheet_path=self.next_sheet_path,
            solved_sheet_answer=self.start_sheet_answer1,
            answer=self.start_sheet_answer1.answer,
            start_time=datetime(2022, 1, 1),
            solved_time=datetime(2022, 1, 1),
        )

    def test_user_sheet_answer_solve_history_item_dto(self):
        # Given
        # When: dto 객체 생성
        user_sheet_answer_solve_history_item_dto = UserSheetAnswerSolveHistoryItemDTO.of(self.user_sheet_answer_solve_history)
        user_sheet_answer_solve_history_item = user_sheet_answer_solve_history_item_dto.to_dict()

        # Then: set dto
        self.assertEqual(user_sheet_answer_solve_history_item['group_id'], self.user_sheet_answer_solve_history.group_id)
        self.assertEqual(user_sheet_answer_solve_history_item['sheet_title'], self.user_sheet_answer_solve_history.sheet.title)
        self.assertEqual(user_sheet_answer_solve_history_item['sheet_question'], self.user_sheet_answer_solve_history.sheet.question)
        self.assertEqual(user_sheet_answer_solve_history_item['user_answer'], self.user_sheet_answer_solve_history.answer)
        self.assertEqual(user_sheet_answer_solve_history_item['solving_status'], self.user_sheet_answer_solve_history.solving_status)
        self.assertEqual(user_sheet_answer_solve_history_item['start_time'], self.user_sheet_answer_solve_history.start_time.strftime('%Y-%m-%d %H:%M:%S'))
        self.assertEqual(user_sheet_answer_solve_history_item['solved_time'], self.user_sheet_answer_solve_history.solved_time.strftime('%Y-%m-%d %H:%M:%S'))


class TestGroupedSheetAnswerSolveDTO(TestCase):
    def test_from_histories(self):
        user_sheet_answer_solve_history_items = [
            UserSheetAnswerSolveHistoryItemDTO(
                group_id=1,
                sheet_title="Sheet A",
                sheet_question="Question A",
                user_answer="Answer A",
                solving_status="solving",
                start_time="2023-04-24 00:31:19",
                solved_time="2023-04-24 00:31:20"
            ),
            UserSheetAnswerSolveHistoryItemDTO(
                group_id=1,
                sheet_title="Sheet B",
                sheet_question="Question B",
                user_answer="Answer B",
                solving_status="solved",
                start_time="2023-04-24 00:27:40",
                solved_time="2023-04-24 00:28:08"
            ),
            UserSheetAnswerSolveHistoryItemDTO(
                group_id=2,
                sheet_title="Sheet C",
                sheet_question="Question C",
                user_answer="Answer C",
                solving_status="solving",
                start_time="2023-04-24 00:31:19",
                solved_time="2023-04-24 00:31:20"
            ),
        ]

        grouped_dto_list = GroupedSheetAnswerSolveDTO.from_histories(user_sheet_answer_solve_history_items)

        expected_output = [
            {
                'group_id': 1,
                'sheet_answer_solve': [
                    {
                        'group_id': 1,
                        'sheet_title': 'Sheet A',
                        'sheet_question': 'Question A',
                        'user_answer': 'Answer A',
                        'solving_status': 'solving',
                        'start_time': '2023-04-24 00:31:19',
                        'solved_time': '2023-04-24 00:31:20',
                    },
                    {
                        'group_id': 1,
                        'sheet_title': 'Sheet B',
                        'sheet_question': 'Question B',
                        'user_answer': 'Answer B',
                        'solving_status': 'solved',
                        'start_time': '2023-04-24 00:27:40',
                        'solved_time': '2023-04-24 00:28:08',
                    },
                ]
            },
            {
                'group_id': 2,
                'sheet_answer_solve': [
                    {
                        'group_id': 2,
                        'sheet_title': 'Sheet C',
                        'sheet_question': 'Question C',
                        'user_answer': 'Answer C',
                        'solving_status': 'solving',
                        'start_time': '2023-04-24 00:31:19',
                        'solved_time': '2023-04-24 00:31:20',
                    },
                ]
            },
        ]

        # Convert grouped_dto_list to list of dictionaries
        actual_output = [grouped_dto.to_dict() for grouped_dto in grouped_dto_list]

        self.assertEqual(actual_output, expected_output)
